import subprocess
scripts = [
    'csv_to_sqlite.py', #wybór kolumn i zamiana na SQLite
    'truncate_and_filter.py', #ograniczenie liczby rekordów
    'clean_data.py', #czyszczenie danych
    'check_tables.py' #weryfikacja tabel
]

#Tworzenie bazy danych
for script in scripts:
    print(f'Running {script}...')
    result = subprocess.run(['python', script], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f'Error in {script}: {result.stderr}')
