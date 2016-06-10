from __future__ import print_function
import socket, sys, os, MySQLdb
import ConfigParser as configparser
from threading import Thread
from math import floor

global conn, cur

def print_status(table, pos, length):
	sys.stdout.write("\033[K\r" + table + " " + str(pos) + "/" + str(length))
	sys.stdout.flush()

	if pos == length:
		print(end='\n')

def keyword_search(keywords):
	cmd = "SELECT name FROM image WHERE keyword = \'" + keywords[0] + "\' "
	for i in range(1, len(keywords)):
		cmd += "OR keyword = \'" + keywords[i] + "\' "

	cur.execute(cmd)
	fetch = cur.fetchall()
	results = str(len(fetch)) + "\n"

	for i in range(min(len(fetch), 100)):
		results += str(fetch[i][0]) + " "

	return results[:-1]

def client_thread(cs):
	job = cs.recv(1024).decode()
	print('Request received: ' + job)
	job = job.split(" ")
	results = keyword_search(job)
	cs.send(results.encode())
	cs.close()

def mysql_server(port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
	with open(home_path + '/big_dataset.csv') as f:
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

	cur.execute("DROP INDEX keywordIndex ON image;")
	conn.commit();
	cur.execute("delete from image;")
	conn.commit()

	count, length = 0, len(content)

	for c in content:
		print_status("images", count+1, length)
		count += 1

		d = c.split()
		d = d[0].split(',')

		cmd = "INSERT INTO image (name, keyword) VALUES (" + "'" + d[0] + "', '" + d[1] + "');"
		cur.execute(cmd)

	conn.commit()
	cur.execute("CREATE INDEX keywordIndex ON image (keyword) USING BTREE;")
	conn.commit();

def prepare(home_path, n_machines, m_id):
	global conn, cur
	conn = MySQLdb.connect('localhost', 'root', '', 'minigoogle' + str(m_id) )
	cur = conn.cursor()

	if "--save" in sys.argv:
		save_tables(home_path, n_machines, m_id)

def start():
	if "--conf" not in sys.argv or sys.argv.index('--conf')+1 == len(sys.argv):
		print("error: missing or invalid option --conf")
		exit(0)

	parser = configparser.ConfigParser()
	conf_file = sys.argv[sys.argv.index('--conf')+1]
	parser.read(conf_file)
	return int(parser.get('config', 'port')), int(parser.get('config', 'n_machines')), int(parser.get('config', 'm_id'))

if __name__ == "__main__":
	port, n_machines, m_id = start()
	prepare(os.getcwd(), n_machines, m_id)
	mysql_server(port)