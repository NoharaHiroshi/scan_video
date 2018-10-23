# encoding=utf-8

import requests
import urllib
import urllib2
import time
import os
import ssl
import math
import sys
import re
import threading
import traceback
from selenium import webdriver

# 视频总大小
total_size = 0
# 当前下载视频大小
current_size = 0
# 启动时间
start_time = time.time()
# 上次下载视频大小
last_size = 0


def web_scan(url):
    with webdriver.PhantomJS() as browser:
        browser.get(url)
        print browser.page_source


def download_bar(part_file_size, part_current_size, part_index, all_percent_bar_list):
    """
    :param part_file_size: 部分视频大小
    :param part_current_size: 部分视频已下载大小
    :param part_index: 部分视频的索引
    :param all_part_num: 所有部分视频的数量
    :param block_size: 块大小
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return:
    """
    global total_size
    global current_size
    global start_time
    global last_size
    end_time = time.time()
    download_flag = u'|'
    not_download_flag = u'·'
    # 部分视频文件下载的百分比 0 - 10
    percent = int(float(part_current_size) / part_file_size * 10)
    current_speed = float(current_size - last_size) / (end_time - start_time + 1)
    percent_bar_str = u'%s%s' % (download_flag * percent, not_download_flag * (10 - percent))
    all_percent_bar_list[part_index-1] = percent_bar_str
    info_str = u'- %s%% | total_size: %s | download_size: %s | speed: %s / s' % (
                                                                round((float(current_size) / total_size) * 100, 2),
                                                                convert_storage_read(total_size),
                                                                convert_storage_read(current_size),
                                                                convert_storage_read(current_speed)
                                                                )
    all_percent_bar_str = u'%s%s' % (u' '.join(all_percent_bar_list), info_str)
    sys.stdout.write('\r' + all_percent_bar_str)


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


def thread_scan_video(url_list):
    result = {
        'code': 0,
        'info': '',
        'response': 'success'
    }
    file_path = os.path.join(os.path.dirname(__file__), 'butterfly01.flv')
    all_part_num = len(url_list)
    all_percent_bar_list = [u'·' * 10 for i in range(all_part_num)]
    print '当前视频共有%s部分' % str(all_part_num)
    try:
        for i, url in enumerate(url_list):
            part_index = i + 1
            file_path_list = file_path.split('.')
            part_file_path = '%s_%s.%s' % (file_path_list[0], str(part_index), file_path_list[-1])
            base_url = re.search('https://.+?\.com', url).group()
            if base_url:
                host = base_url.split(r"https://")[-1]
                headers = {
                    'Host': '%s' % host,
                    'Connection': 'keep-alive',
                    'Origin': 'https://www.bilibili.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
                    'Accept': '*/*',
                    'Referer': 'https://www.bilibili.com/bangumi/play/ep198482/',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                }
            else:
                result.update({
                    'code': 1,
                    'info': u'未获得第%s部分视频host' % part_index,
                    'response': 'fail'
                })
                return result
            t = threading.Thread(target=download_video, name='第%s部分' % part_index,
                                 args=(url, part_file_path, headers, part_index, all_percent_bar_list))
            t.start()
    except Exception as e:
        print e


def download_video(url, part_file_path, headers, part_index, all_percent_bar_list):
    try:
        print '正在获取 %s ' % str(threading.current_thread().name)
        response = requests.get(url, headers=headers, stream=True, verify=False)
        part_video_size = int(response.headers['content-length'])
        if not part_video_size:
            print '未获取到第%s部分视频数据' % part_index
            return
        global total_size
        global current_size
        global last_size
        # 视频文件总大小
        total_size += part_video_size
        # 当前视频文件大小
        part_file_size = 0
        if os.path.exists(part_file_path):
            # 已获取到视频的bytes数
            part_file_size = os.path.getsize(part_file_path)
            current_size += part_file_size
            last_size += part_file_size
            # 判断是否已经获取到视频全部数据
            if part_file_size < part_video_size:
                headers['Range'] = 'bytes=%d-' % part_file_size
                response = requests.get(url, headers=headers, stream=True, verify=False)
            else:
                print u'第%s部分视频已下载完成' % part_index
                return
        with open(part_file_path, 'ab') as f:
            # 块大小1m, 1m 刷新一次
            block_size = pow(1024, 2)
            for block in response.iter_content(chunk_size=block_size):
                if block:
                    f.write(block)
                    f.flush()
                    # 当前部分视频文件大小
                    part_file_size += block_size
                    # 当前视频文件大小
                    current_size += block_size
                    if part_file_size > part_video_size:
                        part_file_size = part_video_size
                    download_bar(part_video_size, part_file_size,
                                 part_index, all_percent_bar_list)
    except Exception as e:
        print traceback.format_exc(e)


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
            f.flush()
            print '已合并文件： %s' % merge_file
    print '合并完成'

