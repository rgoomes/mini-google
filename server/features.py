import PIL, os, sys
from PIL import Image
from pybrain.datasets import ClassificationDataSet

def get_keyword_class(kw_ind, n):
	aux = [0 for i in range(n)]
	aux[kw_ind] = 1
	return aux

def get_color_hist(img):
	return img.histogram()

def get_img_feats(img):
	return get_color_hist(img)

def print_status(table, pos, length):
	sys.stdout.write("\033[K\r" + table + " " + str(pos) + "/" + str(length))
	sys.stdout.flush()

	if pos == length:
		print(end='\n')

def gen_data(csv_file, db):
	keywords = {}
	count = 0
	img_list = []
	X = []
	y = []

	with open(csv_file) as f:
		content = f.readlines()
	f.close()

	for line in content:
		aux = line.replace('\n', '').split(',')
		if aux[1] not in keywords:
			keywords[aux[1]] = count
			count += 1
		img_list.append(aux)

	data = ClassificationDataSet(768, len(keywords), nb_classes=len(keywords))
	n = len(keywords)
	count = 0

	for img in img_list:
		print_status('load', count+1, len(img_list))
		count += 1

		path = db + '/' + img[0]
		im = Image.open(path).convert('RGB')
		#data.addSample(get_img_feats(im), get_keyword_class(keywords[img[1]], n))
		X.append(get_img_feats(im))
		y.append(keywords[img[1]])

	return X, y, n, keywords
	#return data, n, keywords