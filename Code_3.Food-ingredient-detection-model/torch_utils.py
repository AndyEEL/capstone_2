#encoding=utf-8
import torch
import torchvision.transforms as transforms
import main_model
import numpy as np
from PIL import Image
# ToTensor() : transform 한번

# conda activate pytorch
IMAGE_PATH = '/Users/ME/Desktop/Works/Major/Business/Capston/capstone_2.7/CNN/Club_sandwich/Club_sandwich_0002.jpg'
weight_path = '/Users/ME/Desktop/Works/Major/Business/Capston/capstone_2.7/CNN/senet154-c7b49a05.pth'
model_path = '/Users/ME/Desktop/Works/Major/Business/Capston/capstone_2.7/CNN/food500_model.pth'
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


#load model
# input size, hidden size, # of classes 필요
input_size = 256
NUM_CATEGORIES = 500


#1. 모델 선언
model = main_model.MODEL(500, weight_path,multi_scale = True, learn_region=True, use_gpu= False).to(DEVICE)
optimizer = torch.optim.SGD(model.parameters(),lr = 0.0001, momentum=0.9, weight_decay=0.0001)
model.load_state_dict(torch.load(model_path, map_location=DEVICE), strict = False)

model.eval()


# image -> tensor

def myLoader(file):
    #image = Image.open(path)
    image = file.convert('RGB')
    return image

def transformImage(image_bytes):
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
    transform_img = transforms.Compose([
        transforms.Resize((256, 256)), # 256 x 256으로 resize
        transforms.CenterCrop((224, 224)),
        transforms.ToTensor(),
        normalize
    ])

    try:
        image = myLoader(image_bytes)
        image = transform_img(image).unsqueeze(0) # input image가 한개일경우
    # 이후 torch.utils.data.DataLoader 할 필요 없나? (train_loader)
    except:
        image = np.zeros((256, 256, 3), dtype=float)
        image = Image.fromarray(np.uint8(image))
        image = transform_img(image).unsqueeze(0) # input image가 한개일경우

    return image

# predict

def getPrediction(image_tensor):
    #images = image_tensor.reshape(-1, 224*224) #여기에 값 넣어야
    #outputs = model.forward(image_tensor)
    output, global_c, local_c = model(image_tensor)

    rate, prediction = torch.max(output.data, 1) # prediction index 반환

    return rate, prediction