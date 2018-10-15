# encoding=utf-8

import requests
import urllib
import time
import os
import ssl
import math


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


def convert_storage_read(bytes_content):
    bytes_content = int(bytes_content)
    if bytes_content < 1000:
        return '%.2f bytes' % bytes_content
    elif 1000 <= bytes_content < math.pow(1000, 2):
        return '%.2f kb' % (bytes_content / 1000)
    elif math.pow(1000, 2) <= bytes_content < math.pow(1000, 3):
        return '%.2f mb' % (bytes_content / math.pow(1000, 2))
    else:
        return '%.2f gb' % (bytes_content / math.pow(1000, 3))


def scan_video():
    headers = {
        'Host': 'upos-hz-mirrorcos.acgvideo.com',
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
        url = r'https://upos-hz-mirrorcos.acgvideo.com/upgcxcode/07/82/50108207/50108207-1-64.flv?um_deadline=1539619108&platform=pc&rate=207400&oi=997036720&um_sign=7c669f44449971a4be547da8ad2462f3&gen=playurl&os=cos&trid=8f41893986a44612a99fc011d6349817'
        while True:
            if os.path.exists(file_path):
                headers['Range'] = 'bytes=%d-' % os.path.getsize(file_path)
            response = requests.get(url, headers=headers, stream=True, verify=False)
            print response.headers

            # 获取请求视频的长度
            content_length = int(response.headers['content-length'])
            if content_length < pre_content_length or (os.path.exists(file_path) and os.path.getsize(file_path) == content_length):
                break
            pre_content_length = content_length

            with open(file_path, 'ab') as f:
                f.write(response.content)
                f.flush()
                print('receive data，file size : %s   total size: %s' %
                      (convert_storage_read(os.path.getsize(file_path)), convert_storage_read(content_length)))
    except Exception as e:
        print e

if __name__ == '__main__':
    scan_video()