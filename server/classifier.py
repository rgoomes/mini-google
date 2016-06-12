from features import *
from pybrain.datasets import ClassificationDataSet
from pybrain.utilities import percentError
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules import SoftmaxLayer
from pybrain.structure import FeedForwardNetwork, LinearLayer, SigmoidLayer, FullConnection

def get_keyword_class(kw_ind, n):
	aux = [0 for i in range(n)]
	aux[kw_ind] = 1
	return aux

def process_nn_output(nn_out, keywords):
	ind = nn_out.argmax(axis=0)
	for key, value in keywords.items():
		if value == ind:
			return key

def process_svm_output(svm_out, keywords):
	for key, value in keywords.items():
		if value == svm_out:
			return key

def gen_nn(in_size, hidden_size, out_size):
	nn = FeedForwardNetwork()

	inLayer = LinearLayer(in_size)
	hiddenLayer = SigmoidLayer(hidden_size)
	outLayer = LinearLayer(out_size)
	
	nn.addInputModule(inLayer)
	nn.addModule(hiddenLayer)
	nn.addOutputModule(outLayer)
	
	nn.addConnection(FullConnection(inLayer, hiddenLayer))
	nn.addConnection(FullConnection(hiddenLayer, outLayer))
	nn.sortModules()

	return nn

def train_nn(data, nn, epochs):
	trainer = BackpropTrainer(nn, dataset=data, momentum=0.1, verbose=True, weightdecay=0.01)
	trainer.trainEpochs(epochs)
	return nn

def benchmark(nn, keywords, db_path):
	neg = pos = 0.0
	content = os.listdir(db_path)
	for img in content:
		if '.jpg' in img:
			kw = img.replace('.jpg', '')
			im = Image.open(db_path + img).convert('RGB')
			out = nn.activate(get_img_feats(im))
			classif = process_nn_output(out, keywords)
			print('Processing: ' + db_path + img + '\tExpected: ' + kw + '\tGot: ' + classif)
			if classif == kw: 
				pos += 1
			else:
				neg += 1	
	print('Overall Performance: ' + str((pos / (pos + neg)) * 100) + '%')

def complete_benchmark():
	f = open('dataset.csv')
	lines = f.readlines()
	aux = []
	out = []
	for l in lines:
		k = l.replace('\n', '').split(',')
		if k[1] not in aux:
			aux.append(k[1])
			out.append(k[0])

	true_count = 0
	for k in range(len(out)):
		cl = image_search('.images/' + out[k])
		print('Expected: ' + aux[k] + ' | Classified: ' + cl)
		if aux[k] == cl:
			true_count += 1
	print('Accuracy: ' + str(float(true_count) / len(out) * 100) + '%')
	