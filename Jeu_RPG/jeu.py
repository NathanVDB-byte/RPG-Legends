import sys
import os
import json
import random
import time

# --- Constantes & Configuration ---
SAVE_FILE = "savegame.json"

class Character:
    """Classe de base pour tout personnage (Joueur ou Ennemi)."""
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack_value = attack
        self.defense_value = defense
        self.inventory = []

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        actual_damage = max(0, dmg - self.defense_value)
        self.hp -= actual_damage
        return actual_damage

    def attack_target(self, target):
        # Jet critique simple (1 chance sur 10)
        crit_mult = 2 if random.random() < 0.1 else 1
        dmg = self.attack_value * crit_mult
        
        actual = target.take_damage(dmg)
        
        crit_msg = " (COUP CRITIQUE!)" if crit_mult > 1 else ""
        print(f"⚔️ {self.name} attaque {target.name}{crit_msg} et inflige {actual} dégâts.")
        
    def heal(self, amount):
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        print(f"💚 {self.name} récupère {self.hp - old_hp} PV.")

    def to_dict(self):
        """Sérialisation pour JSON"""
        return {
            "name": self.name,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "attack": self.attack_value,
            "defense": self.defense_value,
            "inventory": self.inventory
        }

    @classmethod
    def from_dict(cls, data):
        """Désérialisation depuis JSON"""
        char = cls(data["name"], data["max_hp"], data["attack"], data["defense"])
        char.hp = data["hp"]
        char.inventory = data.get("inventory", [])
        return char

class Player(Character):
    """Classe spécifique au joueur."""
    pass

class Enemy(Character):
    """Classe pour les ennemis standards et Boss."""
    def __init__(self, name, hp, attack, defense, is_boss=False):
        super().__init__(name, hp, attack, defense)
        self.is_boss = is_boss

    def perform_ai_turn(self, target):
        """IA Simple : Soin si PV bas (Boss seulement), sinon Attaque."""
        if self.is_boss and self.hp < self.max_hp * 0.3 and random.random() < 0.4:
            # 40% de chance de se soigner si PV < 30%
            heal_val = 15
            print(f"⚠️ {self.name} (Boss) utilise une potion sombre !")
            self.heal(heal_val)
        else:
            self.attack_target(target)

class GameEngine:
    """Moteur principal du jeu."""
    def __init__(self):
        self.player = None
        self.running = True

    def create_character(self):
        print("\n--- CRÉATION DU PERSONNAGE ---")
        while True:
            name = input("Entrez votre nom de héros : ").strip()
            if name:
                # Stats de départ
                self.player = Player(name, hp=100, attack=15, defense=5)
                print(f"Bienvenue, {self.player.name} ! (PV: 100 | ATK: 15 | DEF: 5)")
                break
            print("Le nom ne peut pas être vide.")

    def save_game(self):
        if not self.player:
            print("Aucune partie en cours à sauvegarder.")
            return
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(self.player.to_dict(), f, indent=4)
            print("💾 Partie sauvegardée avec succès.")
        except IOError as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            print("Aucun fichier de sauvegarde trouvé.")
            return False
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                self.player = Player.from_dict(data)
            print(f"📂 Bon retour, {self.player.name} !")
            return True
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Fichier de sauvegarde corrompu : {e}")
            return False

    def generate_loot(self):
        """Système de loot aléatoire (Exercice 6)."""
        loot_table = [
            ("Potion de Soin", "heal", 20),
            ("Pierre à Aiguiser (+2 Atk)", "buff_atk", 2),
            ("Bouclier en Bois (+1 Def)", "buff_def", 1)
        ]
        item_name, effect_type, value = random.choice(loot_table)
        
        print(f"✨ Vous trouvez un objet : {item_name} !")
        
        if effect_type == "heal":
            self.player.heal(value)
        elif effect_type == "buff_atk":
            self.player.attack_value += value
            print(f"Votre attaque monte à {self.player.attack_value}.")
        elif effect_type == "buff_def":
            self.player.defense_value += value
            print(f"Votre défense monte à {self.player.defense_value}.")

    def combat(self):
        # Génération aléatoire d'ennemi (Standard ou Boss rare)
        if random.random() < 0.2:
            enemy = Enemy("Seigneur des Ombres", 80, 18, 8, is_boss=True)
            print(f"\n👹 ATTENTION ! Un BOSS apparaît : {enemy.name} !")
        else:
            enemy = Enemy(f"Gobelin {random.randint(1, 99)}", 40, 10, 2)
            print(f"\n⚔️ Un ennemi apparaît : {enemy.name} (PV: {enemy.hp})")

        while self.player.is_alive() and enemy.is_alive():
            print(f"\nVos PV: {self.player.hp} | {enemy.name} PV: {enemy.hp}")
            action = input("[A]ttaquer / [F]uir : ").lower().strip()

            if action == 'a':
                self.player.attack_target(enemy)
                if enemy.is_alive():
                    # Tour de l'IA
                    time.sleep(0.5) # Petit délai pour la lisibilité
                    enemy.perform_ai_turn(self.player)
            elif action == 'f':
                if random.random() < 0.5:
                    print("🏃 Vous avez réussi à fuir !")
                    return
                else:
                    print("⛔ Fuite échouée !")
                    enemy.perform_ai_turn(self.player)
            else:
                print("Action invalide.")

        if self.player.is_alive():
            print(f"\n🏆 VICTOIRE ! {enemy.name} a été vaincu.")
            self.generate_loot()
        else:
            print("\n💀 VOUS ÊTES MORT...")

    def main_menu(self):
        while self.running:
            print("\n=== MENU PRINCIPAL ===")
            print("1. Nouvelle Partie")
            print("2. Charger Partie")
            print("3. Quitter")
            
            try:
                choice = input("Choix : ").strip()
                if choice == "1":
                    self.create_character()
                    self.game_loop()
                elif choice == "2":
                    if self.load_game():
                        self.game_loop()
                elif choice == "3":
                    print("Au revoir !")
                    self.running = False
                else:
                    print("Option inconnue.")
            except KeyboardInterrupt:
                print("\nArrêt forcé du jeu.")
                self.running = False

    def game_loop(self):
        """Boucle de gameplay après chargement/création."""
        while self.player.is_alive():
            print("\n--- CAMPEMENT ---")
            print("1. Explorer (Combat)")
            print("2. Se reposer (Soin partiel)")
            print("3. Sauvegarder et Quitter vers menu")
            
            choice = input("Action : ").strip()
            
            if choice == "1":
                self.combat()
            elif choice == "2":
                self.player.heal(10)
                # Risque d'embuscade pendant le repos
                if random.random() < 0.3:
                    print("💤 Vous êtes réveillé par un ennemi !")
                    self.combat()
            elif choice == "3":
                self.save_game()
                break
            else:
                print("Choix invalide.")
        
        if not self.player.is_alive():
            print("Fin de l'aventure. Merci d'avoir joué !")
            # On pourrait supprimer la sauvegarde ici (mode Hardcore)

if __name__ == "__main__":
    game = GameEngine()
    game.main_menu()