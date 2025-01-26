import sqlite3

def print_table_info(table_name, cursor):
    # info o kolumnach
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\nTable: {table_name}")
    print("Columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

# Połączenie z baza
conn = sqlite3.connect('airbnb.db')
cursor = conn.cursor()

# lista tabel w bazie
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Database Structure:")
for table in tables:
    print_table_info(table[0], cursor)

# Zamykanie połączenia
conn.close()