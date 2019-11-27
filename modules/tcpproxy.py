#!/usr/bin/python3
#coding:utf-8
import os,time,re
import sys
import socket
import threading

timeout_count=0

def server_loop(local_host,local_port,remote_host,remote_port,receive_first):
	server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	try:
		server.bind((local_host,local_port))
	except BaseException as ex:
		# print(ex)
		print("\033[1;31m"+"[-]"+"\033[0m"+"Failed to listen on %s:%d"%(local_host,local_port))
		print("\033[1;31m"+"[-]"+"\033[0m"+"Check for other listening sockets or correct permissions.")
		sys.exit(0)
	print("\033[1;32m"+"[+]"+"\033[0m"+"Listening on %s:%d"%(local_host,local_port))

	server.listen(5)
	while True:
		client_socket,addr = server.accept()
		print("\033[1;34m"+"[==>]"+"\033[0m"+"Received incoming connection from %s:%d"%(addr[0],addr[1]))
		proxy_thread = threading.Thread(target=proxy_handler,args=(client_socket,remote_host,remote_port,receive_first))
		proxy_thread.start()

def proxy_handler(client_socket,remote_host,remote_port,receive_first):
	global timeout_count
	remote_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	remote_socket.connect((remote_host,remote_port))
	if(receive_first):
		remote_buffer = receive_from(remote_socket)
		hexdump(remote_buffer)

		remote_buffer = response_handler(remote_buffer)
		if(len(remote_buffer)):
			print("\033[1;34m"+"[<==]"+"\033[0m"+" Sending %d bytes to localhost."%len(remote_buffer))
			client_socket.send(remote_buffer)
	while True:
		local_buffer = receive_from(client_socket)
		if(len(local_buffer)):
			print("\033[1;34m"+"[==>]"+"\033[0m"+" Received %d bytes from localhost."%len(local_buffer))
			hexdump(local_buffer)
			local_buffer = request_handler(local_buffer)
			remote_socket.send(local_buffer)
			print("\033[1;34m"+"[==>]"+"\033[0m"+" Sent to remote.")

		remote_buffer = receive_from(remote_socket)
		if(len(remote_buffer)):
			print("\033[1;34m"+"[<==]"+"\033[0m"+" Received %d bytes from remote."%len(remote_buffer))
			hexdump(remote_buffer)

			remote_buffer = response_handler(remote_buffer)
			client_socket.send(remote_buffer)
			print("\033[1;34m"+"[<==]"+"\033[0m"+" Sent to localhost.")
		if not len(local_buffer) or not len(remote_buffer):
			timeout_count += 1
			if(timeout_count==3):
				client_socket.close()
				remote_socket.close()
				print("\033[1;34m"+"[*]"+"\033[0m"+" No more data. Closing connections.")
			break
		else:
			timeout_count=0

def hexdump(src,length=16):
	result = []
	digits = 4 if isinstance(src,str) else 2
	"""
	"%0*x"%(a,b)
	a -> *	输出位数
	b -> "%0*x"	数值
	"""
	for i in range(0,len(src),length):
		s = src[i:i+length]
		hexa = ' '.join(["%0*x"%(digits,(x if isinstance(x,int) else ord(x))) for x in s])
		text = ''.join([chr(x) if 0x20 <= (x if isinstance(x,int) else ord(x)) < 0x7f else '.' for x in s])
		result.append("%04x %-*s %s"%(i,length*(digits + 1),hexa,text))
	print('\n'.join(result))
		
def receive_from(connection):
	buffer = b""
	connection.settimeout(2)
	try:
		while(True):
			data = connection.recv(4096)
			if not data:
				break
			buffer += data
	except BaseException as ex:
		print(ex)
		pass
	return buffer

def request_handler(buffer):
	return buffer

def response_handler(buffer):
	return buffer

def run(**args):
	local_host = args['local_host']
	local_port = int(args['local_port'])

	remote_host = args['remote_host']
	remote_port = int(args['remote_port'])
	receive_first = args['receive_first']
	if receive_first:
		receive_first = True
	else:
		receive_first = False
	server_loop(local_host,local_port,remote_host,remote_port,receive_first)	


if __name__=='__main__':
	run(local_host="127.0.0.1",local_port=2398,remote_host="96.45.186.216",remote_port=2398,receive_first=False)