### Link for the dataset :
https://drive.google.com/drive/folders/1-1RhYo6NAkyRishT9XiwOYDTmGGdMwb8?usp=sharing

### BDD100K-YOLOV4-tiny
Road Object detection on BDD100K using Yolov4-tiny-tiny trained on Jetson Xavier

### Link to the video

#### Barkeley DeepDrive Dataset
The largest open driving video dataset with 100K videos and 10 tasks to evaluate the exciting progress of image recognition algorithms on autonomous driving. Each video has 40 seconds and a high resolution. The dataset represents more than 1000 hours of driving experience with more than 100 million frames. The videos comes with GPU/IMU data for trajectory information. The dataset possesses geographic, environmental, and weather diversity, which is useful for training models that are less likely to be surprised by new conditions. The dynamic outdoor scenes and complicated ego-vehicle motion make the perception tasks even more challenging. The tasks on this dataset include image tagging, lane detection, drivable area segmentation, road object detection, semantic segmentation, instance segmentation, multi-object detection tracking, multi-object segmentation tracking, domain adaptation, and imitation learning.

Reference from BDD100k_Github

### Dependencies & Dataset
This repository requires the following dependencies and dataset

#### Python3
1. Berkeley DeepDrive Dataset - Download the Images and Labels (Total size bdd100k_images.zip - 6.8 GB)
Yolov4
2. Understanding the Dataset

After being unzipped, all the files will reside in a folder named bdd100k. All the images will reside in bdd100k/images and labels in bdd100k/labels. The images contains the frame at 10th second in the corresponding video.

bdd100k/images contains three other folders called train, test and val.
bdd100k/labels contains two json files based on the label format for training and validation sets.

#### Steps to build
* Download the dataset and unzip the image and labels. Make sure you have \train folder with ~70k images as well as labels with train json file.
* Clone the Yolov4 darknet repository. Configure the Makefile to enable training it on GPU.

1. ```git clone https://github.com/pjreddie/darknet.git```
2. ```cd darknet```
3. ```make```

* Convert the labels into a .txt format where each txt file contains label information of each image. The python script label_to_txt.py to convert this is present in the utils folder. Perform this conversion for both train and val images.
* Check if the number of txt files and the images in the train folder are same. If found unequal, use the python script missing_image_&_label.py to remove the training image if no .txt information present.
* Generate train.txt and val.txt files as required by the yolov4. Use the python script test_val_txt.py to convert.
* Copy the bdd100k.data and bdd100k.names from the \data folder to a new folder (bdd100k_data) in the darknet yolov4 main folder.

1. ```cd darknet```
2. ```mkdir bdd100k_data```

* Copy the yolov4-tiny-BDD100k.cfg from the \config folder to the same (bdd100_data) folder.
* Finally make sure you have the following files in the bdd100k_data folder.

train.txt
val.txt
bdd100k.data
bdd100k.names
yolov4-tiny-BDD100k.cfg
backup folder which stores the weights
Download the yolov4 imagenet darknet53 weights

* Run the following on terminal for training the model

1. ```cd darknet```
2. ```!./darknet detector train /content/gdrive/MyDrive/content/bdd100k/bdd100k.data /content/gdrive/MyDrive/content/Yolov4_tiny_changes.cfg /content/gdrive/MyDrive/content/bdd100k/backup/Yolov4_tiny_changes_last.weights -dont_show -map ```
Test the model performance
The yolov4 trained weights can be used to see the performance by running the following command on terminal.

1. ```cd darknet```
2. ```!./darknet detector demo /content/gdrive/MyDrive/content/bdd100k/bdd100k.data  /content/gdrive/MyDrive/content/Yolov4_tiny_changes.cfg /content/gdrive/MyDrive/content/bdd100k/backup/Yolov4_tiny_changes_last.weights -dont_show ```
/content/gdrive/MyDrive/content/bdd100k/Traffic.mp4 -i 0 -out_filename 


https://user-images.githubusercontent.com/95156513/155829352-86e0ae4c-f327-403f-a8d1-89f85403f80e.mp4

* Instruction :
1) Update Paths of cfg file, names file, best weights file in App.py. All files are in Static folder under Deployment.
1) Run App.py file that is in Deployment Folder.
2) HTML files are in HTML folder. There are two files Input.html and Output.html
3) After running App.py file web link will be there like Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
4) Enter input image on this web link
5) Now Input and Output image will be showing in this HTML page and both images has been saved under Dynamic folder of Deployment.
 


