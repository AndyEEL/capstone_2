import requests
import json
import pandas as pd
import urllib.parse as parse
import time
from datetime import datetime
import sys

if len(sys.argv) <= 1:
    print("-- 사용방법 -- \n다음 내용을 창에다 입력 : pyhton3 insta_crawling_json.py [검색할 해시태그]")
    sys.exit()

hashtag_name = str(sys.argv[1])

start = time.time()
encoded_name = parse.quote(hashtag_name)
header_setting = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Accept-Language': 'ko-kr',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'www.instagram.com'
}
url_first = 'https://www.instagram.com/explore/tags/{}/?__a=1'.format(encoded_name)
sess = requests.Session()
sess.headers.update(header_setting)
response = sess.get(url_first)
result = json.loads(response.text)


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
        time_ = result['data']['hashtag']['edge_hashtag_to_media']['edges'][n]['node']['taken_at_timestamp']
        converted_time = datetime.frometimestamp(time_)
        image_description = result['data']['hashtag']['edge_hashtag_to_media']['edges'][n]['node'][
            'accessibility_caption']
        post = {'time': converted_time, 'text': text, 'like': like, 'img_url': img_url, 'img_desc': image_description}
        post_list.append(post)
    return post_list, end_point


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
            like = result['data']['hashtag']['edge_hashtag_to_media']['edges'][i]['node']['edge_liked_by']['count']
            img_url = result['data']['hashtag']['edge_hashtag_to_media']['edges'][i]['node']['thumbnail_src']
            time_ = result['data']['hashtag']['edge_hashtag_to_media']['edges'][i]['node']['taken_at_timestamp']
            converted_time = datetime.frometimestamp(time_)
            image_description = result['data']['hashtag']['edge_hashtag_to_media']['edges'][i]['node']['accessibility_caption']
            post = {'time': converted_time, 'text': text, 'like': like, 'img_url': img_url, 'img_desc': image_description}
            print(post)
            post_list.append(post)
    return post_list


post_list, end_point = first_page()
post_list = crawl_page(post_list, end_point)

final = pd.DataFrame(post_list)
final.to_csv('instagram_result3.csv', encoding='utf-8-sig')

print("time: ", time.time() - start)