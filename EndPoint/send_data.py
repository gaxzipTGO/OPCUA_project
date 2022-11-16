import socket
import json 

def ReadJsonData(jsonByte,conn,client) :
	jsonfile = jsonByte.decode('utf-8') 
	jsonfile = json.loads(jsonfile)
	if jsonfile["file"] == True :
		data = jsonfile["data"]["file_data"]
		filePath = jsonfile["data"]["file_path"]
		fileName = jsonfile["data"]["file_name"]
		file = open(filePath+"\\"+fileName,'w',newline='')
		data = data.replace('\\r\\n','\n')
		print(data)
		file.write(data)
		file.close()
		client.send(b'fileDone!')
		print("send fileDone!")
	else :
		print("will send to CNC resquest: ",jsonfile["data"].encode())
		conn.send(jsonfile["data"].encode())
		print("send!!")
		print('wait for CNC resquest')
		http_resquest = conn.recv(65535)
		print('recv form CNC response: ', http_resquest)
		client.send(http_resquest)


if __name__ == "__main__" :
	LOCAL_SERVER_HOST='127.0.0.1'
	HOST=502

	SEND_CLINET_PORT=input('please input destination IP adress')
	LOCAL_PORT=int(input('please input destination port'))

	local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	local_server.settimeout(100)
	local_server.bind((LOCAL_SERVER_HOST,HOST))
	local_server.listen(5)

	print("connect to CNC")
	while True :
		try :
			print("wait for listen")
			conn,addr = local_server.accept()
			print(addr)
			while True:
				try :
					print('wait for request data')
					json_byte = b''
					json_len = int(conn.recv(1024).decode('utf-8'))
					conn.send(b'OK')
					while json_len > 0 :
						json_byte = json_byte + conn.recv(1024)
						json_len -= 1024
						print(json_len)
					print('recv from opcua server :', json_byte)
					print(len(json_byte))
					if json_byte == b'' :
						break
					else :
						c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						c.connect((SEND_CLINET_PORT,LOCAL_PORT))
						ReadJsonData(json_byte,c,conn)
						c.close()
				except Exception as e :
					print(str(e))
					conn.close()
					break
		except Exception as e: 
			print(str(e))
			break 
	exit(0)
