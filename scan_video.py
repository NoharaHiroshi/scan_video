# encoding=utf-8

import requests
import urllib
import urllib2
import time
import os
import ssl
import math
import sys
from selenium import webdriver


def web_scan(url):
    with webdriver.PhantomJS() as browser:
        browser.get(url)
        print browser.page_source


def download_bar(total_size, current_size, block_size, start_time, end_time):
    download_flag = u'▎'
    not_download_flag = u'·'
    percent = int(float(current_size) / total_size * 20)
    current_speed = float(block_size) / (end_time - start_time)
    percent_bar_str = r'[ %s%s ] - %s%% | total_size: %s ' \
                      '| download_size: %s | speed: %s / s' % (download_flag * percent,
                                                               not_download_flag * (20 - percent),
                                                               percent * 5,
                                                               convert_storage_read(total_size),
                                                               convert_storage_read(current_size),
                                                               convert_storage_read(current_speed)
                                                               )
    sys.stdout.write('\r' + percent_bar_str)
    sys.stdout.flush()


def convert_storage_read(bytes_content):
    unit = 1024
    bytes_content = int(bytes_content)
    if bytes_content < unit:
        return '%.2f bytes' % bytes_content
    elif unit <= bytes_content < math.pow(unit, 2):
        return '%.2f kb' % (bytes_content / unit)
    elif math.pow(unit, 2) <= bytes_content < math.pow(unit, 3):
        return '%.2f mb' % (bytes_content / math.pow(unit, 2))
    else:
        return '%.2f gb' % (bytes_content / math.pow(unit, 3))


