# -*- coding: utf-8 -*-
"""Movie_review_sentiment_analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15cxPwichbRwz1AVzi_gipALCL_JQwPnJ
"""

! pip install kaggle

import torchtext.data as data
import torchtext.datasets as datasets

!ls -a

!mkdir .kaggle

import json
token = {"username":"tiina0s","key":"dade20c971f71d97b7a6a92a5d3ac74a"}
with open('/content/.kaggle/kaggle.json', 'w') as file:
    json.dump(token, file)

!mkdir train
!mkdir test

import os
os.environ['KAGGLE_CONFIG_DIR'] = "/content/.kaggle"

"""chmod 600 file – owner can read and write"""

!chmod 600 /content/.kaggle/kaggle.json

"""copy kaggle file to destination directory"""

#!cp /content/.kaggle/kaggle.json ~/.kaggle/kaggle.json

!kaggle config set -n path -v{content}

! kaggle competitions download -c movie-review-sentiment-analysis-kernels-only

cd {content}/competitions/movie-review-sentiment-analysis-kernels-only

!unzip -q train.tsv.zip -d train/

!unzip -q test.tsv.zip -d test/

!head train/train.tsv

import pandas as pd

train_data = pd.read_csv("train/train.tsv", sep='\t')

train_data.head()

test_data = pd.read_csv("test/test.tsv", sep='\t')

print(train_data.shape)

#from sklearn.feature_extraction.text import CountVectorizer
#count_vect = CountVectorizer()
#X_train_counts = count_vect.fit_transform(train_data['Phrase'])

#print(X_train_counts)

#X_train_counts.shape

#count_vect.vocabulary_

train_data['Phrase'].iloc[1]

"""To lowercase"""

train_data['Phrase'] = train_data['Phrase'].apply(lambda x: x.lower())
test_data['Phrase'] = test_data['Phrase'].apply(lambda x: x.lower())

test_data['Phrase'].iloc[1]

"""Leida erinevate sentimentide arv, nee arrayks teha"""

import numpy as np

import sklearn
import sklearn.model_selection

"""Esmalt jagada treeningandmed kaheks, 20% jääb testimiseks, sest treeningandmetel on teada klass, kuhu kuulub, testandmetel pole. Seega on vaja proovida, kas mudel töötab ka andmetega, mida ei kasutatud treeningfaasis, mida pole varem "nähtud". Selle 20% osaga saab näha, kas tulevad õiged klassid mudelist või mitte."""

train_data2, dev_data = sklearn.model_selection.train_test_split(train_data, test_size=0.2, random_state=0)
train_data2.shape, dev_data.shape

type(train_data2)

export_csv = train_data2.to_csv (r'train/train2.tsv', sep='\t', index = None, header=True)

export_csv = dev_data.to_csv (r'test/test2.tsv', sep='\t', index = None, header=True)

dev_data.head()



"""Luua list alatooni numbritest"""

from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
le.fit(train_data2['Sentiment'])
le.classes_

y_train2 = le.transform(train_data2['Sentiment'])
y_train = le.transform(train_data['Sentiment'])

y_dev = le.transform(dev_data['Sentiment'])

from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer

"""Lemmatiseerimine"""

import nltk
from nltk import word_tokenize          
from nltk.stem import WordNetLemmatizer 
class LemmaTokenizer(object):
  def __init__(self):
    self.wnl = WordNetLemmatizer()
  def __call__(self, doc):
    return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

#vect = CountVectorizer(tokenizer=LemmaTokenizer())

nltk.download('punkt')
nltk.download('wordnet')

"""Pipeline for **Naive Bayes**"""

from sklearn.pipeline import Pipeline
clf_pipelineNB = Pipeline([('vect', CountVectorizer(tokenizer=LemmaTokenizer(), token_pattern="\S+", max_features=7000, max_df=0.25)), 
                         ('clf', MultinomialNB(fit_prior=True))])
clf_pipelineNB.fit(train_data['Phrase'], y_train)

