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
        'Host': 'upos-hz-mirrorcos.acgvideo.com',
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
    url = r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/07/82/50108207/50108207-1-32.flv?e=ig8euxZM2rNcNbNVnWRVhoMMhW4ghwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1539680709&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=209100&trid=a3ca314910e04caabee6c9bbdfb2819c&uipk=5&uipv=5&um_deadline=1539680709&um_sign=9d7cf242ca446644c7766b3ab775c5dd&upsig=711f29a36422d453797dce8ba73078d1'
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
                f.write(response.content)
                # 从内存中写入文件
                f.flush()
                print('receive data，file size : %s   total size: %s' %
                      (convert_storage_read(os.path.getsize(file_path)), convert_storage_read(all_content_length)))
    except Exception as e:
        print e

if __name__ == '__main__':
    scan_video()