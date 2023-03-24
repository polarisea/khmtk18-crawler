import pexpect
import subprocess
import json
import os
import socket
from _thread import *
from csv import writer
import time



class Crawl:
    def __init__(self) -> None:
        self.__client = 0
        self.__port = 2032
        self.__index = 0
        self.__input_dir = './input.txt'
        self.__waited_dir = "./waited.txt"
        self.__finished_dir = "./finished.txt"
        self.__csv_dir = './csv.csv'
        self.__input = []
        self.__finished = []
        self.__count = 0
        self.__input_length = 0
        self.__max_client = 5
        self.__client_timeout = 60

    def run(self):
        print("Start crawling")
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
        try:
            data = data[8:].split("$$$$$")
            if not os.path.exists(self.__csv_dir):
                with open(self.__csv_dir, 'a') as f_object:
                    field_names = ["id", "name", "artists", "lyric"]
                    writer_object = writer(f_object)        
                    writer_object.writerow(field_names)
                    f_object.close()
        
            with open(self.__csv_dir, 'a') as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(data[1:])
                f_object.close()
            self.__finished.append(data[0])
            self.__count += 1
        except:
            raise Exception("DM error")
            pass
        print("Handle data")
        if self.__count >= self.__input_length:
            self.__check_stop()


    def __check_stop(self):
        if self.__index >= self.__input_length or self.__client == 0 :

            f = open(self.__input_dir, 'w')
            f.write('\n'.join(set(self.__input) - set(self.__finished)))
            f.close()
            f = open(self.__finished_dir, 'w')
            f.write('\n'.join(self.__finished))
            f.close()
            print(f"Total: {self.__count}/{self.__input_length} song was crawled ")
            os._exit(1)





if __name__ == '__main__':
    Crawl().run()