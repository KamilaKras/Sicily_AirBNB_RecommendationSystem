import sqlite3

conn = sqlite3.connect('airbnb.db')
cursor = conn.cursor()

# Count non-empty names
cursor.execute('SELECT COUNT(*) FROM truncated_listings WHERE name IS NOT NULL AND name != ""')
print('Non-empty names:', cursor.fetchone()[0])

# Count non-empty neighborhood overviews
cursor.execute('SELECT COUNT(*) FROM truncated_listings WHERE neighborhood_overview IS NOT NULL AND neighborhood_overview != ""')
print('Non-empty neighborhood overviews:', cursor.fetchone()[0])

# Count non-empty host about
cursor.execute('SELECT COUNT(*) FROM truncated_listings WHERE host_about IS NOT NULL AND host_about != ""')
print('Non-empty host about:', cursor.fetchone()[0])

conn.close()
