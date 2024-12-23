# The Connection Game

## Architecture du code

```
connection-game
├─ main.py
├─ display/
|  └─ display_grid.py
└─ src/
   ├─ solver.py
   └─ start.py
```

## Installation

1. Clonez le dépôt Git

```shell
git clone https://gitlab.univ-nantes.fr/E23B933N/connection-game.git
```

2. Allez dans le dossier du projet

```shell
cd connection-game
```

3. Créez un environnement virtuel Python

```shell
python3 -m venv .venv
```

4. Activez l'environnement virtuel

```shell
source .venv/bin/activate
```

5. Installez les dépendances du projet (à retrouver dans requirements.txt)

```shell
pip install -r requirements.txt
```

6. Modifiez la taille de la grille à votre convenance (ligne 12 du fichier main.py)

```python
def main():
    n, m = 50, 50 # <-- À modifier ici
    t = time.time()
```

7. Lancez l'algorithme de résolution

```shell
python main.py
```

## Visualiser les performances du code

1. Générez le fichier de scan avec la commande suivante

```shell
python -m cProfile -o profile.prof main.py
```

2. Stoppez rapidement le code une fois résolu, pour que pygame ne prenne pas trop de place dans l'analyse

3. Lancez la commande suivante pour accéder à l'interface graphique dans votre navigateur

```shell
snakeviz profile.prof
```

4. Parmi les rectangles de couleurs, cherchez celui qui porte le nom "solver", et cliquez-dessus pour accéder aux détails

## Lancer les tests

1. Lancez la commande suivante pour effectuer les tests sur la rotation d'une cellule, et les vérifications verticales et horizontales de connexions

```shell
pytest
```