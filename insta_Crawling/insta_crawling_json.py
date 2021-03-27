import requests
import json
import pandas as pd
import urllib.parse as parse
import time
from datetime import datetime
import sys

## 해시태그, 아이디, 비밀번호 받기
if len(sys.argv) <= 1:
    print("-- 사용방법 -- \n다음 내용을 창에다 입력 : pyhton3 insta_crawling_json.py [검색할 해시태그] [아이디] [패스워드]")
    sys.exit()

hashtag_name = str(sys.argv[1])
username = str(sys.argv[2])
password = str(sys.argv[3])


## 첫번째 페이지 긁기

def first_page():
    post_list = [] # 크롤링 자료 저장 list
    end_point = result['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor'] # 끝을 나타내는 위치
    edges = result['graphql']['hashtag']['edge_hashtag_to_media']['edges']
    for n in range(len(edges)):
        try:
            text = result['graphql']['hashtag']['edge_hashtag_to_media']['edges'][n]['node']['edge_media_to_caption']['edges'][0]['node']['text']
        except:
            text = None
        try:
            like = result['graphql']['hashtag']['edge_hashtag_to_media']['edges'][n]['node']['edge_liked_by']['count']
        except:
            like = None
        try:
            img_url = result['graphql']['hashtag']['edge_hashtag_to_media']['edges'][n]['node']['thumbnail_src']
        except:
            img_url = None
        try:
            time_ = result['graphql']['hashtag']['edge_hashtag_to_media']['edges'][n]['node']['taken_at_timestamp']
            converted_time = datetime.fromtimestamp(time_)

        except:
            converted_time = None
        try:
            image_description = result['graphql']['hashtag']['edge_hashtag_to_media']['edges'][n]['node']['accessibility_caption']
        except:
            image_description = None

        post = {'time': converted_time, 'text': text, 'like': like, 'img_url': img_url, 'img_desc': image_description}
        post_list.append(post)
    return post_list, end_point

#이후 페이지 긁기
def crawl_page(post_list, end_point):
    while end_point != None:
        url = 'https://www.instagram.com/graphql/query/?query_hash=90cba7a4c91000cf16207e4f3bee2fa2&variables={\"tag_name\":\"%s\",\"first\":1,\"after\":\"%s\"}' % (
            hashtag_name, end_point)
        sess = requests.Session()
        sess.headers.update(header_setting)
        response = sess.get(url)
        print(response.text)
        result = json.loads(response.text)
        end_point = result['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        print(end_point)
        edges = result['data']['hashtag']['edge_hashtag_to_media']['edges']
        for i in range(len(edges)):
            try:
                text = result['data']['hashtag']['edge_hashtag_to_media']['edges'][i]['node']['edge_media_to_caption'][
                    'edges'][0]['node']['text']
            except:
                text = None
            try:
                like = result['data']['hashtag']['edge_hashtag_to_media']['edges'][i]['node']['edge_liked_by']['count']
            except:
                like = None
            try:
                img_url = result['data']['hashtag']['edge_hashtag_to_media']['edges'][i]['node']['thumbnail_src']
            except:
                img_url = None
            try:
                time_ = result['data']['hashtag']['edge_hashtag_to_media']['edges'][i]['node']['taken_at_timestamp']
                converted_time = datetime.fromtimestamp(time_)
            except:
                time_ = None
                converted_time = None
            try:
                image_description = result['data']['hashtag']['edge_hashtag_to_media']['edges'][i]['node']['accessibility_caption']
            except:
                image_description = None

            post = {'time': converted_time, 'text': text, 'like': like, 'img_url': img_url, 'img_desc': image_description}
            print(post)
            post_list.append(post)
    return post_list



# login data setting
time = str(int(datetime.now().timestamp()))
enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{time}:{password}"
login_data = {'username': username, 'enc_password': enc_password}

# url setting
encoded_hashtag = parse.quote(hashtag_name)
url_first = 'https://www.instagram.com/explore/tags/{}/?__a=1'.format(encoded_hashtag)




session = requests.Session()

# header and environment setting
header_setting = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Accept-Language': 'ko-kr',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'www.instagram.com'
}

session.cookies.set("ig_cb", "2")  # "Accept cookie" 배너가 닫혀있도록 쿠키 설정
session.headers.update(header_setting['User-Agent'])
session.headers.update({'Referer': 'https://www.instagram.com'})
res = session.get('https://www.instagram.com')

csrftoken = None #인스타그램은 csrf와 함꼐 csrf토큰 정보도 필요하다.

for key in res.cookies.keys():
    if key == 'csrftoken':
        csrftoken = session.cookies['csrftoken']

session.headers.update({'X-CSRFToken': csrftoken})

# user login
with session as s:
    try:
        login = session.post('https://www.instagram.com/accounts/login/ajax/', data=login_data, allow_redirects=True)
        session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        cookies = login.cookies #쿠키 업데이
        print(login.text) # if accepted, print "user" : true
    except:
        print("로그인 에러")

    print("첫번째 페이지 크롤링 시작")
    try:
        response = session.get(url_first)
        result = json.loads(response.text)
    except:
        print("get or json loads error at crawling first page")
    post_list, end_point = first_page()
    post_list = crawl_page(post_list, end_point)

final = pd.DataFrame(post_list)
final.to_csv('instagram_result3.csv', encoding='utf-8-sig')


session.close()