if __name__ == '__main__':
    # scan_video()
    # merge_video(os.path.join(os.path.dirname(__file__), '1.flv'))
    url_list = [
        r'https://upos-hz-mirrorks3u.acgvideo.com/upgcxcode/41/96/34659641/34659641-1-64.flv?e=ig8euxZM2rNcNbhj7zNVhoMahzKMhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1540268136&gen=playurl&oi=1897879350&os=ks3u&platform=pc&trid=677e6ddb89914966a7e667f8ad6b6543&uipk=5&uipv=5&upsig=4d5c9825ad8f8d4525d4193493459a84',
        r'https://upos-hz-mirrorks3u.acgvideo.com/upgcxcode/41/96/34659641/34659641-2-64.flv?e=ig8euxZM2rNcNbhjnweVhoMahzu3hwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1540268136&gen=playurl&oi=1897879350&os=ks3u&platform=pc&trid=677e6ddb89914966a7e667f8ad6b6543&uipk=5&uipv=5&upsig=ce6d1efc79eb24951f322e6bcb097bd2',
        r'https://cn-jszj-dx-v-01.acgvideo.com/upgcxcode/41/96/34659641/34659641-3-64.flv?expires=1540209900&platform=pc&ssig=UkGR2uYEaGOoL2g95amKiQ&oi=1897879350&nfa=BpfiWF+i4mNW8KzjZFHzBQ==&dynamic=1&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=&trid=98aac7bcc1224e6e962d044f029071d9&nfc=1',
        r'https://cn-jszj-dx-v-01.acgvideo.com/upgcxcode/41/96/34659641/34659641-4-64.flv?expires=1540209900&platform=pc&ssig=TCTrnvpr3iXdtBABlTGCDg&oi=1897879350&nfa=BpfiWF+i4mNW8KzjZFHzBQ==&dynamic=1&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=&trid=98aac7bcc1224e6e962d044f029071d9&nfc=1',
        r'https://upos-hz-mirrorks3u.acgvideo.com/upgcxcode/41/96/34659641/34659641-5-64.flv?e=ig8euxZM2rNcNbhjhz4VhoMahbujhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1540268136&gen=playurl&oi=1897879350&os=ks3u&platform=pc&trid=677e6ddb89914966a7e667f8ad6b6543&uipk=5&uipv=5&upsig=1e00548ef70b825542594119ec2debd4',
        r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/41/96/34659641/34659641-6-64.flv?e=ig8euxZM2rNcNbhjnweVhoMahzu3hwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1540210175&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=368900&trid=98aac7bcc1224e6e962d044f029071d9&uipk=5&uipv=5&um_deadline=1540210175&um_sign=cee6680ff6813bbbb98a8c4dd7d7dece&upsig=ffbaa4a4fef56140eac41b946f30df64',
        r'https://cn-jszj-dx-v-01.acgvideo.com/upgcxcode/41/96/34659641/34659641-7-64.flv?expires=1540209900&platform=pc&ssig=BdiaaG9TL2HqoxcOupalxA&oi=1897879350&nfa=BpfiWF+i4mNW8KzjZFHzBQ==&dynamic=1&hfb=Yjk5ZmZjM2M1YzY4ZjAwYTMzMTIzYmIyNWY4ODJkNWI=&trid=98aac7bcc1224e6e962d044f029071d9&nfc=1',
        r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/41/96/34659641/34659641-8-64.flv?e=ig8euxZM2rNcNbh37zTVhoMa7zUghwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1540210175&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=387600&trid=98aac7bcc1224e6e962d044f029071d9&uipk=5&uipv=5&um_deadline=1540210175&um_sign=7bcea66598edf77998269be3507b638a&upsig=e13ab9eb1bc40ac51440983d5ff0ffd6'
    ]
    thread_scan_video(url_list)