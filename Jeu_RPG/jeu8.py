import pygame
import sys
import json
import random
import os

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVES_DIR = os.path.join(BASE_DIR, "saves")
if not os.path.exists(SAVES_DIR):
    os.makedirs(SAVES_DIR)

# --- BASE DE DONNÉES ITEMS ---
POSSIBLE_LOOT = [
    {"name": "Potion Soin (15)", "type": "heal", "val": 15, "desc": "Rend 15 PV"},
    {"name": "Grde Potion (30)", "type": "heal", "val": 30, "desc": "Rend 30 PV"},
    {"name": "Elixir Force (+5)", "type": "atk", "val": 5, "desc": "+5 Attaque perm."},
    {"name": "Rage du Dragon (+10)", "type": "atk", "val": 10, "desc": "+10 Attaque perm."}
]

# --- INIT PYGAME ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini RPG - Gestion Complète")
CLOCK = pygame.time.Clock()

# --- COULEURS & FONTS ---
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
GRAY = (50, 50, 50)
LIGHT_GRAY = (170, 170, 170)
RED = (200, 50, 50)
DARK_RED = (100, 0, 0) # Pour le bouton suppression
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
GOLD = (218, 165, 32)
PURPLE = (128, 0, 128)
DARK_BLUE = (20, 20, 50)
ORANGE = (255, 140, 0)

FONT_TITLE = pygame.font.SysFont("Arial", 40, bold=True)
FONT_SUBTITLE = pygame.font.SysFont("Arial", 28, bold=True)
FONT_TEXT = pygame.font.SysFont("Arial", 22)
FONT_SMALL = pygame.font.SysFont("Arial", 16)

# --- CLASSES LOGIQUES ---
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
        return f"Soin: +{self.hp - old} PV"

    def to_dict(self):
        return {
            "name": self.name, "max_hp": self.max_hp, "hp": self.hp, 
            "attack": self.attack_value, "defense": self.defense_value, 
            "inventory": self.inventory
        }

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

# --- UI BUTTON ---
class Button:
    def __init__(self, text, x, y, w, h, color, data=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.data = data
        self.hover = False
        self.disabled = False

    def draw(self, surface):
        if self.disabled:
            draw_col = GRAY
        elif self.hover:
            draw_col = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255))
        else:
            draw_col = self.color
        pygame.draw.rect(surface, draw_col, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        txt_surf = FONT_TEXT.render(self.text, True, WHITE)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos):
        if not self.disabled:
            self.hover = self.rect.collidepoint(pos)

    def is_clicked(self, event):
        if self.disabled: return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            return True
        return False

