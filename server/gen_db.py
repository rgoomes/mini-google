import os

def parse_ctg(ctg):
	if '.' in ctg:
		ctg = ctg[ctg.find('.') + 1:]
	if '-101' in ctg:
		ctg = ctg[:ctg.find('-101')]
	if '_' in ctg:
		ctg = '-'.join(ctg.split('_'))
	return ctg

def gen_db():
	f = open('dataset.csv', 'w+')
	img_count = 0

	dir_list = next(os.walk('.'))[1]
	os.mkdir('.images')
	for db in dir_list:
		ctg_list = next(os.walk(db + '/.'))[1]
		for c in ctg_list:
			ctg = parse_ctg(c)
			for img in os.listdir(db + '/' + c):
				if '.jpg' in img:
					os.system('cp ' + db + '/' + c + '/' + img + ' .images/' + str(img_count) + '.jpg')
					f.write(str(img_count) + '.jpg' + ',' + ctg + '\n')
					img_count += 1
	f.close()

if __name__ == '__main__':
	gen_db()
