from gensim import corpora
from nltk import stem
from nltk.corpus import stopwords
from string import punctuation
import os
from gensim import corpora, models, similarities
import re

class buildCorpus(object):
    stops = stopwords.words('english')
    snowball = stem.snowball.EnglishStemmer()
    
    # uses regex to remove punctuation
    def remove_punctuation(self, text):
        return re.sub(r"\\p{P}+", "", text)
    
    # tokenize and stem documents for NLP
    def tokenize_and_stem(self, document):
        # add a space after elipses
        document = re.sub(r"\\.\\.\\.", "... ", document)
        # remove punctuation
        document = self.remove_punctuation(document)
        # lowercase
        document = document.lower()
        # remove stop words
        tokens = [word for word in document.split() if word not in self.stops]
        # stem
        return [self.snowball.stem(word) for word in tokens]
    
    def __init__(self, directory):
        self.directory = directory
        
    def __iter__(self):
        for filename in os.listdir(self.directory):
            if filename.endswith(".txt") and filename != 'love_actually.txt':
                with open(os.path.join(self.directory, filename), 'r') as document:
                    contents = document.read()
                yield((filename[:-4], self.tokenize_and_stem(contents)))
            else:
                continue

corpusBuilder = buildCorpus('love_actually')
dictionary = corpora.Dictionary(tokens for _, tokens in corpusBuilder)
characters = []
corpus = []
for character in corpusBuilder:
    characters.append(character[0])
    corpus.append(dictionary.doc2bow(character[1]))

# train the LSI model with ~200 topics
lsi = models.LsiModel(corpus, id2word = dictionary, num_topics = 200)
# apply the model to our corpus_tfidf
corpus_lsi = lsi[corpus]
# establish an index for querying
index = similarities.MatrixSimilarity(lsi[corpus])

# save everything for access
corpora.MmCorpus.serialize('love_actually/love_actually.mm', corpus)
dictionary.save('love_actually/love_actually.dict')
index.save('love_actually/love_actually.index')