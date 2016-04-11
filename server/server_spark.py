#!/usr/bin/python 

from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.types import Row, StructField, StructType, StringType, IntegerType
from classifier import *
from features import *

import socket, os, sys

global nn, n, keywords

def keyword_search(keywords):
	query = "SELECT name FROM imagesTable WHERE keyword = \'" + keywords[0] + "\' "
	for i in range(1, len(keywords)):
		query += "OR keyword = \'" + keywords[i] + "\' "

	imgdf = sqlContext.sql(query)
	results = str(imgdf.count()) + " "

	for img in imgdf.limit(100).collect():
		results += str(img.name) + " "

	return results[:-1]

def image_search(path):
	global nn, keywords
	im = Image.open(path).convert('RGB')
	feats = get_img_feats(im)
	out = nn.activate(feats)
	clss = process_nn_output(out, keywords)
	return keyword_search([clss])

def save_tables(sc, sqlContext, home_path):
	lines = sc.textFile(home_path + "/dataset.csv")
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
			request = keyword_search(job[1:])
		elif job[0] == "image":
			request = image_search(job[1])

		c.send(request.encode())
		c.close()

	s.close()

if __name__ == "__main__":
	if "--path" not in sys.argv or sys.argv.index('--path')+1 == len(sys.argv):
		print('error: server path not given')
		sys.exit(-1)

	sc = SparkContext(appName="mini-google")
	sqlContext = SQLContext(sc)

	home_path = sys.argv[sys.argv.index('--path') + 1]
	if "--save" in sys.argv and not os.path.isdir(home_path + "/images.parquet"):
		save_tables(sc, sqlContext, home_path)

	if not os.path.isdir(home_path + "/images.parquet"):
		print('error: database not found')
		sys.exit(-1)

	load_tables(sc, sqlContext, home_path)

	data, n, keywords = gen_data(home_path + '/dataset.csv', home_path + '/.images')
	nn = gen_nn(768, n, n)
	nn = train_nn(data, nn, 50)

	server()

	sc.stop()
