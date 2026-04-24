# MFI_projekt

## Funkcje

- iteracyjne obliczanie PageRank,
- podgląd aktualnej iteracji,
- wizualizacja grafu,
- wykres słupkowy wartości PageRank (Top 20 dla dużych grafów),
- wykres zbieżności,
- tabela wszystkich iteracji,
- możliwość przełączania się między przykładowymi grafami,
- porównanie końcowego wyniku z referencją NetworkX (metryki L1 i max |Δ|),
- testy dla różnych skal grafów: małe i duże (25, 75, 150 węzłów).

## Uruchomienie

```bash
uv sync
python app.py
```

W aplikacji można sterować:
- współczynnikiem tłumienia,
- maksymalną liczbą iteracji,
- tolerancją zbieżności (tol = 10^-x).

## Szybka walidacja z NetworkX

```bash
python data/test_networkx_loading.py
```

Skrypt wypisuje liczbę iteracji i różnice między implementacją własną a referencyjną implementacją w NetworkX.

## Requirements

Przed odpaleniem aplikacji:
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
pip install -r requirements.txt
```
