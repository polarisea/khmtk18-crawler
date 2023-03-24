import pexpect
import subprocess
import json
import os
import socket
from _thread import *
from csv import writer
import time

client_count = 0
url_count = 0
index = 0
input_urls = []
waited_urls = []
finished_urls = []
limit = 100
input_urls_length = 0
new_urls_length = 0
input_dir = './waited_urls.txt'
waited_dir = "./waited_urls.txt"
finished_dir = "./finished_urls.txt"
port = 3201

class Crawl:
    def __init__(self) -> None:
        self.__client = 0
        self.__port = 2032
        self.__index = 0
        self.__limit = 100
        self.__input_dir = './input.txt'
        self.__waited_dir = "./waited.txt"
        self.__finished_dir = "./finished.txt"
        self.__input = []
        self.__waited = []
        self.__finished = []
        self.__count = 0
        self.__waited_length = 0
        self.__input_length = 0
        self.__max_client = 5
        self.__client_timeout = 60

    def run(self):
        self.__load_data()
        self.__start_socket()

    def __load_data(self):
        print("Load data")
        if os.path.exists(self.__input_dir):
            f = open(self.__input_dir, 'r')
            raw_data = f.read()
            f.close()
            self.__input = raw_data.split('\n')
            self.__input = list(filter(lambda x: len(x) > 0, self.__input))
            self.__input_length = len(self.__input)
        else:
            raise Exception("Invalid input")
        if self.__input_length == 0:
            raise Exception("Invalid input")
        
        if os.path.exists(self.__finished_dir):
            f = open(self.__finished_dir, 'r')
            raw_data = f.read()
            f.close()
            self.__finished = raw_data.split('\n')
            self.__finished = list(filter(lambda x: len(x) > 0, self.__finished))
        
        if os.path.exists(self.__waited_dir):
            f = open(self.__waited_dir, 'r')
            raw_data = f.read()
            f.close()
            self.__waited = raw_data.split('\n')
            self.__waited = list(filter(lambda x: len(x) > 0, self.__waited))
        
        f = open(self.__waited_dir, 'a')
        for url in self.__input:
            if url not in self.__waited and url not in self.__finished:
                f.write(f'\n{url}')
                self.__count += 1
        f.close()

    def __start_socket(self):
        print("Start socket server")
        self.__socket = socket.socket()
        try:
            self.__socket.bind(('', self.__port))
        except socket.error as e:
            raise Exception("Create socket failed")
        
        self.__socket.listen(self.__max_client)
        print('Socket is listening..')

        while True:
            client, address = self.__socket.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(self.__handle_client, (client, ))
            self.__client += 1
    
    def __handle_client(self, connection):
        connection.send(str.encode('Server is working:'))
        connection.settimeout(self.__client_timeout)
        try:
            while True:
                res = connection.recv(4096)
                if not res:
                    print("Client disconnect")
                    break
                data = res.decode("utf-8", "ignore")

                if data == "get_input":
                    if self.__index < self.__input_length:
                        connection.sendall(str.encode(self.__input[self.__index]))
                    else:
                        connection.sendall(str.encode("exit"))
                    self.__index += 1
                    res = connection.recv(4096)
                    data = res.decode("utf-8", "ignore")
                    if data.startswith("success:"):
                        self.__handle_data(data)
                    self.__check_stop()
                    connection.send(str.encode(f"Next: "))
        except:
            pass

        self.__client -= 1
        connection.close()
        if self.__client <= 0:
            self.__check_stop()

    def __handle_data(self, data):
        data = data[8:].split("$$$$$")
        f = open(self.__waited_dir, 'a')
        for url in data:
            if url not in self.__input:
                if url not in self.__waited and url not in self.__finished:
                    f.write(f"\n{url}")
                    self.__count += 1
                self.__input.append(url)
                self.__input_length += 1

        f.close()

        if self.__count >= self.__limit:
            self.__check_stop()
    # except:
        # pass

    def __check_stop(self):
        if self.__index >= self.__input_length or self.__client == 0 or self.__count > self.__limit:
            print(f"Total: {self.__count} song was crawled ")
            os._exit(1)



if __name__ == '__main__':
    Crawl().run()
# main()