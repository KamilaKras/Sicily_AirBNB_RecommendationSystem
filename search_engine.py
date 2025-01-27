import sqlite3
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# pobranie paczek nltk
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

class SearchEngine:
    def __init__(self, db_path='airbnb.db', similarity_measure='cosine'):
        self.db_path = db_path
        self.vectorizer = None
        self.listing_ids = []
        self.processed_names = []
        self.original_names = []
        self.similarity_measure = similarity_measure
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self._initialize()
    
    def _get_wordnet_pos(self, word):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {
            "J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV
        }
        return tag_dict.get(tag, wordnet.NOUN)
    
    def process_text(self, text):
        if not text:
            return ""
        tokens = word_tokenize(text.lower())
        tokens = [token for token in tokens if token.isalnum() and token not in self.stop_words]
        processed = [self.lemmatizer.lemmatize(token, self._get_wordnet_pos(token)) for token in tokens]
        return " ".join(processed)
    
    def _initialize(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name_tokens, name_en 
            FROM truncated_listings 
            WHERE name_tokens IS NOT NULL
        ''')
        listings = cursor.fetchall()
        conn.close()
        
        self.listing_ids = []
        self.processed_names = []
        self.original_names = []
        
        for listing_id, tokens, original_name in listings:
            if tokens:
                self.listing_ids.append(listing_id)
                self.processed_names.append(tokens.replace('|', ' '))
                self.original_names.append(original_name)
        
        self.vectorizer = TfidfVectorizer(lowercase=True, norm=None)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_names)

    def calculate_similarities(self, query_vector, doc_vector):
        q = query_vector.toarray().flatten()
        d = doc_vector.toarray().flatten()
        
        dot_product = np.sum(q * d)
        q_magnitude = np.sum(q * q)
        d_magnitude = np.sum(d * d)
        
        # maiara cosinusa
        mianownik_cosine = np.sqrt(q_magnitude) * np.sqrt(d_magnitude)
        cosine = dot_product / mianownik_cosine if mianownik_cosine > 0 else 0
        
        #DICE
        mianownik_dice = q_magnitude + d_magnitude
        dice = (2.0 * dot_product) / mianownik_dice if mianownik_dice > 0 else 0
        
        # Jaccard
        mianownik_jaccard = q_magnitude + d_magnitude - dot_product
        jaccard = dot_product / mianownik_jaccard if mianownik_jaccard > 0 else 0
        
        return {
            'dice': round(dice, 4),
            'jaccard': round(jaccard, 4),
            'cosine': round(cosine, 4)
        }

    def search(self, query, top_k=20):
        processed_query = self.process_text(query)
        query_vector = self.vectorizer.transform([processed_query])
        
        results = []
        for idx in range(self.tfidf_matrix.shape[0]):
            doc_vector = self.tfidf_matrix[idx]
            similarities = self.calculate_similarities(query_vector, doc_vector)
            
            similarity_score = similarities[self.similarity_measure]
            if similarity_score > 0:
                results.append({
                    'listing_id': self.listing_ids[idx],
                    'name': self.original_names[idx],
                    'similarity_score': similarity_score,
                    'all_similarities': similarities
                })
        
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return {
            'total_matches': len(results),
            'results': results[:top_k]
        }