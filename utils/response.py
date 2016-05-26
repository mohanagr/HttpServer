from email.utils import formatdate
import socket

class ResponseHandler():

	StatusMapping = {'404' : 'Not Found', '400' : 'Bad Request', '200' : 'OK'}

	
	def __init__(self, request):
		self.request =  request
		self.HeaderTemplate = ''
		self.ResponseLineTemplate = ''
		self.HeaderDict = {}
		#print("IN YOUR SUCKING CLASSES CTOR")
		self.body = '<html><body><h1>Oh my god</h1></body></html>'
		
		self.MasterHandler()
		#self.destination = requestSocket

	def SetHeader(self, key, val):
		self.HeaderDict[key] = val

	def FillHeaderTemplate(self):
		for k, v in self.HeaderDict.items():
			self.HeaderTemplate = self.HeaderTemplate + k + ' : ' + v + '\r\n'

	def FillResponseLineTemplate(self):
		self.ResponseLineTemplate = 'HTTP/1.1 ' + self.StatusCode + ' ' + self.StatusMapping[self.StatusCode] + '\r\n'

	def SendHeaders(self):
		self.request.sendall(bytes(self.HeaderTemplate, 'utf-8'))

	def EndHeaders(self):
		self.request.sendall(bytes('\r\n', 'utf-8'))

	def SendResponseLine(self):
		self.request.sendall(bytes(self.ResponseLineTemplate, 'utf-8'))

	def SendBody(self):
		self.request.sendall(bytes(self.body, 'utf-8'))

	def ParseRequest(self):
		pass

	# def FillErrorTemplate():

	def MasterHandler(self):
		
		self.StatusCode = '200'

		self.SetHeader('Server', 'Python/0.1.0 (Custom)')
		self.SetHeader('Content-Type', 'text/html')
		self.SetHeader('Date', formatdate(timeval=None, localtime=False, usegmt=True))

		self.FillResponseLineTemplate()
		self.FillHeaderTemplate()

		self.SendResponseLine()
		self.SendHeaders()
		self.EndHeaders()
		self.SendBody()




	




