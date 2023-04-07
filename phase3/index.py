import os
import sys
import time
import re
import math
from collections import defaultdict
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

def get_filenames(input_dir):
    filenames = []
    for files in os.listdir(input_dir):
        f = os.path.join(input_dir, files)
        if os.path.isfile(f):
            filenames.append(f)
    return filenames


def parse(input_dir, stop_words_set):
    files = get_filenames(input_dir)
    files_length = len(files)
    #used to store token frequency and avoids checks for existence of a key in a dict
    #outer dictionary are tokens, values of the tokens are in the inner
    token_freq = {}
    document_freq = defaultdict(int)
   # start = time.time()
    for i, file in enumerate(files):
        #Deals with UnicodeDecodeError
        with open(file, 'r', encoding='utf-8', errors='ignore') as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            text = soup.get_text()

            stripped = re.findall(r'\b[a-zA-Z]+\b', text.lower())

            tokens = [token for token in stripped if token not in stop_words_set and len(token) > 1]
            for token in tokens:
                if token not in token_freq:
                    #create empty inner dict if token has not been encountered
                    token_freq[token] = {} 
                if file not in token_freq[token]:
                    token_freq[token][file] = 0  #default value is 0
                token_freq[token][file] += 1
            
            #used a set to not count duplicates as it resulted in negative TF-IDF
            #keeps track of num of documents contain a certain token
            for token in set(tokens):
                document_freq[token]+=1

            #removing tokens that appear once in corpus
            appear_once = [token for token in token_freq if document_freq[token] == 1]
            for token in appear_once:
                del token_freq[token]
    return token_freq, document_freq
        # if i % 100 == 0:
        #     print(f'Number of files processed: {i + 1} ')

    # end = time.time()
    # time_taken = (end - start) * 1000 #convert to milliseconds
    # print(f'Time taken is ~ {time_taken} milliseconds')
    # plt.plot([0, i], [0, time_taken])
    # plt.xlabel('Number of Files')
    # plt.ylabel('Time taken(ms)')
    # plt.show()


def inverted_index(token_freq, doc_freq, output_dir):
    dict_file = os.path.join(output_dir, "dictionary.txt")
    post_file = os.path.join(output_dir, "postings.txt")

    #for calc docs length
    doc_lenghts = {}
    for token, docs in token_freq.items():
        for file, weight in docs.items():
            if file not in doc_lenghts:
                doc_lenghts[file] = 0
            doc_lenghts[file] += weight ** 2
    #stores doc id and term weight for tokens
    postings = []
    #stores dictionary and postings data
    with open(dict_file, 'w') as d_file, open(post_file, 'w') as p_file:
        posting_pos = 1
        for token, docs in token_freq.items():
            #writes token, num of docs containing token, and pos
            d_file.write(f'{token}\n{len(docs)}\n{posting_pos}\n\n')

            for file, weight in docs.items():
                #tuple containing doc id and token weight for that token in the document
                postings.append((file, weight))
                posting_pos += 1
        
        for post in postings:
            p_file.write(f'{post[0]}, {post[1]}\n')

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Use python3 index.py input-dir output-dir")

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    #reads in stop words
    with open('stopwords.txt', 'r') as f:
        stop_words_set = {line.strip() for line in f}

    #returning term frequency and doc frequency
    tf, df = parse(input_dir, stop_words_set)
    inverted_index(tf, df, output_dir)