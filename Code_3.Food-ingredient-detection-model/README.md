# CNN description

> [논문 링크](https://arxiv.org/pdf/2008.05655.pdf)


## Dataset

- large-scale dataset ISIA Food-500 with 399,726 images and 500 categories
<img width="603" alt="_2021-04-10__7 12 45" src="https://user-images.githubusercontent.com/74975256/114573481-5f7c6900-9cb3-11eb-901e-601fc61e44f0.png">


**이미지 전처리에 관한 부분은은 논문을 참고**

## Features(x)(input)

ISIA Food-500 is divided into 60%, 10% and 30% images for training, validation and testing, respectively.

feature은 image file - label의 형태로 이루어져있음. 

## Outputs(y)(output)

<img width="657" alt="_2021-04-12__8 01 01" src="https://user-images.githubusercontent.com/74975256/114573585-758a2980-9cb3-11eb-96f0-16632cabe5f6.png">

<img width="668" alt="_2021-04-12__8 02 29" src="https://user-images.githubusercontent.com/74975256/114573601-79b64700-9cb3-11eb-855d-cdcc588984bc.png">
<img width="676" alt="_2021-04-12__8 03 59" src="https://user-images.githubusercontent.com/74975256/114573606-7ae77400-9cb3-11eb-8783-73ed982e958f.png">

## Model(hypothesis)

### 모델 구조

<img width="662" alt="_2021-04-10__10 04 27" src="https://user-images.githubusercontent.com/74975256/114573640-8175eb80-9cb3-11eb-9c00-d99b84284d32.png">

## 사용된 Networks

### main network

- Stacked Global-Local Attention Network (SGLANet)

    : jointly learn complementary global and local visual features for food recognition

    **ACHIEVED BY 2 sub-networks**

    - Global Feature Learning Subnetwork (GloFLS)

        first utilizes hybrid spatial-channel attention to obtain more discriminative features for each layer, and then aggregates these features from different layers with both coarse and fine-grained levels, such as shape and texture cues about food into global-level features.

### sub-networks

1. GloFLS(Global Feature Learning Subnetwork)
    - learns more discriminative features via hybrid Spatial-Channel Attention (**SCA**) for each layer, and then aggregates these discriminative features from differ- ent layers into global level representations via multi-layer feature fusing
    - first utilizes hybrid spatial-channel attention to obtain more discriminative features for each layer, and then aggregates these features from different layers with both coarse and fine-grained levels, such as shape and texture cues about food into global-level features.
    - can capture various types of global level features, such as shape, texture and edge cues about food
2.  Local- Feature Learning Subnetwork (LocFLS)

    adopts cascaded Spatial Transformers (STs) to localize different attentional regions (e.g., ingredient-relevant regions), and aggregates fused re- gional features from different layers into local-level representation.

    - each layer : inception block이 reginal feature을 추출하고, GAP(global average pooling layer) → Max Pooling을 거쳐 regional feature들을 fuse.

        cf ) GAP를 먼저 사용하는 이유 : inception layer에서는 full-connected layer을 쓰면 overfitting의 위험이 존재. 대신 GAP를 사용함으로써 overfitting 방지. 

    - FUSE : each layer에 산출된 maxpooling 값들은 cancatenation layer → fully-connected layer을 거쳐 fuse. 이후 local loss 산출

3.    Spatial-Channel Attention (SCA)

- combination of both spatial and channel attention can capture discriminative features comprehensively from different dimensions

<img width="642" alt="_2021-04-10__9 58 47" src="https://user-images.githubusercontent.com/74975256/114573727-96527f00-9cb3-11eb-9b6d-7342e588eeb9.png">


## Cost functions(비용함수)

- SGLANet

    trained with different types of losses in an end-to-end fashion to maximize their complementary effect in terms of discriminative power.

- Jointly optimized by three types of losses (joint / global / local loss )
<img width="276" alt="_2021-04-10__10 06 01" src="https://user-images.githubusercontent.com/74975256/114573773-a0747d80-9cb3-11eb-9262-1e90fd7bed97.png">

## optimization methods

- Stochatistic gradient descent
- batch size = 80
- momentum  = 0.9
- learning rate : 0.01 and divided by 10 after 30 epochs

---

## 참고

### Inception model

[link](https://kangbk0120.github.io/articles/2018-01/inception-googlenet-review)

일반적으로 생각하는 Convolution layer는 필터가 움직이면서 해당하는 입력 부분과 곱/합 연산을 수행하고, 활성화함수를 거쳐 결과를 만들어냄. 만약 데이터의 분포가 저러한 선형 관계로 표현될 수 없는 비선형적인 관계라면 비선형적 관계를 표현할 수 있도록, 단순한 곱/합 연산이 아니라 Multi Layer Perceptron, 즉 MLP를 중간에 넣음

<img width="687" alt="_2021-04-10__10 18 32" src="https://user-images.githubusercontent.com/74975256/114573812-ac603f80-9cb3-11eb-8788-4626cbe1bf4c.png">
<img width="697" alt="_2021-04-10__10 18 50" src="https://user-images.githubusercontent.com/74975256/114573844-b4b87a80-9cb3-11eb-8a33-a3af26c40bff.png">

MLP Conv를 세 개 쌓고, 마지막에 Fully-Connected Layer를 넣는 대신 **Global Average Pooling**을 넣었습니다. 이는 오버피팅을 방지하는 효과 있음.

### Attention layer

[200214_강현규_Visual_Attention_세미나_자료.pdf.zip](CNN%20description%20b7bae84f33fa4cb0aa9e41721bc5dea4/200214__Visual_Attention__.pdf.zip)
(출처 : http://dmqm.korea.ac.kr/activity/seminar/280)

### What is SEnet

[https://bskyvision.com/640](https://bskyvision.com/640)
