import os
import sys
import time
import re
import math
from collections import defaultdict

def load_inverted_index():
    '''
    dictionary.txt and postings.txt are loaded in the memory as lists
    '''
    with open('dictionary.txt', 'r', encoding='UTF-8') as dict_file, open('postings.txt', 'r') as post_file:
        dictionary = dict_file.read().splitlines()
        postings = post_file.read().splitlines()
    return dictionary, postings

def printing_top_10(found_query, query):
    #sorting to display top 10 terms
    sorted_found = sorted(found_query.items(), key=lambda x: x[1], reverse=True)
    #query = ' '.join(query)
    
    print(f'{query} was found in {len(found_query)} documents')
    #print(sorted_found)
    count = 0 
    for doc, score in sorted_found:
        #if score > 0:
            print(f'{doc}, {score}')
            count += 1
            if count == 10:
                break

def sum_document_similarity(dictionary, postings, query):

    '''
    performing term at a time 
    '''
    found = {} #document scores
   # tf_idf = {}
    #going term at a time
    for token in query:
        #if the token from the query is in the dictionary file
        if token in dictionary:
            position_of_token = dictionary.index(token) #finding the location of the token in dictionary 
            number_postings = int(dictionary[position_of_token + 1]) #one line below from token is num of postings
            #print(number_postings)
            start_pos_in_postings = int(dictionary[position_of_token + 2]) #2 lines below token is start pos in postings.txt
            #print(type(start_pos_in_postings))
            #find the documentid in posting.txt
            documentid = postings[start_pos_in_postings: start_pos_in_postings + number_postings]
            #print(documentid)
            for word in documentid:

                #here stripping off the comma from postings.txt.
                (doc, score) = word.split(',')
                #print(f"Processing doc: {doc}, score: {score}")
                if doc in found:
                  #  print(f'Doc {doc} already in dictionary, updating score')
                    found[doc] += float(score)
                else:
                  #  print(f'Adding doc {doc} to dictionary')
                    found[doc] = float(score)
                    #print(found)
                #print(f'current score {score}')
        else:
            print('Query not in index')
    printing_top_10(found, query)

if __name__ == "__main__":
    dictionary, postings = load_inverted_index()

    arguments = len(sys.argv)
    if arguments < 2:
        print("Use `python3 retrieval.py query-here`")
    #storing the query
    query = []
    for i in range(1, arguments):
        #lowercasing the query
        word = sys.argv[i].lower()
        query.append(word)
    start = time.time()
    #query = ' '.join(query)
    sum_document_similarity(dictionary, postings, query)
    end = time.time()
    print(f'Total time for query: {end-start}')