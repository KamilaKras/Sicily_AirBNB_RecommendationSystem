import sqlite3
import json

#Sprawdzenie najpopularniejszych udogodnien
def check_amenities():
    #Polaczenie do bazy
    conn = sqlite3.connect('airbnb.db')
    cursor = conn.cursor()
    cursor.execute('SELECT amenities FROM truncated_listings WHERE amenities IS NOT NULL')
    all_amenities = {}
    for row in cursor.fetchall():
        amenities = json.loads(row[0])
        for amenity in amenities:
            all_amenities[amenity] = all_amenities.get(amenity, 0) + 1
    
    # sortowanie
    sorted_amenities = sorted(all_amenities.items(), key=lambda x: x[1], reverse=True)
    
    print(f"Total unique amenities: {len(sorted_amenities)}")
    print("\nTop 20 most common amenities and their frequencies:")
    for amenity, count in sorted_amenities[:20]:
        print(f"{amenity}: {count} listings")
    #zamykanie połączenia
    conn.close()
if __name__ == "__main__":
    check_amenities()