from mimetypes import init
import time
from opcua import ua, uamethod, Server
from opcua.server.history_sql import HistorySQLite
from queue import Queue
import socket
import time
import threading

OPCUA_HOST = '127.0.0.1'
ClIENT_HOST = '127.0.0.1'
PORT = 502

GETVAULE = bytes(1)

def ServerIinital(host,policy,certificate,private_key) :
    '''
    you can use if you are too lazy
    '''
    server = Server()
    server.set_endpoint('opc.tcp://'+host+':4840')
    server.set_security_policy(policy)
    server.load_certificate(certificate)
    server.load_private_key(private_key)

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



if __name__ == '__main__':

    # server initialization
    server = Server()
    server.set_endpoint('opc.tcp://'+OPCUA_HOST+':4840') 
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
    server.load_certificate('security/server_cert.pem')
    server.load_private_key('security/server_prikey.pem')

    # register a namespace
    uri = 'OPCUA_SERVER'
    ns_index = server.register_namespace(uri)
    
    # setup nodes
    objects = server.get_objects_node()
    obj = objects.add_object(f'ns={ns_index};i=1', f'{ns_index}:object')
    resquest = obj.add_property(f'ns={ns_index};i=8', f'{ns_index}:property', b'')
    resquest.set_writable()
    response = obj.add_property(f'ns={ns_index};i=6', f'{ns_index}:property', b'')
    response.set_writable()
    server.start()

    client_to_PLC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_to_PLC.connect((ClIENT_HOST, PORT))

    # print(server.historize_node_event(server.get_server_node()))
    try:
        buf_count = 0
        while True:
            print('wait for recv resquest data')
            data = recv_value(resquest)
            print('recv resquest data : ', data)
            client_to_PLC.send(str(len(data)).encode())
            if client_to_PLC.recv(1024) == b'OK' :
                client_to_PLC.send(data)
                print( 'wait for CNC response' )
                response_info = client_to_PLC.recv(1024)
                print('recv CNC response data : ', response_info)
                response.set_value(response_info)

            
    finally:
        # client_to_PLC.close()
        server.stop()
    # end try-finally
# end if
