 # Henomorphs

Nieoficjalny skrypt w pythonie do interakcji ze smart kontraktami kolekcji NFT Henomorphs wydanej przez społeczność ZICO DAO.\
[Kolekcja Henomorphs Genesis na Magic Eden](https://magiceden.io/collections/polygon/henomorphs-genesis-1)  
[Kolekcja Henomorphs Matrix na Magic Eden](https://magiceden.io/collections/polygon/henomorphs-matrix)  
[Discord CryptoColony 42](https://discord.gg/E8aGBKDp7W)

Skrypt działa z pythonem 3.12 i 3.13 (Nie testowano na starszych wersjach)

## Funkcje:
- Wyświetlanie ststystyk tokenów NFT w formie tabeli
- Wykonywanie inspekcji mecha kurczaków
- Wykonywanie akcji kolonialnych (możliwość wyboru akcji dla każdego tokena)
  - Możliwość użycia zaruwno performAction() jak i batchPerformAction()
- Naprawa kurczaków
- Sprawdzanie i claim zysków ze stakingu
- ‼️NOWOŚĆ‼️
  - Obsługa wielu portfeli i plików konfiguracyjnych (przypisanie akcji do kurczaka)
  - Obsługa akcji specjalnych (6 - 8)
  - Możliwość zmiany specjalizacji kurczaków
  - Zapisywanie wykonywanych operacji do plików - wraz z dokładną datą i godziną
  - Możliwość zmiany opłaty za transakcję (gas fee)
  - Wyświetlanie **Txn hash** - można sprawdzić transakcję na [PolygonScan](https://polygonscan.com/)


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
Pliki konfiguracyjne przechowywane są w katalogu ```userdata```. \
Jeśli katalog ```userdata``` nie istnieje, skrypt utworzy go automatycznie.

Konfiguracja skłąda się z plików:
- ```privkey.bin``` - zaszyfrowany klucz prywatny portfela
- ```config.json``` - plik z konfiguracją skryptu **[Opcjonalny]**
- ```heno.json``` - lista tokenów NFT

Przy pierwszym uruchomieniu skryptu należy zaimportować portfel Polygon wprowadzając klucz prywatny, następnie ustawić hasło. Klucz zostanie zapisany w pliku ```userdata/privkey.bin``` w postaci zaszyfrowanej algorytmem AES z 256 bitowym kluczem utworzonym na podstawie wybranego hasła.

> ❌ Uwaga ❌
> - Zaleca się stosowanie długich i skomplikowanych haseł
> - Nigdy nie udostępniaj nikomu swojego klucza prywatnego ani pliku ```privkey.bin```
> - Nigdy nie przechowuj swojego klucza w formie niezaszyfrowanej (np w pliku .txt)

Jeśli plik ```heno.json``` (lub inny plik zawierający 'heno' w nazwie) nie istnieje, skrypt automatycznie pobierze listę zastakowanych NFT i utworzy go automatycznie.
Po utworzeniu pliku konieczne jest ustawienie parametrów według własnych preferencji (np: akcje dla tokena)

💡 W przypadku późniejszej zmiany tokenów NFT w portfelu, możesz zaktualizować plik używając funkcji **42**


### Opis formatu
#### config.json - wszystkie dostępne parametry
```js
{ // Parametry konfiguracji
    "max_transaction_attempts": (integer), // W nawiasie () podano typy danych
    // Maksymalna ilość prób wykonania transakcji (powtarzanie w przypadku niepowodzenia)

    "random_action_on_fail": (integer),
    // użycie losowej akcji w przypadku niepowodzenia z wybraną akcją (0 - wyłączone, liczba określa po ilu nieudanych próbach stosowana jest losowa). Ta opcja może się przydać, jeśli chcesz mieć większą pweność, że każdy kurczak wykona jakąś akcję. Jak jedna nie działa, to inna.
    // UWAGA: Ta opcja kompatybilna jest tylko z algorytmem SingleChickSequence, NIE DZIAŁA Z BATCH

    "delay": (number),
    // Opóźnienie przed wykonaniem kolejnej transakcji w sekundach (służy do zminimalizowania ryzyka wystąpienia błędów, jeśli wykonujemy za dużo transakcji naraz)

    "debug": (boolean),
    // Po ustawieniu na true wyświetla więcej informacji (niekoniecznie przydatne dla zwykłych użytkowników).

    "dummy": (int),
    // Parametr testowy - tylko do testowania
    // 0 - Normalne działanie (wartość domyślna)
    // 1 - Transakcja zawsze przechodzi pomyślnie
    // 2 - Zawsze błąd

    "rpc": (string)
    // Niestandardowy Link do rpc sieci Polygon.
    // Listę dostępnych darmowych RPC możesz znaleźć na https://chainlist.org/chain/137

    "log": (boolean),
    // Logowanie do pliku
    // Zapisuję historię wykonywanych operacji w katalogu userdata/logs/

    "print_tx_hash": (boolean),
    // Wyświetlaj hash transakcji.

    "print_priv_key": (boolean),
    // Wyświetlaj klucz prywatny
    // Opcja przydatna jeśli chcesz wyeksporwować klucz z pliku privkey.bin

    "gas_mul": (number),
    // Mnożnik do modyfikacji opłaty gas fee. (domyślnie 1)
    // Ustawienie na wyższą wartość (np: 1.2) może zmniejszyć prawdopodobieństwo wystąpienia błędu i przyspieszyć transakcje

    "repair_wear": { // Konfiguracja naprawy wear
      "threshold": (integer),
      // naprawia tylko kurczaki o wear >= threshold
      // Jeśli -1 (lub brak tego parametru) skrypt pyta przy każdej naprawie
      // Jeśli 0, to naprawi każdego kurczaka

      "max_repair": (integer)
      // Maksymalna wartość naprawy
      // Można ustawić na jakąś dużą wartość, np 99 aby całkowicie naprawić kurczaka
    },
    "repair_charge": { // Konfiguracja naprawy charge, działa tak jak z wear
      "threshold": (integer), // (Brakujący Charge) >= threshold
      "max_repair": (integer) // Max naprawa
    },
    "algorithms": {
      // Wybór algorytmów
      // ask - pytaj przy każdym użyciu
      // sequence - sekwencyjnie, po koleji pojedyńczo
      // batch - wiele naraz, oszczędza gas fee
      "actions": (string),
      "repair_wear": (string)
    }
}
```

#### heno.json
```js
[ // Lista tokenów
    {
      "CollectionID": (int),
      // ID kolekcji (2 lub 3)

      "TokenID": (int),
      // ID tokena

      "Action": (int),
      // Akcja (1 - 8). Możesz ustawić na 0, jeśli nie chcesz wykonywać akcji dla tego tokena

      "Spec": (int)
      // Specjalizacjia (0 - 2), parametr opcjonalny
      // -1 - brak
    },
    // ...
]
```

## Przykładowa konfiguracja
**Uwaga: w pliku z konfiguracją nie należy umieszczać komentarzy (//)**  

### config.json
W tym przykładzie podano parametry domyślne.\
Plik ```config.json``` i wszystkie parametery są **opcjonalne**.
```json
{
  "max_transaction_attempts": 5,
  "random_action_on_fail": 0,
  "delay": 3,
  "debug": false,
  "dummy": 0,
  "rpc": "https://polygon-rpc.com",
  "log": false,
  "print_tx_hash": false,
  "print_priv_key": false,
  "gas_mul": 1.0,
  "repair_wear": {
    "threshold": -1,
    "max_repair": -1
  },
  "repair_charge": {
    "threshold": -1,
    "max_repair": -1
  },
  "algorithms": {
    "actions": "ask",
    "repair_wear": "ask"
  }
}
```

### heno.json
Plik **wymagany**\
Jeśli kopiujesz ten przykład, nie zapomnij zmienić przykładowych ID tokenów na swoje
```json
[
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
```

### Multikonta i wiele konfigurcji
Plik ```config.json``` powinien być **tylko jeden**, w katalogu ```userdata```

W celu zaimportowania dodatkowych portfeli, należy utworzyć folder o dowolnej nazwie w katalogu ```userdata```\
Przy uruchomieniu skryptu pojawi się pytanie o wybór konta/portfela ('Default account' to pierwsze konto - folder userdata)\
Przy pierwszym użyciu każdego kolejnego konta należy zaimportować portfel, utworzyć konfigurację tokenów.

W celu utworzenia wielu konfiguracji tokenów, należy w folderze ```userdata``` (lub folderze innego konta) utworzyć dodatkowe pliki .json zawierające w nazwie 'heno'. Skrypt pozwoli wybrać plik przy uruchomieniu.\
💡 Folder nie musi zawierać pliku ```heno.json``` (domyślna nazwa), ale powinien zawierać **co najmniej jeden** plik ze słowem 'heno' w nazwie


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
