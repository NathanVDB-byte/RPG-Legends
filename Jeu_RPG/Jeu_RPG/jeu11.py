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

# --- DONNÉES DE JEU ---
POSSIBLE_LOOT = [
    {"name": "Potion Soin (15)", "type": "heal", "val": 15, "desc": "Rend 15 PV"},
    {"name": "Grde Potion (30)", "type": "heal", "val": 30, "desc": "Rend 30 PV"},
    {"name": "Elixir Force (+5)", "type": "atk", "val": 5, "desc": "+5 Attaque perm."},
    {"name": "Rage Dragon (+10)", "type": "atk", "val": 10, "desc": "+10 Attaque perm."},
    {"name": "Peau de Pierre (+5)", "type": "def", "val": 5, "desc": "+5 Défense perm."},
    {"name": "Acier Liquide (+10)", "type": "def", "val": 10, "desc": "+10 Défense perm."}
]

FLOOR_ENEMIES = {
    1: [("Gobelin", 30, 8, 0), ("Gobelin Vicieux", 40, 10, 1)],
    2: [("Orc", 50, 12, 2), ("Gobelin Elite", 45, 11, 2)],
    3: [("Orc Guerrier", 70, 15, 4), ("Orc Mage", 60, 18, 1)],
    4: [("Golem de Boue", 90, 12, 8), ("Orc Berserk", 80, 20, 3)],
    5: [("Golem de Pierre", 120, 15, 12), ("Garde Royal", 100, 22, 10)]
}

FLOOR_BOSSES = {
    1: ("👑 Gobelin Royal", 150, 18, 5),
    2: ("👑 Orc Royal", 250, 25, 8),
    3: ("👑 Orc Mage Royal", 350, 35, 10),
    4: ("👑 Golem Ancien", 500, 30, 20),
    5: ("👑 EMPEREUR GOLEM", 800, 50, 30)
}

# --- INIT PYGAME ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini RPG - Classes & Donjon")
CLOCK = pygame.time.Clock()

# --- COULEURS & FONTS ---
WHITE = (255, 255, 255); BLACK = (10, 10, 10); GRAY = (50, 50, 50)
LIGHT_GRAY = (170, 170, 170); RED = (200, 50, 50); DARK_RED = (100, 0, 0)
GREEN = (50, 200, 50); BLUE = (50, 50, 200); GOLD = (218, 165, 32)
PURPLE = (128, 0, 128); DARK_BLUE = (20, 20, 50); ORANGE = (255, 140, 0)
CYAN = (0, 255, 255) # Pour le Mage

FONT_TITLE = pygame.font.SysFont("Arial", 40, bold=True)
FONT_SUBTITLE = pygame.font.SysFont("Arial", 28, bold=True)
FONT_TEXT = pygame.font.SysFont("Arial", 22)
FONT_SMALL = pygame.font.SysFont("Arial", 16)

