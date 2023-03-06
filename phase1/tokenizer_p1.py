import os
import sys
import time
import re
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

def get_filenames(input_dir):
    filenames = []
    for files in os.listdir(input_dir):
        f = os.path.join(input_dir, files)
        if os.path.isfile(f):
            filenames.append(f)
    return filenames

def parse(input_dir, output_dir):
    all_tokens = []
    files = get_filenames(input_dir)
    start = time.time()
    for i, file in enumerate(files):
        #start = time.time()
        #Deals with UnicodeDecodeError
        with open(file, 'r', encoding='utf-8', errors='ignore') as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            text = soup.get_text()

            stripped = re.sub(r'[^\sa-zA-Z ]', '\n', text)
            #only keeps tokens with more than 1 letter or words 'a' and 'i'
            tokens = [token.lower() for token in stripped.split() if len(token) > 1 or token.lower() in ['a', 'i']]
            #joins name of files' path to output directory path. 
            output_file = os.path.join(output_dir, os.path.basename(file))
            #removes the .html extension, replaces it with .txt
            output_file = os.path.splitext(output_file)[0] + '.txt'

            with open(output_file, 'w') as out:
                for token in tokens:
                    out.write(str(token + '\n'))
            all_tokens += tokens
            #end = time.time()
            #all_time.append(end-start)
        if i % 100 == 0:
            print(f'Number of files processed: {i + 1} ')
    frequency_count(all_tokens)
    end = time.time()
    time_taken = (end - start) * 1000 #convert to milliseconds
    print(f'Time taken is ~ {time_taken} milliseconds')
    plt.plot([0, len(files)], [0, time_taken])
    plt.xlabel('Number of Files')
    plt.ylabel('Time taken(ms)')
    plt.show()

#function that counts frequency of tokens. Will create two files,
#one where tokens are sorted by frequency. The second, where
#tokens are sorted alphabetically. Both files will contain frequency of each token.
def frequency_count(tokens):
    token_frequency = {}
    for token in tokens:
        if token not in token_frequency:
            token_frequency[token] = 1
        else:
            token_frequency[token] += 1

    sorted_by_frequency = sorted(token_frequency.items(), key=lambda x: x[1], reverse=True)
    #print(type(sorted_by_frequency))
    with open('sorted_by_frequency.txt', 'w') as out:
        for token, amount in sorted_by_frequency:
            out.write(f'{token} \t {amount}\n')
    
    sorted_by_token = dict(sorted(token_frequency.items()))
    #print(type(sorted_by_token))
    with open('sorted_by_token.txt', 'w') as f:
        for token, amount in sorted_by_token.items():
            f.write(f'{token} \t {amount}\n')

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Use python3 tokenizer_p1.py input-dir output-dir")

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    parse(input_dir, output_dir)