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

    print(f'{query} was found in {len(sorted_found)} documents')
    if len(sorted_found) >= 10:
        for x in range(10):
            print(sorted_found[x])
    else:
        for x in range(len(sorted_found)):
            print(sorted_found[x])

def cosine_similarity(dictionary, postings, query):

    '''
    performing term at a time 
    '''
    found = {}
    # print(dictionary)
    # print(postings)

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

            for word in documentid:
                #here stripping off the comma from postings.txt.
                (doc, score) = word.split(',')
                
                found[doc] = score

            printing_top_10(found, query)
        else:
            print('Query not in index')

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
    cosine_similarity(dictionary, postings, query)
    end = time.time()
    print(f'Total time for query: {end-start}')