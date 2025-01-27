from flask import Flask, render_template, request, jsonify, url_for
from search_engine import SearchEngine
import os
import json
import sqlite3

# Inicjalizacja aplikacji Flask i wyszukiwania
app = Flask(__name__)
app.config['DATABASE'] = 'airbnb.db'

# Inicjalizacja silnika wyszukiwania
search_engine = SearchEngine('airbnb.db')

#połączenie z bazą danych
def get_db_connection():
    conn = sqlite3.connect('airbnb.db')
    conn.row_factory = sqlite3.Row
    return conn

# Funkcja pobierająca opcje filtrów z bazy danych
def get_filter_options():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Pobranie unikalnych wartości dla każdego filtra
    filters = {
        'host_response_time': [],
        'neighbourhood_cleansed': [],
        'property_type': [],
        'room_type': [],
        'amenities': {}
    }
    # Iteracja po każdej kolumnie filtrów
    for column in filters.keys():
        if column != 'amenities':
            cursor.execute(f'SELECT DISTINCT {column} FROM truncated_listings WHERE {column} IS NOT NULL')
            filters[column] = sorted([row[0] for row in cursor.fetchall()])
        else:
            # Dla udogodnień, pobierz wszystkie unikalne udogodnienia i ich częstotliwość
            cursor.execute('SELECT amenities FROM truncated_listings WHERE amenities IS NOT NULL')
            all_amenities = {}
            for row in cursor.fetchall():
                amenities = json.loads(row[0])
                for amenity in amenities:
                    all_amenities[amenity] = all_amenities.get(amenity, 0) + 1
            
            # Filtrowanie udogodnień, które pojawiają się w więcej niż 12000 ofertach
            common_amenities = [(amenity, count) for amenity, count in all_amenities.items() if count > 12000]
            filters['amenities'] = sorted([amenity for amenity, _ in common_amenities])
    
    # Pobranie minimalnych i maksymalnych wartości dla pól numerycznych
    numeric_ranges = {}
    
    # Osobna obsługa ceny, ponieważ jest przechowywana jako tekst z punktami dziesiętnymi
    cursor.execute('SELECT MIN(CAST(REPLACE(price, ".","") AS INTEGER)), MAX(CAST(REPLACE(price, ".","") AS INTEGER)) FROM truncated_listings WHERE price IS NOT NULL')
    min_price, max_price = cursor.fetchone()
    numeric_ranges['price'] = {'min': float(min_price)/100 if min_price else 0, 'max': float(max_price)/100 if max_price else 1000}
    
    # Obsługa pozostałych pól numerycznych
    for field in ['review_scores_rating', 'accommodates', 'bedrooms', 'beds']:
        cursor.execute(f'SELECT MIN({field}), MAX({field}) FROM truncated_listings WHERE {field} IS NOT NULL')
        min_val, max_val = cursor.fetchone()
        numeric_ranges[field] = {'min': min_val, 'max': max_val}
    
    conn.close()
    return filters, numeric_ranges

