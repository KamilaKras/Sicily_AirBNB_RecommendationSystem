import sqlite3
from datetime import datetime
import pandas as pd

#czytanie z plikow csv
print("Reading CSV files...")
selected_columns = [
    'id', 'listing_url', 'name', 'description', 'neighborhood_overview',
    'host_name', 'host_since', 'host_location', 'host_about',
    'host_response_time', 'host_response_rate', 'host_acceptance_rate',
    'host_is_superhost', 'host_listings_count', 'host_identity_verified',
    'neighbourhood_cleansed', 'property_type',
    'room_type', 'accommodates', 'bathrooms_text', 'bedrooms', 'beds',
    'amenities', 'price', 'minimum_nights', 'maximum_nights',
    'number_of_reviews', 'review_scores_rating', 'review_scores_accuracy',
    'review_scores_cleanliness', 'review_scores_checkin',
    'review_scores_communication', 'review_scores_location',
    'review_scores_value'
]
listings_df = pd.read_csv('listings.csv', usecols=selected_columns)

#tworzenie bazy danych
print("Creating SQLite database...")
conn = sqlite3.connect('airbnb.db')

#zamiana na sql
print("Converting listings to SQL...")
listings_df.to_sql('listings', conn, if_exists='replace', index=False)

#TWORZENIE INDEXOW
print("Creating indexes...")
conn.execute('CREATE INDEX IF NOT EXISTS idx_listings_id ON listings(id)')

# Zamkniecie połączenia
conn.close()
print("Conversion completed successfully!")
