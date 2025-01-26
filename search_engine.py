import sqlite3
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# Download required NLTK data
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
        """Initialize search engine with specified similarity measure
        Available measures: 'cosine', 'jaccard', 'dice'"""
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
        """Map POS tag to first character lemmatize() accepts"""
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {
            "J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV
        }
        return tag_dict.get(tag, wordnet.NOUN)
    
    def process_text(self, text):
        """Process text using sophisticated NLP techniques"""
        if not text:
            return ""
            
        # Tokenize and convert to lowercase
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphanumeric tokens
        tokens = [token for token in tokens if token.isalnum() and token not in self.stop_words]
        
        # Lemmatize with correct POS tag
        processed = [self.lemmatizer.lemmatize(token, self._get_wordnet_pos(token)) for token in tokens]
        
        return " ".join(processed)
    
    def _initialize(self):
        """Load and preprocess all listing names from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all listings with their tokenized names
        cursor.execute('''
            SELECT id, name_tokens, name_en 
            FROM truncated_listings 
            WHERE name_tokens IS NOT NULL
        ''')
        listings = cursor.fetchall()
        conn.close()
        
        # Store listing IDs and names
        self.listing_ids = []
        self.processed_names = []
        self.original_names = []
        
        for listing_id, tokens, original_name in listings:
            if tokens:  # Only include listings with valid tokens
                self.listing_ids.append(listing_id)
                self.processed_names.append(tokens.replace('|', ' '))  # Convert pipe-separated tokens to space-separated
                self.original_names.append(original_name)
        
        # Calculate TF-IDF matrix
        self.vectorizer = TfidfVectorizer(lowercase=True, norm=None)  # Disable L2 normalization
        self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_names)

    def calculate_similarities(self, query_vector, doc_vector):
        """Calculate all similarity measures for a given query and document vector"""
        # Convert sparse vectors to dense arrays
        q = query_vector.toarray().flatten()
        d = doc_vector.toarray().flatten()
        
        # Helper calculations
        dot_product = np.sum(q * d)
        q_magnitude = np.sum(q * q)  # |q|^2
        d_magnitude = np.sum(d * d)  # |d|^2
        
        # Cosine similarity
        mianownik_cosine = np.sqrt(q_magnitude) * np.sqrt(d_magnitude)
        cosine = dot_product / mianownik_cosine if mianownik_cosine > 0 else 0
        
        # Dice similarity (different from cosine!)
        # Dice = (2 * dot_product) / (|q|^2 + |d|^2)
        mianownik_dice = q_magnitude + d_magnitude
        dice = (2.0 * dot_product) / mianownik_dice if mianownik_dice > 0 else 0
        
        # Jaccard similarity
        # Jaccard = dot_product / (|q|^2 + |d|^2 - dot_product)
        mianownik_jaccard = q_magnitude + d_magnitude - dot_product
        jaccard = dot_product / mianownik_jaccard if mianownik_jaccard > 0 else 0
        
        return {
            'dice': round(dice, 4),
            'jaccard': round(jaccard, 4),
            'cosine': round(cosine, 4)
        }

    def search(self, query, top_k=10):
        """Search for listings similar to the query"""
        # Process query using the same sophisticated processing as listings
        processed_query = self.process_text(query)
        
        # Convert query to TF-IDF vector
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculate similarities for all documents
        results = []
        for idx in range(self.tfidf_matrix.shape[0]):
            doc_vector = self.tfidf_matrix[idx]
            similarities = self.calculate_similarities(query_vector, doc_vector)
            
            # Use the selected similarity measure for ranking
            similarity_score = similarities[self.similarity_measure]
            
            # Only include results with non-zero similarity
            if similarity_score > 0:
                results.append({
                    'listing_id': self.listing_ids[idx],
                    'name': self.original_names[idx],
                    'similarity_score': similarity_score,
                    'all_similarities': similarities
                })
        
        # Sort by similarity score and return top k results
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]