def scan_video():
    headers = {
        'Host': 'upos-hz-mirrorkodo.acgvideo.com',
        'Connection': 'keep-alive',
        'Origin': 'https://www.bilibili.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'https://www.bilibili.com/bangumi/play/ep198482/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    # 请求的url
    url = r'https://cn-jszj-dx-v-06.acgvideo.com/upgcxcode/41/96/34659641/34659641-1-32.flv?expires=1539782400&platform=pc&ssig=gG7tW1RgWKkh_a06LIWuaA&oi=1897879350&nfa=uTIiNt+AQjcYULykM2EttA==&dynamic=1&hfa=2046049971&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=&trid=d74a584db95d4174a7b678b26094aed3&nfc=1'

    url_list = [
        r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/73/96/34659673/34659673-1-32.flv?e=ig8euxZM2rNcNbNz7bhVhoMM7zNjhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1539864775&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=236300&trid=4f90adac328347a48c7e3920552ee30c&uipk=5&uipv=5&um_deadline=1539864775&um_sign=78453b7d29700f165854f1ab954c68d4&upsig=85b5333ca216b9ed23d958e772104443',
        r'https://cn-jszj-dx-v-03.acgvideo.com/upgcxcode/41/96/34659641/34659641-2-32.flv?expires=1539863400&platform=pc&ssig=8tS4-HBDws2y02flJPHR2A&oi=1897879350&nfa=uTIiNt+AQjcYULykM2EttA==&dynamic=1&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=&trid=da44bc16571c4dfd977329f9cb77eee4&nfc=1',
        r'https://cn-jszj-dx-v-06.acgvideo.com/upgcxcode/41/96/34659641/34659641-3-32.flv?expires=1539863400&platform=pc&ssig=LI6MsaoErrW_rphWZUBZLA&oi=1897879350&nfa=uTIiNt+AQjcYULykM2EttA==&dynamic=1&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=&trid=da44bc16571c4dfd977329f9cb77eee4&nfc=1',
        r'https://cn-jszj-dx-v-03.acgvideo.com/upgcxcode/41/96/34659641/34659641-4-32.flv?expires=1539863400&platform=pc&ssig=V6JHAn4Vuua9q0g6kIxV2w&oi=1897879350&nfa=uTIiNt+AQjcYULykM2EttA==&dynamic=1&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=&trid=da44bc16571c4dfd977329f9cb77eee4&nfc=1',
        r'https://cn-jszj-dx-v-03.acgvideo.com/upgcxcode/41/96/34659641/34659641-5-32.flv?expires=1539863400&platform=pc&ssig=RLylD9nnZcMi2PD69R9RpQ&oi=1897879350&nfa=uTIiNt+AQjcYULykM2EttA==&dynamic=1&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=&trid=da44bc16571c4dfd977329f9cb77eee4&nfc=1',
        r'https://cn-jszj-dx-v-05.acgvideo.com/upgcxcode/41/96/34659641/34659641-6-32.flv?expires=1539863400&platform=pc&ssig=rKssmj6f4fKcCubXBxFJwQ&oi=1897879350&nfa=uTIiNt+AQjcYULykM2EttA==&dynamic=1&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=&trid=da44bc16571c4dfd977329f9cb77eee4&nfc=1',
        r'https://cn-jszj-dx-v-05.acgvideo.com/upgcxcode/41/96/34659641/34659641-7-32.flv?expires=1539863400&platform=pc&ssig=vZB9AiV7LlICZfQJvPbpPQ&oi=1897879350&nfa=uTIiNt+AQjcYULykM2EttA==&dynamic=1&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=&trid=da44bc16571c4dfd977329f9cb77eee4&nfc=1',
        r'https://cn-jszj-dx-v-03.acgvideo.com/upgcxcode/41/96/34659641/34659641-8-32.flv?expires=1539863400&platform=pc&ssig=k7jRzS1pFs8O0-FImDzsOw&oi=1897879350&nfa=uTIiNt+AQjcYULykM2EttA==&dynamic=1&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=&trid=da44bc16571c4dfd977329f9cb77eee4&nfc=1',
    ]
    file_path = os.path.join(os.path.dirname(__file__), '1.flv')
    print '当前视频共有%s部分' % str(len(url_list))
    try:
        for i, url in enumerate(url_list):
            print '当前正在下载%s部分' % str(i+1)
            file_path_list = file_path.split('.')
            part_file_path = '%s_%s.%s' % (file_path_list[0], str(i), file_path_list[-1])
            response = requests.get(url, headers=headers, stream=True, verify=False)
            all_content_length = int(response.headers['content-length'])
            if os.path.exists(part_file_path):
                # 已获取到视频的bytes数
                file_content_length = os.path.getsize(part_file_path)
                # 判断是否已经获取到视频全部数据
                if file_content_length < all_content_length:
                    headers['Range'] = 'bytes=%d-' % file_content_length
                    response = requests.get(url, headers=headers, stream=True, verify=False)
                else:
                    print u'视频已下载完成'
                    return
            with open(part_file_path, 'ab') as f:
                # 在此处下载数据
                current_length = os.path.getsize(part_file_path)
                # 块大小1m, 1m 刷新一次
                block_size = pow(1024, 2)
                start_time = time.time()
                for block in response.iter_content(chunk_size=block_size):
                    if block:
                        f.write(block)
                        f.flush()
                        current_length += block_size
                        if current_length > all_content_length:
                            current_length = all_content_length
                        end_time = time.time()
                        download_bar(all_content_length, current_length, block_size, start_time, end_time)
                        start_time = time.time()
    except Exception as e:
        print e


def merge_video(file_path):
    # 判断待合并文件是否已存在
    if os.path.exists(file_path):
        print '待合并文件已存在'
        return
    print '待合并文件： %s' % file_path
    root_path = os.path.dirname(file_path)
    file_name_list = os.listdir(root_path)
    file_name = file_path.split('\\')[-1]
    merge_file_list = [f for f in file_name_list if f.split('_')[0] == file_name.split('.')[0]]
    print '当前待合并文件列表： %s' % ', '.join(merge_file_list)
    with open(file_path, 'ab') as f:
        for merge_file in merge_file_list:
            merge_full_file = os.path.join(root_path, merge_file)
            part_f = open(merge_full_file, mode='rb')
            part_f_content = part_f.read()
            f.write(part_f_content)
            print '已合并文件： %s' % merge_file
    print '合并完成'

if __name__ == '__main__':
    # scan_video()
    merge_video(os.path.join(os.path.dirname(__file__), '1.flv'))
