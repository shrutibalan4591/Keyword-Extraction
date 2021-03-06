# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
nltk.download('wordnet') 
from nltk.stem.wordnet import WordNetLemmatizer
from os import path
from PIL import Image
import matplotlib.pyplot as plt
# % matplotlib inline
from sklearn.feature_extraction.text import CountVectorizer
import re
from sklearn.feature_extraction.text import TfidfTransformer
import pickle
from flask import Flask, request, render_template

app = Flask(__name__)

#Creating a list of stop words and adding custom stopwords
stop_words = set(stopwords.words("english"))
#Creating a list of custom stopwords
new_words = ["using", "show", "result", "large", "also", "iv", "one", "two", "new", "previously", "shown", "useful"]
stop_words = stop_words.union(new_words)
#**************************
# TEXT PREPROCESSING
# FUNCTION TO CREATE A CORPUS
def create_corpus(data):
  corpus = []
#for i in range(0, df.word_count.count()):
  #Remove punctuations
  text = re.sub('[^a-zA-Z]', ' ', data)
    
  #Convert to lowercase
  text = text.lower()
    
  #remove tags
  text=re.sub("&lt;/?.*?&gt;"," &lt;&gt; ",text)
    
  # remove special characters and digits
  text=re.sub("(\\d|\\W)+"," ",text)
    
  #Convert to list from string
  text = text.split()
    
  #Stemming
  ps=PorterStemmer()
  #Lemmatisation
  lem = WordNetLemmatizer()
  text = [lem.lemmatize(word) for word in text if not word in  
          stop_words] 
  text = " ".join(text)
  corpus.append(text) 

  return corpus

#************************************************
#Function for sorting tf_idf in descending order
from scipy.sparse import coo_matrix
def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)
 #***********************************************
def extract_topn_from_vector(feature_names, sorted_items):
    """get the feature names and tf-idf score of top n items"""
    
    #use only topn items from vector
    sorted_items = sorted_items[:10]
 
    score_vals = []
    feature_vals = []
    
    # word index and corresponding tf-idf score
    for idx, score in sorted_items:
        
        #keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])
 
    #create a tuples of feature,score
    #results = zip(feature_vals,score_vals)
    results= {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]]=score_vals[idx]
    
    return results
#*****************************************
@app.route('/')
def home():
	return render_template('home.html')
#****************************************
@app.route('/predict',methods=['POST'])
def predict():
  if request.method == 'POST':
    data = request.form['message']
    word_count = len(str(data).split(" "))

    if word_count<400:
      return render_template('home.html', error_msg='Article must be of minimum 400 words!')
    else:
      corpus = create_corpus(data)

      # Vectorisation - CountVectorizer
      cv=CountVectorizer(stop_words=stop_words, 
                          max_features=300, 
                          ngram_range=(1,3))
      X=cv.fit_transform(corpus)

      # Converting to a matrix of integers
      tfidf_transformer=TfidfTransformer(smooth_idf=True,use_idf=True)
      tfidf_transformer.fit(X)
      # get feature names
      feature_names=cv.get_feature_names()

      #generate tf-idf for the given document
      tf_idf_vector=tfidf_transformer.transform(cv.transform(corpus))

      #vect = cv.transform(data).toarray()

      #sort the tf-idf vectors by descending order of scores
      sorted_items=sort_coo(tf_idf_vector.tocoo())
      #extract only the top 10
      keywords=extract_topn_from_vector(feature_names,sorted_items)
      
      return render_template('extraction.html', extraction=keywords)

if __name__ == '__main__':
    app.run(debug=True)
