from deep_translator import GoogleTranslator
from langdetect import detect
import sqlite3
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_untranslated_descriptions(cursor, batch_size=100):
    """Get descriptions that haven't been translated yet"""
    cursor.execute("""
        SELECT id, description 
        FROM truncated_listings 
        WHERE description_en IS NULL 
        AND description IS NOT NULL 
        LIMIT ?
    """, (batch_size,))
    return cursor.fetchall()

def is_italian(text):
    """Check if text is in Italian"""
    try:
        return detect(text) == 'it'
    except:
        return False

def translate_text(text):
    """Translate text from Italian to English"""
    try:
        translator = GoogleTranslator(source='it', target='en')
        return translator.translate(text)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return None

def update_database_translations():
    """Update database with translations, handling all batches automatically"""
    conn = sqlite3.connect('airbnb.db')
    cursor = conn.cursor()
    
    total_translated = 0
    batch_size = 100
    error_count = 0
    max_errors = 5  # Maximum number of consecutive errors before stopping
    
    try:
        while True:
            # Get next batch of untranslated descriptions
            descriptions = get_untranslated_descriptions(cursor, batch_size)
            
            if not descriptions:
                logger.info("No more descriptions to translate!")
                break
                
            logger.info(f"Processing batch of {len(descriptions)} descriptions")
            
            for id, description in descriptions:
                try:
                    # Skip if description is empty or not Italian
                    if not description or not is_italian(description):
                        cursor.execute(
                            "UPDATE truncated_listings SET description_en = ? WHERE id = ?",
                            (description, id)
                        )
                        continue
                    
                    # Translate the description
                    translated = translate_text(description)
                    if translated:
                        cursor.execute(
                            "UPDATE truncated_listings SET description_en = ? WHERE id = ?",
                            (translated, id)
                        )
                        total_translated += 1
                        error_count = 0  # Reset error count on success
                    else:
                        error_count += 1
                        
                    # Commit every translation to avoid losing progress
                    conn.commit()
                    
                    # Add a small delay to avoid hitting API limits
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing description {id}: {e}")
                    error_count += 1
                    
                # Check if we've hit too many errors
                if error_count >= max_errors:
                    logger.error("Too many consecutive errors, stopping translation")
                    raise Exception("Translation stopped due to too many errors")
                    
                if total_translated % 10 == 0:
                    logger.info(f"Translated {total_translated} descriptions so far")
            
            # Log progress after each batch
            logger.info(f"Completed batch. Total translated: {total_translated}")
            
    except KeyboardInterrupt:
        logger.info("\nTranslation interrupted by user")
    except Exception as e:
        logger.error(f"Translation stopped due to error: {e}")
    finally:
        # Make sure to commit any remaining changes
        conn.commit()
        conn.close()
        logger.info(f"Translation complete. Total translated: {total_translated}")

def main():
    logger.info("Starting translation process...")
    update_database_translations()

if __name__ == "__main__":
    main()
