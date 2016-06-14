from __future__ import print_function
import socket, sys, os, MySQLdb, itertools, random
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
	count_cmd  = "SELECT count(*) FROM image WHERE "
	select_cmd = "SELECT name FROM image WHERE "
	limit_cmd  = " LIMIT 100 "

	keyword_cmd = "keyword = \'" + keywords[0] + "\' "
	for i in range(1, len(keywords)):
		keyword_cmd += "OR keyword = \'" + keywords[i] + "\' "

	cur.execute(count_cmd + keyword_cmd + ";")
	fetch = cur.fetchall()
	results = str(int(fetch[0][0])) + "\n"

	cur.execute(select_cmd + keyword_cmd + limit_cmd + ";")
	fetch = cur.fetchall()
	conn.commit()

	for i in random.sample(range(len(fetch)), len(fetch)):
		results += str(fetch[i][0]) + " "

	return results[:-1]

def client_thread(cs):
	job = cs.recv(8192).decode()
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
	dataset = home_path + '/big_dataset.csv'

	with open(dataset) as f:
		file_lines = sum(1 for _ in f)

	data_size = file_lines / n_machines
	beg = m_id * data_size
	end = file_lines if m_id == n_machines-1 else beg + data_size

	with open(dataset) as f:
		content = [l.strip() for l in itertools.islice(f, beg, end)]

	# counter and content length
	count, length = 0, len(content)
	# Disable MySQL autocommit
	conn.autocommit(False)

	cur.execute("DROP INDEX keywordIndex ON image;")
	conn.commit();
	cur.execute("delete from image;")
	conn.commit()

	query = "INSERT INTO image (name, keyword) VALUES (%s, %s)"

	if "--bulk" in sys.argv:
		# NEED to set max_allowed_packet in mysql command line:
		# SET GLOBAL max_allowed_packet=536870912;

		batchs_pos = sys.argv.index('--bulk')+1
		if batchs_pos == len(sys.argv) or not sys.argv[batchs_pos].isdigit():
			print("error: invalid or incomplete batch number in option --bulk")
			exit(0)

		batchs = int(sys.argv[batchs_pos])
		batchs = min(max(1, batchs), 64)
		batch_size = length / batchs

		for batch in range(batchs):
			print_status("batchs", count+1, batchs)
			count += 1

			items = []
			lb = batch * batch_size
			ub = lb + (length-lb if batch == batchs-1 else batch_size)

			for i in xrange(lb, ub):
				d = content[i].split(',')
				items.append((d[0], d[1]))

			cur.executemany(query, items)
	else:
		for i in xrange(length):
			print_status("images", count+1, length)
			count += 1

			d = content[i].split(',')
			cur.execute(query, (d[0], d[1],))

	conn.commit();
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