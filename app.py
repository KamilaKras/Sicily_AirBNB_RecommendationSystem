from flask import Flask, render_template, request, jsonify, url_for
from search_engine import SearchEngine
import os
import json
import sqlite3

app = Flask(__name__)
search_engine = SearchEngine()

def get_db_connection():
    conn = sqlite3.connect('airbnb.db')
    return conn

def get_filter_options():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get unique values for each filter
    filters = {
        'host_response_time': [],
        'neighbourhood_cleansed': [],
        'property_type': [],
        'room_type': [],
        'amenities': []
    }
    
    for column in filters.keys():
        if column != 'amenities':
            cursor.execute(f'SELECT DISTINCT {column} FROM truncated_listings WHERE {column} IS NOT NULL')
            filters[column] = sorted([row[0] for row in cursor.fetchall()])
        else:
            # For amenities, get the most common ones
            cursor.execute('SELECT amenities FROM truncated_listings LIMIT 1')
            sample_amenities = json.loads(cursor.fetchone()[0])
            filters['amenities'] = sorted(list(set(sample_amenities))[:20])  # Take top 20 amenities and sort them
    
    # Get min and max values for numeric fields
    numeric_ranges = {}
    
    # Handle price separately since it's stored as text with decimal points
    cursor.execute('SELECT MIN(CAST(REPLACE(price, ".","") AS INTEGER)), MAX(CAST(REPLACE(price, ".","") AS INTEGER)) FROM truncated_listings WHERE price IS NOT NULL')
    min_price, max_price = cursor.fetchone()
    numeric_ranges['price'] = {'min': float(min_price)/100 if min_price else 0, 'max': float(max_price)/100 if max_price else 1000}
    
    # Handle other numeric fields
    for field in ['review_scores_rating', 'accommodates', 'bedrooms', 'beds']:
        cursor.execute(f'SELECT MIN({field}), MAX({field}) FROM truncated_listings WHERE {field} IS NOT NULL')
        min_val, max_val = cursor.fetchone()
        numeric_ranges[field] = {'min': min_val, 'max': max_val}
    
    conn.close()
    return filters, numeric_ranges

