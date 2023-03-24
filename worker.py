import socket
import time
import hashlib
import hmac
import requests
import json
import os
import re
import html

class Zing:
    def __init__(self, url) -> None:
        self.__url = url
        self.__output_dir = "./output"
        self.__zing_version = '1.9.12'
        self.__secret_key = "acOrvUS15XRW2o9JksiK1KgQ6Vbds8ZW".encode()
        self.__api_key = 'X5BM3w8N7MKozC0B85o4KMlzLZKhV00y'
        self.__space = '$$$$$'

    def run(self):
        result = None
        try:
            self.__load_foler()
            self.__set_song_id()
            self.__set_cookies()
            self.__set_ctime()
            self.__set_song_key()

            self.__crawl_info()
            self.__craw_thumbnail()

            if self.__has_lyric:
                self.__crawl_lyric()
            else:
                self.__song_lyric = "No lyric"
            
            if self.__song_name == '':
                self.__song_name == "No name"
            if self.__song_artists == '':
                self.__song_artists == 'No artists'
                

            self.__craw_mp3()
            result = f"success:{self.__url}{self.__space}{self.__song_id}{self.__space}{self.__song_name}{self.__space}{self.__song_artists}{self.__space}{self.__song_lyric}"
        except Exception:
            self.__clear_song()
            raise Exception
            result = False

        return result
    
    
    def __load_foler(self):
        if not os.path.exists(self.__output_dir):
            os.mkdir(self.__output_dir)

    def __set_song_id(self):
        self.__song_id = hashlib.md5(self.__url.encode()).hexdigest()

    def __set_cookies(self):
        res = requests.get("https://zingmp3.vn")
        self.__cookies = res.cookies.get_dict()

    def __set_ctime(self):
        self.__ctime = int(time.time())  

    def __set_song_key(self):
        self.__song_key = re.search( '[/]([a-zA-Z0-9]+).html',self.__url).group(1)


    def __crawl_info(self):
        self.__set_info_url()
        
        res = requests.get(self.__info_url, cookies=self.__cookies)
        res_data = json.loads(res.content)["data"]

        self.__song_name = res_data["title"]
        self.__song_artists = res_data["artistsNames"]
        self.__song_thumbnail_url = res_data["thumbnailM"]
        if "hasLyric" in res_data:
            self.__has_lyric = res_data["hasLyric"]
        else:
            self.__has_lyric = False
        

    def __set_info_url(self):
        msg = '/api/v2/page/get/song{}'.format(hashlib.sha256(f"ctime={self.__ctime}id={self.__song_key}version={self.__zing_version}".encode()).hexdigest())
        sig = hmac.new(self.__secret_key, msg.encode(), hashlib.sha512).hexdigest()
        self.__info_url = f"https://zingmp3.vn/api/v2/page/get/song?id={self.__song_key}&ctime={self.__ctime}&version={self.__zing_version}&sig={sig}&apiKey={self.__api_key}"


    def __craw_thumbnail(self):
        img_format = self.__song_thumbnail_url.split(".")[-1]
        stream = requests.get(self.__song_thumbnail_url, cookies=self.__cookies)
        open(f"{self.__output_dir}/{self.__song_id}.{img_format}", "wb").write(stream.content)
        

    def __crawl_lyric(self):
        self.__set_lyric_url()
        
        res = requests.get(self.__lyric_url, cookies=self.__cookies)
        lyric_file_link = json.loads(res.content)['data']['file']

        stream = requests.get(lyric_file_link)
        open(f'{self.__output_dir}/{self.__song_key}.lyric.lrc', 'wb').write(stream.content)
        
        f = open(f'{self.__output_dir}/{self.__song_key}.lyric.lrc', "r")
        lyric = f.read()
        f.close()
        os.remove(f'{self.__output_dir}/{self.__song_key}.lyric.lrc')
        
        self.__song_lyric = re.sub('(.+:.+])', '', str(lyric)).strip()


    def __set_lyric_url(self):
        msg = '/api/v2/lyric/get/lyric{}'.format(hashlib.sha256(f"ctime={self.__ctime}id={self.__song_key}version={self.__zing_version}".encode()).hexdigest())
        sig = hmac.new(self.__secret_key, msg.encode(), hashlib.sha512).hexdigest()
        self.__lyric_url = f"https://zingmp3.vn/api/v2/lyric/get/lyric?id={self.__song_key}&ctime={self.__ctime}&version={self.__zing_version}&sig={sig}&apiKey={self.__api_key}"


    def __craw_mp3(self):
        self.__set_mp3_url()

        res = requests.get(self.__mp3_url, cookies=self.__cookies)
        mp3_file_link = json.loads(res.content)['data']['128']
     
        stream = requests.get(mp3_file_link)
        open(f'{self.__output_dir}/{self.__song_id}.mp3', 'wb').write(stream.content)

    
    def __set_mp3_url(self):
        msg = '/api/v2/song/get/streaming{}'.format(hashlib.sha256(f"ctime={self.__ctime}id={self.__song_key}version={self.__zing_version}".encode()).hexdigest())
        sig = hmac.new(self.__secret_key, msg.encode(), hashlib.sha512).hexdigest()
        self.__mp3_url = f"https://zingmp3.vn/api/v2/song/get/streaming?id={self.__song_key}&ctime={self.__ctime}&version={self.__zing_version}&sig={sig}&apiKey={self.__api_key}"
 

    def __clear_song(self):
        if os.path.exists(f"{self.__output_dir}/{self.__song_key}.mp3"):
            os.remove(f"{self.__output_dir}/{self.__song_key}.mp3")
        if os.path.exists(f"{self.__output_dir}/{self.__song_key}.jpg"):
            os.remove(f"{self.__output_dir}/{self.__song_key}.jpg")




