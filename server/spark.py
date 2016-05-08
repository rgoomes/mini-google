from __future__ import print_function
import socket, sys, os
import ConfigParser as configparser
from threading import Thread
from math import floor
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.types import Row, StructField, StructType, StringType, IntegerType

def keyword_search(keywords):
	query = "SELECT name FROM imagesTable WHERE keyword = \'" + keywords[0] + "\' "
	for i in range(1, len(keywords)):
		query += "OR keyword = \'" + keywords[i] + "\' "

	imgdf = sqlContext.sql(query)
	results = str(imgdf.count()) + "\n"

	for img in imgdf.limit(100).collect():
		results += str(img.name) + " "

	return results[:-1]

def client_thread(cs):
	job = cs.recv(1024).decode()
	print('Request received: ' + job)
	job = job.split(" ")
	results = keyword_search(job)
	cs.send(results.encode())
	cs.close()

def spark_server(port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((socket.gethostname(), port))
	s.listen(10)

	while True:
		print('Waiting for clients...')
		(cs, addr) = s.accept()
		print("Client connected: " + str(addr))
		ct = Thread(target = client_thread, args = (cs, ))
		ct.start()

	s.close()

def save_tables(home_path, n_machines, m_id):
	with open(home_path + '/dataset.csv') as f:
		content = f.readlines()
	f.close()

	data_size = int(floor(len(content) / n_machines))
	start_index = 0
	for i in range(m_id):
		start_index += data_size
	if m_id == n_machines - 1:
		content = content[start_index : ]
	else:
		content = content[start_index : start_index + data_size]
		pass
	f = open(home_path + '/new_dataset.csv', 'w+')
	print(''.join(content)[:-1], file = f)
	f.close()

	lines = sc.textFile(home_path + "/new_dataset.csv")

	entry = lines.map(lambda p: p.split(","))
	images = entry.map(lambda p: Row(name=p[1], keyword=p[0]))

	schemaString = "name keyword"
	fields = [StructField(field_name, StringType(), True) for field_name in schemaString.split()]
	schema = StructType(fields)
	schemaImages = sqlContext.createDataFrame(images, schema)
	schemaImages.write.parquet(home_path + "/images.parquet")

def load_tables(home_path):
	parquetFile = sqlContext.read.parquet(home_path + "/images.parquet")
	parquetFile.registerTempTable("imagesTable");

def prepare(home_path, n_machines, m_id):
	if "--save" in sys.argv and not os.path.isdir(home_path + "/images.parquet"):
		save_tables(home_path, n_machines, m_id)

	if not os.path.isdir(home_path + "/images.parquet"):
		print('error: database not found')
		sys.exit(-1)

	load_tables(home_path)

def start():
	parser = configparser.ConfigParser()
	parser.read('machine.conf')
	return int(parser.get('config', 'port')), int(parser.get('config', 'n_machines')), int(parser.get('config', 'm_id'))

if __name__ == "__main__":
	port, n_machines, m_id = start()
	sc = SparkContext(appName="mini-google")
	sqlContext = SQLContext(sc)
	prepare(os.getcwd(), n_machines, m_id)
	spark_server(port)