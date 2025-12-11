import pygame
import sys
import json
import random
import os

# --- CONFIGURATION DES CHEMINS ---
# On se base sur l'emplacement du script pour créer un dossier "saves"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVES_DIR = os.path.join(BASE_DIR, "saves")

# Création du dossier s'il n'existe pas
if not os.path.exists(SAVES_DIR):
    os.makedirs(SAVES_DIR)

# --- INITIALISATION PYGAME ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini RPG - Multi Saves Edition")
CLOCK = pygame.time.Clock()

# --- COULEURS & FONTS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (170, 170, 170)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
GOLD = (218, 165, 32)

FONT_TITLE = pygame.font.SysFont("Arial", 40, bold=True)
FONT_TEXT = pygame.font.SysFont("Arial", 24)
FONT_SMALL = pygame.font.SysFont("Arial", 18)

# --- CLASSES LOGIQUES (Inchangées) ---
class Character:
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
        actual = max(0, dmg - self.defense_value)
        self.hp -= actual
        return actual

    def attack_target(self, target):
        crit = 2 if random.random() < 0.1 else 1
        dmg = self.attack_value * crit
        actual = target.take_damage(dmg)
        crit_str = " (CRITIQUE!)" if crit > 1 else ""
        return f"{self.name} attaque {target.name}{crit_str}: -{actual} PV"

    def heal(self, amount):
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return f"{self.name} se soigne de {self.hp - old} PV"

    def to_dict(self):
        return {"name": self.name, "max_hp": self.max_hp, "hp": self.hp, 
                "attack": self.attack_value, "defense": self.defense_value, "inventory": self.inventory}

    @classmethod
    def from_dict(cls, data):
        c = cls(data["name"], data["max_hp"], data["attack"], data["defense"])
        c.hp = data["hp"]
        c.inventory = data.get("inventory", [])
        return c

class Enemy(Character):
    def __init__(self, name, hp, attack, defense, is_boss=False):
        super().__init__(name, hp, attack, defense)
        self.is_boss = is_boss

# --- UI ---
class Button:
    def __init__(self, text, x, y, w, h, color, data=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.data = data # Pour stocker le nom de fichier par exemple
        self.hover = False

    def draw(self, surface):
        col = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255)) if self.hover else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=5)
        
        txt_surf = FONT_TEXT.render(self.text, True, WHITE)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            return True
        return False

