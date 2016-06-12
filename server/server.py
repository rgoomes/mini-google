from threading import Thread, Lock
from sys import argv

import socket, os, sys
import configparser
import time

from classifier import *
from features import *

from sklearn import svm

global parser
global nn, n, ckeywords
global svm_clf

class Result:
	def set_size(self, _size):
		self.mutex.acquire()
		self.size += _size
		self.mutex.release()

	def set_imgs(self, _imgs):
		self.mutex.acquire()
		self.imgs += " " + _imgs
		self.mutex.release()

	def __init__(self):
		self.size = 0
		self.imgs = ""
		self.mutex = Lock()

def image_search(path):
	global nn, ckeywords, response, svm_clf

	try:
		im = Image.open(path)
	except:
		return None

	im = im.convert('RGB')
	feats = get_img_feats(im)
	#out = nn.activate(feats)
	#clss = process_nn_output(out, ckeywords)
	out = svm_clf.predict([feats])
	clss = process_svm_output(out, ckeywords)
	return clss

def spark_thread(ip, port, request, result):
	s = socket.socket()

	try:
		ip = socket.gethostname() if ip == '127.0.0.1' else ip
		s.connect((ip, int(port)))
	except:
		s.close()
		return

	s.send(request.encode())
	data = s.recv(4096)
	data = data.decode()
	data = data.split('\n')

	if(int(data[0]) > 0):
		result.set_size(int(data[0]))
		result.set_imgs(data[1])

	s.close()

def client_thread(c, request):
	if request == None:
		data = '0.0 0 0'
		c.send(data.encode())
		c.close()
		return

	result = Result()
	clusters = int(parser.get('config', 'clusters'))
	
	threads = []
	t0 = time.time()

	for i in range(clusters):
		ip = parser.get('config', 'ip' + str(i))
		port = parser.get('config', 'port' + str(i))
		threads.append(Thread(target=spark_thread, args=(ip, port, request, result, )))
		threads[i].start()

	for i in range(clusters):
		threads[i].join()

	t1 = time.time()
	elapsed = t1 - t0

	data = str(round(elapsed, 3)) + " " + str(result.size) + result.imgs
	c.send(data.encode())
	c.close()

def server():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((socket.gethostname(), 20000))
	s.listen(1)

	print('Listening to clients..')

	while True:
		c, addr = s.accept()
		job = c.recv(1024).decode().split(" ")

		if job[0] == "exit":
			c.close()
			break
		if job[0] not in ["keyword", "image"] or len(job) < 2:
			c.close()
			continue
		
		if job[0] == "keyword":
			request = ' '.join([i for i in job[1:] ])
		elif job[0] == "image":
			request = image_search(job[1])

		thread = Thread(target=client_thread, args=(c, request, ))
		thread.start()

	s.close()

def neural_network():
	global nn, ckeywords
	#data, n, ckeywords = gen_data(os.getcwd() + '/train.csv', os.getcwd() + '/.images')
	nn = gen_nn(768, n, n)
	nn = train_nn(data, nn, 10)

def svm_classifier():
	global svm_clf, ckeywords
	X, y, n, ckeywords = gen_data(os.getcwd() + '/train.csv', os.getcwd() + '/.images')
	print('Creating SVM Classifier...')
	svm_clf = svm.SVC()
	print('Training SVM classifier...')
	svm_clf.fit(X, y)
	print('Ready for classification...')

def complete_benchmark():
	f = open('dataset.csv')
	lines = f.readlines()
	aux = []
	out = []
	for l in lines:
		k = l.replace('\n', '').split(',')
		if k[1] not in aux:
			aux.append(k[1])
			out.append(k[0])

	true_count = 0
	for k in range(len(out)):
		cl = image_search('.images/' + out[k])
		print('Expected: ' + aux[k] + ' | Classified: ' + cl)
		if aux[k] == cl:
			true_count += 1
	print('Accuracy: ' + str(float(true_count) / len(out) * 100) + '%')

def read_conf():
	if "--conf" not in sys.argv or sys.argv.index('--conf')+1 == len(sys.argv):
		print("error: missing or invalid option --conf")
		exit(0)

	global parser
	parser = configparser.ConfigParser()
	conf_file = sys.argv[sys.argv.index('--conf')+1]
	parser.read(conf_file)

if __name__ == '__main__':
	svm_classifier()
	complete_benchmark()
	#read_conf()
	#server()
