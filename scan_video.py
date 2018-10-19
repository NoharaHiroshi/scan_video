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


def web_scan(url):
    with webdriver.PhantomJS() as browser:
        browser.get(url)
        print browser.page_source


def download_bar(all_file_size, all_current_size, file_size, current_size,
                 part_index, start_time, end_time, all_percent_bar_list):
    """
    :param all_file_size: 当前完整视频文件的大小
    :param all_current_size：完整视频已下载的大小
    :param file_size: 部分视频文件的大小
    :param current_size: 部分视频已下载的文件大小
    :param part_index: 部分视频的索引
    :param all_part_num: 所有部分视频的数量
    :param block_size: 块大小
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return:
    """
    download_flag = u'|'
    not_download_flag = u'·'
    # 部分视频文件下载的百分比 0 - 10
    percent = int(float(current_size) / file_size * 10)
    current_speed = float(all_file_size - all_current_size) / (end_time - start_time + 1)
    percent_bar_str = u'%s%s' % (download_flag * percent, not_download_flag * (10 - percent))
    all_percent_bar_list[part_index-1] = percent_bar_str
    info_str = u'- %s%% | total_size: %s | download_size: %s | speed: %s / s' % (
                                                                round((float(all_current_size) / all_file_size), 2),
                                                                convert_storage_read(all_file_size),
                                                                convert_storage_read(all_current_size),
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
    file_path = os.path.join(os.path.dirname(__file__), '2.flv')
    total_size = 0
    current_size = 0
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
                                 args=(url, part_file_path, headers, part_index, total_size, current_size, all_percent_bar_list))
            t.start()
    except Exception as e:
        print e


def download_video(url, part_file_path, headers, part_index, all_file_size, current_file_size, all_percent_bar_list):
    try:
        print '正在获取 %s ' % str(threading.current_thread().name)
        response = requests.get(url, headers=headers, stream=True, verify=False)
        all_content_length = int(response.headers['content-length'])
        if not all_content_length:
            print '未获取到第%s部分视频数据' % part_index
            return
        all_file_size += all_content_length
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
                    current_file_size += current_length
                    if current_length > all_content_length:
                        current_length = all_content_length
                    end_time = time.time()
                    download_bar(all_file_size, current_file_size, all_content_length, current_length,
                                 part_index, start_time, end_time, all_percent_bar_list)
                    start_time = time.time()
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
        r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/73/96/34659673/34659673-1-15.flv?e=ig8euxZM2rNcNbRVhwhVhoMghwdjhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1539946681&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=100300&trid=e7dfe0f420294c7ebe66f86a1b366334&uipk=5&uipv=5&um_deadline=1539946681&um_sign=0283b646004fd50f381a9833c375e778&upsig=46ce5014f0255f8897981fd49555dea2',
        r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/73/96/34659673/34659673-2-15.flv?e=ig8euxZM2rNcNbRVhzuVhoMghwuMhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1539946681&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=103700&trid=e7dfe0f420294c7ebe66f86a1b366334&uipk=5&uipv=5&um_deadline=1539946681&um_sign=33d588a6f06df20acdbcd91f1839dedd&upsig=4f1ef872e2f1e1512207f6d570b0c7f4',
        r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/73/96/34659673/34659673-3-15.flv?e=ig8euxZM2rNcNbRVhwhVhoMghwdjhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1539946681&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=100300&trid=e7dfe0f420294c7ebe66f86a1b366334&uipk=5&uipv=5&um_deadline=1539946681&um_sign=d0c9f32db7303561c1078d9050411f18&upsig=4fe9139c3ec326bd27029a6e2a9afb07',
        r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/73/96/34659673/34659673-4-64.flv?e=ig8euxZM2rNcNbha7wdVhoMa7w4VhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1539947403&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=374000&trid=32f859003ecf4845a53739bbd599ffd7&uipk=5&uipv=5&um_deadline=1539947403&um_sign=7332fc70fab21e21b2a94c197c1bb0c0&upsig=242e111d1cc80673ec56b207eeb937fb',
        r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/73/96/34659673/34659673-5-15.flv?e=ig8euxZM2rNcNbRV7WKVhoMghWd3hwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1539946681&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=105400&trid=e7dfe0f420294c7ebe66f86a1b366334&uipk=5&uipv=5&um_deadline=1539946681&um_sign=64b30b30b78fba7d899eeb151087886e&upsig=90c01686a8e9096e8c440536d12df023',
        r'https://upos-hz-mirrorks3u.acgvideo.com/upgcxcode/73/96/34659673/34659673-6-64.flv?e=ig8euxZM2rNcNbhjnweVhoMahzu3hwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1539947403&gen=playurl&oi=1897879350&os=ks3u&platform=pc&trid=32f859003ecf4845a53739bbd599ffd7&uipk=5&uipv=5&upsig=fdb59b2eaefe239dc4cb3706af2cd15b',
        r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/73/96/34659673/34659673-7-15.flv?e=ig8euxZM2rNcNbejnWdVtWRHhz4VhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEVEuxTEto8i8o859r1qXg8xNEVE5XREto8GuFGv2U7SuxI72X6fTr859IB_&deadline=1539946681&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=96900&trid=e7dfe0f420294c7ebe66f86a1b366334&uipk=5&uipv=5&um_deadline=1539946681&um_sign=0ca76a63914b8c77a511f9347590b364&upsig=c96793789c6b3badb5003b7690d6ed7e',
        r'https://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/73/96/34659673/34659673-8-15.flv?e=ig8euxZM2rNcNbR17WTVhoMghzRghwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1539946681&dynamic=1&gen=playurl&oi=1897879350&os=kodo&platform=pc&rate=115600&trid=e7dfe0f420294c7ebe66f86a1b366334&uipk=5&uipv=5&um_deadline=1539946681&um_sign=d1f38f875602b3a28b85b164fee28ab6&upsig=76f4c992718b5c47ea2b6b5bfd0372dd'
    ]
    thread_scan_video(url_list)