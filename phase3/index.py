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

    files = input_dir
    #used to store token frequency and avoids checks for existence of a key in a dict
    #outer dictionary are tokens, values of the tokens are in the inner
    token_freq = {}
    document_freq = defaultdict(int)
    for file in files:
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


def inverted_index(token_freq, doc_freq, output_dir):
    dict_file = os.path.join(output_dir, "dictionary.txt")
    post_file = os.path.join(output_dir, "postings.txt")

    #for calc docs length
    doc_lengths = {}
    #docs is another dict that contains token freq of current token in each document
    for token, docs in token_freq.items():
        #weight is token frequency of current token in current document
        for file, weight in docs.items():
            if file not in doc_lengths:
                doc_lengths[file] = 0
            doc_lengths[file] += weight ** 2

    #normalizing docs length
    for file in doc_lengths:
        doc_lengths[file] = math.sqrt(doc_lengths[file])
    num_docs = len(doc_lengths)
    #stores doc id and term weight for tokens
    postings = []
    #stores dictionary and postings data
    with open(dict_file, 'w') as d_file, open(post_file, 'w') as p_file:
        posting_pos = 1
        for token, docs in token_freq.items():
            idf = math.log(num_docs / len(docs))
            #writes token, num of docs containing token, and pos
            d_file.write(f'{token}\n{len(docs)}\n{posting_pos}\n\n')

            for file, weight in docs.items():
                tf = weight
                tf_idf = tf*idf
                norm_weight = tf_idf / doc_lengths[file]
                #extract just name of filename from the path 
                doc_id = os.path.basename(file)
                #tuple containing doc id and token weight for that token in the document
                postings.append((doc_id, norm_weight))
                posting_pos += 1
        
        for post in postings:
            p_file.write(f'{post[0]}, {post[1]}\n')

def measure_time(input_dir, output_dir, stop_words_set, num_docs_list):
    files = get_filenames(input_dir)
    times_list = [] #for total elapsed time
    total_start_timer = time.time()
    for num_docs in num_docs_list:
        start = time.time()
        #subset of files that will contain the first num_docs elements from the files list
        input_dir_subset = files[:num_docs]
        #returning term frequency and doc frequency
        tf, df = parse(input_dir_subset, stop_words_set)
        inverted_index(tf, df, output_dir)
        end = time.time()
        total_time = end - start
        print(f'Processed {num_docs} files. Time Taken: {total_time} seconds')
        times_list.append(total_time)
    total_end_timer = time.time()
    total_time_taken = total_end_timer - total_start_timer
    print(f'Total time taken for the whole program: {total_time_taken} seconds')
    return times_list

def plot_time(num_docs_list, time_list):
    plt.plot(num_docs_list, time_list, label = 'Total Time')
    plt.xlabel('Num of Documents')
    plt.ylabel('Time (s)')
    plt.legend()
    plt.show()

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Use python3 index.py input-dir output-dir")

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    #reads in stop words
    with open('stopwords.txt', 'r') as f:
        stop_words_set = {line.strip() for line in f}

    num_docs_list = [10, 20, 40, 80, 160, 220, 300, 380, 460, 503]
    elapsed_time = measure_time(input_dir, output_dir, stop_words_set, num_docs_list)
    plot_time(num_docs_list, elapsed_time)
