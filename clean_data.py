import sqlite3

#Polaczenie do bazy danych
conn = sqlite3.connect('airbnb.db')
cursor = conn.cursor()

#Czyszczenie danych
cursor.execute("UPDATE truncated_listings SET neighborhood_overview = 'Host did not specify' WHERE neighborhood_overview IS NULL OR neighborhood_overview = 'NA'")

cursor.execute("UPDATE truncated_listings SET host_response_time = 'Unknown' WHERE host_response_time = 'N/A'")

cursor.execute("UPDATE truncated_listings SET host_about = 'No description given' WHERE host_about IS NULL OR host_about = '' OR host_about = '.'")

cursor.execute("UPDATE truncated_listings SET price = REPLACE(price, '$', '')")

conn.commit()

#Weryfikacja
cursor.execute("SELECT COUNT(*) FROM truncated_listings WHERE neighborhood_overview = 'Host did not specify'")
neighborhood_updates = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM truncated_listings WHERE host_response_time = 'Unknown'")
host_response_updates = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM truncated_listings WHERE host_about = 'No description given'")
host_about_updates = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM truncated_listings")
updated_rows = cursor.fetchone()[0]

#Zamkniecie połączenia
conn.close()
