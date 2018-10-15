# encoding=utf-8

import requests
import urllib
import time
import os
import ssl


def calc_download_speed(block_num, block_size, total_size, start_time):
    """
    :param block_num: 已下载的数据块大小
    :param block_size: 数据块大小
    :param total_size: 文件总大小
    :param start_time: 开始下载时的时间点
    :return:
    """
    # 已下载百分比
    download_percent = '%.2f' % (block_num * block_size * 100 / total_size)
    speed_bytes = (block_num * block_size) / (time.time() - start_time)
    if speed_bytes < 1024:
        speed_str = '%s KB/s' % float(speed_bytes / 1024)
    else:
        speed_str = '%s MB/s' % float(speed_bytes / 1024)
    print '当前下载速度：%s | 当前下载百分比：%s' % (speed_str, download_percent)


def scan_video():
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

            # 获取请求视频的长度
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
    scan_video()