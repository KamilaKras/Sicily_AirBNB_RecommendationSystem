import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from lemmatize_names import process_text

class SearchEngine:
    def __init__(self, db_path='airbnb.db'):
        self.db_path = db_path
        self.vectorizer = None
        self.listing_ids = []
        self.processed_names = []
        self.original_names = []
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
        
        # Calculate TF-IDF only for the database names
        self.vectorizer = TfidfVectorizer(
            lowercase=True,  # This won't affect our texts as they're already processed
            token_pattern=r'\S+'  # Match any non-whitespace characters
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_names)
    
    def process_query(self, query):
        """Process user query the same way as database names but without TF-IDF"""
        tokens = process_text(query)
        return tokens
    
    def get_feature_names(self):
        """Get all terms in the vocabulary with their indices"""
        return self.vectorizer.get_feature_names_out()
    
    def get_tfidf_scores(self, listing_idx):
        """Get TF-IDF scores for a specific listing"""
        feature_names = self.get_feature_names()
        scores = self.tfidf_matrix[listing_idx].toarray()[0]
        
        # Create a dictionary of term -> score, excluding zero scores
        term_scores = {}
        for term, score in zip(feature_names, scores):
            if score > 0:
                term_scores[term] = score
        
        return term_scores

def main():
    # Initialize search engine
    search_engine = SearchEngine()
    
    print("\nWelcome to the Airbnb Search Engine!")
    print("Enter your search query (or 'quit' to exit):")
    
    while True:
        query = input("\nSearch query: ").strip()
        
        if query.lower() == 'quit':
            break
        
        if not query:
            print("Please enter a valid search query.")
            continue
        
        # Process the query
        processed_query = search_engine.process_query(query)
        print(f"\nProcessed query tokens: {processed_query}")
        
        # Show TF-IDF scores for first 5 listings as an example
        print("\nTF-IDF scores for first 5 listings:")
        for idx in range(min(5, len(search_engine.listing_ids))):
            listing_id = search_engine.listing_ids[idx]
            original_name = search_engine.original_names[idx]
            processed_name = search_engine.processed_names[idx]
            term_scores = search_engine.get_tfidf_scores(idx)
            
            print(f"\nListing ID: {listing_id}")
            print(f"Original name: {original_name}")
            print(f"Processed name: {processed_name}")
            print("Term scores:")
            for term, score in sorted(term_scores.items(), key=lambda x: x[1], reverse=True):
                print(f"  {term}: {score:.4f}")

if __name__ == '__main__':
    main()
