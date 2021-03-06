import io
import os
import sys
import time

import numpy as np

from cv2 import cv2
from fastapi import FastAPI
from fastapi import Request
from fastapi import File
from fastapi import UploadFile

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


IMAGE_FILE_EXT_JPG = ".jpg"
IMAGE_FILE_EXT_PNG = ".png"
INPUT_FILE_NAME = "InputFile"
OUTPUT_FILE_NAME = "OutputFile"

PATH_LABELS = "./MyFiles/Static/bdd100k.names"
PATH_CONFIG = "./MyFiles/Static/Yolov4_tiny_changes_testing1.cfg"
PATH_WEIGHT = "./MyFiles/Static/Yolov4_tiny_changes_best.weights"
CLEANUP_FOLDER = "./MyFiles/Dynamic/"

RESIZE_IMG_TO = (640, 480)

CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.1

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)


# Object of FastAPI.
App = FastAPI()

# Templates.
Templates = Jinja2Templates(directory = "HTML")

# static/js/post.index js.Required to call from html.
App.mount("/MyFiles", StaticFiles(directory="MyFiles"), name="MyFiles")


def ProcessUserFile(UserFile):
  """
  # Function to process the file ONLY with specific extensions which is uploaded by the user.
  """

  # Prepare the binary data from the uploaded file.
  BinaryData = io.BytesIO(UserFile.file.read())
  BinaryDataArray = np.asarray(bytearray(BinaryData.read()), dtype=np.uint8)
  
  # File name and the relative path to save the file.
  FullPath = CLEANUP_FOLDER + INPUT_FILE_NAME + UserFile.filename[-4:]

  # Open the file in binary mode and write the binary data into the file.
  with open(FullPath, "wb") as BinaryFile:
      # Write binary bytes to the file.
      BinaryFile.write(BinaryDataArray)


  return FullPath


def DetectRoadObjects(InputFile):
  """
  # Function to get the road objects detected with bounding boxes.
  """
  
  # Local variable(s).
  LayerNameNeedList = list()
  
  # Initialize the lists of bounding boxes, confidences and class IDs respectively.
  BoundingBoxesList = list()
  ConfidencesList = list()
  ClassIDsList = list()


  # Read the image from the input file using 'cv2'.
  OriginalRgbColorImg = cv2.imread(InputFile)

  # Resize the image to a spefied size.
  ResizedRgbColorImg = cv2.resize(OriginalRgbColorImg, RESIZE_IMG_TO)

  
  # Get the labels as a list from the labels file.
  Labels = open(PATH_LABELS).read().strip().split("\n")
  
 
  # To assign colors randomly.
  # Initialize a list of colors to represent each possible class label.
  np.random.seed(42)
  Colors = np.random.randint(0, 255, size = (len(Labels), 3), dtype = "uint8")
  
  # Load YOLOv3 object detector trained on custom i.e. bdd100k dataset (Currently 3 classes i.e. Person, Vehicle, TrafficInfo).
  Network = cv2.dnn.readNetFromDarknet(PATH_CONFIG, PATH_WEIGHT)


  # Get the image height and image width values from the resized color image.
  (ImgHeight, ImgWidth) = ResizedRgbColorImg.shape[:2]
  
  
  # Get all the *output* layer names that we have in YOLOv3.
  LayerNameFullList = Network.getLayerNames()
  print(LayerNameFullList)
  print(type(LayerNameFullList))
  print("--------------------------------------------------------")

  # Find only the *output* layer names that we need from YOLOv3.
  # Detection layer: 82
  # Detection layer: 94
  # Detection layer: 106
  for Idx in Network.getUnconnectedOutLayers():
    LayerNameNeedList.append(LayerNameFullList[Idx - 1])
  print(LayerNameNeedList)
  print(type(LayerNameNeedList))
  print("--------------------------------------------------------")
  

  # Construct a blob from the input image and then perform a forward pass of the
  # YOLO object detector, giving us our bounding boxes and associated probabilities.
  # The input to the network is a so-called blob object. 
  # blob = cv2.dnn.blobFromImage(image, scalefactor=1.0, size, mean, swapRB=True)
  Blob = cv2.dnn.blobFromImage(ResizedRgbColorImg, 1/255.0, (416, 416), swapRB=True, crop=False)
  print(Blob)
  print(type(Blob))
  print("--------------------------------------------------------")
  Network.setInput(Blob)
  print(Blob)
  print(type(Blob))
  print("--------------------------------------------------------")
  
  # Note down the start time.
  StartTime = time.time()
  LayerOutputs = Network.forward(LayerNameNeedList)
  print(LayerOutputs)
  print(type(LayerOutputs))
  print("--------------------------------------------------------")
  # Note down the end time.
  EndTime = time.time()
  # Info = "YOLO took {:.6f} seconds".format(EndTime - StartTime)


  # Loop over each of the layer outputs.
  for Output in LayerOutputs:
    # Loop over each of the detections.
    for Detection in Output:
      # Extract the class ID and confidence (i.e., probability) of the current object detection.
      Scores = Detection[5:]
      ClassID = np.argmax(Scores)
      Confidence = Scores[ClassID]

      # Filter out weak predictions by ensuring that the detected
      # probability is greater than the thershold/minimum probability.
      if Confidence > CONFIDENCE_THRESHOLD:
        # Scale the bounding box coordinates back relative to the size of the image,
        # keeping in mind that YOLO actually returns the center (x, y) coordinates of the
        # bounding box followed by the boxes' width and height.
        Box = Detection[0:4] * np.array([ImgWidth, ImgHeight, ImgWidth, ImgHeight])
        (CenterX, CenterY, Width, Height) = Box.astype("int")

        # Use the center (x, y) coordinates to derive the top and left corner of the bounding box.
        x = int(CenterX - (Width/2))
        y = int(CenterY - (Height/2))

        # Update the lists of bounding boxes, confidences and class IDs.
        BoundingBoxesList.append([x, y, int(Width), int(Height)])
        ConfidencesList.append(float(Confidence))
        ClassIDsList.append(ClassID)

  # Apply non-maxima suppression to suppress weak, overlapping bounding boxes.
  Idxs = cv2.dnn.NMSBoxes(BoundingBoxesList, ConfidencesList, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

  # Ensure at least one detection exists.
  if len(Idxs) > 0:
    # Loop over the indexes we are keeping.
    for Idx in Idxs.flatten():
      # extract the bounding box coordinates
      (x, y) = (BoundingBoxesList[Idx][0], BoundingBoxesList[Idx][1])
      (w, h) = (BoundingBoxesList[Idx][2], BoundingBoxesList[Idx][3])

      Color = [int(c) for c in Colors[ClassIDsList[Idx]]]
      # Draw a bounding box rectangle over the object.
      cv2.rectangle(ResizedRgbColorImg, (x, y), (x + w, y + h), Color, 2)
      # Draw a box to display the object name and confidence.
      cv2.rectangle(ResizedRgbColorImg, (x, y-26), (x + 180, y), Color, -1)
      # Prepare the text of object name and confidence.
      Text = "{}: {:.2f}".format(Labels[ClassIDsList[Idx]], ConfidencesList[Idx])
      cv2.putText(ResizedRgbColorImg, Text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_BLACK, 2)


  # File name and the relative path to save the file.
  FullPath = CLEANUP_FOLDER + OUTPUT_FILE_NAME + InputFile[-4:]

  # Save the image file which is having the objects detected with bounding boxes.
  cv2.imwrite(FullPath, ResizedRgbColorImg)


  return FullPath


# GET option.
@App.get('/')
def root(request:Request):
  return Templates.TemplateResponse("Input.html", context = {'request':request})


# POST option.
@App.post('/')
async def root(request:Request, UserFile: UploadFile = File(...)):
  # Clean-up the directory where we kept the processed files in previous execution.
  for FileName in os.listdir(CLEANUP_FOLDER):
      os.remove(os.path.join(CLEANUP_FOLDER, FileName))


  # Get the filename and  the file name extension of the uploaded file.
  UserFileName = UserFile.filename
  UserFileExtn = UserFileName[-4:]
  
  # Check the file extension to take appropriate action.
  if UserFileExtn == IMAGE_FILE_EXT_JPG or UserFileExtn == IMAGE_FILE_EXT_PNG:
    # If the user uploaded file is of specific type(s) then only process it.
    InputFile = ProcessUserFile(UserFile)
    # Check whether the specific file got created at the specific path or not.
    if not os.path.exists(InputFile):
      return {"Return":"File is NOT available."}


    # After confirming about the image file creation, send this file to get the road objects detected with bounding boxes.
    OutputFile = DetectRoadObjects(InputFile)
    # Check whether the specific file got created at the specific path or not.
    if not os.path.exists(OutputFile):
      return {"Return":"File is NOT available."}


    # Return the HTML page that can display the input and output images.
    return Templates.TemplateResponse("Output.html", context = {'request':request, "InputFile":InputFile, "OutputFile":OutputFile})
  else:
    return {"Return":"Unsupported File Selected."}
