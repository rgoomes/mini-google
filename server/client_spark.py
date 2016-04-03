#!/usr/bin/python
#usage example: python client_spark.py keyword orange

from __future__ import print_function
from socket import socket, gethostname
from sys import argv

if len(argv) >= 2 and len(argv[1]):
	s = socket()
	s.connect((gethostname(), 12345))
	s.send(argv[1] + " " + (argv[2] if len(argv) > 2 else ""))
	request = s.recv(256)
	print(request, end="")
	s.close()
