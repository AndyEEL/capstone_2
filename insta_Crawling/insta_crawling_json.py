import requests
import json
import pandas as pd
import urllib.parse as parse
import time
from datetime import datetime
import sys

if len(sys.argv) <= 1:
    print("-- 사용방법 -- \n다음 내용을 창에다 입력 : pyhton3 insta_crawling_json.py [검색할 해시태그] [아이디] [패스워드]")
    sys.exit()

hashtag_name = str(sys.argv[1])
username = str(sys.argv[2])
password = str(sys.argv[3])

#첫번째 페이지 긁기
def first_page():
    post_list = []
    end_point = result['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
    edges = result['graphql']['hashtag']['edge_hashtag_to_media']['edges']
    for n in range(len(edges)):
        try:
            text = \
            result['graphql']['hashtag']['edge_hashtag_to_media']['edges'][n]['node']['edge_media_to_caption']['edges'][
                0]['node']['text']
        except:
            text = None
        like = result['graphql']['hashtag']['edge_hashtag_to_media']['edges'][n]['node']['edge_liked_by']['count']
        img_url = result['graphql']['hashtag']['edge_hashtag_to_media']['edges'][n]['node']['thumbnail_src']
        time_ = result['graphql']['hashtag']['edge_hashtag_to_media']['edges'][n]['node']['taken_at_timestamp']
        converted_time = datetime.fromtimestamp(time_)
        image_description = result['graphql']['hashtag']['edge_hashtag_to_media']['edges'][n]['node'][
            'accessibility_caption']
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




start = time.time()
encoded_name = parse.quote(hashtag_name)
header_setting = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Accept-Language': 'ko-kr',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'www.instagram.com'
}
url_first = 'https://www.instagram.com/explore/tags/{}/?__a=1'.format(encoded_name)



time = str(int(datetime.now().timestamp()))
enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{time}:{password}"

session = requests.Session()
#  "Accept cookie" 배너가 닫혀있도록 쿠키 설
session.cookies.set("ig_cb", "2")
session.headers.update({'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"})
session.headers.update({'Referer': 'https://www.instagram.com'})
res = session.get('https://www.instagram.com')

csrftoken = None

for key in res.cookies.keys():
    if key == 'csrftoken':
        csrftoken = session.cookies['csrftoken']

session.headers.update({'X-CSRFToken': csrftoken})
login_data = {'username': username, 'enc_password': enc_password}
with session as s:
    login = session.post('https://www.instagram.com/accounts/login/ajax/', data=login_data, allow_redirects=True)
    session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
    cookies = login.cookies
    print(login.text)



#insta_session.headers.update(header_setting)

    response = session.get(url_first)
    result = json.loads(response.text)

    post_list, end_point = first_page()
    post_list = crawl_page(post_list, end_point)

final = pd.DataFrame(post_list)
final.to_csv('instagram_result3.csv', encoding='utf-8-sig')

print("time: ", time.time() - start)

session.close()