# --- CLASSES ---
class Character:
    def __init__(self, name, hp, attack, defense, job_class="Guerrier"):
        self.name = name; self.max_hp = hp; self.hp = hp
        self.attack_value = attack; self.defense_value = defense
        self.job_class = job_class # Nouvelle propriété
        self.inventory = []
        self.floor = 1
        self.kills = 0

    def is_alive(self): return self.hp > 0

    def take_damage(self, dmg):
        reduced_dmg = max(0, dmg - (self.defense_value // 2))
        block_chance = min(50, self.defense_value * 2)
        is_blocked = False
        if random.randint(0, 100) < block_chance:
            is_blocked = True
            reduced_dmg = reduced_dmg // 2
        self.hp -= reduced_dmg
        return reduced_dmg, is_blocked

    def attack_target(self, target):
        crit = 2 if random.random() < 0.1 else 1
        raw_dmg = self.attack_value * crit
        actual, blocked = target.take_damage(raw_dmg)
        crit_str = " (CRIT!)" if crit > 1 else ""
        block_str = " [PARÉ]" if blocked else ""
        return f"{self.name} attaque{crit_str}{block_str}: -{actual} PV"

    def heal(self, amount):
        old = self.hp; self.hp = min(self.max_hp, self.hp + amount)
        return f"Soin: +{self.hp - old} PV"

    def to_dict(self):
        return {
            "name": self.name, "max_hp": self.max_hp, "hp": self.hp, 
            "attack": self.attack_value, "defense": self.defense_value, 
            "inventory": self.inventory, "floor": self.floor, "kills": self.kills,
            "job_class": self.job_class
        }

    @classmethod
    def from_dict(cls, data):
        c = cls(data["name"], data["max_hp"], data["attack"], data["defense"], data.get("job_class", "Aventurier"))
        c.hp = data["hp"]
        c.inventory = data.get("inventory", [])
        c.floor = data.get("floor", 1)
        c.kills = data.get("kills", 0)
        return c

class Enemy(Character):
    def __init__(self, name, hp, attack, defense, is_boss=False):
        super().__init__(name, hp, attack, defense, "Monstre")
        self.is_boss = is_boss

class Button:
    def __init__(self, text, x, y, w, h, color, data=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text; self.color = color; self.data = data
        self.hover = False; self.disabled = False; self.selected = False # Nouvel attribut

    def draw(self, surface):
        if self.disabled:
            draw_col = GRAY
        elif self.hover:
            draw_col = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255))
        else:
            draw_col = self.color
            
        pygame.draw.rect(surface, draw_col, self.rect, border_radius=8)
        
        # Bordure spéciale si sélectionné
        border_col = GOLD if self.selected else WHITE
        border_width = 4 if self.selected else 2
        pygame.draw.rect(surface, border_col, self.rect, border_width, border_radius=8)
        
        txt_surf = FONT_TEXT.render(self.text, True, WHITE)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos):
        if not self.disabled: self.hover = self.rect.collidepoint(pos)

    def is_clicked(self, event):
        if self.disabled: return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover: return True
        return False

