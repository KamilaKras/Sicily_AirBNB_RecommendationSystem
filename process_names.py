import sqlite3
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import time
from datetime import timedelta
import sys

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

def get_wordnet_pos(word):
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV
    }
    return tag_dict.get(tag, wordnet.NOUN)

def process_name(text):
    if not text:
        return []
    
    # Tokenize and convert to lowercase
    tokens = word_tokenize(text.lower())
    
    # Remove stopwords and non-alphanumeric tokens
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
    
    # Lemmatize with correct POS tag
    lemmatizer = WordNetLemmatizer()
    processed = [lemmatizer.lemmatize(token, get_wordnet_pos(token)) for token in tokens]
    
    return processed

def process_batch(cursor, batch):
    updates = []
    for id, name in batch:
        tokens = process_name(name)
        tokens_str = '|'.join(tokens)
        updates.append((tokens_str, id))
    
    cursor.executemany('UPDATE truncated_listings SET name_tokens = ? WHERE id = ?', updates)

# Connect to database
conn = sqlite3.connect('airbnb.db')
cursor = conn.cursor()

# Check if name_tokens column exists
cursor.execute("PRAGMA table_info(truncated_listings)")
columns = [col[1] for col in cursor.fetchall()]

if 'name_tokens' in columns:
    print("Dropping existing name_tokens column...")
    cursor.execute('ALTER TABLE truncated_listings DROP COLUMN name_tokens')
    conn.commit()
    print("Column dropped successfully")

print("Adding new name_tokens column...")
cursor.execute('ALTER TABLE truncated_listings ADD COLUMN name_tokens TEXT')
conn.commit()
print("Column added successfully")

# Process all names
cursor.execute('SELECT id, name_en FROM truncated_listings WHERE name_en IS NOT NULL')
rows = cursor.fetchall()
total = len(rows)

print(f"\nStarting to process {total} names...")
start_time = time.time()

# Process in batches of 500
batch_size = 500
for i in range(0, total, batch_size):
    batch = rows[i:i + batch_size]
    process_batch(cursor, batch)
    conn.commit()
    
    # Show progress
    processed = min(i + batch_size, total)
    elapsed_time = time.time() - start_time
    progress = (processed / total) * 100
    avg_time_per_record = elapsed_time / processed
    remaining_records = total - processed
    estimated_time_left = remaining_records * avg_time_per_record
    
    print(f"\nProgress: {progress:.1f}% ({processed}/{total})")
    print(f"Time elapsed: {timedelta(seconds=int(elapsed_time))}")
    print(f"Estimated time remaining: {timedelta(seconds=int(estimated_time_left))}")
    print(f"Processing speed: {processed/elapsed_time:.1f} records/second")
    
    # Show example from this batch
    example_id, example_name = batch[0]
    example_tokens = process_name(example_name)
    print(f"\nExample from current batch:")
    print(f"Original: {example_name}")
    print(f"Tokens: {example_tokens}")
    print("-" * 50)

conn.commit()
conn.close()

total_time = time.time() - start_time
print(f"\nDone! All {total} names have been processed and saved.")
print(f"Total processing time: {timedelta(seconds=int(total_time))}")
print(f"Average speed: {total/total_time:.1f} records/second")