# --- MOTEUR PRINCIPAL ---
class Game:
    def __init__(self):
        self.state = "MENU" 
        self.player = None
        self.enemy = None
        self.logs = ["Bienvenue !"]
        self.input_text = ""
        self.save_files_buttons = [] 
        self.item_buttons = [] 
        self.next_rest_time = 0 
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
        
        # Input Name
        self.btn_confirm_name = Button("Créer le Héros", 300, 320, 200, 50, BLUE)

        # Stats View
        self.btn_resume = Button("Reprendre l'aventure", 250, 430, 300, 50, GREEN)
        self.btn_back_stats = Button("Choisir un autre", 250, 490, 300, 40, GRAY)
        # NOUVEAU BOUTON : Mort Définitive
        self.btn_delete = Button("💀 Mort Définitive", 550, 530, 180, 40, DARK_RED)

        # Camp
        self.btn_explore = Button("Explorer (Combat)", 50, 450, 200, 50, RED)
        self.btn_rest = Button("Se Reposer (+10PV)", 270, 450, 220, 50, GREEN)
        self.btn_inventory = Button("Inventaire / Items", 270, 380, 220, 50, PURPLE)
        self.btn_save = Button("Sauvegarder", 510, 450, 200, 50, BLUE)
        self.btn_menu = Button("Menu Principal", 510, 20, 200, 40, GRAY)

        # Inventory View
        self.btn_back_inv = Button("Retour Camp", 300, 530, 200, 40, GRAY)

        # Combat
        self.btn_attack = Button("ATTAQUER", 200, 450, 200, 60, RED)
        self.btn_flee = Button("FUIR 🏃", 420, 450, 180, 60, ORANGE)
        
        # Menu Charger
        self.btn_back_load = Button("Retour Menu", 300, 520, 200, 40, GRAY)

    def refresh_save_list(self):
        self.save_files_buttons = []
        if os.path.exists(SAVES_DIR):
            files = [f for f in os.listdir(SAVES_DIR) if f.endswith('.json')]
            for i, filename in enumerate(files[:6]):
                display_name = filename[:-5]
                btn = Button(display_name, 200, 100 + (i * 60), 400, 50, GOLD, data=filename)
                self.save_files_buttons.append(btn)

    def refresh_inventory_ui(self):
        self.item_buttons = []
        if self.player:
            start_x, start_y = 50, 100
            col_width = 240
            row_height = 100
            cols = 3
            for i, item in enumerate(self.player.inventory):
                row = i // cols; col = i % cols
                x = start_x + (col * col_width); y = start_y + (row * row_height)
                btn = Button(item["name"], x, y, 220, 80, PURPLE, data=item)
                self.item_buttons.append(btn)

    def draw_text_centered(self, text, font, y, color=WHITE):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(SCREEN_WIDTH//2, y))
        screen.blit(surf, rect)

    def draw_logs(self):
        pygame.draw.rect(screen, (20, 20, 20), (0, 520, SCREEN_WIDTH, 80))
        pygame.draw.line(screen, WHITE, (0, 520), (SCREEN_WIDTH, 520), 2)
        for i, log in enumerate(self.logs[:3]):
            surf = FONT_SMALL.render(f"> {log}", True, LIGHT_GRAY)
            screen.blit(surf, (20, 530 + i * 20))

    def save_current_game(self):
        if self.player:
            safe_name = "".join([c for c in self.player.name if c.isalnum() or c in (' ', '_')]).strip()
            filename = f"{safe_name}.json"
            filepath = os.path.join(SAVES_DIR, filename)
            try:
                with open(filepath, 'w') as f:
                    json.dump(self.player.to_dict(), f, indent=4)
                self.add_log(f"Sauvegarde auto.")
            except Exception as e: print(e)

    def delete_current_save(self):
        """Supprime définitivement le fichier du joueur actuel."""
        if self.player:
            safe_name = "".join([c for c in self.player.name if c.isalnum() or c in (' ', '_')]).strip()
            filename = f"{safe_name}.json"
            filepath = os.path.join(SAVES_DIR, filename)
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Fichier {filename} supprimé.")
            except Exception as e:
                print(f"Erreur suppression : {e}")

    def run(self):
        while True:
            pos = pygame.mouse.get_pos()
            events = pygame.event.get()
            current_time = pygame.time.get_ticks()

            for event in events:
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if self.state in ["CAMP", "STATS_VIEW", "INVENTORY"]:
                    if self.btn_menu.is_clicked(event): self.state = "MENU"

            screen.fill(BLACK)

            # =================== MENU PRINCIPAL ===================
            if self.state == "MENU":
                self.draw_text_centered("RPG LEGENDS", FONT_TITLE, 100, GOLD)
                for btn in [self.btn_new, self.btn_load_menu, self.btn_quit]:
                    btn.check_hover(pos); btn.draw(screen)

                for event in events:
                    if self.btn_new.is_clicked(event):
                        self.state = "INPUT_NAME"; self.input_text = ""
                    if self.btn_load_menu.is_clicked(event):
                        self.refresh_save_list(); self.state = "LOAD_MENU"
                    if self.btn_quit.is_clicked(event): pygame.quit(); sys.exit()

            # =================== CHARGEMENT ===================
            elif self.state == "LOAD_MENU":
                self.draw_text_centered("CHOIX DU PERSONNAGE", FONT_TITLE, 50, WHITE)
                for btn in self.save_files_buttons: btn.check_hover(pos); btn.draw(screen)
                self.btn_back_load.check_hover(pos); self.btn_back_load.draw(screen)
                for event in events:
                    if self.btn_back_load.is_clicked(event): self.state = "MENU"
                    for btn in self.save_files_buttons:
                        if btn.is_clicked(event):
                            try:
                                with open(os.path.join(SAVES_DIR, btn.data), 'r') as f:
                                    self.player = Character.from_dict(json.load(f))
                                self.state = "STATS_VIEW"
                            except Exception as e: print(e)

            # =================== STATS (Avec Suppr) ===================
            elif self.state == "STATS_VIEW":
                pygame.draw.rect(screen, DARK_BLUE, (100, 80, 600, 380), border_radius=15)
                pygame.draw.rect(screen, GOLD, (100, 80, 600, 380), 3, border_radius=15)
                self.draw_text_centered(f"FICHE DU HÉROS", FONT_TITLE, 130, GOLD)
                p = self.player
                self.draw_text_centered(f"Nom : {p.name}", FONT_SUBTITLE, 200)
                screen.blit(FONT_TEXT.render(f"❤️ Santé : {p.hp}/{p.max_hp}", True, WHITE), (250, 260))
                screen.blit(FONT_TEXT.render(f"⚔️ Attaque : {p.attack_value}", True, WHITE), (250, 300))
                screen.blit(FONT_TEXT.render(f"🛡️ Défense : {p.defense_value}", True, WHITE), (250, 340))
                screen.blit(FONT_TEXT.render(f"🎒 Items : {len(p.inventory)}", True, WHITE), (250, 380))
                
                # Dessin des boutons
                self.btn_resume.check_hover(pos); self.btn_resume.draw(screen)
                self.btn_back_stats.check_hover(pos); self.btn_back_stats.draw(screen)
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                self.btn_delete.check_hover(pos); self.btn_delete.draw(screen) # Bouton Supprimer

                for event in events:
                    if self.btn_resume.is_clicked(event): self.state = "CAMP"
                    if self.btn_back_stats.is_clicked(event): self.state = "LOAD_MENU"
                    
                    # LOGIQUE SUPPRESSION
                    if self.btn_delete.is_clicked(event):
                        self.delete_current_save() # Supprime le fichier
                        self.player = None # Vide la mémoire
                        self.refresh_save_list() # Met à jour la liste
                        self.state = "LOAD_MENU" # Retourne au menu de chargement

            # =================== INVENTAIRE ===================
            elif self.state == "INVENTORY":
                self.draw_text_centered("CLIQUEZ POUR UTILISER", FONT_TITLE, 50, PURPLE)
                for btn in self.item_buttons:
                    btn.check_hover(pos); btn.draw(screen)
                    if btn.hover:
                         desc_txt = FONT_SMALL.render(btn.data["desc"], True, GOLD)
                         screen.blit(desc_txt, (btn.rect.x, btn.rect.y + 55))
                self.btn_back_inv.check_hover(pos); self.btn_back_inv.draw(screen)
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                for event in events:
                    if self.btn_back_inv.is_clicked(event): self.state = "CAMP"
                    for btn in self.item_buttons:
                        if btn.is_clicked(event):
                            item = btn.data
                            if item["type"] == "heal":
                                msg = self.player.heal(item["val"]); self.add_log(msg)
                            elif item["type"] == "atk":
                                self.player.attack_value += item["val"]
                                self.add_log(f"Force accrue ! (+{item['val']} ATK)")
                            self.player.inventory.remove(item)
                            self.refresh_inventory_ui(); self.save_current_game()
                            break

            # =================== INPUT NAME ===================
            elif self.state == "INPUT_NAME":
                self.draw_text_centered("Nommez votre Héros :", FONT_TITLE, 150)
                pygame.draw.rect(screen, WHITE, (250, 240, 300, 50), 2)
                txt_surf = FONT_TEXT.render(self.input_text, True, WHITE)
                screen.blit(txt_surf, (260, 250))
                self.btn_confirm_name.check_hover(pos); self.btn_confirm_name.draw(screen)
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
                        elif len(self.input_text) < 15 and event.unicode.isalnum(): self.input_text += event.unicode
                    if self.btn_confirm_name.is_clicked(event) and self.input_text:
                        self.player = Character(self.input_text, 100, 15, 5)
                        self.state = "CAMP"; self.save_current_game()

            # =================== CAMP ===================
            elif self.state == "CAMP":
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                self.draw_text_centered(f"CAMPEMENT", FONT_TITLE, 80)
                self.draw_text_centered(f"{self.player.name} (PV: {self.player.hp})", FONT_SUBTITLE, 140, GREEN)

                # Timer Repos
                time_left = self.next_rest_time - current_time
                if time_left > 0:
                    self.btn_rest.text = f"Repos ({time_left//1000}s)"
                    self.btn_rest.disabled = True
                else:
                    self.btn_rest.text = "Se Reposer (+10PV)"
                    self.btn_rest.disabled = False
                
                for btn in [self.btn_explore, self.btn_rest, self.btn_inventory, self.btn_save]:
                    btn.check_hover(pos); btn.draw(screen)
                self.draw_logs()

                for event in events:
                    if self.btn_explore.is_clicked(event):
                        self.enemy = Enemy("Gobelin", 40, 10, 2)
                        self.state = "COMBAT"
                    if self.btn_rest.is_clicked(event):
                        self.add_log(self.player.heal(10))
                        self.next_rest_time = current_time + 60000 
                    if self.btn_save.is_clicked(event): self.save_current_game()
                    if self.btn_inventory.is_clicked(event):
                        self.refresh_inventory_ui(); self.state = "INVENTORY"

            # =================== COMBAT ===================
            elif self.state == "COMBAT":
                self.draw_text_centered("COMBAT", FONT_TITLE, 50, RED)
                pygame.draw.rect(screen, BLUE, (100, 150, 200, 200), border_radius=10)
                self.draw_text_centered(self.player.name, FONT_TEXT, 130)
                screen.blit(FONT_TEXT.render(f"PV: {self.player.hp}", True, WHITE), (150, 230))
                pygame.draw.rect(screen, GRAY, (500, 150, 200, 200), border_radius=10)
                screen.blit(FONT_TEXT.render(self.enemy.name, True, WHITE), (530, 120))
                screen.blit(FONT_TEXT.render(f"PV: {self.enemy.hp}", True, WHITE), (550, 230))

                self.btn_attack.check_hover(pos); self.btn_attack.draw(screen)
                self.btn_flee.check_hover(pos); self.btn_flee.draw(screen)
                self.draw_logs()

                for event in events:
                    if self.btn_attack.is_clicked(event):
                        self.add_log(self.player.attack_target(self.enemy))
                        if not self.enemy.is_alive():
                            loot_item = random.choice(POSSIBLE_LOOT).copy()
                            self.player.inventory.append(loot_item)
                            self.add_log(f"Loot: {loot_item['name']}")
                            self.state = "CAMP"; self.save_current_game()
                        else:
                            dmg = max(0, self.enemy.attack_value - self.player.defense_value)
                            self.player.hp -= dmg
                            self.add_log(f"RIPOSTE : -{dmg} PV")
                            if not self.player.is_alive(): self.state = "MENU"
                    
                    if self.btn_flee.is_clicked(event):
                        if random.random() < 0.5:
                            self.add_log("🏃 Fuite réussie !")
                            self.state = "CAMP"
                        else:
                            self.add_log("⛔ Fuite ratée !")
                            dmg = max(0, self.enemy.attack_value - self.player.defense_value)
                            self.player.hp -= dmg
                            self.add_log(f"Coups reçus : -{dmg} PV")
                            if not self.player.is_alive(): self.state = "MENU"

            pygame.display.flip()
            CLOCK.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()