clf_pipelineNB.score(dev_data['Phrase'], y_dev)

np.mean(predicted2 == y_dev)

"""Leitakse GridSearchCV abil parimad hüperparameetrid NB jaoks"""

from sklearn.model_selection import GridSearchCV

grid_params = {
  #'vect__max_features': [5000, 7000, 10000],
  'vect__max_df' : [0.25, 0.50, 1],
  #'vect__ngram_range': ((1, 1), (1, 2)),
  #'clf__alpha': np.linspace(0.5, 1, 1.24),
  #'clf__fit_prior': [True, False],
  
    
}
clf = GridSearchCV(clf_pipelineNB, grid_params, cv=3)
clf.get_params().keys() # leiab koik parameetrid
clf.fit(train_data2['Phrase'], y_train2)
print("Best Score: ", clf.best_score_)
print("Best Params: ", clf.best_params_)

"""Pipeline for **Support Vector Machine** classifier"""

from sklearn.linear_model import SGDClassifier

from sklearn.pipeline import Pipeline
clf_pipelineSGD = Pipeline([('vect', CountVectorizer(tokenizer=LemmaTokenizer(), stop_words='english',max_features=10000)),
                         ('clf', SGDClassifier())])
                       #  loss='hinge', penalty='l2',
                        #   alpha=1e-3, random_state=42,
                         #  max_iter=5))])
clf_pipelineSGD.fit(train_data2['Phrase'], y_train2)

from sklearn.svm import LinearSVC

clf_pipelineSVM = Pipeline([('vect', CountVectorizer(tokenizer=LemmaTokenizer(), token_pattern="\S+", max_features=7000, max_df=0.25)),
                         ('clf', LinearSVC(max_iter=5000, C = 0.5))])
                       #  loss='hinge', penalty='l2',
                        #   alpha=1e-3, random_state=42,
                         #  max_iter=5))])
clf_pipelineSVM.fit(train_data2['Phrase'], y_train2)

grid_params = {#'clf__C': [0.01, 0.1, 1, 10],
               #'clf__max_iter': [1000, 10000],
               'clf__C': np.linspace(0.5, 1, 1.24),

    
}
clf = GridSearchCV(clf_pipelineSVM, grid_params, cv=5)
clf.get_params().keys()

clf.fit(train_data2['Phrase'], y_train2)
print("Best Score: ", clf.best_score_)
print("Best Params: ", clf.best_params_)

predictedSGD = clf_pipelineSGD.predict(dev_data['Phrase'])

np.mean(predictedSGD == y_dev)

predicted2 = clf_pipelineSVM.predict(dev_data['Phrase'])

np.mean(predicted2 == y_dev)

"""Pipeline for  **Multinomial Logistic regression**

Using token_pattern="\S+", argument when constructing it, so that it won't break features like "word=foo" into pieaces "word" "foo".
"""

from sklearn.pipeline import Pipeline
import sklearn.linear_model
from sklearn.linear_model import LogisticRegression

clf_pipelineLR = Pipeline([('vect', CountVectorizer(tokenizer=LemmaTokenizer(), token_pattern="\S+", max_features=10000)),
                         ('lr', LogisticRegression(C = 1.7, solver = 'lbfgs', verbose=1, max_iter=300, multi_class='multinomial'))])
clf_pipelineLR.fit(train_data2['Phrase'], y_train2)

predicted2 = clf_pipelineLR.predict(dev_data['Phrase'])

np.mean(predicted2 == y_dev)

grid_params = {
  'lr__C': [1.5, 1.7, 1.9],
  'vect__max_df':[0.1, 0.25, 0.5, 1]
  #'lr__max_iter': [100, 300, 900],
  #'lr__solver': ['newton-cg', 'sag', 'lbfgs']
  
}
clf = GridSearchCV(clf_pipelineLR, grid_params)
clf.get_params().keys()
clf.fit(train_data2['Phrase'], y_train2)
print("Best Score: ", clf.best_score_)
print("Best Params: ", clf.best_params_)

