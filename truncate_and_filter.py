import sqlite3
# Polaczenie do bazy danych
conn = sqlite3.connect('airbnb.db')
cursor = conn.cursor()

#Nowa tabela z czescia danych airbnb
cursor.execute("CREATE TABLE IF NOT EXISTS truncated_listings AS SELECT * FROM listings LIMIT 27000")

#Nowa tabela z czescia danych opinii
cursor.execute("CREATE TABLE IF NOT EXISTS filtered_reviews AS \
                SELECT * FROM reviews WHERE listing_id IN (SELECT id FROM truncated_listings)")

# Usuniecie oryginalnych tabel listings i reviews
cursor.execute("DROP TABLE IF EXISTS listings")
cursor.execute("DROP TABLE IF EXISTS reviews")

# Zatwierdzenie zmian
conn.commit()

# Sprawdzenie statystyk nowych tabel (spelnienie kryteriow)
cursor.execute("SELECT COUNT(*) FROM truncated_listings")
truncated_rows = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM filtered_reviews")
filtered_rows = cursor.fetchone()[0]

print("\nTruncated and Filtered Database Summary:")
print("-------------------------------------")
print(f"Truncated Listings table: {truncated_rows:,} rows")
print(f"Filtered Reviews table: {filtered_rows:,} rows")

# Zamykanie połączenia z bazą danych
conn.close()
