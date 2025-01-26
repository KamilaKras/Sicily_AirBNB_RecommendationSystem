from deep_translator import GoogleTranslator
from langdetect import detect
import sqlite3
import time
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_untranslated_descriptions(cursor, batch_size=100):
    cursor.execute("""
        SELECT id, description 
        FROM truncated_listings 
        WHERE description_en IS NULL 
        AND description IS NOT NULL 
        LIMIT ?
    """, (batch_size,))
    return cursor.fetchall()

def is_italian(text):
    try:
        return detect(text) == 'it'
    except:
        return False

def translate_text(text):
    try:
        translator = GoogleTranslator(source='it', target='en')
        return translator.translate(text)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return None

def update_database_translations():
    conn = sqlite3.connect('airbnb.db')
    cursor = conn.cursor()
    
    total_translated = 0
    batch_size = 100
    error_count = 0
    max_errors = 5 
    
    try:
        while True:
            descriptions = get_untranslated_descriptions(cursor, batch_size)
            
            if not descriptions:
                logger.info("No more descriptions to translate!")
                break
                
            logger.info(f"Processing batch of {len(descriptions)} descriptions")
            
            for id, description in descriptions:
                try:
                    if not description or not is_italian(description):
                        cursor.execute(
                            "UPDATE truncated_listings SET description_en = ? WHERE id = ?",
                            (description, id)
                        )
                        continue
                    translated = translate_text(description)
                    if translated:
                        cursor.execute(
                            "UPDATE truncated_listings SET description_en = ? WHERE id = ?",
                            (translated, id)
                        )
                        total_translated += 1
                        error_count = 0 
                    else:
                        error_count += 1
                    
                    conn.commit()
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing description {id}: {e}")
                    error_count += 1
                    
                if error_count >= max_errors:
                    logger.error("Too many consecutive errors, stopping translation")
                    raise Exception("Translation stopped due to too many errors")
                    
                if total_translated % 10 == 0:
                    logger.info(f"Translated {total_translated} descriptions so far")
            logger.info(f"Completed batch. Total translated: {total_translated}")
            
    except KeyboardInterrupt:
        logger.info("\nTranslation interrupted by user")
    except Exception as e:
        logger.error(f"Translation stopped due to error: {e}")
    finally:
        conn.commit()
        conn.close()
        logger.info(f"Translation complete. Total translated: {total_translated}")

def main():
    logger.info("Starting translation process...")
    update_database_translations()

if __name__ == "__main__":
    main()
