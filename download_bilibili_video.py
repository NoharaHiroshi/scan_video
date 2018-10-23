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


class DownloadBilibiliVideo:

    def __init__(self, file_name):
        # 视频文件名称
        self.file_name = file_name
        # 视频文件总大小
        self.total_size = 0
        # 已下载视频文件大小
        self.current_size = 0
        # 默认单元大小
        self.unit = 1024
        # 初始化下载进度条
        self.all_percent_bar_list = list()
        # 初始headers
        self.headers = {
            'Connection': 'keep-alive',
            'Origin': 'https://www.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'https://www.bilibili.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        # 已下载视频文件大小
        self.last_size = 0
        # 上次下载记录时间
        self.last_record_time = time.time()
        # 部分进度条划分数
        self.part_download_bar_num = 10
        # 块大小
        self.block_size = pow(1024, 2)

    # 下载进度条
    def download_bar(self, part_file_size, part_current_size, part_index):
        point_time = time.time()
        download_flag = u'|'
        not_download_flag = u'·'
        percent = int(float(part_current_size) / part_file_size * self.part_download_bar_num)
        time_interval = (point_time - self.last_record_time) if (point_time - self.last_record_time) != 0 else 1
        current_speed = float(self.current_size - self.last_size) / time_interval
        percent_bar_str = u'%s%s' % (download_flag * percent, not_download_flag * (self.part_download_bar_num - percent))
        self.all_percent_bar_list[part_index - 1] = percent_bar_str
        download_percent = round((float(self.current_size) / self.total_size) * 100, 2)
        info_str = u'- %s%% | total_size: %s | download_size: %s | speed: %s / s' % (
            download_percent if download_percent <= 100 else 100,
            self.convert_storage_read(self.total_size),
            self.convert_storage_read(self.current_size),
            self.convert_storage_read(current_speed)
        )
        all_percent_bar_str = u'%s%s' % (u' '.join(self.all_percent_bar_list), info_str)
        self.last_record_time = point_time
        sys.stdout.write('\r' + all_percent_bar_str)

    def convert_storage_read(self, bytes_content):
        bytes_content = int(bytes_content)
        if bytes_content < self.unit:
            return '%.2f bytes' % bytes_content
        elif self.unit <= bytes_content < math.pow(self.unit, 2):
            return '%.2f kb' % (bytes_content / self.unit)
        elif math.pow(self.unit, 2) <= bytes_content < math.pow(self.unit, 3):
            return '%.2f mb' % (bytes_content / math.pow(self.unit, 2))
        else:
            return '%.2f gb' % (bytes_content / math.pow(self.unit, 3))

    def assign_download_task(self, url_list):
        file_path = os.path.join(os.path.dirname(__file__), self.file_name)
        # 判断当前文件是否已存在
        if os.path.exists(file_path):
            print u'current file is exist'
            return
        all_part_num = len(url_list)
        # 初始化下载进度条
        self.all_percent_bar_list = [u'·' * 10 for i in range(all_part_num)]
        try:
            for i, url in enumerate(url_list):
                part_index = i + 1
                file_path_list = file_path.split('.')
                part_file_path = '%s_%s.%s' % (file_path_list[0], str(part_index), file_path_list[-1])
                base_url = re.search('https://.+?\.com', url).group()
                if base_url:
                    host = base_url.split(r"https://")[-1]
                    self.headers.update({
                        'Host': host
                    })
                    # 注册任务
                    t = threading.Thread(target=self.download_video, args=(url, part_file_path, self.headers, part_index))
                    t.start()
                else:
                    continue
        except Exception as e:
            print traceback.format_exc(e)

    def download_video(self, url, part_file_path, headers, part_index):
        try:
            response = requests.get(url, headers=headers, stream=True, verify=False)
            part_video_size = int(response.headers['content-length'])
            if not part_video_size:
                print u'part %s data 0' % part_index
                return
            # 视频文件总大小
            self.total_size += part_video_size
            # 当前视频文件大小
            part_file_size = 0
            if os.path.exists(part_file_path):
                # 已获取到视频的bytes数
                part_file_size = os.path.getsize(part_file_path)
                self.current_size += part_file_size
                self.last_size += part_file_size
                # 判断是否已经获取到视频全部数据
                if part_file_size < part_video_size:
                    headers['Range'] = 'bytes=%d-' % part_file_size
                    response = requests.get(url, headers=headers, stream=True, verify=False)
                else:
                    print u'part %s finish' % part_index
                    return
            with open(part_file_path, 'ab') as f:
                for block in response.iter_content(chunk_size=self.block_size):
                    if block:
                        f.write(block)
                        f.flush()
                        # 当前部分视频文件大小
                        part_file_size += self.block_size
                        # 当前视频文件大小
                        self.current_size += self.block_size
                        if part_file_size > part_video_size:
                            part_file_size = part_video_size
                        self.download_bar(part_video_size, part_file_size, part_index)
                        self.last_size += self.block_size
        except Exception as e:
            print traceback.format_exc(e)

if __name__ == '__main__':
    bd = DownloadBilibiliVideo('jojo38.flv')
    url_list = [
        r'https://upos-hz-mirrorbos.acgvideo.com/upgcxcode/60/64/57506460/57506460-1-80.flv?e=ig8euxZM2rNcNbKa7zuVhoMH7WUMhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IB5QK==&deadline=1540289387&dynamic=1&gen=playurl&oi=1897879350&os=bos&platform=pc&rate=477700&trid=e5b6b2939f534c289a57642e9fa978b8&uipk=5&uipv=5&um_deadline=1540289387&um_sign=b7cad1a0ec9072b9f22053053b1416b7&upsig=6444a2edb6ce4b8d2c30be3cc6d4885a'
    ]
    bd.assign_download_task(url_list)