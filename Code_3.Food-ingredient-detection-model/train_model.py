import torch.nn as nn 
import torch.optim as optim
import torch.utils.data
import torch.backends.cudnn as cudnn
import torchvision
from torchvision import transforms as transforms
import numpy as np
import torch.nn.functional as F
from torch.autograd import Variable
import torchvision.models as models
import shutil
import argparse
import os 
import PIL
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import torch
import time
import pretrainedmodels
from main_model import MODEL

os.environ.setdefault('CUDA_VISIBLE_DEVICES', '0,1')

# ==================================================================
# Constants
# ==================================================================
EPOCH         = 120            # number of times for each run-through
BATCH_SIZE    = 8            # number of images for each epoch
LEARNING_RATE = 0.0001          # default learning rate 
WEIGHT_DECAY  = 0             # default weight decay
N             = 256          # size of input images (512 or 640)
MOMENTUM      = (0.9, 0.997)  # momentum in Adam optimization 
GPU_IN_USE    = torch.cuda.is_available()  # whether using GPU
DIR_TRAIN_IMAGES   = ''
DIR_TEST_IMAGES    = ''
IMAGE_PATH = ''
PATH_MODEL_PARAMS  = './model/ISIAfood500.pth'
NUM_CATEGORIES     = 500
LOSS_OUTPUT_INTERVAL = 100
WEIGHT_PATH= ''

# ==================================================================
# Parser Initialization
# ==================================================================

## argpars를 사용하면, command line 으로 파이썬 디스크립터를 실행할 때 옵션을 주어 설정값을 쉽게 지정할 수 있음
## 예) python 파일_이름.py --lr learning_rate_value
parser = argparse.ArgumentParser(description='Pytorch Implementation of Nasnet Finetune')
parser.add_argument('--lr',              default=LEARNING_RATE,     type=float, help='learning rate')
parser.add_argument('--epoch',           default=EPOCH,             type=int,   help='number of epochs')
parser.add_argument('--trainBatchSize',  default=BATCH_SIZE,        type=int,   help='training batch size')
parser.add_argument('--testBatchSize',   default=BATCH_SIZE,        type=int,   help='testing batch size')
parser.add_argument('--weightDecay',     default=WEIGHT_DECAY,      type=float, help='weight decay')
parser.add_argument('--pathModelParams', default=PATH_MODEL_PARAMS, type=str,   help='path of model parameters')
parser.add_argument('--saveModel',       default=True,              type=bool,  help='save model parameters')
parser.add_argument('--loadModel',       default=False,             type=bool,  help='load model parameters')
parser.add_argument('--classnumble',     default=NUM_CATEGORIES,    type=int,  help='the class number of the dataset')
parser.add_argument('--weightpath',     default=WEIGHT_PATH,        type=str,  help='inint weight path')
parser.add_argument('--print_freq',     default=200,                type=int,  help='print')

args = parser.parse_args()


# ==================================================================
# Prepare Dataset(training & test)
# ==================================================================
print('***** Prepare Data ******')

## 이미지의 픽셀 하나는  0 ~ 255 범위의 값을 가짐, 이를 특정 범위의 값으로 정규화
## mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225]는 이미지넷의 이미지들을 통해 계산된 관례값이라고 함
## (관련 링트) https://stackoverflow.com/questions/58151507/why-pytorch-officially-use-mean-0-485-0-456-0-406-and-std-0-229-0-224-0-2
normalize = transforms.Normalize(mean = [0.485, 0.456, 0.406],
                                std = [0.229, 0.224, 0.225])

## 이미지를 랜덤으로 학습시키기 위하여 이미지를 조금씩 Flip, Crop을 수행한다.
## 이미지 사이즈를 N * N 으로 변형한다.
## 이미지를 텐서로 바꾼다.
## 이미지를 정규화 한다.
train_transforms = transforms.Compose([
                     transforms.RandomHorizontalFlip(p=0.5), # default value is 0.5
                     transforms.Resize((N, N)),
                     transforms.RandomCrop((224,224)),
                     transforms.ToTensor(),
                     normalize
                  ])

## 테스트 데이터셋에는 랜덤을 적용하지 않는다.
## 이미지 사이즈를 N * N 으로 변형한다.
## 이미지를 텐서로 바꾼다.
## 이미지를 정규화 한다.
test_transforms = transforms.Compose([
                    transforms.Resize((N, N)), 
                    transforms.CenterCrop((224, 224)),
                    transforms.ToTensor(),
                    normalize
                  ]) 


