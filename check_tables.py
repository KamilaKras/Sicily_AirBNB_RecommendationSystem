import sqlite3

#POLĄCZENIE DO BAZY DANYCH
conn = sqlite3.connect('airbnb.db')
cursor = conn.cursor()

#LICZBA KOLUMN W TABELACH
cursor.execute("PRAGMA table_info(truncated_listings)")
truncated_listings_columns = len(cursor.fetchall())

cursor.execute("PRAGMA table_info(filtered_reviews)")
filtered_reviews_columns = len(cursor.fetchall())

#LICZBA WIERSZY
cursor.execute("SELECT COUNT(*) FROM truncated_listings")
truncated_rows = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM filtered_reviews")
filtered_rows = cursor.fetchone()[0]

print("\nDatabase Summary:")
print("-----------------")
print(f"Truncated Listings table: {truncated_listings_columns} columns, {truncated_rows:,} rows")
print(f"Filtered Reviews table: {filtered_reviews_columns} columns, {filtered_rows:,} rows")

#ZAMKNIENIE POŁĄCZENIA
conn.close()
