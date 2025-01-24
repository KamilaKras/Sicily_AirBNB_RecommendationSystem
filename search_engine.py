import sqlite3
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

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
            # Convert to lowercase and remove symbols
            processed_name = name.lower()
            for symbol in [",", ".", ":", ";", "!", "?"]:
                processed_name = processed_name.replace(symbol, "")
            
            self.listing_ids.append(listing_id)
            self.processed_names.append(processed_name)
            self.original_names.append(name)
        
        # Calculate TF-IDF matrix
        self.vectorizer = TfidfVectorizer(lowercase=True)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_names)

    def calculate_similarities(self, query_vector, doc_vector):
        """Calculate all similarity measures for a given query and document vector"""
        # Convert sparse vectors to dense arrays
        q = query_vector.toarray().flatten()
        d = doc_vector.toarray().flatten()
        
        # Helper calculations
        dot_product = np.sum(q * d)
        suma_kw_wag = np.sum(d * d)
        query_terms = np.count_nonzero(q)
        
        # Dice similarity
        mianownik_dice = query_terms * suma_kw_wag
        dice = 2 * dot_product / mianownik_dice if mianownik_dice > 0 else 0
        
        # Jaccard similarity
        mianownik_jaccard = query_terms + suma_kw_wag - dot_product
        jaccard = dot_product / mianownik_jaccard if mianownik_jaccard > 0 else 0
        
        # Cosine similarity
        mianownik_cosine = (query_terms ** 0.5) * (suma_kw_wag ** 0.5)
        cosine = dot_product / mianownik_cosine if mianownik_cosine > 0 else 0
        
        return {
            'dice': round(dice, 2),
            'jaccard': round(jaccard, 2),
            'cosine': round(cosine, 2)
        }

    def search(self, query, top_k=5):
        """Search for listings similar to the query"""
        # Process query
        query = query.lower()
        for symbol in [",", ".", ":", ";", "!", "?"]:
            query = query.replace(symbol, "")
        
        # Convert query to TF-IDF vector
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities for all documents
        results = []
        for idx in range(self.tfidf_matrix.shape[0]):
            doc_vector = self.tfidf_matrix[idx]
            similarities = self.calculate_similarities(query_vector, doc_vector)
            
            # Use the selected similarity measure for ranking
            similarity_score = similarities[self.similarity_measure]
            
            results.append({
                'listing_id': self.listing_ids[idx],
                'name': self.original_names[idx],
                'similarity_score': similarity_score,
                'all_similarities': similarities
            })
        
        # Sort by similarity score and return top k results
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]

def main():
    # Initialize search engine with default cosine similarity
    search_engine = SearchEngine()
    
    print("\nWelcome to the Airbnb Search Engine!")
    print("Available similarity measures: 'cosine' (default), 'jaccard', 'dice'")
    
    # Get similarity measure preference
    measure = input("Enter similarity measure (or press Enter for default 'cosine'): ").strip().lower()
    if measure in ['jaccard', 'dice']:
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
        
        # Display results
        print(f"\nTop {len(results)} matches:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Listing ID: {result['listing_id']}")
            print(f"Name: {result['name']}")
            print(f"Similarity score: {result['similarity_score']:.4f}")
            print(f"All similarities: {result['all_similarities']}")

if __name__ == '__main__':
    main()