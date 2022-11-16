from cmath import isclose
from sqlite3 import Time
import socket
from opcua import ua, Client
import threading
import server_function
import json
from queue import Queue

OPCUA_HOST = '127.0.0.1'

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5050

NOT_SAFE_HOST = '192.168.1.64'
NOT_SAFE_PORT = 502

def wait_value(prop,queue) :
    
    while True :
        data_recv = prop.get_value() 
        if data_recv != b'' :
            queue.put(data_recv)
            prop.set_value(b'')
            break

def recv_value(prop) :
    data_recv_queue = Queue()
    read = threading.Thread(target=wait_value, args=(prop,data_recv_queue,))
    read.setDaemon(True)
    read.start()
    print("waiting for read")
    read.join() 
    return data_recv_queue.get() 


def Connect_MES() :
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(5) 
    return server


def Connect_NotSafe() :
    print('wait connect to not safe TCP/IP')
    client_not_safe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_not_safe.connect((NOT_SAFE_HOST, NOT_SAFE_PORT))
    print('not safe TCP/IP successly')
    return client_not_safe

def ClientInitial(host,security_string) :
    client = Client('opc.tcp://'+host+':4840')
    client.set_security_string(security_string)
    return client

def OPCUA_Send_Data(var,data) :
    var.set_value(data)

def NOT_Safe_Send_Data(notsafe_server,data) :
    notsafe_server.send(data)

if __name__ == '__main__' :    

    # server initialization  
    #wait MES connect

    print('wait connect to opcua server')
    client_opcua = ClientInitial(OPCUA_HOST,'Basic256Sha256,SignAndEncrypt,security/client_cert.pem,security/client_prikey.pem')
    client_opcua.connect() 
    print('Username/Password authentication passed')
    ns_index = client_opcua.get_namespace_array().index('OPCUA_SERVER')
    # (1) get nodes via nodeid
    request = client_opcua.get_node(f'ns={ns_index};i=8')
    response = client_opcua.get_node(f'ns={ns_index};i=6')
    # connect to opcua safe module

    #print('wait connect to notSafe Server')
    #clinet_not_safe = Connect_NotSafe()
    #connect to not safe server
    try :
        while True :
            # server initialization
            server = Connect_MES()
            #wait MES connect   
            while True :
                try :
                    # waiting for modbusFunctionCode
                    print('wait connect to MES')
                    conn, addr = server.accept()
                    conn.settimeout(100)   
                    print('MES connect successly')
                    print("wait client send")
                    recv_data = server_function.Recv(conn) 
                    if recv_data != b'' :
                        print('recv client send : ', recv_data)
                        threads = []
                        t1 = threading.Thread(target=OPCUA_Send_Data, args=(request,recv_data,))

                        threads.append(t1)
                            
                        for t in threads :
                            t.start()
                        for t in threads :
                            t.join()
                        print('send successly!!')
                        print('wait for response')
                        response_info = recv_value(response)
                        print( "recv server send response : ", response_info )
                        conn.send(response_info)
                        conn.close()
                        #elif machine_name == 'MV66A' :
                            #t2 = threading.Thread(target=NOT_Safe_Send_Data, args=(client_not_safe,recv_data,))                             
                            #threads.append(t2)
                            #response_info = client_not_safe.recv(65535)
                            #print( "recv server send response : ", response_info )
                            #conn.send(response_info)
                            #conn.close()
                        
                    else :
                        conn.close()
                        break 
                except Exception as e :
                    print(str(e))
                    conn.close()
                    break                                        

    except Exception as e:
        client_opcua.disconnect()
        print(str(e))    

  






  







  
