# System Rekomendacji AirBnB dla Sycylii

System wyszukiwania i rekomendacji ofert AirBnB na Sycylii.

![Sycylia](static/Sicily_photo/Sicily_photo2.jpg)

## Spis treści
- [Wymagania systemowe](#wymagania-systemowe)
- [Instalacja i uruchomienie](#instalacja-i-uruchomienie)
- [Struktura projektu](#struktura-projektu)

## Wymagania systemowe
- Python 3.8 lub nowszy
- Pip (menedżer pakietów Python)
- Minimum 500MB wolnego miejsca na dysku
- Dostęp do internetu 

## Instalacja i uruchomienie

1. Klonowanie repozytorium:
```bash
git clone https://github.com/KamilaKras/Sicily_AirBNB_RecommendationSystem.git
cd Sicily_AirBNB_RecommendationSystem
```

2. Zainstalowanie wymaganych pakietów:
```bash
pip install -r requirements.txt
```

3. Uruchomienie aplikacji - skrypt `app.py`

## Struktura projektu

### Główne pliki aplikacji
- `app.py` - Główny plik aplikacji Flask, zawierający routing i logikę serwera
- `search_engine.py` - Silnik wyszukiwania wykorzystujący NLP i uczenie maszynowe
- `requirements.txt` - Lista wymaganych pakietów Python

### Bazy danych
- `airbnb.db` - Główna baza danych SQLite zawierająca wszystkie dane
- `airbnb_backup_2025_01_26.db` - Kopia zapasowa bazy danych

### Pliki przetwarzania danych (historyczne)
Poniższe pliki zostały użyte do utworzenia i przetworzenia bazy danych. Nie są wymagane do uruchomienia systemu:

- `csv_to_sqlite.py` - Konwersja danych z CSV do SQLite
- `clean_data.py` - Czyszczenie danych
- `process_names.py` - Przetwarzanie nazw ofert
- `truncate_and_filter.py` - Filtrowanie i przycinanie danych
- `check_tables.py` - Sprawdzanie struktury tabel

### Pliki tłumaczenia (historyczne)
Pliki użyte do tłumaczenia treści na język angielski. Nie są wymagane do uruchomienia systemu. Zostały w repozytorium dla zaprezentowania sposobu tłumaczenia:
- `translation_utils.py` - Narzędzia do tłumaczenia
- `translate_names.py` - Tłumaczenie nazw ofert
- `translate_host_about.py` - Tłumaczenie opisów gospodarzy
- `translate_neighborhoods.py` - Tłumaczenie nazw dzielnic

### Pliki pomocnicze
- `generate_wordcloud.py` - Generowanie chmury słów z nazw ofert
- `check_amenities.py` - Sprawdzanie dostępnych udogodnień
- `check_db.py` - Narzędzie do sprawdzania stanu bazy danych

### Katalogi
- `/static` - Pliki statyczne (CSS, JavaScript, obrazy)
- `/templates` - Szablony HTML

## Uwagi
- System używa przetworzonej bazy danych SQLite (`airbnb.db`), która zawiera już wszystkie potrzebne dane
- Pliki związane z przetwarzaniem danych i tłumaczeniem są zachowane w celach dokumentacyjnych
- System działa lokalnie na serwerze Flask

## Funkcje
- Wyszukiwanie ofert przy użyciu języka naturalnego
- Filtrowanie wyników według różnych kryteriów
- Generowanie chmury słów z najpopularniejszych termów w nazwach ogloszeń Airbnb
- Wyświetlanie ogólnych i szczegółowych informacji o ofertach