# Simple extended boolean search engine: indexer based on cranfield format
# Hussein Suleman
# 21 April 2016

import os
import re
import sys

import porter

import parameters

# check parameter for collection name
if len(sys.argv)==1:
   print ("Syntax: index.py <collection type: -f file, -d directory> <relative collection directory/name>\n * Directory (-d) contains multiple separate documents *")
   exit(0)

collection  =   sys.argv[2]
identifier  =   ''
document    =   ''
title       =   ''
indocument  =   False
intitle     =   False
data        =   {}
titles      =   {}

# Check to see if the inputted data is a directory (-d) or a file (-f)
if (sys.argv[1] == "-f"):
    # read and parse input data - extract words, identifiers and titles
   f = open (collection, "r")
    
   for line in f:
      mo = re.match (r'\.I ([0-9]+)', line)
      if mo:
         if document!='':
               data[identifier] = document
         identifier = mo.group (1)
         indoc = False
      else:
         mo = re.match (r'\.T', line)
         if mo:
            title = ''
            intitle = True
         else:
            mo = re.match (r'\.W', line)
            if mo:
                  document = ''
                  indoc = True
            else:
                  if intitle:
                     intitle = False
                     if identifier!='':
                        titles[identifier] = line[:-1][:50]
                  elif indoc:
                     document += " "
                     if parameters.case_folding:
                        document += line.lower()
                     else:
                        document += line    
   f.close ()
elif (sys.argv[1] == "-d"):
   path = os.getcwd() + "\\" + collection + "\\";
   for i in os.listdir(path):
        # Only open documents and not the queries/relevance files
      if i.startswith("document"):
         mo = re.search(r'[0-9]+', i)
         # Get the document identification number
         if mo:
               identifier = mo.group(0)
         # Use 'with' for automated closing of open files
         with open(path + i, 'r',encoding="utf8") as f:
               content =   f.read()
               title  =   content[:-1][:50]
               # Add aproximate data heading to title array
               title = re.sub(r'\n.*', '', title)
               title = re.sub(r'\_', ' ', title)
               titles[identifier] = title
               print(titles[identifier])
               # If case folding is true, convert the body to lower case text
               if parameters.case_folding:
                  content = content.lower()
               # Add the document content to the data array
               data[identifier] = content

# document length/title file
g = open (collection + "_index_len", "w")

# create inverted files in memory and save titles/N to file
index = {}
N = len (data.keys())
p = porter.PorterStemmer ()
for key in data:
   print(key)
   content = re.sub (r'[^ a-zA-Z0-9]', ' ', data[key])
   content = re.sub (r'\s+', ' ', content)
   words = content.split (' ')
   doc_length = 0
   for word in words:
      if word != '':
         if parameters.stemming:
               word = p.stem (word, 0, len(word)-1)
         doc_length += 1
         if not word in index:
               index[word] = {key:1}
         else:
               if not key in index[word]:
                  index[word][key] = 1
               else:
                  index[word][key] += 1
   print (key, doc_length, titles[key], sep=':', file=g) 

# document length/title file
g.close ()

# write inverted index to files
try:
   os.mkdir (collection+"_index")
except:
   pass
for key in index:
   f = open (collection+"_index/"+key, "w")
   for entry in index[key]:
      print (entry, index[key][entry], sep=':', file=f)
   f.close ()

# write N
f = open (collection+"_index_N", "w")
print (N, file=f)
f.close ()
    