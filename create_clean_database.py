import subprocess
scripts = [
    'csv_to_sqlite.py',
    'truncate_and_filter.py',
    'clean_data.py',
    'check_tables.py'
]

#TWORZENIE BAZY DANYCH
for script in scripts:
    print(f'Running {script}...')
    result = subprocess.run(['python', script], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f'Error in {script}: {result.stderr}')