!pip install sklearn_crfsuite
import sklearn_crfsuite

def features(sentence):
    result = []
    sentence = sentence.split(' ')
    i = len(sentence)
    for k in range(i):

      word = sentence[k-1]

      result.append("word:" + word.lower())
    return result

def label2label(data):
  result = []
  for d in data:
    d2 = []
    d2.append(d)
  #  print(d)
    result.append(d2)
  return result

def sentence2features_and_labels(data):
    X = []
    for sentence in data:
        X_i = []
        X_i.append(features(sentence))
        y_i.append(sentence[i][1])
        X.append(X_i)
    return X

X_train_crf = sentence2features_and_labels(train_data2['Phrase'])
X_dev_crf = sentence2features_and_labels(dev_data['Phrase'])
Y_train_crf = label2label(y_train2)

print(X_train_crf[2])
print(Y_train_crf[2])

#crf = sklearn_crfsuite.CRF(
#    algorithm='lbfgs',
#    c1=0.1,
#    c2=0.1,
#    max_iterations=100,
#    all_possible_transitions=True
#)
#crf.fit(X_train_crf, Y_train_crf)

#y_pred_crf = crf.predict(X_dev_crf)

#print(sklearn_crfsuite.metrics.flat_accuracy_score(y_dev, y_pred_crf))

"""multinomial klasse võimaldavad ainult 'newton-cg', 'sag', 'saga' ja 'lbfgs'

Pipeline for **Decision Tree**
"""

from sklearn.tree import DecisionTreeClassifier

clf_pipelineDT = Pipeline([('vect', CountVectorizer(max_features=5000)),
                         ('clf', DecisionTreeClassifier(random_state=0))])
clf_pipelineDT.fit(train_data2['Phrase'], y_train2)

predicted2 = clf_pipelineDT.predict(dev_data['Phrase'])

np.mean(predicted2 == y_dev)

grid_params = {
  'clf__min_samples_leaf' : np.arange(1, 3),
 # 'clf__max_depth' : np.arange(18, 21),
  #'lr__max_iter': [100, 300, 900],
  #'lr__solver': ['newton-cg', 'sag', 'lbfgs']
  
}
clf = GridSearchCV(clf_pipelineDT, grid_params)
clf.get_params().keys()
clf.fit(train_data2['Phrase'], y_train2)
print("Best Score: ", clf.best_score_)
print("Best Params: ", clf.best_params_)

"""# **Tulemused**"""

import sklearn.metrics

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report

predicted = clf_pipelineLR.predict(dev_data['Phrase'])
print(classification_report(y_dev, predicted))
print("accuracy_score", accuracy_score(y_dev, predicted))

print("precision_score", precision_score(y_dev, predicted, average='weighted'))
print("recall_score", recall_score(y_dev, predicted, average='weighted'))
print("f1_score", f1_score(y_dev, predicted, average='weighted'))

predicted = clf_pipelineSVM.predict(dev_data['Phrase'])
print(classification_report(y_dev, predicted))
print("accuracy_score", accuracy_score(y_dev, predicted))

print("precision_score", precision_score(y_dev, predicted, average='weighted'))
print("recall_score", recall_score(y_dev, predicted, average='weighted'))
print("f1_score", f1_score(y_dev, predicted, average='weighted'))

predicted = clf_pipelineNB.predict(dev_data['Phrase'])
print(classification_report(y_dev, predicted))
print("accuracy_score", accuracy_score(y_dev, predicted))

print("precision_score", precision_score(y_dev, predicted, average='weighted'))
print("recall_score", recall_score(y_dev, predicted, average='weighted'))
print("f1_score", f1_score(y_dev, predicted, average='weighted'))

predicted = clf_pipelineDT.predict(dev_data['Phrase'])
print(classification_report(y_dev, predicted))
print("accuracy_score", accuracy_score(y_dev, predicted))

