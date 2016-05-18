# Simple extended boolean search engine: blind relevance calculator
# Takes a set of docs and returns a query with their most relevant terms
# Sam Alfred
# 16 April 2016

import os
import re
import math

import porter

import parameters

def blindRelevance(topDocs, collection, N):
    
    query_words = []
    p = porter.PorterStemmer ()
    
    for doc in topDocs:
        counts = {}
        
        #Get number of each term in each top result (tf)
        path = os.getcwd() + "\\" + collection
        f = open (path+"\\"+"document."+str(doc),"r")
        content = f.read()
        f.close() 
        if parameters.case_folding:
            content = content.lower()                
        content = re.sub (r'[^ a-zA-Z0-9]', ' ', content)
        content = re.sub (r'\s+', ' ', content)
        words = content.split (' ')
        doc_length = 0
        for word in words:
            if word != '':
                if parameters.stemming:
                    word = p.stem (word, 0, len(word)-1)
                if (word in counts):
                    counts[word] += 1
                else:
                    counts[word] = 1       
        
        #Get the tf.idf for each term in the document
        tfidf = {}
        for term in counts.keys():
            f = open (path+"_index"+"\\"+str(term),"r")
            content = f.readlines()
            f.close()         
            idf = math.log(N/len(content))
            
            tfidf[term] = counts[term]*idf
        
        #Add top 20 to the result query
        result = sorted (tfidf, key=tfidf.__getitem__, reverse=True)
        for i in range (min (len (result), 20)):        
            if (result[i] not in query_words):
                query_words.append(result[i])
                
    return query_words