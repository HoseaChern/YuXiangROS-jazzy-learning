"""
先进入 docs/ 目录
再"python3 -m http.server"

之后可以使用此节点
"""

import threading

import requests


class Download:
    def download(self, url, callback):
        print(f"Thread: {threading.get_ident()} is downloading {url}")
        response = requests.get(url)
        response.encoding = "utf-8"
        callback(url, response.text)

    def start_download(self, url, callback):
        thread = threading.Thread(target=self.download, args=(url, callback))
        thread.start()


def finish_callback(url, content):
    print(f"Thread: {threading.get_ident()} has downloaded {url}")
    print(f"Content: {content}")


def main(args=None):
    downloader = Download()
    downloader.start_download("http://0.0.0.0:8000/novel1.txt", finish_callback)
    downloader.start_download("http://0.0.0.0:8000/novel2.txt", finish_callback)
    downloader.start_download("http://0.0.0.0:8000/novel3.txt", finish_callback)
