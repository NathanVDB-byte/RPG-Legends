import pygame
import sys
import json
import random
import os

# --- INITIALISATION PYGAME ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini RPG - Pygame Edition")
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

SAVE_FILE = "savegame.json"

# --- CLASSES LOGIQUES (Mêmes que précédemment) ---
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

# --- CLASSES UI ---
class Button:
    def __init__(self, text, x, y, w, h, color, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.action = action
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
        self.state = "MENU" # MENU, INPUT_NAME, CAMP, COMBAT
        self.player = None
        self.enemy = None
        self.logs = ["Bienvenue dans le jeu !"]
        self.input_text = ""
        
        # UI Elements
        self.setup_ui()

    def add_log(self, msg):
        self.logs.insert(0, msg)
        if len(self.logs) > 6:
            self.logs.pop()

    def setup_ui(self):
        # Menu Buttons
        self.btn_new = Button("Nouvelle Partie", 300, 200, 200, 50, BLUE)
        self.btn_load = Button("Charger", 300, 270, 200, 50, GREEN)
        self.btn_quit = Button("Quitter", 300, 340, 200, 50, RED)
        
        # Input Button
        self.btn_confirm_name = Button("Valider", 300, 300, 200, 50, BLUE)

        # Camp Buttons
        self.btn_explore = Button("Explorer (Combat)", 50, 450, 200, 50, RED)
        self.btn_rest = Button("Se Reposer (+10PV)", 270, 450, 220, 50, GREEN)
        self.btn_save = Button("Sauvegarder", 510, 450, 200, 50, BLUE)
        self.btn_menu = Button("Menu Principal", 510, 20, 200, 40, GRAY)

        # Combat Buttons
        self.btn_attack = Button("ATTAQUER", 300, 450, 200, 60, RED)

    def draw_text_centered(self, text, font, y, color=WHITE):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(SCREEN_WIDTH//2, y))
        screen.blit(surf, rect)

    def draw_logs(self):
        # Zone de logs en bas
        pygame.draw.rect(screen, (30, 30, 30), (0, 520, SCREEN_WIDTH, 80))
        pygame.draw.line(screen, WHITE, (0, 520), (SCREEN_WIDTH, 520), 2)
        
        for i, log in enumerate(self.logs[:3]): # Affiche les 3 derniers logs
            surf = FONT_SMALL.render(f"> {log}", True, LIGHT_GRAY)
            screen.blit(surf, (20, 530 + i * 20))

    def run(self):
        while True:
            pos = pygame.mouse.get_pos()
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                # Gestion des clics boutons globaux
                if self.state != "MENU" and self.state != "INPUT_NAME":
                    if self.btn_menu.is_clicked(event):
                        self.state = "MENU"

            screen.fill(BLACK)

            # --- MACHINE A ETATS ---
            if self.state == "MENU":
                self.draw_text_centered("MINI RPG LEGENDS", FONT_TITLE, 100, GOLD)
                
                for btn in [self.btn_new, self.btn_load, self.btn_quit]:
                    btn.check_hover(pos)
                    btn.draw(screen)

                for event in events:
                    if self.btn_new.is_clicked(event):
                        self.state = "INPUT_NAME"
                        self.input_text = ""
                    if self.btn_load.is_clicked(event):
                        if os.path.exists(SAVE_FILE):
                            with open(SAVE_FILE, 'r') as f:
                                self.player = Character.from_dict(json.load(f))
                            self.state = "CAMP"
                            self.add_log("Partie chargée !")
                    if self.btn_quit.is_clicked(event):
                        pygame.quit(); sys.exit()

            elif self.state == "INPUT_NAME":
                self.draw_text_centered("Nom de votre Héros :", FONT_TITLE, 150)
                
                # Zone de texte
                pygame.draw.rect(screen, WHITE, (250, 220, 300, 50), 2)
                txt_surf = FONT_TEXT.render(self.input_text, True, WHITE)
                screen.blit(txt_surf, (260, 230))

                self.btn_confirm_name.check_hover(pos)
                self.btn_confirm_name.draw(screen)

                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        elif len(self.input_text) < 15 and event.unicode.isalnum():
                            self.input_text += event.unicode
                    
                    if self.btn_confirm_name.is_clicked(event) and self.input_text:
                        self.player = Character(self.input_text, 100, 15, 5)
                        self.state = "CAMP"
                        self.add_log(f"Bienvenue {self.player.name} !")

            elif self.state == "CAMP":
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                self.draw_text_centered(f"CAMPEMENT - {self.player.name}", FONT_TITLE, 80)
                
                # Stats
                stats = f"PV: {self.player.hp}/{self.player.max_hp}  |  ATK: {self.player.attack_value}  |  DEF: {self.player.defense_value}"
                self.draw_text_centered(stats, FONT_TEXT, 150, GREEN)

                # Boutons Actions
                for btn in [self.btn_explore, self.btn_rest, self.btn_save]:
                    btn.check_hover(pos)
                    btn.draw(screen)

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
                        msg = self.player.heal(10)
                        self.add_log(msg)
                    
                    if self.btn_save.is_clicked(event):
                        with open(SAVE_FILE, 'w') as f:
                            json.dump(self.player.to_dict(), f)
                        self.add_log("Partie sauvegardée.")

            elif self.state == "COMBAT":
                self.draw_text_centered("⚔️ COMBAT ⚔️", FONT_TITLE, 50, RED)

                # Joueur (Gauche)
                pygame.draw.rect(screen, BLUE, (100, 150, 200, 200), border_radius=10)
                self.draw_text_centered(self.player.name, FONT_TEXT, 130) # Nom un peu décalé
                screen.blit(FONT_TEXT.render(f"PV: {self.player.hp}", True, WHITE), (150, 230))
                
                # Ennemi (Droite)
                col_enn = RED if self.enemy.is_boss else GRAY
                pygame.draw.rect(screen, col_enn, (500, 150, 200, 200), border_radius=10)
                screen.blit(FONT_TEXT.render(self.enemy.name, True, WHITE), (530, 120))
                screen.blit(FONT_TEXT.render(f"PV: {self.enemy.hp}", True, WHITE), (550, 230))

                self.btn_attack.check_hover(pos)
                self.btn_attack.draw(screen)
                
                self.draw_logs()

                for event in events:
                    if self.btn_attack.is_clicked(event):
                        # Tour Joueur
                        msg = self.player.attack_target(self.enemy)
                        self.add_log(msg)
                        
                        # Mort Ennemi ?
                        if not self.enemy.is_alive():
                            self.add_log(f"Victoire ! {self.enemy.name} vaincu.")
                            loot = random.choice([("Potion", "heal", 20), ("+2 ATK", "buff", 2)])
                            if loot[1] == "heal":
                                self.player.heal(loot[2])
                                self.add_log("Loot: Potion bue !")
                            else:
                                self.player.attack_value += loot[2]
                                self.add_log("Loot: +2 ATK !")
                            self.state = "CAMP"
                        else:
                            # Tour Ennemi
                            dmg = max(0, self.enemy.attack_value - self.player.defense_value)
                            self.player.hp -= dmg
                            self.add_log(f"{self.enemy.name} riposte : -{dmg} PV")
                            
                            if not self.player.is_alive():
                                self.add_log("💀 VOUS ÊTES MORT")
                                self.state = "MENU" # Retour brutal au menu

            pygame.display.flip()
            CLOCK.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()