@app.route('/')
def index():
    filters, numeric_ranges = get_filter_options()
    similarity_metrics = ['cosine', 'jaccard', 'dice', 'product']
    
    # Use absolute path for photos directory
    photos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'Sicily_photo')
    
    # Create the directory if it doesn't exist
    if not os.path.exists(photos_dir):
        os.makedirs(photos_dir)
    
    # Get list of photos if any exist, otherwise use an empty list
    try:
        photo_files = [f for f in os.listdir(photos_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    except Exception as e:
        print(f"Error reading photos directory: {e}")
        photo_files = []
    
    return render_template('index.html', 
                         filters=filters, 
                         numeric_ranges=numeric_ranges,
                         similarity_metrics=similarity_metrics,
                         photos=photo_files)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    filters = data.get('filters', {})
    
    # Update search engine similarity measure if provided
    similarity_metric = filters.get('similarity_metric', 'cosine')
    if similarity_metric != search_engine.similarity_measure:
        search_engine.similarity_measure = similarity_metric
    
    # Perform the search
    results = search_engine.search(query)
    
    # Apply filters to results
    filtered_results = []
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for result in results:
        listing_id = result['listing_id']
        similarity_score = result['similarity_score']
        
        # Build dynamic query based on filters
        query_conditions = ['id = ?']
        query_params = [listing_id]
        
        for key, value in filters.items():
            if key == 'similarity_metric':
                continue
            
            if key.endswith('_range'):
                field = key[:-6]  # Remove '_range' suffix
                min_val, max_val = value
                if field == 'price':
                    # Special handling for price since it's stored as text
                    if min_val is not None:
                        query_conditions.append(f'CAST(REPLACE(price, ".", "") AS INTEGER) >= ?')
                        query_params.append(int(float(min_val) * 100))
                    if max_val is not None:
                        query_conditions.append(f'CAST(REPLACE(price, ".", "") AS INTEGER) <= ?')
                        query_params.append(int(float(max_val) * 100))
                else:
                    if min_val is not None:
                        query_conditions.append(f'{field} >= ?')
                        query_params.append(min_val)
                    if max_val is not None:
                        query_conditions.append(f'{field} <= ?')
                        query_params.append(max_val)
            elif value:
                if key == 'amenities':
                    # Handle amenities separately as they're stored as JSON
                    amenities_conditions = []
                    for amenity in value:
                        amenities_conditions.append(f"json_array_contains(amenities, ?)")
                        query_params.append(amenity)
                    if amenities_conditions:
                        query_conditions.append(f"({' AND '.join(amenities_conditions)})")
                else:
                    query_conditions.append(f'{key} = ?')
                    query_params.append(value)
        
        # Execute query
        query = f'''
            SELECT id, name, host_response_time, neighbourhood_cleansed, 
                   property_type, room_type, accommodates, bathrooms_text, 
                   bedrooms, beds, amenities, review_scores_rating, price,
                   listing_url, description_en, neighborhood_overview,
                   minimum_nights, maximum_nights,
                   host_name, host_since, host_location, host_about,
                   host_response_time, host_response_rate, host_acceptance_rate,
                   host_is_superhost, host_listings_count, host_identity_verified,
                   number_of_reviews, review_scores_accuracy, review_scores_cleanliness,
                   review_scores_checkin, review_scores_communication,
                   review_scores_location, review_scores_value
            FROM truncated_listings 
            WHERE {" AND ".join(query_conditions)}
        '''
        cursor.execute(query, query_params)
        listing = cursor.fetchone()
        
        if listing:
            # Create a default image URL using the Sicily photo
            default_image_url = url_for('static', filename='Sicily_photo/Sicily_photo.jpg')
            
            filtered_results.append({
                'id': listing[0],
                'name': listing[1],
                'host_response_time': listing[2],
                'neighbourhood': listing[3],
                'property_type': listing[4],
                'room_type': listing[5],
                'accommodates': listing[6],
                'bathrooms': listing[7],
                'bedrooms': listing[8],
                'beds': listing[9],
                'amenities': json.loads(listing[10]),
                'review_scores_rating': listing[11],
                'price': f"€{listing[12]} per night",  # Add currency symbol and clarify it's per night
                'listing_url': listing[13],
                'description': listing[14] or "No English description available.",  # Use description_en and provide fallback text
                'neighborhood_overview': listing[15],
                'minimum_nights': listing[16],
                'maximum_nights': listing[17],
                'host_name': listing[18],
                'host_since': listing[19],
                'host_location': listing[20],
                'host_about': listing[21],
                'host_response_time': listing[22],
                'host_response_rate': listing[23],
                'host_acceptance_rate': listing[24],
                'host_is_superhost': listing[25],
                'host_listings_count': listing[26],
                'host_identity_verified': listing[27],
                'number_of_reviews': listing[28],
                'review_scores_accuracy': listing[29],
                'review_scores_cleanliness': listing[30],
                'review_scores_checkin': listing[31],
                'review_scores_communication': listing[32],
                'review_scores_location': listing[33],
                'review_scores_value': listing[34],
                'picture_url': default_image_url,  # Use the default image
                'similarity_score': similarity_score
            })
    
    conn.close()
    return jsonify(filtered_results)

@app.route('/statistics')
def statistics():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Generate word cloud if it doesn't exist
    if not os.path.exists('static/data/wordcloud_data.json'):
        from generate_wordcloud import generate_wordcloud
        generate_wordcloud()

    # Get database statistics
    cursor.execute("SELECT COUNT(*) FROM truncated_listings")
    total_rows = cursor.fetchone()[0]

    cursor.execute("PRAGMA table_info(truncated_listings)")
    total_columns = len(cursor.fetchall())

    # Get price data
    cursor.execute("SELECT price FROM truncated_listings WHERE price < 1000")
    prices = [row[0] for row in cursor.fetchall()]

    # Get property types
    cursor.execute("""
        SELECT property_type, COUNT(*) as count 
        FROM truncated_listings 
        GROUP BY property_type 
        ORDER BY count DESC 
        LIMIT 10
    """)
    property_types_data = cursor.fetchall()
    property_types = [row[0] for row in property_types_data]
    property_type_counts = [row[1] for row in property_types_data]

    # Get room types
    cursor.execute("""
        SELECT room_type, COUNT(*) as count 
        FROM truncated_listings 
        GROUP BY room_type
    """)
    room_types_data = cursor.fetchall()
    room_types = [row[0] for row in room_types_data]
    room_type_counts = [row[1] for row in room_types_data]

    # Get top amenities
    cursor.execute("""
        SELECT amenities, COUNT(*) as count 
        FROM truncated_listings 
        GROUP BY amenities 
        ORDER BY count DESC 
        LIMIT 15
    """)
    amenities_data = cursor.fetchall()
    amenities = [row[0] for row in amenities_data]
    amenity_counts = [row[1] for row in amenities_data]

    conn.close()

    data = {
        'total_rows': total_rows,
        'total_columns': total_columns,
        'prices': prices,
        'propertyTypes': property_types,
        'propertyTypeCounts': property_type_counts,
        'roomTypes': room_types,
        'roomTypeCounts': room_type_counts,
        'topAmenities': amenities,
        'amenityCounts': amenity_counts
    }

    return render_template('statistics.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)