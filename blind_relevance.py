# Simple extended boolean search engine: blind relevance calculator
# Takes a set of docs and returns a query with their most relevant terms
# Sam Alfred
# 16 April 2016

import os
import re
import math

import porter

import parameters
import unicodedata

def blindRelevance(topDocs, collection, N):
    query_words    = []
    p              = porter.PorterStemmer ()
	
    for doc in topDocs:

        #Get number of each term in each top result (tf)
        path = os.getcwd() + "\\" + collection
        with open (path+"\\"+"document."+str(doc),"r", encoding="utf-8") as f:
            content = f.read()
            if parameters.case_folding:
                content = content.lower()

            content     = re.sub (r'[^ a-zA-Z0-9]', ' ', content)
            content     = re.sub (r'\s+', ' ', content)
            content     = unicodedata.normalize('NFKD', content).encode('ascii','ignore').decode('utf-8')
            words       = content.split (' ')

            #Get all the terms in a document and their frequencies
            terms = {}
            for word in words:
                if word != '':
                    if parameters.stemming:
                        word = p.stem (word, 0, len(word)-1)
                    
                    if (word not in terms):
                        terms[word] = 1
                    else:
                        terms[word] += 1
            
            #Work out tfidf for each term            
            tfidf = {}
            for term in terms:
                tf = terms[term]
                idf = 1
                if parameters.use_idf:
                    if not os.path.isfile (collection+"_index/"+term):
                        continue
                    with open (collection+"_index/"+term, "r",encoding="utf8") as l:                    
                        df = len(l.readlines())
                        idf = 1/df
                        if parameters.log_idf:
                            idf = math.log (1 + N/df)
                        
                    if not term in tfidf:
                        tfidf[term] = 0
                    if parameters.log_tf:
                        tf = (1 + math.log (tf))
                    tfidf[term] += (tf * idf)

            #Add top 20 to the result query
            result = sorted (tfidf, key=tfidf.__getitem__, reverse=True)
            for i in range (min (len (result), 20)):        
                if (result[i] not in query_words):
                    query_words.append(result[i])
                    
    return query_words