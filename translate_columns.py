import sqlite3
from deep_translator import GoogleTranslator
import json
import time
from datetime import datetime
import sys

def translate_text(text, source_lang='it', target_lang='en'):
    if not text or text.strip() == '':
        return text
    
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        time.sleep(1)  # Dodajemy opóźnienie, aby nie przekroczyć limitu zapytań
        return translated
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

def translate_column(column_name):
    if column_name not in ['name', 'neighborhood_overview', 'host_about']:
        print(f"Error: Column {column_name} is not supported.")
        print("Supported columns: name, neighborhood_overview, host_about")
        return
        
    conn = sqlite3.connect('airbnb.db')
    cursor = conn.cursor()
    
    # Dodaj nową kolumnę dla przetłumaczonego tekstu
    new_column = f"{column_name}_en"
    try:
        cursor.execute(f"ALTER TABLE truncated_listings ADD COLUMN {new_column} TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        print(f"Column {new_column} already exists")
    
    print(f"\nProcessing column: {column_name}")
    
    # Pobierz tylko niepuste wiersze, które nie były jeszcze przetłumaczone
    query = f"""
        SELECT id, {column_name} 
        FROM truncated_listings 
        WHERE {column_name} IS NOT NULL 
        AND {column_name} != '' 
        AND ({column_name}_en IS NULL OR {column_name}_en = '')
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    
    total_rows = len(rows)
    if total_rows == 0:
        print(f"No untranslated rows found for {column_name}")
        return
        
    print(f"Found {total_rows} rows to translate")
    start_time = datetime.now()
    
    for i, (listing_id, text) in enumerate(rows, 1):
        # Oblicz szacowany czas pozostały
        if i > 1:
            elapsed_time = (datetime.now() - start_time).total_seconds()
            avg_time_per_row = elapsed_time / (i - 1)
            remaining_rows = total_rows - i + 1
            estimated_remaining_seconds = avg_time_per_row * remaining_rows
            estimated_remaining_minutes = estimated_remaining_seconds / 60
            
            print(f"\rProcessing row {i}/{total_rows} - Estimated time remaining: {estimated_remaining_minutes:.1f} minutes", end='')
        else:
            print(f"\rProcessing row {i}/{total_rows}", end='')
        
        # Tłumacz tekst
        translated_text = translate_text(text)
        
        # Aktualizuj bazę danych
        update_query = f"UPDATE truncated_listings SET {column_name}_en = ? WHERE id = ?"
        cursor.execute(update_query, [translated_text, listing_id])
        conn.commit()
    
    print(f"\nFinished translating {column_name}")
    elapsed_time = (datetime.now() - start_time).total_seconds() / 60
    print(f"Time taken: {elapsed_time:.1f} minutes")

    conn.close()
    print("\nTranslation completed!")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python translate_columns.py <column_name>")
        print("Supported columns: name, neighborhood_overview, host_about")
        sys.exit(1)
        
    column_name = sys.argv[1]
    translate_column(column_name)
