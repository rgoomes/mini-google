import os, sys
from PIL import *

def print_status(table, pos, length):
	sys.stdout.write("\033[K\r" + table + " " + str(pos) + "/" + str(length))
	sys.stdout.flush()

	if pos == length:
		print(end='\n')

def get_color_hist(img):
	return img.histogram()

def get_img_feats(img):
	return get_color_hist(img)

def gen_data(csv_file, db):
	keywords = {}
	count = 0
	img_list = []
	X = []
	y = []

	with open(csv_file) as f:
		content = f.readlines()

	for line in content:
		aux = line.replace('\n', '').split(',')
		if aux[1] not in keywords:
			keywords[aux[1]] = count
			count += 1
		img_list.append(aux)

	n = len(keywords)
	count = 0

	for img in img_list:
		print_status('load', count+1, len(img_list))
		count += 1

		path = db + '/' + img[0]
		im = Image.open(path).convert('RGB')
		X.append(get_img_feats(im))
		y.append(keywords[img[1]])

	return X, y, n, keywords