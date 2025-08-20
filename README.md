 # Henomorphs

Nieoficjalny skrypt w pythonie do interakcji ze smart kontraktami kolekcji NFT Henomorphs wydanej przez społeczność ZICO DAO.\
[Kolekcja Henomorphs Genesis na Magic Eden](https://magiceden.io/collections/polygon/henomorphs-genesis-1)  
[Kolekcja Henomorphs Matrix na Magic Eden](https://magiceden.io/collections/polygon/henomorphs-matrix)  
[Discord CryptoColony 42](https://discord.gg/YWpAGBwhqa)

Skrypt działa z pythonem 3.12 i 3.13 (Nie testowano na starszych wersjach)

## Funkcje:
- Wyświetlanie ststystyk tokenów NFT w formie tabeli
- Wykonywanie inspekcji mecha kurczaków
- Wykonywanie akcji kolonialnych (możliwość wyboru akcji dla każdego tokena)
  - Możliwość użycia zaruwno performAction() jak i batchPerformAction()
- Naprawa kurczaków
- Sprawdzanie i claim zysków ze stakingu


## Instalacja:
Upewnij się, że masz zainstalowany: [git](https://git-scm.com/) i [python](https://www.python.org/)

Sklonuj repozytorium:
```sh
git clone https://github.com/dominikp3/Henomorphs.git
```

W celu automatycznego utworzenia środowiska [venv](https://docs.python.org/3/library/venv.html) i instalacji zależności, można skorzystać z dołączonych skryptów dla systemu Windows (install.bat) i Linux (install.sh)

### Manualna instalacja
#### Windows (powershell lub cmd)
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```
#### Linux (bash)
```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Aktualizacja
W celu zaktualizowania do najnowszej wersji, można użyć skyptów (update.bat lub update.sh) lub zrobić to ręcznie:
#### Windows (powershell lub cmd)
```powershell
git pull
.\.venv\Scripts\activate
pip install -r requirements.txt
```
#### Linux (bash)
```sh
git pull
source .venv/bin/activate
pip install -r requirements.txt
```

## Konfiguracja
Przed pierwszym użyciem należy odpowiednio skonfigurować skrypt. \
Konfiguracja skłąda sie z dwóch czynności:
- Import portfela EVM
- Utworzenie pliku konfiguracyjnego

Konfiguracja przechowywana jest w katalogu ```userdata```. \
Jeśli katalog ```userdata``` nie istnieje, zostanie on utworzony automatycznie.

Przy pierwszym uruchomieniu skryptu należy zaimportować portfel Polygon wprowadzając klucz prywatny, następnie ustawić hasło. Klucz zostanie zapisany w pliku ```userdata/privkey.bin``` w postaci zaszyfrowanej algorytmem AES z 256 bitowym kluczem utworzonym na podstawie wybranego hasła.

Należy utworzyć plik tekstowy ```userdata/config.json``` \
W pliku umieścić dane tokenów. Można użyć innej [nieoficjalnej nakładki](https://henomorphs.xyz/) w celu sprawdzenia swoich NFT \
Na stronie [chainlist.org](https://chainlist.org/chain/137) można znaleźć linki do darmowych serwerów rpc
### Opis formatu (z komentarzami)
```json
{
  "Config": { // Parametry konfiguracji
    "max_transaction_attempts": (integer), 
    // Maksymalna ilość prób wykonania transakcji (powtarzanie w przypadku niepowodzenia)

    "random_action_on_fail": (integer),
    // użycie losowej akcji w przypadku niepowodzenia z wybraną akcją (0 - wyłączone, liczba określa po ilu nieudanych próbach stosowana jest losowa). Ta opcja może się przydać, jeśli chcesz mieć większą pweność, że każdy kurczak wykona jakąś akcję. Jak jedna nie działa, to inna.
    // UWAGA: Ta opcja kompatybilna jest tylko z algorytmem SingleChickSequence, NIE DZIAŁA Z BATCH

    "delay": (number),
    // Opóźnienie przed wykonaniem kolejnej transakcji w sekundach (służy do zminimalizowania ryzyka wystąpienia błędów, jeśli wykonujemy za dużo transakcji naraz)

    "debug": (boolean),
    // Po ustawieniu na true wyświetla więcej informacji (niekoniecznie przydatne dla zwykłych użytkowników). Parametr opcjonalny

    "rpc": (string)
    // Niestandardowy Link do rpc sieci Polygon. Parametr opcjonalny
  },
  "Henomorphs": [ // Lista tokenów
    {
      "CollectionID": (int),
      // ID kolekcji (2 lub 3)

      "TokenID": (int),
      // ID tokena

      "Action": (int)
      // Akcja (1 - 5). Możesz ustawić na 0, jeśli nie chcesz wykonywać akcji dla tego tokena
    },
    ...
  ]
}
```

## Przykładowa konfiguracja
**Uwaga: w pliku z konfiguracją nie należy umieszczać komentarzy (//)**  
**Jeśli kopiujesz ten przykład, nie zapomnij zmienić przykładowych ID tokenów na swoje**
```json
{
  "Config": {
    "max_transaction_attempts": 5,
    "random_action_on_fail": 2,
    "delay": 3,
    "rpc": "https://polygon-pokt.nodies.app"
  },
  "Henomorphs": [
    {
      "CollectionID": 2,
      "TokenID": 1853,
      "Action": 4
    },
    {
      "CollectionID": 2,
      "TokenID": 1887,
      "Action": 5
    },
    {
      "CollectionID": 2,
      "TokenID": 364,
      "Action": 1
    },
    {
      "CollectionID": 2,
      "TokenID": 873,
      "Action": 4
    },
    {
      "CollectionID": 2,
      "TokenID": 1632,
      "Action": 5
    },
    {
      "CollectionID": 2,
      "TokenID": 322,
      "Action": 2
    },
    {
      "CollectionID": 3,
      "TokenID": 1702,
      "Action": 5
    },
    {
      "CollectionID": 3,
      "TokenID": 1612,
      "Action": 3
    },
    {
      "CollectionID": 3,
      "TokenID": 1510,
      "Action": 2
    },
    {
      "CollectionID": 3,
      "TokenID": 1492,
      "Action": 4
    },
    {
      "CollectionID": 3,
      "TokenID": 1641,
      "Action": 2
    },
    {
      "CollectionID": 3,
      "TokenID": 696,
      "Action": 5
    }
  ]
}
```

## Uruchamianie
Użyć dołączonych skryptów (run.bat lub run.sh) \
Ręcznie:
#### Windows (powershell lub cmd)
```powershell
.\.venv\Scripts\activate
python main.py
```
#### Linux (bash)
```sh
source .venv/bin/activate
python main.py
```

## Użytkowanie
**Ta sekcja instrukcji zakłada, że masz już skrypt skonfigurowany i gotowy do użycia**

Po uruchomieniu należy wprowadzić hasło do odszyfrowania portfela.\
Do nawigacji należy używać przycisków z cyframi i klawisza Enter