class Nct:
    def __init__(self, url) -> None:
        self.__url = url
        self.__output_dir = "./output"
        self.__space = "$$$$$"


    def run(self):
        result = None
        try:
            self.__set_song_id()

            res = requests.get(self.__url)
            res_data = res.content.decode()

            title = re.search(f"<title>(.+)</title>", res_data).group(1)
            self.__song_name = title.split("-")[0].strip()
            self.__song_artists = title.split("-")[1][1:]

            lyric = re.findall(r'<br />(.+)\n', res_data)
            self.__song_lyric = html.unescape("\n".join(lyric))

            self.__info_key = re.search(r'true&key1=(.+)";', res_data).group(1)
            
            self.__thumbnail_link = re.search(r"(https://avatar.+jpg)", res_data).group(1)
            thumbnail_format = self.__thumbnail_link.split(".")[-1]

            stream = requests.get(self.__thumbnail_link)
            open(f'{self.__output_dir}/{self.__song_id}.{thumbnail_format}', 'wb').write(stream.content)

            res = requests.get(f"https://www.nhaccuatui.com/flash/xml?html5=true&key1={self.__info_key}")

            mp3_link = re.search(r'(https.+)]]', res.content.decode("utf-8")).group(1)

            stream = requests.get(mp3_link)
            open(f'{self.__output_dir}/{self.__song_id}.mp3', 'wb').write(stream.content)
            
            if self.__song_name == '':
                self.__song_name == "No name"
            if self.__song_artists == '':
                self.__song_artists == 'No artists'
            if self.__song_lyric == '':
                self.__song_lyric = "No lyric"
            
            result = f"success:{self.__url}{self.__space}{self.__song_id}{self.__space}{self.__song_name}{self.__space}{self.__song_artists}{self.__space}{self.__song_lyric}"

        except:
            result = False
        
        return result
    
    def __set_song_id(self):
        self.__song_id = hashlib.md5(self.__url.encode()).hexdigest()


def crawl(url):
    result = None
    print("Crawl: ",url)
    if url.startswith("https://zingmp3.vn"):
        result = Zing(url).run()
    if url.startswith("https://www.nhaccuatui.com"):
        print("Nct: ")
        result = Nct(url).run()
    return result

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
                client_socket.sendall(str.encode(msg))
        

start_client()