# --- MOTEUR PRINCIPAL ---
class Game:
    def __init__(self):
        self.state = "MENU" # MENU, LOAD_MENU, INPUT_NAME, CAMP, COMBAT
        self.player = None
        self.enemy = None
        self.logs = ["Bienvenue !"]
        self.input_text = ""
        
        self.save_files_buttons = [] # Liste dynamique des boutons de sauvegarde
        self.setup_ui()

    def add_log(self, msg):
        self.logs.insert(0, msg)
        if len(self.logs) > 6:
            self.logs.pop()

    def setup_ui(self):
        # Menu Principal
        self.btn_new = Button("Nouvelle Partie", 300, 200, 200, 50, BLUE)
        self.btn_load_menu = Button("Charger Partie", 300, 270, 200, 50, GREEN)
        self.btn_quit = Button("Quitter", 300, 340, 200, 50, RED)
        
        # Input
        self.btn_confirm_name = Button("Valider", 300, 300, 200, 50, BLUE)

        # Camp
        self.btn_explore = Button("Explorer (Combat)", 50, 450, 200, 50, RED)
        self.btn_rest = Button("Se Reposer (+10PV)", 270, 450, 220, 50, GREEN)
        self.btn_save = Button("Sauvegarder", 510, 450, 200, 50, BLUE)
        self.btn_menu = Button("Menu Principal", 510, 20, 200, 40, GRAY)

        # Combat
        self.btn_attack = Button("ATTAQUER", 300, 450, 200, 60, RED)
        
        # Menu Charger (Bouton retour)
        self.btn_back = Button("Retour", 300, 500, 200, 40, GRAY)

    def refresh_save_list(self):
        """Scanne le dossier saves/ et crée des boutons."""
        self.save_files_buttons = []
        try:
            files = [f for f in os.listdir(SAVES_DIR) if f.endswith('.json')]
            for i, filename in enumerate(files):
                # On enlève le .json pour l'affichage
                display_name = filename[:-5]
                # On crée un bouton pour chaque fichier
                btn = Button(display_name, 250, 100 + (i * 60), 300, 50, GOLD, data=filename)
                self.save_files_buttons.append(btn)
        except Exception as e:
            print(f"Erreur lecture dossier : {e}")

    def draw_text_centered(self, text, font, y, color=WHITE):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(SCREEN_WIDTH//2, y))
        screen.blit(surf, rect)

    def draw_logs(self):
        pygame.draw.rect(screen, (30, 30, 30), (0, 520, SCREEN_WIDTH, 80))
        pygame.draw.line(screen, WHITE, (0, 520), (SCREEN_WIDTH, 520), 2)
        for i, log in enumerate(self.logs[:3]):
            surf = FONT_SMALL.render(f"> {log}", True, LIGHT_GRAY)
            screen.blit(surf, (20, 530 + i * 20))

    def save_current_game(self):
        """Sauvegarde avec le nom du joueur."""
        if self.player:
            # On nettoie le nom pour éviter les bugs de fichier
            safe_name = "".join([c for c in self.player.name if c.isalnum() or c in (' ', '_')]).strip()
            filename = f"{safe_name}.json"
            filepath = os.path.join(SAVES_DIR, filename)
            
            try:
                with open(filepath, 'w') as f:
                    json.dump(self.player.to_dict(), f, indent=4)
                self.add_log(f"Sauvegardé : {filename}")
            except Exception as e:
                self.add_log("Erreur sauvegarde !")
                print(e)

    def run(self):
        while True:
            pos = pygame.mouse.get_pos()
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                # Bouton retour global (sauf en menu principal)
                if self.state != "MENU" and self.state != "INPUT_NAME" and self.state != "LOAD_MENU":
                    if self.btn_menu.is_clicked(event):
                        self.state = "MENU"

            screen.fill(BLACK)

            # --- MACHINE A ETATS ---
            if self.state == "MENU":
                self.draw_text_centered("RPG MULTI-SAVES", FONT_TITLE, 100, GOLD)
                for btn in [self.btn_new, self.btn_load_menu, self.btn_quit]:
                    btn.check_hover(pos); btn.draw(screen)

                for event in events:
                    if self.btn_new.is_clicked(event):
                        self.state = "INPUT_NAME"; self.input_text = ""
                    if self.btn_load_menu.is_clicked(event):
                        self.refresh_save_list() # On met à jour la liste avant d'afficher
                        self.state = "LOAD_MENU"
                    if self.btn_quit.is_clicked(event):
                        pygame.quit(); sys.exit()

            elif self.state == "LOAD_MENU":
                self.draw_text_centered("CHOISISSEZ UNE SAUVEGARDE", FONT_TITLE, 50, WHITE)
                
                # Afficher les boutons de sauvegarde
                if not self.save_files_buttons:
                    self.draw_text_centered("Aucune sauvegarde trouvée.", FONT_TEXT, 200, LIGHT_GRAY)
                
                for btn in self.save_files_buttons:
                    btn.check_hover(pos); btn.draw(screen)

                self.btn_back.check_hover(pos); self.btn_back.draw(screen)

                for event in events:
                    if self.btn_back.is_clicked(event):
                        self.state = "MENU"
                    
                    # Vérifier clic sur un fichier
                    for btn in self.save_files_buttons:
                        if btn.is_clicked(event):
                            filepath = os.path.join(SAVES_DIR, btn.data)
                            try:
                                with open(filepath, 'r') as f:
                                    self.player = Character.from_dict(json.load(f))
                                self.state = "CAMP"
                                self.add_log(f"Chargé : {self.player.name}")
                            except Exception as e:
                                print(f"Erreur chargement: {e}")

            elif self.state == "INPUT_NAME":
                self.draw_text_centered("Nom du Héros :", FONT_TITLE, 150)
                pygame.draw.rect(screen, WHITE, (250, 220, 300, 50), 2)
                txt_surf = FONT_TEXT.render(self.input_text, True, WHITE)
                screen.blit(txt_surf, (260, 230))

                self.btn_confirm_name.check_hover(pos); self.btn_confirm_name.draw(screen)

                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
                        elif len(self.input_text) < 15 and event.unicode.isalnum(): self.input_text += event.unicode
                    
                    if self.btn_confirm_name.is_clicked(event) and self.input_text:
                        self.player = Character(self.input_text, 100, 15, 5)
                        self.state = "CAMP"
                        self.add_log(f"Bienvenue {self.player.name} !")

            elif self.state == "CAMP":
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                self.draw_text_centered(f"CAMPEMENT - {self.player.name}", FONT_TITLE, 80)
                stats = f"PV: {self.player.hp}/{self.player.max_hp}  |  ATK: {self.player.attack_value}  |  DEF: {self.player.defense_value}"
                self.draw_text_centered(stats, FONT_TEXT, 150, GREEN)

                for btn in [self.btn_explore, self.btn_rest, self.btn_save]:
                    btn.check_hover(pos); btn.draw(screen)
                self.draw_logs()

                for event in events:
                    if self.btn_explore.is_clicked(event):
                        if random.random() < 0.2:
                            self.enemy = Enemy("BOSS Ogre", 80, 20, 5, True)
                            self.add_log("⚠️ UN BOSS APPARAÎT !")
                        else:
                            self.enemy = Enemy("Gobelin", 40, 10, 2)
                            self.add_log("Un ennemi approche !")
                        self.state = "COMBAT"
                    if self.btn_rest.is_clicked(event):
                        msg = self.player.heal(10); self.add_log(msg)
                    if self.btn_save.is_clicked(event):
                        self.save_current_game() # Appel de la nouvelle méthode

            elif self.state == "COMBAT":
                self.draw_text_centered("⚔️ COMBAT ⚔️", FONT_TITLE, 50, RED)
                # Affichage simple Joueur vs Ennemi
                pygame.draw.rect(screen, BLUE, (100, 150, 200, 200), border_radius=10)
                self.draw_text_centered(self.player.name, FONT_TEXT, 130)
                screen.blit(FONT_TEXT.render(f"PV: {self.player.hp}", True, WHITE), (150, 230))
                
                col_enn = RED if self.enemy.is_boss else GRAY
                pygame.draw.rect(screen, col_enn, (500, 150, 200, 200), border_radius=10)
                screen.blit(FONT_TEXT.render(self.enemy.name, True, WHITE), (530, 120))
                screen.blit(FONT_TEXT.render(f"PV: {self.enemy.hp}", True, WHITE), (550, 230))

                self.btn_attack.check_hover(pos); self.btn_attack.draw(screen)
                self.draw_logs()

                for event in events:
                    if self.btn_attack.is_clicked(event):
                        msg = self.player.attack_target(self.enemy); self.add_log(msg)
                        if not self.enemy.is_alive():
                            self.add_log(f"Victoire ! {self.enemy.name} vaincu.")
                            loot = random.choice([("Potion", "heal", 20), ("+2 ATK", "buff", 2)])
                            if loot[1] == "heal": self.player.heal(loot[2]); self.add_log("Loot: Potion !")
                            else: self.player.attack_value += loot[2]; self.add_log("Loot: +2 ATK !")
                            self.state = "CAMP"
                            # Autosave optionnel après victoire ?
                            # self.save_current_game() 
                        else:
                            dmg = max(0, self.enemy.attack_value - self.player.defense_value)
                            self.player.hp -= dmg
                            self.add_log(f"{self.enemy.name} riposte : -{dmg} PV")
                            if not self.player.is_alive():
                                self.add_log("💀 MORT"); self.state = "MENU"

            pygame.display.flip()
            CLOCK.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()