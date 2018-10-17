# encoding=utf-8

import requests
import urllib
import urllib2
import time
import os
import ssl
import math
import sys


def download_bar(total_size, current_size, block_size, start_time, end_time):
    download_flag = u'|'
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
    print percent_bar_str
    sys.stdout.flush()
    time.sleep(1)


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
    # 文件的初始大小
    file_content_length = 0
    # 网络中数据流的初始化大小
    all_content_length = 0
    # 请求的url
    url = r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/07/82/50108207/50108207-1-32.flv?e=ig8euxZM2rNcNbNVnWRVhoMMhW4ghwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1539774028&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=209100&trid=1fa10cec170741c4aab5a35dbb14975b&uipk=5&uipv=5&um_deadline=1539774028&um_sign=751a892345e4dffcd9fe6d3057f5671d&upsig=1dcd7beb98d7ead2d9f679b8c870df7f'
    file_path = os.path.join(os.path.dirname(__file__), '1.flv')
    try:
        if not all_content_length:
            # 接通连接但未请求数据
            response = requests.get(url, headers=headers, stream=True, verify=False)
            all_content_length = int(response.headers['content-length'])
        while True:
            if os.path.exists(file_path):
                # 已获取到视频的bytes数
                file_content_length = os.path.getsize(file_path)
                # 判断是否已经获取到视频全部数据
                if file_content_length == all_content_length:
                    break
            headers['Range'] = 'bytes=%d-' % file_content_length
            if not response:
                response = requests.get(url, headers=headers, stream=True, verify=False)

            with open(file_path, 'ab') as f:
                # 在此处下载数据
                current_length = os.path.getsize(file_path)
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
                        print all_content_length, current_length
                        download_bar(all_content_length, current_length, block_size, start_time, end_time)
                        start_time = time.time()
    except Exception as e:
        print e

if __name__ == '__main__':
    scan_video()