def My_loader(path):
    return PIL.Image.open(path).convert('RGB')
 
class MyDataset(torch.utils.data.Dataset):

    ## Constructor 파라미터: txt_dir, transform, target_transfpr,. loader
    def __init__(self, txt_dir, transform=None, target_transform=None, loader=My_loader):

        ## 이미지가 저잗되어있는 폴더 목록을 연다.
        data_txt = open(txt_dir, 'r')
        imgs = []

        ## data_txt ["이미지 이름 1", "이미지 이름 2", "이미지 이름 3"]
        for line in data_txt: ## "이미지 이름 1"
            line = line.strip()
            words = line.split() ## [이미지 이름, 1]

            imgs.append((words[0], int(words[1]))) ## (이미지 이름, (int) 숫자)

        self.imgs = imgs ## [(이미지 이름, 1), (이미지 이름, 2), (이미지 이름, 3), (이미지 이름, 4)]
        self.transform = transform ## 파라미터로 받은 transform 저장
        self.target_transform = target_transform ## 파라미터로 받은 target_transform 저장
        self.loader = My_loader  ## MY_loader 저장
 
    def __len__(self):
        return len(self.imgs) ## 이미지 개수 저장

    ## 특정 index에 있는 이미지의 이름과 번호를 찾아서 리턴
    def __getitem__(self, index):
        img_name, label = self.imgs[index] ## imgs[index] 가 (이미지 이름, 1) 일 때 img_name: 이미지 이름 / label: 1

        try:
            img = self.loader(os.path.join(IMAGE_PATH,img_name)) ## IMAGE_PATH/이미지 이름 위치의 이미지 로딩
            if self.transform is not None: ## 만약, transform 파라미터가 생성자를 통해 입력되었다면, 이미지 transform 시키기
                img = self.transform(img)
                img = self.transform(img)
        except: ## 이미지 로딩에 실패하는 경우
            img = np.zeros((256,256,3),dtype=float)
            img  = PIL.Image.fromarray(np.uint8(img))
            if self.transform is not None:
            print('erro picture:', img_name) ## "error picture 이미지 이름" 출력하고, 빈 이미지 생성
        return img, label ## 이미지와 라벨 리턴

## Dataset 로드
train_dataset = MyDataset(txt_dir=DIR_TRAIN_IMAGES , transform=train_transforms)
test_dataset = MyDataset(txt_dir=DIR_TEST_IMAGES , transform=test_transforms)
train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=40, shuffle=True,  num_workers=2)
test_loader  = torch.utils.data.DataLoader(dataset=test_dataset,  batch_size=20,  shuffle=False, num_workers=2)
print('Data Preparation : Finished')


# ==================================================================쳐
# Prepare Model
# ==================================================================
print('\n***** Prepare Model *****')

## 모델 이름 지정 및 설정
model_name = 'se_resnext101_32x4d'
model = MODEL(num_classes= 500 , senet154_weight = WEIGHT_PATH, multi_scale = True, learn_region=True)
## DataParallel 함수에 모델을 입력하면 메모리 불균형을 해결할 수 있음
## (참고자료) https://medium.com/daangn/pytorch-multi-gpu-%ED%95%99%EC%8A%B5-%EC%A0%9C%EB%8C%80%EB%A1%9C-%ED%95%98%EA%B8%B0-27270617936b
model = torch.nn.DataParallel(model)
vgg16 = model
vgg16.load_state_dict(torch.load('./model/ISIAfood500.pth'))

print('\n*****  Model load the weight*****')

## GPU_IN_USE = torch.cuda.is_available(), GPU가 사용가능한지에 대한 boolean 값
if GPU_IN_USE
    print('CUDA_VISIBLE_DEVICES:', os.environ['CUDA_VISIBLE_DEVICES']) ## CUDA_VISIBLE_DEVICES 환경 변수 출력 - (int) 값을 가짐
    print('cuda: move all model parameters and buffers to the GPU')
    vgg16.cuda()

    ## 내장된 cudnn 자동 튜너를 활성화하여 하드웨어에 맞는 최상의 알고리즘을 찾아주는 옵션
    ## 입력되는 이미지의 크기가 비교적 동일할 때, 런타임 시간 축소
    cudnn.benchmark = True

criterion = nn.CrossEntropyLoss().cuda()

concate_output = list(map(id,  vgg16.module.classifier_global.parameters()))

