# 질환별, 식습관별 안전한 식당 및 배달음식 추천 서비스 
##### 음식 인식 딥러닝 모델과 식품 DB를 활용한 안전한 식당과 배달음식 안내

### 🚩Table of Contents
* why this service?
* Features
* Examples
* How it works

### Why this service?

**본 서비스는 질환을 가지고 있는 사람도 편하게 음식점을 고를 수 있도록 음식점에 `안전 음식 신호등`을 부여합니다.**

배달의 시대에서 먹고 싶은 음식을 찾아 주문하기란 정말 쉽습니다. 하지만 만약 알러지가 있거나, 질환자라면 음식점을 고르는데 어려움이 많을 것입니다. 본 서비스는 이 불편함을 해소합니다.

음식점의 음식 사진과 방문자 후기사진, 음식 이름을 활용하여 영양성분을 분석해 질환자에 맞춘 음식 안전도를 판단합니다. 
사용자는 지도에서 음식점 옆에 나타난 신호등을 보고, 편하게 고를 수 있게 됩니다. `안전 음식 신호등`은 어떤 질환을 설정하냐에 따라 바뀝니다. 

예를 들어 같은 음식점이 갑상선기능저하증 질환자에게는 초록색이지만, 갑각류 알러지 질환자에게는 빨간색일 수 있습니다. 본 서비스는 모두가 행복하게 먹고싶은 음식을 안전하게 먹을 수 있는 세상을 위해 태어나게 되었습니다.
 
### Features 
- 입력된 질환 정보 혹은 식습관에 대해 동작합니다 

- 사용자의 위치 혹은 검색한 장소를 중심으로, 이용 가능한 배달 범위 혹은 특정 거리 반경 안에 있는 음식점의 음식 사진을 분석하여 `음식 안전도`를 평가합니다. 

	- 음식 사진과 이름을 분석하여 음식 종류를 특정하고, 식품 DB를 활용하여 음식의 영양성분를 산출합니다. 
 	 
	 *예)들기름육회파스타 - 이미지 인식으로 '파스타' '면과 다른 재료의 비율' 추출, 이름에서 육회 추출하여 최종 영양성분 도출*
	- 음식에 안좋은 영양소를 대체할 수 있는 옵션이 있는경우, 안전도에 반영됩니다. 
	 
	 *예)떡볶이 떡을 곤약떡으로 대체 가능한 경우 - 빨간색에서 초록색으로 변경*

-  음식 안전도를 종합하여 `음식점의 종합 안전도`를 나타냅니다 

### How it works
1. 지도 상 음식점 및 판매 음식 정보, 음식 사진 크롤링 
2. 음식 인식 딥러닝 모델 구현
3. 식품 DB 구축 
4. 네이버 지도 API를 활용한 음식점 안내 지도 웹 구현 


##### This is Team 2 of Capstone Design by Professor Park Jae-hong of Business Administration at Kyung Hee University.
