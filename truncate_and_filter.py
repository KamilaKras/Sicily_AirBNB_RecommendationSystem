import sqlite3
# Polaczenie do bazy danych
conn = sqlite3.connect('airbnb.db')
cursor = conn.cursor()

#Nowa tabela z czescia danych airbnb
cursor.execute("CREATE TABLE IF NOT EXISTS truncated_listings AS SELECT * FROM listings LIMIT 27000")
# Usuniecie oryginalnej tabeli listings
cursor.execute("DROP TABLE IF EXISTS listings")
# Zatwierdzenie zmian
conn.commit()

# Sprawdzenie statystyk nowej tabeli
cursor.execute("SELECT COUNT(*) FROM truncated_listings")
truncated_rows = cursor.fetchone()[0]

# Zamykanie połączenia z bazą danych
conn.close()
