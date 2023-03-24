import requests
import json
import hashlib
import hmac
import re
import socket
import time
from bs4 import BeautifulSoup


class Zing:
    def __init__(self, url) -> None:
        self.__zing_version = '1.9.12'
        self.__api_key = 'X5BM3w8N7MKozC0B85o4KMlzLZKhV00y'
        self.__secret_key = 'acOrvUS15XRW2o9JksiK1KgQ6Vbds8ZW'.encode()
        self.__url = url
        self.__new_urls = []
        self.__count = 0     
        self.__space = '$$$$$'



    def run(self):
        result = None
        try:
            self.__set_cookies()
            self.__set_ctime()
            self.__set_craw_url()
                
            res = requests.get(self.__crawl_url, cookies=self.__cookies)

            res_data = res.content.decode()
            items = json.loads(res_data)['data']['items']

            for item in items:
                if not f'https://zingmp3.vn{item["link"]}' in self.__new_urls:
                    self.__new_urls.append(f'https://zingmp3.vn{item["link"]}')
                    self.__count += 1
            result = f'success:{self.__space.join(self.__new_urls)}'
        except Exception:
            result = False
        #     raise Exception
            
        return result
        # self.__save_data()


    def __save_data(self):
        print(len(''.join(self.__new_urls)))
        f = open('bytes.txt', 'a')
        f.write(''.join(self.__new_urls))
        f.close()
        # print(len(''.join(self.__new_urls)))

    def __set_craw_url(self):
        self.__set_song_key()
        msg = '/api/v2/recommend/get/songs{}'.format(hashlib.sha256(f"ctime={self.__ctime}id={self.__song_key}version={self.__zing_version}".encode()).hexdigest())
        sig = hmac.new(self.__secret_key, msg.encode(), hashlib.sha512).hexdigest()
        self.__crawl_url = f"https://zingmp3.vn/api/v2/recommend/get/songs?id={self.__song_key}&ctime={self.__ctime}&version={self.__zing_version}&sig={sig}&apiKey={self.__api_key}"

    
    def __set_song_key(self):
        self.__song_key = re.search( '[/]([a-zA-Z0-9]+).html',self.__url).group(1)

    def __set_ctime(self):
        self.__ctime = int(time.time())

    def __set_cookies(self):
        res = requests.get("https://zingmp3.vn")
        self.__cookies = res.cookies.get_dict()


class Nct:
    def __init__(self, url) -> None:
        self.__url = url
        self.__new_urls = []
        self.__count = 0  
        self.__space = '$$$$$'


    def run(self):
        result = None
        try:
            self.__set_song_key()
            res = requests.get(f"https://www.nhaccuatui.com/ajax/get-recommend-nextsmarty?key={self.__song_key}&type=song&deviceId=&ref_event=")
            res_data = res.content.decode("utf-8")
            soup = BeautifulSoup(json.loads(res_data)['data']["html"], features="html5lib")
            song_links =  soup.find_all('h3')
            for s in song_links:
                if s.a["href"] not in self.__new_urls:
                    self.__new_urls.append(s.a["href"])
                    self.__count+=1
            result = f'success:{self.__space.join(self.__new_urls)}'
        except:
            result = False

        return result
    
    def __set_song_key(self):
        self.__song_key = self.__url.split(".")[-2]


def crawl(url):
    result = None
    try:
        print("Crawl: ",url)
        if url.startswith("https://zingmp3.vn"):
            result = Zing(url).run()
        if url.startswith("https://www.nhaccuatui.com"):
            print("Nct: ")
            result = Nct(url).run()
    except Exception:
        pass
    return result

    #     raise Exception


def start_client():
        client_socket = socket.socket()
        host = '192.168.1.12'
        port = 2032

        print('Waiting for connection response')
        try:
            client_socket.connect((host, port))
        except socket.error as e:
            print(str(e))

        res = client_socket.recv(2048)

        while True:
            msg = "get_input"
            client_socket.sendall(str.encode(msg))
            res = client_socket.recv(2048)
            data = res.decode('utf-8')
            if data == 'exit':
                print("Exit")
                exit()
            result = crawl(data)
            if result:
                msg = result
                # print(result)
                client_socket.sendall(str.encode(msg))
                res = client_socket.recv(2048)
                print(res.decode('utf-8'))

start_client()