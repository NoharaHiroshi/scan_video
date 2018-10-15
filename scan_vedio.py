# encoding=utf-8

import requests
import time
import os
import ssl


def scan_vedio():
    headers = {
        'Host': 'cn-jszj-dx-v-06.acgvideo.com',
        'Connection': 'keep-alive',
        'Origin': 'https://www.bilibili.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'https://www.bilibili.com/bangumi/play/ep198482/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    pre_content_length = 0
    file_path = os.path.join(os.path.dirname(__file__), '1.flv')
    try:
        url = r'https://cn-jszj-dx-v-06.acgvideo.com/upgcxcode/41/96/34659641/34659641-1-32.flv?' \
              r'expires=1539604500&platform=pc&ssig=5VY_tytrPwL68EMecpPzZQ' \
              r'&oi=1897879350&nfa=uTIiNt+AQjcYULykM2EttA==&dynamic=1' \
              r'&hfa=2046248726&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=' \
              r'&trid=a2d880c40e0c42848e7f8e1841e83ceb&nfc=1'
        while True:
            if os.path.exists(file_path):
                headers['Range'] = 'bytes=%d-' % os.path.getsize(file_path)
            response = requests.get(url, headers=headers, stream=True, verify=False)
            content_length = int(response.headers['content-length'])
            if content_length < pre_content_length or (os.path.exists(file_path) and os.path.getsize(file_path) == content_length):
                break
            pre_content_length = content_length

            with open(file_path, 'ab') as f:
                f.write(response.content)
                f.flush()
                print('receive data，file size : %d   total size:%d' % (os.path.getsize(file_path), content_length))
    except Exception as e:
        print e

if __name__ == '__main__':
    scan_vedio()