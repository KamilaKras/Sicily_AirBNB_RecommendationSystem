from search_engine import SearchEngine

def test_search():
    se = SearchEngine()
    query = "beautiful beach apartment with sea view"
    results = se.search(query, top_k=3)
    
    print(f"\nWyszukiwanie dla zapytania: '{query}'")
    print("\nWyniki wyszukiwania:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['name']}")
        print(f"Similarity scores: {result['all_similarities']}")

if __name__ == '__main__':
    test_search()
