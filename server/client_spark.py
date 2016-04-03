#!/usr/bin/python
#usage example: python client_spark.py keyword orange

from __future__ import print_function
from socket import socket, gethostname
from sys import argv

if len(argv) >= 2 and len(argv[1]):
	s = socket()
	s.connect((gethostname(), 12345))

	keywords = ""
	for i in range(1, len(argv)):
		keywords += argv[i] + " "

	s.send(keywords[:-1])
	request = s.recv(4096)
	print(request, end="")
	s.close()
