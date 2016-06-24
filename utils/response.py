from email.utils import formatdate
import urllib.request
import urllib.parse
from string import Template
from argparse import Namespace
import mimetypes
import os
import socket
import subprocess

class ResponseHandler():

	StatusMapping = {'404' : 'Not Found', '400' : 'Bad Request', '200' : 'OK', '301' : 'Moved Permanently'}

	ErrorTemplate = Template('''
		<html>
		<title> $err </title>
		<h1> Oops! Looks like something went wrong. <br> </h1>
		<h2> Error $err  $message </h2>
		</html>
	''')

	def __init__(self, request, data, directory):

		self.request = request
		self.ResponseLineTemplate = ''
		self.Body = b''
		self.BaseDir = directory
		self.RequestAttr = Namespace()
		self.environ = {
			'SERVER_NAME' : 'Python/0.1.0 (Custom)',
			'SERVER_SOFTWARE' : 'Python3',
			'GATEWAY_INTERFACE' : 'CGI/1.1',
			'SERVER_PROTOCOL' : 'HTTP/1.1',
			'QUERY_STRING' : '',
			'SCRIPT_NAME' : '',
			'PATH_TRANSLATED' : '',
			'PATH_INFO' : '',
			'REMOTE_ADDR' : self.request.getpeername()[0]
		}

		self.MasterHandler(data)

	def FillResponseLineTemplate(self):
		self.ResponseLineTemplate = 'HTTP/1.1 ' + self.StatusCode + ' ' + self.StatusMapping[self.StatusCode] + '\r\n'

	def SendHeader(self, key, val):
		header = key + ' : ' + val + '\r\n'
		self.request.sendall(bytes(header, 'utf-8'))

	def EndHeaders(self):
		self.request.sendall(bytes('\r\n', 'utf-8'))

	def SendResponseLine(self):
		self.request.sendall(bytes(self.ResponseLineTemplate, 'utf-8'))

	def SendBody(self):
		self.request.sendall(self.body)

	def ParseRequest(self, data):
		data = data.decode('utf-8')
		
		if not data:
			raise RuntimeError('No data receieved')
		
		fragments = data.split('\r\n')

		if not fragments:
			return False

		fragments = list(filter(None, fragments)) #Remove empty '' entries at the end
		
		request_line = fragments[0].split(' ')    # GET /some/path HTTP/1.1
		
		headers = {}

		payload = ''

		for i in range(1, len(fragments)):
			try:
				key, val = fragments[i].split(':', 1)
			except ValueError:
				payload = fragments[i]
				break
			key = key.strip()
			val = val.strip()
			headers[key] = val

		mthd = request_line[0]
		
		# User can send absolute url as path eg. http://domain.com/path?var1=val&var2=val2 with HTTP/1.1
		abspth = request_line[1]

		# To separate absolute path into path, query string and network component
		#
		# Eg. http://mysite.com/path/to/script/index.php?var1=hello%20world
		#
		# network component = mysite.com
		# path = /path/to/script/index.php
		# query = hello%20world

		PathAttr = urllib.parse.urlparse(abspth)

		relpth = urllib.request.unquote(PathAttr.path)
		
		query = PathAttr.query

		self.environ['QUERY_STRING'] = query if query else ''
 		
		self.RequestAttr = Namespace(method = mthd, rel_path = relpth, headers = headers, payload = payload)

		self.filepath = self.BaseDir + self.RequestAttr.rel_path


	def ValidateRequest(self):

		if self.RequestAttr.method not in self.SupportedMethods.keys():
			self.send_error('400')
			return False
		else:
			self.environ['REQUEST_METHOD'] = self.RequestAttr.method

		# HTTP 1.1 compliancy

		if 'Host' not in self.RequestAttr.headers.keys():
			self.send_error('400')
			return False

		# Possbile to add other options to validate requests here
		#
		# Eg. based on 'Referer' or 'User-Agent' headers etc.

		return True


	def send_error(self, errorcode):

		self.body = bytes(self.ErrorTemplate.substitute(err = errorcode, message = self.StatusMapping[errorcode]), 'utf-8')
		
		self.send_response(errorcode)

		self.SendHeader('Server', 'Python/0.1.0 (Custom)')
		self.SendHeader('Content-Type', 'text/html')
		self.SendHeader('Content-Length', str(len(self.body)))
		self.SendHeader('Date', formatdate(timeval=None, localtime=False, usegmt=True))
		self.EndHeaders()

		self.SendBody()

	def send_response(self, status):

		self.StatusCode = status

		self.FillResponseLineTemplate()

		self.SendResponseLine()	


	def respond(self):

		if os.path.isdir(self.filepath):

			if not self.filepath.endswith('/'):

				self.send_response('301')
				self.SendHeader("Location", self.RequestAttr.rel_path + "/")
				self.EndHeaders()
				return False

			for index in  "index.php", "index.html", "index.htm":

				index = os.path.join(self.filepath, index)
				if os.path.exists(index):
					self.filepath = index
					self.RequestAttr.rel_path = os.path.join(self.RequestAttr.rel_path, index)
					break
			else:

				self.body = bytes('''
					<html>
					<title>Sorry!</title>
					<h2>Sorry! The server does not serve directories.</h2>
					</html>''', 
					'utf-8'
				)

				self.send_response('200')
				self.SendHeader('Date', formatdate(timeval=None, localtime=False, usegmt=True))
				self.SendHeader('Server', 'Python/0.1.0 (Custom)')
				self.EndHeaders()
				self.SendBody()
				return False

		self.file_is_script = False
		self.filepath = os.path.normpath(self.filepath)
		if self.is_php():
			self.file_is_script = True
		try:
			f = open(self.filepath, 'rb')
		except IOError:
			self.send_error('404')
			return None

		self.send_response('200')

		print('RESPONSE SENT')

		if not self.file_is_script:

			# Serve the file 

			fd = os.fstat(f.fileno())
			ctype = mimetypes.guess_type(self.filepath)[0]
			if ctype:
				self.SendHeader('Content-Type', ctype)
			self.SendHeader('Content-Length', str(fd[6]))
		else:

			# Set the remaining environment variables necessary to execute PHP

			type = self.RequestAttr.headers['Content-Type'] if 'Content-Type' in self.RequestAttr.headers else ''
			if type :
				self.environ['CONTENT_TYPE'] = type

			length = self.RequestAttr.headers['Content-Length'] if 'Content-Length' in self.RequestAttr.headers else ''
			if length:
				self.environ['CONTENT_LENGTH'] = length 

			referer = self.RequestAttr.headers['Referer'] if 'Referer' in self.RequestAttr.headers else ''
			if referer:
				self.environ['HTTP_REFERER'] = referer

		# Mandatory Headers
		self.SendHeader('Date', formatdate(timeval=None, localtime=False, usegmt=True))
		self.SendHeader('Server', 'Python/0.1.0 (Custom)')
		

		return f

	def exec_php(self):

		script = '/usr/bin/php5-cgi'

		data = self.RequestAttr.payload

		cmd = script + ' -q ' + self.filepath

		if self.environ['REQUEST_METHOD'] == 'POST' :
			cmd = 'echo "{}"'.format(data) + ' | ' + cmd

		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, env=self.environ)

		buff = p.stdout.read()

		dat = buff.decode('utf-8')

		dat = dat.split('\r\n')[2]

		self.body = bytes(dat, 'utf-8')

		self.SendHeader('Content-Type', 'text/html')
		self.SendHeader('Content-Length', str(len(dat)))
		self.EndHeaders()
		self.SendBody()
		
		#print(buff.decode('utf-8'))


	def is_php(self):

		'''
		# Separate additional path following the script name (if script present)
		#
		# Eg: http://mysite.com/somepath/index.php/stub1/stub2
		# stub1, stub2 might be meant for MVC controller purposes.
		# In case stub1/stub2 do not mean anything, index.php will be served.
		#
		# Sets Path related environment variables
		'''

		path =  self.RequestAttr.rel_path
		rest = ''
		if (path.find('.php')>0) or (path.find('.php5')>0):
			while True:
				head, ext = os.path.splitext(path)
				if ext.lower() in ('.php', '.php5'):
					break
				elif path == '':
					return False
				i = path.rfind('/')
				if(i>=0):
					path, rest = path[:i], path[i:]+rest

			# Set path related environment variables

			self.environ['SCRIPT_NAME'] = path
			self.environ['PATH_INFO'] = rest

			# Replace filepath (path to load script) after removing additional path_info
			self.filepath = os.path.normpath(self.BaseDir + path)
			self.environ['SCRIPT_FILENAME'] = self.filepath
			return True

		return False

	def do_GET(self):

		fobj = self.respond()

		if fobj:
			if self.file_is_script:
				self.exec_php()
			else:
				self.body = fobj.read()
				self.EndHeaders()
				self.SendBody()
			fobj.close()

	def do_HEAD(self):
		fobj = self.respond()

		if fobj:
			fobj.close()

	def do_POST(self):
		fobj = self.respond()

		if fobj:
			if self.file_is_script:
				self.exec_php()
			else:
				self.body = fobj.read()
				self.EndHeaders()
				self.SendBody()
			fobj.close()


	SupportedMethods = {'GET' : do_GET, 'HEAD': do_HEAD, 'POST': do_POST}

	def MasterHandler(self, data):
		
		try:
			self.ParseRequest(data)
		except RuntimeError as e:
			print(e)
		except Exception as e:
			print("Fatal error\n", e)
			return
		else:
			if self.ValidateRequest():
				self.SupportedMethods[self.RequestAttr.method](self)






	




