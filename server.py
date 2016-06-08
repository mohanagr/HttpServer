#!/usr/bin/python3

import socketserver
import socket
from utils import response


class MyTCPServer(socketserver.TCPServer):
	def server_bind(self):
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(self.server_address)

class MyRequestHandler(socketserver.BaseRequestHandler, response.ResponseHandler):

	def __init__(self, request, client_address, server):
		socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
		

	def handle(self):
		data = self.request.recv(1024)
		print(data)
		response.ResponseHandler(self.request, data)
		# self.request.sendall(bytes('damn it', 'utf-8'))



if __name__ == "__main__":
	
	HOST, PORT = '127.0.0.1', 8020
	
	server = MyTCPServer((HOST, PORT), MyRequestHandler)

	server.serve_forever()