print("precision_score", precision_score(y_dev, predicted, average='weighted'))
print("recall_score", recall_score(y_dev, predicted, average='weighted'))
print("f1_score", f1_score(y_dev, predicted, average='weighted'))

predictedTest = clf_pipelineLR.predict(test_data['Phrase'])

"""## **Neural network model**"""

import torch

device = 'cpu'
if torch.cuda.is_available():
  device = torch.device('cuda')

print(device)

import spacy
import torchtext
from torchtext.data import Field, BucketIterator, TabularDataset

!head train/train.tsv

import spacy
spacy_en = spacy.load('en')

def tokenizer(text): # create a tokenizer function
    return [tok.text for tok in spacy_en.tokenizer(text)]

"""sequential – Whether the datatype represents sequential data. If False, no tokenization is applied. Default: True.

use_vocab – Whether to use a Vocab object. If False, the data in this field should already be numerical. Default: True.

preprocessing – The Pipeline that will be applied to examples using this field after tokenizing but before numericalizing. Many Datasets replace this attribute with a custom preprocessor. Default: None.

batch_first – Whether to produce tensors with the batch dimension first. Default: False.

Allikas: https://blog.fromkk.com/post/textcnn-with-pytorch-and-torchtext-on-colab/
"""

clf_pipelineNN = Pipeline([('vect', CountVectorizer(tokenizer=LemmaTokenizer(), token_pattern="\S+", max_features=10000))]) # preprocessing osa
#clf_pipelineNN.fit(train_data2['Phrase'], y_train2)

LABEL1 = data.Field(sequential=False)
LABEL2 = data.Field(sequential=False)
REVIEW = data.Field(lower=True,batch_first=True)#, tokenize=tokenizer)#,use_vocab=True)

LABEL = data.Field(sequential=False, pad_token=None, unk_token=None)
#fields = [('Phrase', NAME), ('LABEL', LABEL)]
#dataset = data.TabularDataset(path="train/train.tsv", format="tsv", fields=fields)
train_dataset, test_dataset = data.TabularDataset.splits(path='.', train='train/train2.tsv', validation='test/test2.tsv', format='tsv', skip_header=True, fields=[('PhraseId',LABEL1), ('SentenceId', LABEL2), ('Phrase',REVIEW),('Sentiment',LABEL)])

train_size = int(0.8 * len(train_dataset))
test_size = len(train_dataset) - train_size
train_size
test_size

REVIEW.build_vocab(train_dataset)
LABEL.build_vocab(train_dataset)
LABEL2.build_vocab(train_dataset)
LABEL1.build_vocab(train_dataset)

LABEL.vocab.itos

LABEL.vocab.stoi

type(train_dataset)

train_iter, test_iter = data.BucketIterator.splits((train_dataset, test_dataset), batch_size=32,  device=device, repeat=False)
# The following two lines are needed to work around a bug in Torchtext. It will be fixed soon (I hope)
test_iter.sort_within_batch = train_iter.sort_within_batch
test_iter.sort = train_iter.sort

batch = next(iter(train_iter))
print(batch)

print(train_dataset[0].Phrase, train_dataset[0].Sentiment)

import sys
import torch.nn as nn
import torch.nn.functional as F

class CnnText(nn.Module):
  
  def __init__(self, num_classes, vocab_size, embedding_dim, dropout_prob):
    super(CnnText, self).__init__()
    print(vocab_size)
    print(num_classes)
    print(embedding_dim)
    self.embed = nn.Embedding(vocab_size, embedding_dim)
    self.conv1 = nn.Conv1d(embedding_dim, 32, kernel_size=3, stride=1)
    self.conv2 = nn.Conv1d(32, 64, kernel_size=1, stride=1)
    self.conv3 = nn.Conv1d(64, 64, kernel_size=1, stride=1)
    self.dropout = nn.Dropout(dropout_prob)
    self.fc = nn.Linear(64, num_classes)
    
  def forward(self, x):
    # Conv1d takes in (batch, channels, seq_len), but raw embedded is (batch, seq_len, channels)
    x = self.embed(x).permute(0, 2, 1)
   # print(x.shape)
    x = F.relu(self.conv1(x))
   # print(x.shape)
    x = F.max_pool1d(x, 2)
   # print(x.shape)
    x = F.relu(self.conv2(x))
   # print(x.shape)
    x = F.relu(self.conv3(x))
   # print(x.shape)
    x = F.max_pool1d(x, x.size(2))
   # print(x.shape)
    x = x.view(-1, 64)
   # print(x.shape)
    x = self.dropout(x) 
    logit = self.fc(x)
    return F.log_softmax(logit, dim=1)

