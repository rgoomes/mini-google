#!/usr/bin/python 

from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.types import Row, StructField, StructType, StringType, IntegerType

import socket, os, sys

def keyword_search(keywords):
	query = "SELECT name FROM imagesTable WHERE keyword = \'" + keywords[0] + "\' "
	for i in range(1, len(keywords)):
		query += "OR keyword = \'" + keywords[i] + "\' "

	imgdf = sqlContext.sql(query)

	results = ""
	for img in imgdf.collect():
		results += str(img.name) + " "

	return results[:-1]

def image_search():
	return ''

def save_tables(sc, sqlContext, home_path):
	lines = sc.textFile("dataset.csv")
	entry = lines.map(lambda p: p.split(","))
	images = entry.map(lambda p: Row(name=p[1], keyword=p[0]))

	schemaString = "name keyword"
	fields = [StructField(field_name, StringType(), True) for field_name in schemaString.split()]
	schema = StructType(fields)
	schemaImages = sqlContext.createDataFrame(images, schema)
	schemaImages.write.parquet(home_path + "/images.parquet")

def load_tables(sc, sqlContext, home_path):
	parquetFile = sqlContext.read.parquet(home_path + "/images.parquet")
	parquetFile.registerTempTable("imagesTable");

def server():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((socket.gethostname(), 12345))
	s.listen(1)

	print 'Listening to clients..'

	while True:
		c, addr = s.accept()
		job = c.recv(1024).split(" ")

		if job[0] == "exit":
			c.close()
			break
		if job[0] not in ["keyword", "image"] or len(job) < 2:
			c.close()
			continue

		#FIXME: client request might excede 4096 bytes. two possible
		#solutions: do several send's here and receive's on the client
		#or limit the results and send the number of results in the request

		request = keyword_search(job[1:])
		c.send(request)
		c.close()

	s.close()

if __name__ == "__main__":
	if "--path" not in sys.argv or sys.argv.index('--path')+1 == len(sys.argv):
		print 'error: server path not given'
		sys.exit(-1)

	sc = SparkContext(appName="mini-google")
	sqlContext = SQLContext(sc)

	home_path = sys.argv[sys.argv.index('--path') + 1]
	if "--save" in sys.argv and not os.path.isdir(home_path + "/images.parquet"):
		save_tables(sc, sqlContext, home_path)

	if not os.path.isdir(home_path + "/images.parquet"):
		print 'error: database not found'
		sys.exit(-1)

	load_tables(sc, sqlContext, home_path)
	server()

	sc.stop()
