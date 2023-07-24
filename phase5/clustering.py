import os
import sys
import time
import re
import math
import pandas as pd
import numpy as np
from collections import defaultdict
from bs4 import BeautifulSoup
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics.pairwise import cosine_similarity

def get_filenames(input_dir):
    filenames = []
    for files in os.listdir(input_dir):
        f = os.path.join(input_dir, files)
        if os.path.isfile(f):
            filenames.append(f)
    return filenames


def parse(input_dir, stop_words_set):

    files = get_filenames(input_dir)
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

def tf_idf_matrix(tf, idf):
    doc_set = set()
    for i in tf.values():
        for j in i.keys():
            doc_set.add(j)
    N = len(doc_set)

    #calculating tf_idf
    tf_idf = {}
    for token, docs in tf.items():
        df_t = df[token]
        idf_t = math.log(N / (1 + df_t))
        for doc, freq in docs.items():
            tf_t_d = freq / len(docs) 
            tf_idf_t_d = tf_t_d * idf_t
            if doc not in tf_idf:
                tf_idf[doc] = {}
            tf_idf[doc][token] = tf_idf_t_d

    #normalizing the tf_idf
    tf_idf = pd.DataFrame.from_dict(tf_idf, orient='index').fillna(0)
    norms = np.linalg.norm(tf_idf.values, axis=1, keepdims=True)
    tf_idf_normalized = tf_idf.values / norms
    tf_idf_normalized = pd.DataFrame(tf_idf_normalized, index=tf_idf.index, columns=tf_idf.columns)
    return tf_idf_normalized

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Use python3 clustering.py input-dir output-dir")

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    #reads in stop words
    with open('stopwords.txt', 'r') as f:
        stop_words_set = {line.strip() for line in f}
    
    tf, df = parse(input_dir, stop_words_set)
    tf_idf = tf_idf_matrix(tf,df)

    tfidf_matrix = tf_idf.values  # convert DataFrame to numpy array
    num_docs = tfidf_matrix.shape[0]
    #initialize an empty similarity matrix
    similarity_matrix = np.zeros((num_docs, num_docs))
    #for each pair of documents...constructing the similarity matrix
    for i in range(num_docs):
        for j in range(i+1, num_docs):  #only compute for j > i due to symmetry

            #compute dot product
            dot_product = np.dot(tfidf_matrix[i], tfidf_matrix[j])
    
            #compute cosine similarity and store in matrix
            similarity_matrix[i, j] = dot_product
            #ue to symmetry, similarity[i, j] is the same as similarity[j, i]
            similarity_matrix[j, i] = similarity_matrix[i, j] #symmetry
    #print(similarity_matrix)

    distance_matrix = 1 - similarity_matrix
    #print(distance_matrix)
    Z = linkage(distance_matrix, method='complete')
    threshold = .4
    clusters = fcluster(Z, threshold, criterion='distance')

    print(clusters)

    document_names = tf_idf.index.tolist()

    with open(os.path.join(output_dir, 'first_100.txt'), 'w') as f:
       
        for i, (doc1, doc2, dist, num_docs_in_cluster) in enumerate(Z):
            if i == 100:
                break
            else:
                if doc1 < num_docs:
                    doc1_name = os.path.basename(document_names[int(doc1)])
                    distance = dist
                else:
                 doc1_name = f"Cluster {int(doc1) - num_docs}"

                if doc2 < num_docs:
                    doc2_name = os.path.basename(document_names[int(doc2)])
                    distance = dist
                else:
                    doc2_name = f"Cluster {int(doc2) - num_docs}"
                f.write(f"Line {i+1}: ({doc1_name}, {doc2_name}) Distance: {distance}\n")
            
    # most_similar_pair = document_names[int(Z[0, 0])], document_names[int(Z[0, 1])]
    # print("Most similar pair:", most_similar_pair)
    max_similarity = -1
    most_similar_pair = ()
    for i in range(num_docs):
        for j in range(i+1, num_docs):
            if similarity_matrix[i, j] > max_similarity:
                max_similarity = similarity_matrix[i, j]
                most_similar_pair = (i, j)

    #grabbing clusters which are most similar
    cluster_i = clusters[most_similar_pair[0]]  
    cluster_j = clusters[most_similar_pair[1]]
    print(f"\nMost similar pair of documents: {document_names[most_similar_pair[0]]}, {document_names[most_similar_pair[1]]}")

    min_similarity = 1
    most_dissimilar_pair = ()
    for i in range(num_docs):
        for j in range(i+1, num_docs):
            if similarity_matrix[i, j] < min_similarity:
                min_similarity = similarity_matrix[i, j]
                most_dissimilar_pair = (i, j)

    #grabbing the clusters with most dissimilar
    cluster_x = clusters[most_dissimilar_pair[0]]
    cluster_y = clusters[most_dissimilar_pair[1]]

    print(f"\nMost dissimilar pair of documents: {document_names[most_dissimilar_pair[0]]}, {document_names[most_dissimilar_pair[1]]}")

    # Figuring out which one are closest to centroid
    centroid = np.mean(tfidf_matrix, axis=0)
    similarity_to_centroid = cosine_similarity(tfidf_matrix, centroid.reshape(1, -1))
    closest_to_centroid = document_names[np.argmax(similarity_to_centroid)]
    print("\nClosest to centroid:", closest_to_centroid)