from email.utils import formatdate
from urllib import parse
from string import Template
import mimetypes
import os
import socket

class ResponseHandler():

	StatusMapping = {'404' : 'Not Found', '400' : 'Bad Request', '200' : 'OK', '301' : 'Moved Permanently'}

	ErrorTemplate = Template('\
	<html>\
	<title>$err </title>\
	<h1> Oops! Looks like something went wrong. <br> </h1>\
	<h2> Error $err  $message </h2>\
	</html>')

	def __init__(self, request, data, directory):
		self.request =  request
		self.HeaderTemplate = ''
		self.ResponseLineTemplate = ''
		self.Body = b''
		self.BaseDir = directory
		self.HeaderDict = {}
		self.RequestAttr = {}

		self.MasterHandler(data)

	def SetHeader(self, key, val):
		self.HeaderDict[key] = val

	def FillHeaderTemplate(self):
		for key, val in self.HeaderDict.items():
			self.HeaderTemplate = self.HeaderTemplate + key + ' : ' + val + '\r\n'

	def FillResponseLineTemplate(self):
		self.ResponseLineTemplate = 'HTTP/1.1 ' + self.StatusCode + ' ' + self.StatusMapping[self.StatusCode] + '\r\n'

	def SendHeaders(self):
		self.request.sendall(bytes(self.HeaderTemplate, 'utf-8'))

	def EndHeaders(self):
		self.request.sendall(bytes('\r\n', 'utf-8'))

	def SendResponseLine(self):
		self.request.sendall(bytes(self.ResponseLineTemplate, 'utf-8'))

	def SendBody(self):
		self.request.sendall(self.body)

	def ParseRequest(self, data):
		data = data.decode('utf-8')

		fragments = data.split('\r\n')

		request_line = fragments[0].split(' ')    # GET /some/path HTTP/1.1

		self.RequestAttr['method'] = request_line[0]

		# User can send absolute url as path eg. http://domain.com/path 
		self.RequestAttr['abs_path'] = request_line[1]

		PathAttr = parse.urlparse(self.RequestAttr['abs_path'])

		self.RequestAttr['rel_path'] = PathAttr.path

		self.filepath = self.BaseDir + self.RequestAttr['rel_path']


	def ValidateRequest(self):

		if self.RequestAttr['method'] not in self.SupportedMethods.keys():
			self.send_error('400')
			return False

		# Possbile to add other options to validate requests here
		# Eg. based on 'Referer' or 'User-Agent' headers etc.

		return True


	def send_error(self, errorcode):

		self.StatusCode = errorcode
		self.SetHeader('Server', 'Python/0.1.0 (Custom)')
		self.SetHeader('Content-Type', 'text/html')
		self.SetHeader('Date', formatdate(timeval=None, localtime=False, usegmt=True))

		self.FillResponseLineTemplate()
		self.FillHeaderTemplate()
		self.body = bytes(self.ErrorTemplate.substitute(err = errorcode, message = self.StatusMapping[errorcode]), 'utf-8')
		
		self.SendResponseLine()
		self.SendHeaders()
		self.EndHeaders()
		self.SendBody()

	def send_response(self, status):

		self.StatusCode = status

		self.FillResponseLineTemplate()

		self.SendResponseLine()	


	def respond(self):

		if os.path.isdir(self.filepath):

			if not self.filepath.endswith('/'):

				self.SetHeader("Location", self.RequestAttr['rel_path'] + "/")
				self.FillHeaderTemplate()
				self.send_response('301')
				self.SendHeaders()
				self.EndHeaders()
				return False

			for index in "index.html", "index.htm":

				index = os.path.join(self.filepath, index)
				if os.path.exists(index):
					self.filepath = index
					break
			else:

				self.body = bytes('<html><title>Sorry!</title><h2>Sorry! The server doesn\'t serve directories.</h2></html>', 'utf-8')
				self.SetHeader('Date', formatdate(timeval=None, localtime=False, usegmt=True))
				self.SetHeader('Server', 'Python/0.1.0 (Custom)')
				self.FillHeaderTemplate()

				self.send_response('200')
				self.SendHeaders()
				self.EndHeaders()
				self.SendBody()
				return False
				
		try:
			f = open(self.filepath, 'rb')
		except IOError:
			self.send_error('404')
			return None

		fd = os.fstat(f.fileno())

		self.SetHeader('Content-Type', mimetypes.guess_type(self.filepath)[0])
		self.SetHeader('Content-Length', str(fd[6]))
		self.SetHeader('Date', formatdate(timeval=None, localtime=False, usegmt=True))
		self.SetHeader('Server', 'Python/0.1.0 (Custom)')

		self.FillHeaderTemplate()

		self.send_response('200')
		self.SendHeaders()
		self.EndHeaders()

		return f

	def do_GET(self):

		fobj = self.respond()

		if fobj:
			self.body = fobj.read()
			self.SendBody()
			fobj.close()

	def do_HEAD():
		fobj = self.respond()

		if fobj:
			fobj.close()

	SupportedMethods = {'GET' : do_GET, 'HEAD': do_HEAD}

	def MasterHandler(self, data):
		
		self.ParseRequest(data)

		if self.ValidateRequest():
		
			self.SupportedMethods[self.RequestAttr['method']](self)






	




