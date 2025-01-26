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

#pobieram stopwords z nltk
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# pobranie słów z bazy
STOP_WORDS = set(stopwords.words('english') + stopwords.words('italian'))
ADDITIONAL_STOP_WORDS = {'con', 'per', 'del', 'della', 'delle', 'dei', 'degli', 'nel', 'nella', 'nelle', 'nei', 'agli', 
                        'sul', 'sulla', 'sulle', 'sui', 'dal', 'dalla', 'dalle', 'dai', 'al', 'alla', 'alle', 'ai',
                        'con', 'col', 'coi', 'da', 'di', 'in', 'su', 'per', 'tra', 'fra', 'casa', 'appartamento',
                        'stanza', 'room', 'house', 'apartment', 'home', 'flat'}
STOP_WORDS.update(ADDITIONAL_STOP_WORDS)

def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zàèéìòóù\s]', '', text)
    text = ' '.join(text.split())
    words = text.split()
    words = [word for word in words if word not in STOP_WORDS]
    return ' '.join(words)

def get_word_frequencies(listings):
    all_words = []
    for name in listings:
        if name[0]:
            cleaned_text = clean_text(name[0])
            words = cleaned_text.split()
            all_words.extend(words)
    word_counts = Counter(all_words)
    
    # wyfiltrowanie krotszych niz 2
    filtered_counts = {word: count for word, count in word_counts.items() 
                      if len(word) > 2}
    return filtered_counts

def generate_wordcloud():
    # połączenie z baza
    conn = sqlite3.connect('airbnb.db')
    cursor = conn.cursor()
    # pobranie wszystkich tokenów 
    cursor.execute('SELECT name_tokens FROM truncated_listings WHERE name_en IS NOT NULL')
    rows = cursor.fetchall()
    # lista slow wloskich do wykluczenia
    italian_words = {
        'casa', 'mare', 'villa', 'appartamento', 'della', 'del', 'di', 'il', 'la', 'le', 'lo',
        'nel', 'nella', 'delle', 'dei', 'al', 'sul', 'sulla', 'con', 'e', 'ed', 'in',
        'appartamenti', 'stanza', 'camera', 'camere', 'posto', 'posti', 'vista', 'vicino',
        'bella', 'bello', 'bellissima', 'bellissimo', 'grande', 'piccolo', 'nuovo', 'nuova',
        'centro', 'citta', 'città', 'mare', 'spiaggia', 'terrazza', 'giardino', 'vacanza',
        'vacanze', 'sole', 'aria', 'cucina', 'bagno', 'letto', 'letti',
        'taormina', 'messina', 'agrigento',
        'trapani', 'noto', 'modica', 'ortigia', 'enna', 'marsala',
        'lipari', 'pantelleria', 'favignana', 'stromboli', 'vulcano',        
        'casa', 'appartamento', 'palazzo', 'castello', 'masseria',
        'casetta', 'villetta', 'villino'
    }
    
    all_tokens = []
    for row in rows:
        if row[0]: 
            tokens = row[0].split('|')
            tokens = [token for token in tokens if token.lower() not in italian_words and len(token) > 1]
            all_tokens.extend(tokens)
    
    word_freq = Counter(all_tokens)
    wordcloud = WordCloud(
        width=1600, 
        height=800,
        background_color='white',
        max_words=100,
        min_font_size=10,
        max_font_size=150,
        colormap='viridis'
    )
    
    wordcloud.generate_from_frequencies(word_freq)
    plt.figure(figsize=(20,10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Most Common Words in English Listing Names', pad=20, fontsize=16)
    plt.savefig('wordcloud_english.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    img = BytesIO()
    plt.figure(figsize=(12, 6), dpi=100)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    img_base64 = base64.b64encode(img.getvalue()).decode()
    # zapisanie do pliku
    os.makedirs('static/data', exist_ok=True)
    
    with open('static/data/wordcloud_data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'image': img_base64,
            'word_frequencies': dict(word_freq.most_common(20))
        }, f)
    
    conn.close()

if __name__ == '__main__':
    generate_wordcloud()