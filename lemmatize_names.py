import nltk
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
nltk.download('stopwords')

def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)

def process_text(text):
    """Process text in order: tokenize -> remove stop words -> lemmatize"""
    if not text:
        return []
    
    # 1. Tokenize and convert to lowercase
    tokens = word_tokenize(text.lower())
    
    # 2. Remove stop words and non-alphanumeric tokens
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
    
    # 3. Lemmatize
    lemmatizer = WordNetLemmatizer()
    processed_tokens = []
    
    for token in tokens:
        pos = get_wordnet_pos(token)
        lemma = lemmatizer.lemmatize(token, pos=pos)
        processed_tokens.append(lemma)
    
    return processed_tokens

if __name__ == '__main__':
    test_names = [
        "Beautiful Houses with Gardens",
        "Cozy Villa & Swimming Pool",
        "Modern Apartments near Beach!"
    ]
    
    for name in test_names:
        tokens = process_text(name)
        print(f"\nOriginal: {name}")
        print(f"Tokens: {tokens}")