theta_out2 = list(map(id, vgg16.module.ha2.hard_attn.fc.parameters()))
theta_out3 = list(map(id, vgg16.module.ha3.hard_attn.fc.parameters()))
theta_out4 = list(map(id, vgg16.module.ha4.hard_attn.fc.parameters()))
theta_out = theta_out2 + theta_out3 + theta_out4

ignored_params = concate_output + theta_out

base_params = filter(lambda p: id(p) not in ignored_params, vgg16.module.parameters())

## optim은 최적화 방법을 모아놓은 패키지, 대표적으로 Adam, SGD, RMS가 있음
## 파라미터와 learning rate 설정
optimizer = optim.SGD([
    {'params': base_params},
    {'params':vgg16.module.classifier_global.parameters(), 'lr': args.lr},
    # {'params': vgg16.global_out.parameters(), 'lr': args.lr*1},
    # {'params':vgg16.classifier_local.parameters(), 'lr': args.lr*1},
    # {'params':vgg16.local_fc.parameters(), 'lr': args.lr*10},
    # {'params':vgg16.x1_fc.parameters(), 'lr': args.lr*1},
    # {'params':vgg16.x2_fc.parameters(), 'lr': args.lr*1},
    # {'params':vgg16.x3_fc.parameters(), 'lr': args.lr*1},
    # {'params':vgg16.module.x4_fc.parameters(), 'lr': args.lr*10},
    # {'params':vgg16.ha1.hard_attn.fc.parameters(),'lr':args.lr*1},
    {'params':vgg16.module.ha2.hard_attn.fc.parameters(),'lr':args.lr*0.01},
    {'params':vgg16.module.ha3.hard_attn.fc.parameters(),'lr':args.lr*0.01},
    {'params':vgg16.module.ha4.hard_attn.fc.parameters(),'lr':args.lr*0.01}], lr=args.lr, momentum=0.9, weight_decay=0.0001)
#scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.9)
# optimizer = optim.SGD([
    # {'params': base_params},
    # {'params':vgg16.module.classifier_global.parameters(), 'lr': args.lr*10},
    # {'params':vgg16.module.ha1.hard_attn.fc.parameters(),'lr':args.lr*0.1},
    # {'params':vgg16.module.ha2.hard_attn.fc.parameters(),'lr':args.lr*0.1},
    # {'params':vgg16.module.ha3.hard_attn.fc.parameters(),'lr':args.lr*0.1},
    # {'params':vgg16.module.ha4.hard_attn.fc.parameters(),'lr':args.lr*0.1}], lr=args.lr, momentum=0.9, weight_decay=0.00001)
print('Model Preparation : Finished')
# optimizer = optim.Adam([
#     {'params': base_params},
#     {'params':vgg16.last_linear.parameters(), 'lr': args.lr*10}], lr=args.lr, weight_decay=args.weightDecay, betas=MOMENTUM)

## training 함수
## train_loader, model, criterion, optimizer, epoch을 입력으로 받음
def train(train_loader, model, criterion, optimizer, epoch):
    batch_time = AverageMeter() ## bach_time, date_time, losses, top1, top5의 현재 값 및 평균, 합, 카운트 저장
    data_time = AverageMeter()
    losses = AverageMeter()
    top1 = AverageMeter()
    top5 = AverageMeter()

    # switch to train mode
    model.train()

    end = time.time()
    for i, (input, target) in enumerate(train_loader):
        # measure data loading time
        data_time.update(time.time() - end) #시간 업데이트

        ## 미분 값을 계산할 함수
        target = target.cuda()
        input = input.cuda()

        ## torch.autograd.Variable는 자동 미분 클래스
        ## 속성으로 data(Tensor 형태의 데이터), grad(Data가 가져온 layer에 대한 미분 값), grad_fn(미분 값을 계산한 함수에 대한 정보))를 가짐
        input_var = torch.autograd.Variable(input)
        target_var = torch.autograd.Variable(target)

        # compute output
        output, global_c, local_c= model(input_var)
        concate_loss = criterion(output, target_var)
        global_loss = criterion(global_c, target_var)
        local_loss = criterion(local_c, target_var)
        loss = concate_loss + 0.5*(global_loss + local_loss)

        # measure accuracy and record loss
        # Accuracy 및 losses, top1, top5 업데이트
        prec1, prec5 = accuracy(output.data, target_var, topk=(1, 5))
        losses.update(loss.item(), input.size(0))
        top1.update(prec1.item(), input.size(0))
        top5.update(prec5.item(), input.size(0))

        # compute gradient and do SGD step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # measure elapsed time
        batch_time.update(time.time() - end)
        end = time.time()

        if i % args.print_freq == 0:
            print('Epoch: [{0}][{1}/{2}]\t'
                  'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
                  'Data {data_time.val:.3f} ({data_time.avg:.3f})\t'
                  'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
                  'Prec@1 {top1.val:.3f} ({top1.avg:.3f})\t'
                  'Prec@5 {top5.val:.3f} ({top5.avg:.3f})'.format(
                   epoch, i, len(train_loader), batch_time=batch_time,
                   data_time=data_time, loss=losses, top1=top1, top5=top5))

