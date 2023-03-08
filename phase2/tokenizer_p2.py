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


def parse(input_dir, output_dir, stop_words_set):
    files = get_filenames(input_dir)
    files_length = len(files)
    #used to store token frequency and avoids checks for existence of a key in a dict
    #outer dictionary are tokens, values of the tokens are in the inner
    token_freq = {}
    document_freq = defaultdict(int)
    start = time.time()
    for i, file in enumerate(files):
        #Deals with UnicodeDecodeError
        with open(file, 'r', encoding='utf-8', errors='ignore') as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            text = soup.get_text()

            stripped = re.findall(r'\b[a-zA-Z]+\b', text.lower())

            #The two lines below are how I stripped tokens in the Phase 1 of the project
            #stripped = re.sub(r'[^\sa-zA-Z ]', '\n', text)
            #tokens = [token.lower() for token in stripped.split() if len(token) > 1 and token.lower() not in stop_words_list]
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

            #METHOD 1 of removing tokens that appear once in corpus
            # appear_once = [token for token in token_freq if document_freq[token] == 1]
            # for token in appear_once:
            #     del token_freq[token]

        output_file = os.path.join(output_dir, os.path.basename(file))
        #removes the .html extension, replaces it with .wts
        output_file = os.path.splitext(output_file)[0] + '.wts'

        #output TF-IDF to .wts
        with open(output_file, 'w') as out:
            for token in token_freq.keys():
                if file in token_freq[token]:
                    #METHOD 2 of ignore tokens that only appear once in corpus
                    #Not sure if this is the correct way to not count tokens that occur once in entire corpus
                    if document_freq[token] == 1:
                        continue
                    tf = token_freq[token][file] / len(tokens)
                    idf = math.log(files_length / document_freq[token])
                    tf_idf = tf*idf
                    out.write(f'{token} \t {tf_idf}\n')

        if i % 100 == 0:
            print(f'Number of files processed: {i + 1} ')

    end = time.time()
    time_taken = (end - start) * 1000 #convert to milliseconds
    print(f'Time taken is ~ {time_taken} milliseconds')
    plt.plot([0, i], [0, time_taken])
    plt.xlabel('Number of Files')
    plt.ylabel('Time taken(ms)')
    plt.show()

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Use python3 tokenizer_p1.py input-dir output-dir")

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    #reads in stop words
    with open('stopwords.txt', 'r') as f:
        stop_words_set = {line.strip() for line in f}
    #print(type(stop_words_set))
    #print(len(stop_words_set))
    parse(input_dir, output_dir, stop_words_set)