# Strona główna aplikacji
@app.route('/')
def index():
    # Pobranie opcji filtrów i zakresów numerycznych
    filters, numeric_ranges = get_filter_options()
    similarity_metrics = ['cosine', 'jaccard', 'dice']
    
    photos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'Sicily_photo')
    
    if not os.path.exists(photos_dir):
        os.makedirs(photos_dir)
    
    try:
        photo_files = [f for f in os.listdir(photos_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    except Exception as e:
        print(f"Błąd odczytu katalogu ze zdjęciami: {e}")
        photo_files = []
    
    return render_template('index.html', 
                         filters=filters, 
                         numeric_ranges=numeric_ranges,
                         similarity_metrics=similarity_metrics,
                         photos=photo_files)

# Funkcja obsługująca wyszukiwanie
@app.route('/search', methods=['POST'])
def search():
    # Pobranie danych z żądania
    data = request.get_json()
    query = data.get('query', '')
    filters = data.get('filters', {})
    print(f"Debug - Received filters: {filters}")
    
    # Aktualizacja miary podobieństwa
    similarity_metric = filters.get('similarity_metric', 'cosine')
    if similarity_metric != search_engine.similarity_measure:
        search_engine.similarity_measure = similarity_metric
    
    results = search_engine.search(query)
    
    filtered_results = []
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for result in results:
        listing_id = result['listing_id']
        similarity_score = result['similarity_score']
        
        query_conditions = ["1=1"]  # Zawsze prawdziwy warunek jako początek
        query_params = []
        
        if listing_id:
            query_conditions.append("id = ?")
            query_params.append(listing_id)
            
        if 'price_range' in filters:
            price_min, price_max = filters['price_range']
            if price_min is not None:
                query_conditions.append("CAST(REPLACE(REPLACE(price, '€', ''), ',', '') AS DECIMAL) >= ?")
                query_params.append(price_min)
                
            if price_max is not None:
                query_conditions.append("CAST(REPLACE(REPLACE(price, '€', ''), ',', '') AS DECIMAL) <= ?")
                query_params.append(price_max)
                
        if 'min_reviews' in filters:
            min_reviews = filters['min_reviews']
            if min_reviews is not None:
                query_conditions.append("number_of_reviews >= ?")
                query_params.append(min_reviews)
                
        if 'accommodates_range' in filters:
            accommodates_min, accommodates_max = filters['accommodates_range']
            if accommodates_min is not None:
                query_conditions.append("accommodates >= ?")
                query_params.append(accommodates_min)
                
            if accommodates_max is not None:
                query_conditions.append("accommodates <= ?")
                query_params.append(accommodates_max)
                
        if 'bedrooms_range' in filters:
            bedrooms_min, bedrooms_max = filters['bedrooms_range']
            if bedrooms_min is not None:
                query_conditions.append("bedrooms >= ?")
                query_params.append(bedrooms_min)
                
            if bedrooms_max is not None:
                query_conditions.append("bedrooms <= ?")
                query_params.append(bedrooms_max)
                
        if 'beds_range' in filters:
            beds_min, beds_max = filters['beds_range']
            if beds_min is not None:
                query_conditions.append("beds >= ?")
                query_params.append(beds_min)
                
            if beds_max is not None:
                query_conditions.append("beds <= ?")
                query_params.append(beds_max)
                
        if 'room_type' in filters:
            room_type = filters['room_type']
            query_conditions.append("room_type = ?")
            query_params.append(room_type)
            
        if 'property_type' in filters:
            property_type = filters['property_type']
            query_conditions.append("property_type = ?")
            query_params.append(property_type)
            
        if 'neighbourhood_cleansed' in filters:
            neighbourhood = filters['neighbourhood_cleansed']
            query_conditions.append("neighbourhood_cleansed = ?")
            query_params.append(neighbourhood)
            
        if 'amenities' in filters:
            amenities = filters['amenities']
            for amenity in amenities:
                query_conditions.append("amenities LIKE ?")
                query_params.append(f"%{amenity}%")
                
        if 'host_response_time' in filters:
            host_response_time = filters['host_response_time']
            query_conditions.append("host_response_time = ?")
            query_params.append(host_response_time)
            
        if 'superhost' in filters:
            superhost = filters['superhost']
            value = 't' if superhost else 'f'
            query_conditions.append("host_is_superhost = ?")
            query_params.append(value)
            
        if 'review_scores_rating_range' in filters:
            min_rating, max_rating = filters['review_scores_rating_range']
            print(f"Debug - Review Rating Filter: min={min_rating}, max={max_rating}")
            if min_rating is not None:
                query_conditions.append("COALESCE(review_scores_rating, 0) >= ?")
                query_params.append(float(min_rating))  # Upewniamy się, że to float
            if max_rating is not None:
                query_conditions.append("COALESCE(review_scores_rating, 0) <= ?")
                query_params.append(float(max_rating))  # Upewniamy się, że to float
        query = f'''
            SELECT id, listing_url, name, description, neighborhood_overview,
                   host_name, host_since, host_location, host_about,
                   host_response_time, host_response_rate, host_acceptance_rate,
                   host_is_superhost, host_listings_count, host_identity_verified,
                   neighbourhood_cleansed, property_type, room_type, accommodates,
                   bathrooms_text, bedrooms, beds, amenities, price,
                   minimum_nights, maximum_nights, number_of_reviews,
                   review_scores_rating, review_scores_accuracy, review_scores_cleanliness,
                   review_scores_checkin, review_scores_communication,
                   review_scores_location, review_scores_value,
                   description_en, neighborhood_overview_en, name_en, host_about_en
            FROM truncated_listings 
            WHERE {" AND ".join(query_conditions)}
        '''
        print(f"Debug - SQL Query: {query}")
        print(f"Debug - Query params: {query_params}")
        cursor.execute(query, query_params)
        listing = cursor.fetchone()
        
        if listing:
            print(f"Debug - Review scores rating from DB: {listing[27]}")
            default_image_url = url_for('static', filename='Sicily_photo/Sicily_photo.jpg')
            
            def safe_float_convert(value):
                if value is None:
                    return None
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str) and value.replace('.', '').isdigit():
                    return float(value)
                return None

            filtered_results.append({
                'id': listing[0],
                'name': listing[36],  # name_en
                'host_response_time': listing[9],
                'neighbourhood': listing[15],
                'property_type': listing[16],
                'room_type': listing[17],
                'accommodates': listing[18],
                'bathrooms': listing[19],
                'bedrooms': listing[20],
                'beds': listing[21],
                'amenities': json.loads(listing[22]),
                'review_scores_rating': listing[27],
                'price': f"€{listing[23]} per night",
                'listing_url': listing[1],
                'description': listing[34] or "No description",  # description_en
                'neighborhood_overview': listing[35] or "No neighborhood overview",  # neighborhood_overview_en
                'host_about': listing[37] or "No host information",  # host_about_en
                'minimum_nights': listing[24],
                'maximum_nights': listing[25],
                'host_name': listing[5],
                'host_since': listing[6],
                'host_location': listing[7],
                'host_response_time': listing[9],
                'host_response_rate': listing[10],
                'host_acceptance_rate': listing[11],
                'host_is_superhost': listing[12],
                'host_listings_count': listing[13],
                'host_identity_verified': listing[14],
                'number_of_reviews': int(listing[26]) if listing[26] is not None else 0,
                'review_scores_accuracy': listing[28],
                'review_scores_cleanliness': listing[29],
                'review_scores_checkin': listing[30],
                'review_scores_communication': listing[31],
                'review_scores_location': listing[32],
                'review_scores_value': listing[33],
                'picture_url': default_image_url,
                'similarity_score': similarity_score
            })
    conn.close()
    return jsonify(filtered_results)

# Strona statystyk
@app.route('/statistics')
def statistics():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Wygenerowanie chmury słów, jeśli nie istnieje
    if not os.path.exists('static/data/wordcloud_data.json'):
        from generate_wordcloud import generate_wordcloud
        generate_wordcloud()
    # Pobranie statystyk bazy danych
    cursor.execute("SELECT COUNT(*) FROM truncated_listings")
    total_rows = cursor.fetchone()[0]
    cursor.execute("PRAGMA table_info(truncated_listings)")
    total_columns = len(cursor.fetchall())
    conn.close()

    # Przygotowanie danych do wysłania do szablonu
    data = {
        'total_rows': total_rows,
        'total_columns': total_columns
    }
    return render_template('statistics.html', data=data)

# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)