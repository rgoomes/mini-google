import PIL, os
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

def gen_data(csv_file, db):
	keywords = {}
	count = 0
	img_list = []

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

	for img in img_list:
		path = db + '/' + img[0]
		im = Image.open(path).convert('RGB')
		data.addSample(get_img_feats(im), get_keyword_class(keywords[img[1]], n))

	return data, n, keywords