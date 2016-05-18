# Simple extended boolean search engine: query module
# Hussein Suleman
# 14 April 2016

import re
import math
import sys
import os

import porter
import blind_relevance

import parameters

def performQuery():
   # create accumulators and other data structures
   accum = {}
   filenames = []
   p = porter.PorterStemmer ()
   
   # get N
   f = open (collection+"_index_N", "r")
   N = eval (f.read ())
   f.close ()
   
   # get document lengths/titles
   titles = {}
   f = open (collection+"_index_len", "r")
   lengths = f.readlines ()
   f.close ()
   
   # get index for each term and calculate similarities using accumulators
   for term in query_words:
      if term != '':
         if parameters.stemming:
            term = p.stem (term, 0, len(term)-1)
         if not os.path.isfile (collection+"_index/"+term):
            continue
         f = open (collection+"_index/"+term, "r",encoding="utf8")
         lines = f.readlines ()
         idf = 1
         if parameters.use_idf:
            df = len(lines)
            idf = 1/df
            if parameters.log_idf:
               idf = math.log (1 + N/df)
         for line in lines:
            mo = re.match (r'([0-9]+)\:([0-9\.]+)', line)
            if mo:
                  file_id = mo.group(1)
                  tf = float (mo.group(2))
                  if not file_id in accum:
                     accum[file_id] = 0
                  if parameters.log_tf:
                     tf = (1 + math.log (tf))
                  accum[file_id] += (tf * idf)                           
         f.close()
      
   # parse lengths data and divide by |N| and get titles
   for l in lengths:
      mo = re.match (r'([0-9]+)\:([0-9\.]+)\:(.+)', l)
      if mo:
         document_id = mo.group (1)
         length = eval (mo.group (2))
         title = mo.group (3)
         if document_id in accum:
            if parameters.normalization:
               accum[document_id] = accum[document_id] / length
            titles[document_id] = title
   
   # print top ten results
   result = sorted (accum, key=accum.__getitem__, reverse=True)
   topResults = []
   for i in range (min (len (result), 10)):
         topResults.append(result[i])
      
   return topResults, N, titles, accum



def removeStopwords(query_words):
  query_words = [a for a in query_words if a]
  with open ("stopwords", "r") as f:
    stopwords = f.readlines ()
    for sw in stopwords:
      sw = sw.replace("\n","")
      if (sw in query_words):
        query_words.remove(sw)
  return query_words

def evaluationMap(orderedResults, queryRelevance):
  # TODO
  return 0

def evaluationNDCG(topResults, queryRelevance) :
  # TODO
  return 0


# check parameter for collection name
if len(sys.argv)<2:
   print ("Syntax: query.py <flag> <collection> <query>\n\t-e for evaluation with NDCG & MAP\n\t-s to search for a <query>")
   exit(0)

collection        = sys.argv[2]
queries           = []
evaluation        = False
path              = os.getcwd() + "\\" + collection + "\\"
query_relevance   = []
query_index       = 0

# Check for evaluation flag
if (sys.argv[1] == '-e'):
  print("Evaluating search results...")
  evaluation = True
  
  # Load in queries
  for file_in in os.listdir(path):
    if file_in.startswith("query"):
      mo = re.search(r'[0-9]+', file_in)
      # Get the document identification number
      if mo:
        query_number = mo.group(0)
        # Use 'with' for automated closing of open files
        with open(path + file_in, 'r',encoding='utf-8') as f:
          queries.append(f.read().strip())
        with open(path + "relevance." + query_number, 'r',encoding="utf-8") as g:
          query_relevance.append(g.read().split('\n'))
  print("MAP\tNDCG\tQuery")

elif (sys.argv[1] == '-s'):
  arg_index = 3

  # construct collection and query
  queries.append(sys.argv[arg_index] + ' ')
  arg_index += 1
  while arg_index < len(sys.argv):
    queries[0] += sys.argv[arg_index] + ' '
    arg_index += 1

for query in queries:
  # clean query
  if parameters.case_folding:
    query = query.lower () 
  query = re.sub (r'[^ a-zA-Z0-9]', ' ', query)
  query = re.sub (r'\s+', ' ', query)
  query_words = query.split (' ')

  #Remove stopwords
  if (parameters.stopwords):
    query_words = removeStopwords(query_words)

  #Perform inital query
  N         = 0
  titles    = {}
  accum     = {}
  topResults, N, titles, accum = performQuery()

  #Perform blind relevance
  if (parameters.blind_relevance):
    query_words += blind_relevance.blindRelevance(topResults,collection,N)
    #Remove stopwords
    if (parameters.stopwords):
      query_words = removeStopwords(query_words)
    topResults, N, titles, accum = performQuery()

  if (evaluation):
    # Perform evaluation
    evaluation_MAP    = evaluationMap(topResults, query_relevance[query_index])
    evaluation_NDCG   = evaluationNDCG(topResults, query_relevance[query_index]) 
    print("{1:.3f}\t{2:.3f}\t{0}".format (query, evaluation_MAP, evaluation_NDCG))
    # Progress the query index to next query
    query_index += 1
  else:
    for i in range(len(topResults)):
      print("{0:10.8f} {1:5} {2}".format (accum[topResults[i]], topResults[i], titles[topResults[i]]))