## train 함수와 동일
def validate(val_loader, model, criterion):
    batch_time = AverageMeter()
    losses = AverageMeter()
    top1 = AverageMeter()
    top5 = AverageMeter()

    # switch to evaluate mode
    model.eval()

    end = time.time()
    for i, (input, target) in enumerate(val_loader):
        target = target.cuda()
        input = input.cuda()
        input_var = torch.autograd.Variable(input)
        target_var = torch.autograd.Variable(target)

        # compute output
        output, global_c, local_c= model(input_var)
        concate_loss = criterion(output, target_var)
        global_loss = criterion(global_c, target_var)
        local_loss = criterion(local_c, target_var)
        loss = concate_loss + 0.5*(global_loss + local_loss)

        # measure accuracy and record loss
        prec1, prec5 = accuracy(output.data, target_var, topk=(1, 5))
        losses.update(loss.data.item(), input.size(0))
        top1.update(prec1.item(), input.size(0))
        top5.update(prec5.item(), input.size(0))

        # measure elapsed time
        batch_time.update(time.time() - end)
        end = time.time()

        if i % args.print_freq == 0:
            print('Test: [{0}/{1}]\t'
                  'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
                  'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
                  'Prec@1 {top1.val:.3f} ({top1.avg:.3f})\t'
                  'Prec@5 {top5.val:.3f} ({top5.avg:.3f})'.format(
                   i, len(val_loader), batch_time=batch_time, loss=losses,
                   top1=top1, top5=top5))

    print(' * Prec@1 {top1.avg:.3f} Prec@5 {top5.avg:.3f}'
          .format(top1=top1, top5=top5))

    return top1.avg

def save():
    torch.save(vgg16.state_dict(), args.pathModelParams)
    print('Checkpoint saved to {}'.format(args.pathModelParams))

## AverageMeter 초기화 시 reset 함수를 통해 val, avg, sum, count 초기화
## update 함수를 통해 새로운 값(val)을 입력 받고, 추가된 값을 반영한 sum, count, avg를 업데이트
class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


## 30 에폭마다 learning rate를 10퍼센트 만큼 감소시킴
def adjust_learning_rate(optimizer, epoch):
    """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""

    lr = args.lr * (0.1 ** (epoch // 40))
    param_groups = optimizer.state_dict()['param_groups']
    # print param_groups
    param_groups[0]['lr']=lr
    param_groups[1]['lr']=lr
    param_groups[2]['lr']=lr*0.01
    param_groups[3]['lr']=lr*0.01
    param_groups[4]['lr']=lr*0.01

    for param_group in param_groups:
        print param_group
        # param_group['lr'] = lr

def accuracy(output, target, topk=(1,)):
    """Computes the precision@k for the specified values of k"""
    maxk = max(topk)
    batch_size = target.size(0)

    _, pred = output.topk(maxk, 1, True, True)
    pred = pred.t()
    correct = pred.eq(target.view(1, -1).expand_as(pred))

    res = []
    for k in topk:
        correct_k = correct[:k].view(-1).float().sum(0)
        res.append(correct_k.mul_(100.0 / batch_size))
    return res

## main 문
best_prec1 = 0
for epoch in range(0, args.epoch):
    adjust_learning_rate(optimizer, epoch) ##learning rate 계산
    # train for one epoch
    train(train_loader, vgg16, criterion, optimizer, epoch) ## training
    # evaluate on validation set
    prec1 = validate(test_loader,vgg16, criterion) ## validate 함수로 정확도 계산
    # prec1 = test(epoch)
    # remember best prec@1 and save checkpoint
    is_best = prec1 > best_prec1 # 현재 best_prec1에 저장된 값보다 정확도가 더 클 #때 해당 값 저장
    if prec1 > best_prec1:
        save()
    best_prec1 = max(prec1, best_prec1) #best# _prec1 값 업데이트