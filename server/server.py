from threading import Thread
from sys import argv

import socket, os, sys
import configparser
import time

from classifier import *
from features import *

global parser
global response, response_count
global nn, n, ckeywords

def image_search(path):
	global nn, ckeywords, response

	try:
		im = Image.open(path)
	except:
		return "0"

	im = im.convert('RGB')
	feats = get_img_feats(im)
	out = nn.activate(feats)
	clss = process_nn_output(out, ckeywords)
	return clss

def spark_thread(ip, port, request):
	global response, response_count

	s = socket.socket()

	try:
		s.connect((ip, int(port)))
	except:
		s.close()
		response = ""
		response_count = 0
		return

	s.send(request.encode())
	rec = s.recv(4096).decode()
	print(rec)
	rec2 = rec.split()
	
	response_count += int(rec2[0])
	if(int(rec2[0])):
		response += rec[len(rec2[0])+1:] + " "

	s.close()

def client_thread(c, request):
	global response, response_count
	response = ""
	response_count = 0

	clusters = int(parser.get('config', 'clusters'))

	spark_threads = []
	
	for i in range(clusters):
		ip = parser.get('config', 'ip' + str(i))
		port = parser.get('config', 'port' + str(i))

		spark_threads.append(Thread(target=spark_thread, args=(ip, port, request, )))
		spark_threads[i].start()

	for i in range(clusters):
		spark_threads[i].join()

	finall = (str(response_count) + " " + response[:-1])
	print(finall)
	c.send(finall.encode())
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
			request = job[1:]
			request = ' '.join([i for i in request])
		elif job[0] == "image":
			request = image_search(job[1])
		
		print(request)
		if request == "0":
			c.send("0".encode())
			c.close()
		else:
			thread = Thread(target=client_thread, args=(c, request, ))
			thread.start()

	s.close()

def neural_network():
	global nn, ckeywords
	data, n, ckeywords = gen_data(os.getcwd() + '/dataset.csv', os.getcwd() + '/.images')
	nn = gen_nn(768, n, n)
	nn = train_nn(data, nn, 50)

def read_conf():
	global parser
	parser = configparser.ConfigParser()
	parser.read("server.conf")

if __name__ == '__main__':
	neural_network()
	read_conf()
	server()
