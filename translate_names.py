import sqlite3
from deep_translator import GoogleTranslator
from langdetect import detect
import time
from datetime import datetime
import logging

#Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('names_translation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

#sprawdzenie czy nazwa po włosku
def is_italian(text):
    try:
        return detect(text) == 'it'
    except:
        return False

#tłumaczenie tekstu
def translate_text(text):
    if not text or text.strip() == '':
        return text
    try:
        #tlumaczenie jeżeli po włosku
        if is_italian(text):
            translator = GoogleTranslator(source='it', target='en')
            translated = translator.translate(text)
            time.sleep(1)
            return translated
        else:
            logger.info("Text not in Italian, skipping translation")
            return text
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return text

#funkcja do tłumaczenia wszystkich nazw
def translate_names():
    logger.info("Starting names translation")
    conn = sqlite3.connect('airbnb.db')
    cursor = conn.cursor()
   # Dodanie kolumny name_en
    try:
        cursor.execute("ALTER TABLE truncated_listings ADD COLUMN name_en TEXT")
        conn.commit()
        logger.info("Added name_en column")
    except sqlite3.OperationalError:
        logger.info("Column name_en already exists")
    
    # Pobranie nieprzetłumaczonych wierszy
    cursor.execute("""
        SELECT id, name 
        FROM truncated_listings 
        WHERE name IS NOT NULL 
        AND name != '' 
        AND (name_en IS NULL OR name_en = '')
    """)
    rows = cursor.fetchall()
    
    total = len(rows)
    logger.info(f"Found {total} names to translate")
    
    start_time = datetime.now()
    for i, (id, text) in enumerate(rows, 1):
        try:
            #Pokazywanie postępu
            if i > 1:
                elapsed = (datetime.now() - start_time).total_seconds()
                avg_time = elapsed / (i - 1)
                remaining = total - i + 1
                est_minutes = (avg_time * remaining) / 60
                logger.info(f"Progress: {i}/{total} - Est. remaining: {est_minutes:.1f} min")
            else:
                logger.info(f"Progress: {i}/{total}")
            # Tłumaczenie i aktualizacja
            translated = translate_text(text)
            cursor.execute("UPDATE truncated_listings SET name_en = ? WHERE id = ?", 
                          [translated, id])
            conn.commit()
        except Exception as e:
            logger.error(f"Error processing row {id}: {e}")
            continue
    elapsed = (datetime.now() - start_time).total_seconds() / 60
    logger.info(f"Finished! Time taken: {elapsed:.1f} minutes")
    conn.close()

if __name__ == '__main__':
    try:
        translate_names()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise