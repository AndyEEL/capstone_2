#encoding=utf-8
import torch
import main_model
import senet
import collections, torch, torchvision
import numpy as np
import os
from PIL import Image
import PIL
from torchvision import transforms, utils
from torch.autograd import Variable
from torch_utils import transformImage, getPrediction




DIR_IMAGES = '/Users/ME/Desktop/Works/Major/Business/Capston/capstone_2.7/CNN/img_Dir.txt'
IMAGE_PATH = '/Users/ME/Desktop/Works/Major/Business/Capston/capstone_2.7/CNN/Club_sandwich/Club_sandwich_0002.jpg'
LABEL_PATH = '/Users/ME/Desktop/Works/Major/Business/Capston/capstone_2.7/CNN/metadata_ISIAFood_500/ISIAFood500_classLabel.txt'
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
label = dict()

def predict():
    file = Image.open(IMAGE_PATH) # 1. load image
    tensor = transformImage(file) # 2. image -> tensor
    rate, prediction = getPrediction(tensor) # 3. prediction
    data = {'ID' : prediction.item(), 'rate' : rate }# 4. return index

    return data

def getLabel(label):
    with open(LABEL_PATH, 'r') as r:
        for line in r:
            line = line.strip()
            words = line.split()
            label[words[1]] = words[0]

# 정답 레이블 받아오기
getLabel(label)

#prediction ID 출력
prediction = predict()

#prediction 출력
print(label[str(prediction['ID'])])

