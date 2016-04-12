#!/usr/bin/python
#usage example 1: python client_spark.py keyword orange
#usage example 2: python client_spark.py image /path

from socket import socket, gethostname
from sys import argv

if len(argv) >= 2 and len(argv[1]):
	s = socket()
	s.connect((gethostname(), 12345))

	keywords = ""
	for i in range(1, len(argv)):
		keywords += argv[i] + " "

	s.send(keywords[:-1].encode())
	request = s.recv(4096).decode()
	print(request, end="")
	s.close()
