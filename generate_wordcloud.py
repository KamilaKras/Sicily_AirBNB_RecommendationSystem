import sqlite3
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import json
import re
from collections import Counter
from nltk.corpus import stopwords
import nltk
import os

# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Get stopwords for both English and Italian
STOP_WORDS = set(stopwords.words('english') + stopwords.words('italian'))
# Add additional common words we want to filter out
ADDITIONAL_STOP_WORDS = {'con', 'per', 'del', 'della', 'delle', 'dei', 'degli', 'nel', 'nella', 'nelle', 'nei', 'agli', 
                        'sul', 'sulla', 'sulle', 'sui', 'dal', 'dalla', 'dalle', 'dai', 'al', 'alla', 'alle', 'ai',
                        'con', 'col', 'coi', 'da', 'di', 'in', 'su', 'per', 'tra', 'fra', 'casa', 'appartamento',
                        'stanza', 'room', 'house', 'apartment', 'home', 'flat'}
STOP_WORDS.update(ADDITIONAL_STOP_WORDS)

def clean_text(text):
    if not text:
        return ""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and numbers, keeping accented characters
    text = re.sub(r'[^a-zàèéìòóù\s]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove stopwords
    words = text.split()
    words = [word for word in words if word not in STOP_WORDS]
    return ' '.join(words)

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
    # Connect to database
    conn = sqlite3.connect('airbnb.db')
    cursor = conn.cursor()
    
    # Get all name tokens from English names only
    cursor.execute('SELECT name_tokens FROM truncated_listings WHERE name_en IS NOT NULL')
    rows = cursor.fetchall()
    
    # Comprehensive list of Italian words and location-specific terms to filter
    italian_words = {
        # Common Italian words
        'casa', 'mare', 'villa', 'appartamento', 'della', 'del', 'di', 'il', 'la', 'le', 'lo',
        'nel', 'nella', 'delle', 'dei', 'al', 'sul', 'sulla', 'con', 'e', 'ed', 'in',
        'appartamenti', 'stanza', 'camera', 'camere', 'posto', 'posti', 'vista', 'vicino',
        'bella', 'bello', 'bellissima', 'bellissimo', 'grande', 'piccolo', 'nuovo', 'nuova',
        'centro', 'citta', 'città', 'mare', 'spiaggia', 'terrazza', 'giardino', 'vacanza',
        'vacanze', 'sole', 'aria', 'cucina', 'bagno', 'letto', 'letti',
        
        # Location names (keep only major ones like Sicily, Etna)
        'taormina', 'messina', 'agrigento',
        'trapani', 'noto', 'modica', 'ortigia', 'enna', 'marsala',
        'lipari', 'pantelleria', 'favignana', 'stromboli', 'vulcano',        
        # Common property names
        'casa', 'appartamento', 'palazzo', 'castello', 'masseria',
        'casetta', 'villetta', 'villino'
    }
    
    all_tokens = []
    for row in rows:
        if row[0]:  # Check if tokens exist
            tokens = row[0].split('|')
            # Only add non-Italian words and filter out single characters/numbers
            tokens = [token for token in tokens if token.lower() not in italian_words and len(token) > 1]
            all_tokens.extend(tokens)
    
    # Count token frequencies
    word_freq = Counter(all_tokens)
    
    # Create and configure the WordCloud object
    wordcloud = WordCloud(
        width=1600, 
        height=800,
        background_color='white',
        max_words=100,
        min_font_size=10,
        max_font_size=150,
        colormap='viridis'  # Using a nice color scheme
    )
    
    # Generate the word cloud
    wordcloud.generate_from_frequencies(word_freq)
    
    # Create the plot for saving as PNG
    plt.figure(figsize=(20,10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Most Common Words in English Listing Names', pad=20, fontsize=16)
    
    # Save the PNG file
    plt.savefig('wordcloud_english.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    # Create base64 encoded image for web display
    img = BytesIO()
    plt.figure(figsize=(12, 6), dpi=100)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    
    img_base64 = base64.b64encode(img.getvalue()).decode()
    
    # Ensure the static/data directory exists
    os.makedirs('static/data', exist_ok=True)
    
    # Save the data to a JSON file
    with open('static/data/wordcloud_data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'image': img_base64,
            'word_frequencies': dict(word_freq.most_common(20))
        }, f)
    
    conn.close()

if __name__ == '__main__':
    generate_wordcloud()