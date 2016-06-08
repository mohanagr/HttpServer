from email.utils import formatdate
from urllib import parse
import mimetypes
import socket

class ResponseHandler():

	StatusMapping = {'404' : 'Not Found', '400' : 'Bad Request', '200' : 'OK'}
	
	def __init__(self, request, data):
		self.request =  request
		self.HeaderTemplate = ''
		self.ResponseLineTemplate = ''
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
		#print(data)
		fragments = data.split('\r\n')

		request_line = fragments[0].split(' ')    # GET /some/path HTTP/1.1

		self.RequestAttr['method'] = request_line[0]
		self.RequestAttr['abs_path'] = request_line[1]

		PathAttr = parse.urlparse(self.RequestAttr['path'])

		BaseDir = "/home/mohan/projects/Mysite"

		self.RequestAttr['rel_path'] = PathAttr.path

		filepath = BaseDir + self.RequestAttr['rel_path']

		f = open(filepath, mode = 'rb')

		self.body = f.read()

		f.close()

	def ValidateRequest(self)
		

	# def FillErrorTemplate():

	def MasterHandler(self, data):
		
		self.ParseRequest(data)

		self.StatusCode = '200'

		self.SetHeader('Server', 'Python/0.1.0 (Custom)')
		self.SetHeader('Content-Type', mimetypes.guess_type(self.RequestAttr['path'])[0])
		self.SetHeader('Date', formatdate(timeval=None, localtime=False, usegmt=True))

		self.FillResponseLineTemplate()
		self.FillHeaderTemplate()

		self.SendResponseLine()
		self.SendHeaders()
		self.EndHeaders()
		self.SendBody()




	




