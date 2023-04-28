import os
import sys
import time
import re
import math
from collections import defaultdict

def load_inverted_index():
    
    with open('dictionary.txt', 'r', encoding='UTF-8') as dict_file, open('postings.txt', 'r') as post_file:
        index = dict_file.read().splitlines()
        postings = post_file.read().splitlines()
    return index, postings



if __name__ == "__main__":
    index, postings = load_inverted_index()

    arguments = len(sys.argv)
    if arguments < 2:
        print("Use `python3 retrieval.py query-here`")
    #storing the query
    query = []
    for i in range(1, arguments):
        #lowercasing the query
        word = sys.argv[i].lower()
        query.append(word)
    
