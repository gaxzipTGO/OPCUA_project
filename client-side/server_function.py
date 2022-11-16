#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time
destination_IP = input('please input destination IP address').encode()
destination_port = input('please input destination Port').encode()
def RecvFile(conn) :
        conn.send( b'OK!' )
        print('wait for file size')
        file_size = int(conn.recv(1024).decode("utf-8"))
        conn.send( b'OK!' )
        time.sleep(1)
        print(file_size)
        print('wait for file')
        file_byte = b''
        while file_size > 0 :
            buffer = conn.recv(1024)
            file_byte = file_byte + buffer
            file_size -= 1024
            print(file_size)
        file = file_byte.decode('utf-8')
        conn.send( b'filedone!' )
        localPath = conn.recv(1024).decode("utf-8")
        conn.send( b'localPathdone!' )
        nc_name = conn.recv(1024).decode("utf-8")
        conn.send( b'ncNamePathdone!' )
        data = {
            "file_data" : file,
            "file_path" : localPath,
            "file_name" : nc_name
        }
        jsondata = json.dumps(data)
        print(jsondata.encode())
        jsonfile = {
            "file" :True,
            "data" : data
        }
        print(jsonfile)
        return json.dumps(jsonfile).encode() 

def RecvCmd(command) :
    getbyte = command.replace(b'127.0.0.1:5050',destination_IP+b':'+destination_port)
    data = getbyte.decode('utf-8')
    jsonfile = {
        "file" :False,
        "data" :data 
    }
    return json.dumps(jsonfile).encode() 
       

def Recv(conn) :
    command = conn.recv(1024)
    #http_info =  command.decode('utf-8').split('\\r\\n')
    #json_info = http_info[len(http_info)-1].replace('\\','')
    #info_data = json.loads(json_info)
    #machine_name = info_data['name']
    if command == b'sendfile!' :
        return RecvFile(conn) #,machine_name
    else :    
        return RecvCmd(command) #,machine_name
        

