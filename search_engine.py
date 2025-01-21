import sqlite3
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from lemmatize_names import process_text

class SearchEngine:
    def __init__(self, db_path='airbnb.db', similarity_measure='cosine'):
        """Initialize search engine with specified similarity measure
        Available measures: 'cosine', 'jaccard', 'dice', 'product'"""
        self.db_path = db_path
        self.vectorizer = None
        self.listing_ids = []
        self.processed_names = []
        self.original_names = []
        self.similarity_measure = similarity_measure
        self._initialize()
    
    def _initialize(self):
        """Load and preprocess all listing names from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all listings
        cursor.execute('SELECT id, name FROM truncated_listings WHERE name IS NOT NULL')
        listings = cursor.fetchall()
        conn.close()
        
        # Process names and store listing IDs
        self.listing_ids = []
        self.processed_names = []
        self.original_names = []
        
        for listing_id, name in listings:
            # Process the name
            tokens = process_text(name)
            if tokens:  # Only include non-empty token lists
                self.listing_ids.append(listing_id)
                self.original_names.append(name)
                self.processed_names.append(' '.join(tokens))
        
        # Calculate TF-IDF for all names
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            token_pattern=r'\S+'
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_names)
    
    def process_query(self, query):
        """Process user query the same way as database names"""
        tokens = process_text(query)
        return tokens
    
    def calculate_jaccard_similarity(self, query_vector, listing_vector):
        """Calculate Jaccard similarity using TF-IDF weights
        Formula: sum(w_i,q * w_i,j) / (sum(w_i,q^2) + sum(w_i,j^2) - sum(w_i,q * w_i,j))"""
        # Get vectors as arrays
        q = query_vector.toarray().flatten()
        d = listing_vector.toarray().flatten()
        
        # Calculate dot product (numerator)
        dot_product = np.sum(q * d)
        
        # Calculate denominator
        denominator = np.sum(q * q) + np.sum(d * d) - dot_product
        
        return dot_product / denominator if denominator > 0 else 0
    
    def calculate_dice_similarity(self, query_vector, listing_vector):
        """Calculate Dice coefficient using TF-IDF weights
        Formula: 2 * sum(w_i,q * w_i,j) / (|Q| * sum(w_i,j^2))
        where |Q| is the number of query terms"""
        # Get vectors as arrays
        q = query_vector.toarray().flatten()
        d = listing_vector.toarray().flatten()
        
        # Calculate numerator (sum of weights for matching terms)
        numerator = np.sum(q * d)
        
        # Calculate denominator
        query_term_count = np.count_nonzero(q)  # Number of query terms
        sum_squared_weights = np.sum(d * d)  # Sum of squared weights for document
        denominator = query_term_count * sum_squared_weights
        
        return 2 * numerator / denominator if denominator > 0 else 0

    def calculate_product_similarity(self, query_vector, listing_vector):
        """Calculate product similarity using TF-IDF weights
        Formula: sum(w_i,q * w_i,j)
        Simple sum of products of weights for matching terms"""
        # Get vectors as arrays
        q = query_vector.toarray().flatten()
        d = listing_vector.toarray().flatten()
        
        # Calculate dot product (sum of weight products)
        return np.sum(q * d)
    
    def search(self, query, top_k=5):
        """Search for listings similar to the query"""
        processed_query = self.process_query(query)
        
        if not processed_query:
            return []
            
        # Convert query to TF-IDF vector
        query_text = ' '.join(processed_query)
        query_vector = self.vectorizer.transform([query_text])
        
        if self.similarity_measure == 'cosine':
            # Use sklearn's optimized cosine similarity
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        else:
            # Calculate other similarities
            similarity_functions = {
                'jaccard': self.calculate_jaccard_similarity,
                'dice': self.calculate_dice_similarity,
                'product': self.calculate_product_similarity
            }
            
            similarity_func = similarity_functions.get(self.similarity_measure)
            if not similarity_func:
                raise ValueError(f"Unknown similarity measure: {self.similarity_measure}")
            
            # Calculate similarities using the selected measure
            similarities = np.array([
                similarity_func(query_vector, self.tfidf_matrix[i])
                for i in range(self.tfidf_matrix.shape[0])
            ])
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Prepare results
        results = []
        for idx in top_indices:
            results.append({
                'listing_id': self.listing_ids[idx],
                'original_name': self.original_names[idx],
                'processed_name': self.processed_names[idx],
                'similarity_score': similarities[idx]
            })
        
        return results

def main():
    # Initialize search engine with default cosine similarity
    search_engine = SearchEngine()
    
    print("\nWelcome to the Airbnb Search Engine!")
    print("Available similarity measures: 'cosine' (default), 'jaccard', 'dice', 'product'")
    
    # Get similarity measure preference
    measure = input("Enter similarity measure (or press Enter for default 'cosine'): ").strip().lower()
    if measure in ['jaccard', 'dice', 'product']:
        search_engine = SearchEngine(similarity_measure=measure)
    
    print("\nEnter your search query (or 'quit' to exit):")
    
    while True:
        query = input("\nSearch query: ").strip()
        
        if query.lower() == 'quit':
            break
        
        if not query:
            print("Please enter a valid search query.")
            continue
        
        # Process the query and get results
        results = search_engine.search(query)
        
        if not results:
            print("\nNo matching listings found.")
            continue
        
        # Display results
        print(f"\nTop {len(results)} matches:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Listing ID: {result['listing_id']}")
            print(f"Original name: {result['original_name']}")
            print(f"Processed name: {result['processed_name']}")
            print(f"Similarity score: {result['similarity_score']:.4f}")

if __name__ == '__main__':
    main()
