import streamlit as st
from ruwordnet import RuWordNet
import numpy as np
import spacy
import pymorphy2
import gensim

st.set_page_config(page_title="Text Augmentation NLP", layout="wide")
st.title("Text Augmentation NLP")

model = gensim.models.KeyedVectors.load_word2vec_format('ruwikiruscorpora_upos_cbow_300_20_2017.bin.gz', binary=True)
morph = pymorphy2.MorphAnalyzer()
wn = RuWordNet()
nlp = spacy.load("ru_core_news_sm")

def get_tags(word):
    """
    Get case and number for word with pymorphy2
    
    Returns 
    -------
    tags: case, number
    """
    word_current = morph.parse(word)[0]
    case = word_current.tag.case
    number = word_current.tag.number
    return case, number


def set_tags(word, case, number):
    """
    Set case and number for word with pymorphy2
    
    Returns 
    -------
    word: with new case and number
    """
    synonym = morph.parse(word)[0]
    word_inflect = synonym.inflect({case})
    return word_inflect.word


def inflect_as(word_current, word_target):
    """
    Inflect target wordы like as current
    
    Returns 
    -------
    string new words with target case and number
    """
    case, number = get_tags(word_current)
    result = []
    for word in word_target.split(' '):
        try:
            word_inflect = set_tags(word, case, number)
            result.append(word_inflect)
        except BaseException:
            result.append(word)
    return ' '.join(result)
    
def get_synonyms(word):
    """
    Get word 
    
    Return 
    ------
    One random synonym
    """
    synonyms = [s.name for ss in wn[word][0].synset.hypernyms for s in ss.senses]
    synonym = np.random.choice(synonyms)
    return synonym.lower()

def get_similarity_embedding(word):
    """
    Get word 
    
    Return 
    ------
    One similarity embedding 
    [gensim : ruwikiruscorpora_upos_cbow_300_20_2017.bin.gz]
    """
    POS = morph.parse(word)[0].tag.POS
    synonyms = model.most_similar(word +'_'+POS)
    return synonyms[np.random.randint(0,9)][0].split('_')[0]

def ruwordnet_augmentation(text, model='RuWordNet', N=5):
    """
    Receives an sentence and N 

    Return 
    ------
    Sentences with like cases and number
    """
    result = []
    doc = nlp(text)
    
    for _ in range(N):
        paraphrases = []
        
        for word in doc:
            try:
                lemma = word.lemma_.replace('ё', 'е')
                
                if model == 'RuWordNet':
                    synonym = get_synonyms(lemma)
                elif model == 'Word2Vec':
                    synonym = get_similarity_embedding(lemma)

                synonym_inflect = inflect_as(word.text, synonym)
                paraphrases.append(synonym_inflect)
                
            except KeyError:
                paraphrases.append(word.text)
                
        result.append(' '.join(paraphrases))

    return list(set(result))

option = st.sidebar.selectbox('Which model will be use?',('RuWordNet', 'Word2Vec'))
limit = st.number_input('Limit: ', min_value=1, max_value=30, value=10)
text = st.text_area(label='Input text here', value='веселый молочник', height=200)

if st.button("Process"):
    st.write(ruwordnet_augmentation(text, model=option, N=limit))
