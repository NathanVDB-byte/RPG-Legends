# 🏰 Mini RPG - Dungeon Crawler (Pygame)

## 📋 Description du Projet

Ce projet est un jeu de rôle (RPG) de type **Dungeon Crawler** infini développé en Python avec la bibliothèque **Pygame**. Le joueur incarne un héros qui doit progresser d'étage en étage, combattre des monstres, vaincre des boss tous les 10 kills, et gérer son équipement pour devenir plus fort.

Le projet met l'accent sur la **persistance des données** (sauvegardes JSON), la **gestion d'inventaire dynamique** et un **système de combat au tour par tour**.

---

## 🛠️ Prérequis et Installation

### Environnement
- **Langage :** Python 3.x
- **Bibliothèque :** `pygame-ce` (Community Edition) ou `pygame` standard

### Installation des dépendances
Ouvrez votre terminal (PowerShell ou CMD) et exécutez :
```bash
pip install pygame
```


### Lancement du Jeu
```bash
python jeu20.py
```


---

## 📂 Structure du Code : Explication Étape par Étape

Le fichier `jeu20.py` est structuré de manière **monolithique** pour faciliter le prototypage, mais divisé en sections logiques distinctes.

### 1. Configuration et Imports
- **Bibliothèques standards :** `os` (gestion des chemins de fichiers compatible Windows/Linux), `json` (système de sauvegarde), `random` (génération procédurale des combats/loots)
- **Initialisation :** Création automatique du dossier `/saves` si celui-ci n'existe pas, garantissant qu'aucune erreur ne survient lors de la première sauvegarde

### 2. Bases de Données (Dictionnaires & Listes)
Le jeu n'utilise pas de SQL, mais des **structures de données constantes** en haut du fichier pour définir le contenu du jeu :
- `POSSIBLE_CONSUMABLES` : Liste des potions et élixirs
- `POSSIBLE_EQUIPMENT` : Liste des armes et armures avec leurs stats (ATK/DEF/HP)
- `FLOOR_ENEMIES` : Dictionnaire définissant quels monstres apparaissent à quel étage (scaling de difficulté)
- `FLOOR_BOSSES` : Liste des Boss uniques apparaissant tous les 10 niveaux

### 3. Les Classes (Programmation Orientée Objet)

#### A. Classe `Character` (Le Cœur du Jeu)
C'est l'objet le plus complexe. Il gère le joueur.

- **Attributs :** Vie, Attaque, Défense, Classe (Guerrier/Mage/Tank)
- **Système de Stats Dynamiques (`@property`) :**
  - Le jeu ne stocke pas la "Défense Totale" en dur
  - Il calcule `base_defense + équipement` à la volée. Si vous changez de casque, la stat se met à jour instantanément
- **Gestion d'Inventaire (`equip_item`) :**
  - Gère l'échange d'objets entre le **Sac à Dos** (liste) et l'**équipement actif** (dictionnaire)
  - Gère le bonus de PV lors de l'équipement/déséquipement pour éviter les bugs de santé négative
- **Sérialisation (`to_dict` / `from_dict`) :**
  - Transforme l'objet Joueur en format JSON pour la sauvegarde
  - Intègre un **script de migration forcée** (`from_dict`) qui répare automatiquement les vieilles sauvegardes si la structure des données change (ex: ajout de catégories d'objets)

#### B. Classe `Enemy`
Hérite de `Character`. Elle simplifie la création de monstres et ajoute un flag `is_boss` pour gérer les événements spéciaux (butin de boss, passage à l'étage suivant).

#### C. Classe `Button`
Une classe **UI (Interface Utilisateur)** personnalisée.
- Gère l'affichage des rectangles et du texte
- Gère les événements de **survol (hover)** et de **clic**
- Permet de créer des interfaces réactives sans utiliser de librairies GUI externes

### 4. Le Moteur de Jeu (class `Game`)
Le jeu utilise un **Pattern de Machine à États** (State Machine).

- `self.state` : Variable qui détermine ce qui s'affiche à l'écran (`MENU`, `CAMP`, `COMBAT`, `INVENTORY`, etc.)
- **La Boucle Principale (`run`) :**
  - **Events :** Écoute les clics souris et le clavier (`pygame.event.get()`)
  - **Logique & Affichage :** Une grande structure `if/elif` vérifie `self.state` et dessine l'écran correspondant
  - **Refresh :** `pygame.display.flip()` met à jour l'écran 60 fois par seconde

---

## 💾 Système de Sauvegarde (JSON)

- **Stockage :** Les fichiers sont stockés dans le dossier `/saves`
- **Nom du fichier :** Basé sur le nom du personnage (aseptisé pour éviter les caractères spéciaux)
- **Contenu :** Tout l'état du joueur (Inventaire, Équipement, Progression, Kills)
- **Chargement :** Le jeu lit le fichier JSON et reconstruit l'objet `Character` grâce à la méthode `from_dict`

---

## 🐛 Gestion des Erreurs Connues (Fixées)

- ✅ **Bug de l'inventaire vide :** Corrigé en inversant l'ordre de mise à jour (Changement d'état → Rafraîchissement UI)
- ✅ **Crash `current_time` :** Corrigé en déclarant `pygame.time.get_ticks()` au début de la boucle `run`
- ✅ **Items invisibles :** Corrigé par le script de migration qui force l'ajout de catégories par défaut aux vieux objets

---

## 🚀 Prochaines Améliorations (Roadmap)

- [ ] Ajout d'effets visuels pour les coups critiques
- [X] Système de boutique (Marchand)
- [ ] Compétences spéciales par classe (Mana)
- [X] Interface de "Drag & Drop" pour l'équipement (optionnel)

---

## 📜 Licence

Ce projet est distribué sous licence MIT. Vous êtes libre de le modifier et le redistribuer.

## 👤 Auteur

Développé par **Nathan VDB** - Administrateur Systèmes et Réseaux

---
## Versions du jeu

Jeu_RPG\Versions Alpha : `Jeu 12` Version finale du jeu, sans système d’items d’armes et d’armures.

Jeu_RPG : `Jeu 20` Version finale du jeu avec système complet d’armes et d’armures.


