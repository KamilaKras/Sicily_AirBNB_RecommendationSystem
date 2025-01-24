import sqlite3
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import json
import re
from collections import Counter

def clean_text(text):
    if not text:
        return ""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and numbers, keeping accented characters
    text = re.sub(r'[^a-zàèéìòóù\s]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def get_word_frequencies(listings):
    # Clean and split all words
    all_words = []
    for name in listings:
        if name[0]:  # Check if name is not None
            cleaned_text = clean_text(name[0])
            words = cleaned_text.split()
            all_words.extend(words)
    
    # Count word frequencies
    word_counts = Counter(all_words)
    
    # Filter out very short words and keep only top words
    filtered_counts = {word: count for word, count in word_counts.items() 
                      if len(word) > 2}  # Only words longer than 2 characters
    
    return filtered_counts

def generate_wordcloud():
    # Connect to SQLite database
    conn = sqlite3.connect('airbnb.db')
    cursor = conn.cursor()
    
    # Get all listing names
    cursor.execute("SELECT name FROM truncated_listings")
    listings = cursor.fetchall()
    
    # Get word frequencies
    word_frequencies = get_word_frequencies(listings)
    
    # Generate word cloud
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color='white',
        min_font_size=10,
        max_font_size=150,
        prefer_horizontal=0.7,
        collocations=False,  # This prevents duplicate words
        colormap='viridis',
        regexp=r'\w+',
        min_word_length=3,
        max_words=100,
        relative_scaling=0.5
    ).generate_from_frequencies(word_frequencies)
    
    # Convert the word cloud to base64 image
    img = BytesIO()
    plt.figure(figsize=(12, 6), dpi=100)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    
    img_base64 = base64.b64encode(img.getvalue()).decode()
    
    # Save the data to a JSON file
    with open('static/data/wordcloud_data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'image': img_base64
        }, f)

if __name__ == "__main__":
    generate_wordcloud()