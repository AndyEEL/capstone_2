from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import pandas as pd
from pyvirtualdisplay import Display

#Display 세팅하기
display = Display(visible=0, size=(1920, 1080))
display = Display()
display.start()

#Option 세팅하기
options = Options()
options.add_argument("disable-infobars")
options.add_argument("enable-automation")
options.add_argument("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome")

#Driver 세팅하기
path = "/home/luckyrookie/chromedriver"
driver = webdriver.Chrome(path, options = options)
driver.get("https://www.instagram.com/accounts/login/?next=https://www.instagram.com/&source=mobile_nav");
time.sleep(5);
print("드라이버 세팅 완료");

#login하기 
userId = "testclassroomluckyrookie@gmail.com"
userPw = "luckyone77!"
idField = driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input')
pwField = driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input')
idField.send_keys(userId)
pwField.send_keys(userPw)
time.sleep(5);

loginButton = driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]');
loginButton.click()
time.sleep(5)
print("로그인 완료")

#검색하기
tagUrl = "https://www.instagram.com/explore/tags/" + "인스타푸드"
driver.get(tagUrl)
time.sleep(11)
print("검색 완료")

#첫번째 페이지 열기
firstPost = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a')
firstPost.click()
time.sleep(7)
print("첫번쨰 게시글 접속 완료")


##크롤링
print("크롤링 시작")

#데이터 저장 리스트
idxs = []
dates = []
bodies = []
comments = []
likes = []

for idx in range(3):
	html = driver.page_source
	soup = BeautifulSoup(html, "html.parser")
	date = soup.select_one("div.k_Q0X time")["datetime"]
	body = soup.select_one("ul.XQXOT > div:nth-child(1) span:nth-child(2)").text
	comment = []
	for c in soup.select("ul.Mr508 div.C4VMK span:nth-child(2)"):
		comment.append(c.text)
	like = soup.select_one("div.Nm9Fw span").text

	idxs.append(idx)
	dates.append(date)
	bodies.append(body)
	comments.append(comment)
	likes.append(like)
		
	#print("idx: ", idx);
	#print("date: ", date);
	#print("body: ", body);
	#print("comment: ", comment);
	#print("like: ", like);
	#print("\n");
	idx += 1
	try: 
		nextButton = driver.find_element_by_xpath("html/body/div[5]/div[1]/div/div/a[2]")
	except:
		nextButton = driver.find_element_by_xpath("/html/body/div[5]/div[1]/div/div/a")
	nextButton.click()
	time.sleep(8)

#결과 저장하기
df = pd.DataFrame()
df["id"] = idxs
df["날짜"] = dates
df["본문"] = bodies
df["댓글"] = comments
df["좋아요수"] = likes
df.to_excel("result.xlsx")