# --- MOTEUR ---
class Game:
    def __init__(self):
        self.state = "MENU"
        self.player = None
        self.enemy = None
        self.logs = ["Bienvenue !"]
        self.input_text = ""
        self.save_files_buttons = []; self.item_buttons = []
        self.next_rest_time = 0
        self.selected_class = "Guerrier" # Classe par défaut
        self.setup_ui()

    def add_log(self, msg):
        self.logs.insert(0, msg)
        if len(self.logs) > 6: self.logs.pop()

    def setup_ui(self):
        # Menu Principal
        self.btn_new = Button("Nouvelle Partie", 300, 200, 200, 50, BLUE)
        self.btn_load_menu = Button("Charger Partie", 300, 270, 200, 50, GREEN)
        self.btn_quit = Button("Quitter", 300, 340, 200, 50, RED)
        
        # Choix de Classe (Boutons carrés alignés)
        self.btn_class_warrior = Button("Guerrier", 150, 300, 150, 100, RED, "Guerrier")
        self.btn_class_tank = Button("Tank", 325, 300, 150, 100, GRAY, "Tank")
        self.btn_class_mage = Button("Mage", 500, 300, 150, 100, BLUE, "Mage")
        self.class_buttons = [self.btn_class_warrior, self.btn_class_tank, self.btn_class_mage]

        # Validation Création
        self.btn_confirm_name = Button("Lancer l'aventure", 300, 450, 200, 50, GREEN)

        # Stats
        self.btn_resume = Button("Reprendre", 250, 430, 300, 50, GREEN)
        self.btn_back_stats = Button("Choisir un autre", 250, 490, 300, 40, GRAY)
        self.btn_delete = Button("💀 Mort Définitive", 550, 530, 180, 40, DARK_RED)

        # Camp
        self.btn_explore = Button("Explorer (Combat)", 50, 450, 200, 50, RED)
        self.btn_rest = Button("Se Reposer (+10PV)", 270, 450, 220, 50, GREEN)
        self.btn_inventory = Button("Inventaire / Items", 270, 380, 220, 50, PURPLE)
        self.btn_save = Button("Sauvegarder", 510, 450, 200, 50, BLUE)
        self.btn_menu = Button("Menu Principal", 510, 20, 200, 40, GRAY)

        # Inv/Load/Combat
        self.btn_back_inv = Button("Retour Camp", 300, 530, 200, 40, GRAY)
        self.btn_attack = Button("ATTAQUER", 200, 450, 200, 60, RED)
        self.btn_flee = Button("FUIR 🏃", 420, 450, 180, 60, ORANGE)
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
            start_x, start_y = 50, 100; col_width = 240; row_height = 100; cols = 3
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
                with open(filepath, 'w') as f: json.dump(self.player.to_dict(), f, indent=4)
                self.add_log(f"Sauvegarde auto.")
            except Exception as e: print(e)

    def delete_current_save(self):
        if self.player:
            safe_name = "".join([c for c in self.player.name if c.isalnum() or c in (' ', '_')]).strip()
            filename = f"{safe_name}.json"
            filepath = os.path.join(SAVES_DIR, filename)
            try:
                if os.path.exists(filepath): os.remove(filepath)
            except Exception as e: print(e)

    def spawn_enemy(self):
        floor = self.player.floor
        kills = self.player.kills

        if kills >= 10:
            boss_data = FLOOR_BOSSES.get(floor, ("BOSS INCONNU", 1000, 50, 50))
            name, hp, atk, defense = boss_data
            self.enemy = Enemy(name, hp, atk, defense, is_boss=True)
            self.add_log(f"⚠️ BOSS ÉTAGE {floor}: {name} !")
        else:
            safe_floor = min(floor, 5) 
            possible_mobs = FLOOR_ENEMIES.get(safe_floor)
            name, base_hp, base_atk, base_def = random.choice(possible_mobs)
            factor = random.uniform(0.8, 1.2)
            infinite_scaling = 1 + (max(0, floor - 5) * 0.2)
            
            final_hp = int(base_hp * factor * infinite_scaling)
            final_atk = int(base_atk * factor * infinite_scaling)
            final_def = int(base_def * factor * infinite_scaling)
            
            self.enemy = Enemy(name, final_hp, final_atk, final_def, is_boss=False)
            self.add_log(f"⚔️ {name} (Niv.{floor}) apparaît !")

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

            # MENU
            if self.state == "MENU":
                self.draw_text_centered("DONJON INFINI", FONT_TITLE, 100, GOLD)
                for btn in [self.btn_new, self.btn_load_menu, self.btn_quit]:
                    btn.check_hover(pos); btn.draw(screen)
                for event in events:
                    if self.btn_new.is_clicked(event):
                        self.state = "INPUT_NAME"; self.input_text = ""
                        self.selected_class = "Guerrier" # Reset
                    if self.btn_load_menu.is_clicked(event): self.refresh_save_list(); self.state = "LOAD_MENU"
                    if self.btn_quit.is_clicked(event): pygame.quit(); sys.exit()

            # INPUT NAME (NOUVEAU)
            elif self.state == "INPUT_NAME":
                self.draw_text_centered("Création du Personnage", FONT_TITLE, 50)
                
                # Saisie Nom
                self.draw_text_centered("Nom du Héros :", FONT_TEXT, 120)
                pygame.draw.rect(screen, WHITE, (250, 140, 300, 40), 2)
                txt_surf = FONT_TEXT.render(self.input_text, True, WHITE)
                screen.blit(txt_surf, (260, 150))
                
                # Choix Classe
                self.draw_text_centered("Choisissez votre Classe :", FONT_TEXT, 250)
                
                for btn in self.class_buttons:
                    # Gestion sélection visuelle
                    btn.selected = (btn.data == self.selected_class)
                    btn.check_hover(pos)
                    btn.draw(screen)
                    
                    # Affichage stats sous les boutons
                    if btn.data == "Guerrier":   desc = "PV:100 ATK:15 DEF:5"
                    elif btn.data == "Tank":     desc = "PV:120 ATK:10 DEF:12"
                    elif btn.data == "Mage":     desc = "PV:70 ATK:22 DEF:3"
                    
                    screen.blit(FONT_SMALL.render(desc, True, WHITE), (btn.rect.x + 10, btn.rect.y + 110))

                self.btn_confirm_name.check_hover(pos); self.btn_confirm_name.draw(screen)

                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
                        elif len(self.input_text) < 15 and event.unicode.isalnum(): self.input_text += event.unicode
                    
                    # Clic sur une classe
                    for btn in self.class_buttons:
                        if btn.is_clicked(event):
                            self.selected_class = btn.data
                    
                    # Validation
                    if self.btn_confirm_name.is_clicked(event) and self.input_text:
                        # Application des stats selon la classe
                        if self.selected_class == "Guerrier": hp=100; atk=15; defense=5
                        elif self.selected_class == "Tank":   hp=120; atk=10; defense=12
                        elif self.selected_class == "Mage":   hp=70;  atk=22; defense=3
                        
                        self.player = Character(self.input_text, hp, atk, defense, self.selected_class)
                        self.state = "CAMP"; self.save_current_game()

            # LOAD
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

            # STATS
            elif self.state == "STATS_VIEW":
                pygame.draw.rect(screen, DARK_BLUE, (100, 80, 600, 380), border_radius=15)
                pygame.draw.rect(screen, GOLD, (100, 80, 600, 380), 3, border_radius=15)
                self.draw_text_centered(f"FICHE DU HÉROS", FONT_TITLE, 130, GOLD)
                p = self.player
                self.draw_text_centered(f"{p.name} - {p.job_class}", FONT_SUBTITLE, 200) # Affiche la classe
                screen.blit(FONT_TEXT.render(f"❤️ Santé : {p.hp}/{p.max_hp}", True, WHITE), (250, 260))
                screen.blit(FONT_TEXT.render(f"⚔️ Attaque : {p.attack_value}", True, WHITE), (250, 300))
                block_pct = min(50, p.defense_value * 2)
                screen.blit(FONT_TEXT.render(f"🛡️ Défense : {p.defense_value} ({block_pct}%)", True, WHITE), (250, 340))
                
                prog_txt = f"🏰 Étage : {p.floor}  |  💀 Kills étage : {p.kills}/10"
                screen.blit(FONT_TEXT.render(prog_txt, True, ORANGE), (250, 380))
                
                self.btn_resume.check_hover(pos); self.btn_resume.draw(screen)
                self.btn_back_stats.check_hover(pos); self.btn_back_stats.draw(screen)
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                self.btn_delete.check_hover(pos); self.btn_delete.draw(screen)

                for event in events:
                    if self.btn_resume.is_clicked(event): self.state = "CAMP"
                    if self.btn_back_stats.is_clicked(event): self.state = "LOAD_MENU"
                    if self.btn_delete.is_clicked(event):
                        self.delete_current_save(); self.player = None; self.refresh_save_list(); self.state = "LOAD_MENU"

            # INVENTORY
            elif self.state == "INVENTORY":
                self.draw_text_centered("INVENTAIRE", FONT_TITLE, 50, PURPLE)
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
                            if item["type"] == "heal": self.add_log(self.player.heal(item["val"]))
                            elif item["type"] == "atk":
                                self.player.attack_value += item["val"]; self.add_log(f"+{item['val']} ATK")
                            elif item["type"] == "def":
                                self.player.defense_value += item["val"]; self.add_log(f"+{item['val']} DEF")
                            self.player.inventory.remove(item); self.refresh_inventory_ui(); self.save_current_game(); break

            # CAMP
            elif self.state == "CAMP":
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                self.draw_text_centered(f"ÉTAGE {self.player.floor}", FONT_TITLE, 80)
                self.draw_text_centered(f"{self.player.name} (PV: {self.player.hp})", FONT_SUBTITLE, 140, GREEN)
                
                prog = min(1.0, self.player.kills / 10)
                pygame.draw.rect(screen, GRAY, (250, 180, 300, 20))
                pygame.draw.rect(screen, ORANGE, (250, 180, 300 * prog, 20))
                screen.blit(FONT_SMALL.render(f"Boss: {self.player.kills}/10", True, WHITE), (350, 182))

                time_left = self.next_rest_time - current_time
                if time_left > 0: self.btn_rest.text = f"Repos ({time_left//1000}s)"; self.btn_rest.disabled = True
                else: self.btn_rest.text = "Se Reposer (+10PV)"; self.btn_rest.disabled = False
                
                for btn in [self.btn_explore, self.btn_rest, self.btn_inventory, self.btn_save]:
                    btn.check_hover(pos); btn.draw(screen)
                self.draw_logs()

                for event in events:
                    if self.btn_explore.is_clicked(event):
                        self.spawn_enemy()
                        self.state = "COMBAT"
                    if self.btn_rest.is_clicked(event):
                        self.add_log(self.player.heal(10)); self.next_rest_time = current_time + 60000 
                    if self.btn_save.is_clicked(event): self.save_current_game()
                    if self.btn_inventory.is_clicked(event):
                        self.refresh_inventory_ui(); self.state = "INVENTORY"

            # COMBAT
            elif self.state == "COMBAT":
                self.draw_text_centered("COMBAT", FONT_TITLE, 50, RED)
                pygame.draw.rect(screen, BLUE, (100, 150, 200, 200), border_radius=10)
                self.draw_text_centered(self.player.name, FONT_TEXT, 130)
                screen.blit(FONT_TEXT.render(f"PV: {self.player.hp}", True, WHITE), (150, 230))
                
                col_enn = GOLD if self.enemy.is_boss else GRAY
                pygame.draw.rect(screen, col_enn, (500, 150, 200, 200), border_radius=10)
                screen.blit(FONT_TEXT.render(self.enemy.name, True, WHITE), (530, 120))
                screen.blit(FONT_TEXT.render(f"PV: {self.enemy.hp}", True, WHITE), (550, 230))

                self.btn_attack.check_hover(pos); self.btn_attack.draw(screen)
                self.btn_flee.check_hover(pos); self.btn_flee.draw(screen)
                self.draw_logs()

                for event in events:
                    if self.btn_attack.is_clicked(event):
                        self.add_log(self.player.attack_target(self.enemy))
                        if not self.enemy.is_alive():
                            # VICTOIRE
                            if self.enemy.is_boss:
                                self.player.floor += 1; self.player.kills = 0
                                self.add_log("🏆 BOSS VAINCU ! ÉTAGE SUIVANT !")
                                self.player.inventory.append(random.choice(POSSIBLE_LOOT).copy())
                            else:
                                self.player.kills += 1
                                self.add_log(f"Ennemi vaincu ({self.player.kills}/10)")
                            
                            if random.random() < 0.6:
                                loot_item = random.choice(POSSIBLE_LOOT).copy()
                                self.player.inventory.append(loot_item)
                                self.add_log(f"Loot: {loot_item['name']}")
                            self.state = "CAMP"; self.save_current_game()
                        else:
                            dmg, blocked = self.player.take_damage(self.enemy.attack_value)
                            block_msg = " [BLOQUÉ]" if blocked else ""
                            self.add_log(f"RIPOSTE : -{dmg} PV{block_msg}")
                            if not self.player.is_alive(): self.state = "MENU"
                    
                    if self.btn_flee.is_clicked(event):
                        if self.enemy.is_boss:
                            self.add_log("⛔ Impossible de fuir un BOSS !")
                            dmg, blocked = self.player.take_damage(self.enemy.attack_value)
                            self.add_log(f"Attaque Gratuite : -{dmg} PV")
                            if not self.player.is_alive(): self.state = "MENU"
                        elif random.random() < 0.5:
                            self.add_log("🏃 Fuite réussie !"); self.state = "CAMP"
                        else:
                            self.add_log("⛔ Fuite ratée !")
                            dmg, blocked = self.player.take_damage(self.enemy.attack_value)
                            self.add_log(f"Coups reçus : -{dmg} PV")
                            if not self.player.is_alive(): self.state = "MENU"

            pygame.display.flip()
            CLOCK.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()