model = CnnText(5, len(REVIEW.vocab), 100, 0.2).to(device)

print(batch.Sentiment)

print(model.forward(batch.Phrase))

# for calculating metrics
!pip install sklearn_crfsuite
import sklearn_crfsuite
import sklearn_crfsuite.metrics
from __future__ import absolute_import, division
from functools import wraps
from sklearn_crfsuite.metrics import flat_accuracy_score, flat_precision_score, flat_recall_score, flat_f1_score

from sklearn_crfsuite.utils import flatten
def train(model, num_epochs, train_iter, test_iter):

  optimizer = torch.optim.Adam(model.parameters())

  steps = 0
  best_acc = 0
  last_step = 0
  for epoch in range(1, num_epochs+1):
    print("Epoch %d" % epoch)
    model.train()
    for batch in train_iter:
      text, target = batch.Phrase, batch.Sentiment
     # print(target)
     # print(text)

      optimizer.zero_grad()
      output = model(text)

      loss = F.nll_loss(output, target)
      loss.backward()
      optimizer.step()

      steps += 1

    train_acc = evaluate("train", train_iter, model)                
    dev_acc = evaluate("test", test_iter, model)

def evaluate(dataset_name, data_iter, model, full_report=False):
  
  model.eval()
  total_corrects, avg_loss = 0, 0
  for batch in data_iter:
    text, target = batch.Phrase, batch.Sentiment


    output = model(text)
    
    loss = F.nll_loss(output, target, reduction='sum').item() # sum up batch loss
    pred = output.argmax(dim=1, keepdim=True) # get the index of the max log-probability
    

    correct = pred.eq(target.view_as(pred)).sum().item()
    
    avg_loss += loss
    
    total_corrects += correct

  size = len(data_iter.dataset)
  avg_loss /= size
  accuracy = 100.0 * total_corrects/size
  print('  Evaluation on {} - loss: {:.6f}  acc: {:.4f}%({}/{})'.format(dataset_name,
                                                                     avg_loss, 
                                                                     accuracy, 
                                                                     total_corrects, 
                                                                     size))

  targetList = []
  for tar in target:
    list1 = []
    list1.append(tar)
    targetList.append(list1)
  pred = pred.tolist()
  predList = []
  for pre in pred:
    list1 = []
    list1.append(pre)
    predList.append(list1)
  

  if full_report:
    print(sklearn_crfsuite.metrics.flat_classification_report(targetList, predList, labels=[0,1,2,3,4]))
    print("accuracy_score", flat_accuracy_score(targetList, predList))

    print("precision_score", flat_precision_score(targetList, predList, average='weighted'))
    print("recall_score", flat_recall_score(targetList, predList, average='weighted'))
    print("f1_score", flat_f1_score(targetList, predList, average='weighted'))
  return accuracy

train(model, 10, train_iter, test_iter)

"""# Testandmetele klasside leidmine logistilise  regressioonimudeliga"""

predicted2 = clf_pipelineLR.predict(test_data['Phrase'])

predicted2

#test_data["PhraseId"]

predicted2[215]

test_data.loc[215]

#predicted2 = clf_pipelineSVM.predict(test_data['Phrase'])

results = pd.read_csv('sampleSubmission.csv')
results["PhraseId"] = test_data["PhraseId"]
results["Sentiment"] = predicted2
results.to_csv(
    'submission.csv',
    index=False)

