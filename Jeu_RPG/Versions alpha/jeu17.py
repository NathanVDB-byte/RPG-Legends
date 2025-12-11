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

# --- BASES DE DONNÉES ---
POSSIBLE_CONSUMABLES = [
    {"name": "Potion Soin (15)", "type": "heal", "val": 15, "desc": "Rend 15 PV", "cat": "consommable", "base_price": 20},
    {"name": "Grde Potion (30)", "type": "heal", "val": 30, "desc": "Rend 30 PV", "cat": "consommable", "base_price": 45},
    {"name": "Elixir Force (+2)", "type": "atk", "val": 2, "desc": "+2 Base Atk", "cat": "consommable", "base_price": 60},
    {"name": "Peau Pierre (+2)", "type": "def", "val": 2, "desc": "+2 Base Def", "cat": "consommable", "base_price": 60}
]

# Liste standard (Loot gratuit)
POSSIBLE_EQUIPMENT = [
    {"name": "Épée Rouillée", "cat": "equipment", "slot": "weapon", "atk": 5, "def": 0, "hp": 0, "desc": "+5 ATK", "base_price": 10},
    {"name": "Hache Guerre", "cat": "equipment", "slot": "weapon", "atk": 12, "def": -2, "hp": 0, "desc": "+12 ATK/-2 DEF", "base_price": 30},
    {"name": "Casque Cuir", "cat": "equipment", "slot": "head", "atk": 0, "def": 3, "hp": 0, "desc": "+3 DEF", "base_price": 15},
    {"name": "Heaume Acier", "cat": "equipment", "slot": "head", "atk": 0, "def": 6, "hp": 0, "desc": "+6 DEF", "base_price": 40},
    {"name": "Tunique Tissu", "cat": "equipment", "slot": "chest", "atk": 0, "def": 2, "hp": 20, "desc": "+2 DEF/+20 HP", "base_price": 25},
    {"name": "Cotte Mailles", "cat": "equipment", "slot": "chest", "atk": 0, "def": 10, "hp": 10, "desc": "+10 DEF/+10 HP", "base_price": 55},
    {"name": "Jambières Cuir", "cat": "equipment", "slot": "legs", "atk": 0, "def": 4, "hp": 0, "desc": "+4 DEF", "base_price": 20},
    {"name": "Bottes Marche", "cat": "equipment", "slot": "feet", "atk": 0, "def": 2, "hp": 0, "desc": "+2 DEF", "base_price": 10},
    {"name": "Anneau Vie", "cat": "equipment", "slot": "ring", "atk": 0, "def": 0, "hp": 40, "desc": "+40 HP", "base_price": 80},
    {"name": "Anneau Rage", "cat": "equipment", "slot": "ring", "atk": 5, "def": 0, "hp": 0, "desc": "+5 ATK", "base_price": 70}
]

# Liste Marchand (Items exclusifs ou rares)
MERCHANT_GEAR = [
    {"name": "Katana Aiguisé", "cat": "equipment", "slot": "weapon", "atk": 18, "def": 0, "hp": 0, "desc": "+18 ATK", "base_price": 120},
    {"name": "Masse d'Or", "cat": "equipment", "slot": "weapon", "atk": 14, "def": 2, "hp": 0, "desc": "+14 ATK/+2 DEF", "base_price": 110},
    {"name": "Plastron Doré", "cat": "equipment", "slot": "chest", "atk": 0, "def": 15, "hp": 30, "desc": "+15 DEF/+30 HP", "base_price": 150},
    {"name": "Bottes Vitesse", "cat": "equipment", "slot": "feet", "atk": 2, "def": 4, "hp": 0, "desc": "+2 ATK/+4 DEF", "base_price": 90},
    {"name": "Casque Royal", "cat": "equipment", "slot": "head", "atk": 0, "def": 9, "hp": 10, "desc": "+9 DEF/+10 HP", "base_price": 130}
]

BOSS_LOOT = [
    {"name": "Grde Potion (30)", "type": "heal", "val": 30, "desc": "Rend 30 PV", "cat": "consommable"},
    {"name": "Épée Légendaire", "cat": "equipment", "slot": "weapon", "atk": 25, "def": 5, "hp": 0, "desc": "+25 ATK/+5 DEF"}
]

FLOOR_ENEMIES = {
    1: [("Gobelin", 30, 8, 0), ("Rat Géant", 25, 6, 0)],
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
pygame.display.set_caption("Mini RPG - Merchant Update")
CLOCK = pygame.time.Clock()

# --- COULEURS & FONTS ---
WHITE = (255, 255, 255); BLACK = (10, 10, 10); GRAY = (50, 50, 50)
LIGHT_GRAY = (170, 170, 170); RED = (200, 50, 50); DARK_RED = (100, 0, 0)
GREEN = (50, 200, 50); BLUE = (50, 50, 200); GOLD = (218, 165, 32)
PURPLE = (128, 0, 128); DARK_BLUE = (20, 20, 50); ORANGE = (255, 140, 0)
CYAN = (0, 255, 255)

FONT_TITLE = pygame.font.SysFont("Arial", 40, bold=True)
FONT_SUBTITLE = pygame.font.SysFont("Arial", 28, bold=True)
FONT_TEXT = pygame.font.SysFont("Arial", 20)
FONT_SMALL = pygame.font.SysFont("Arial", 16)

# --- CLASSES ---
class Character:
    def __init__(self, name, hp, attack, defense, job_class="Guerrier"):
        self.name = name
        self.base_max_hp = hp
        self.hp = hp
        self.base_attack = attack
        self.base_defense = defense
        self.job_class = job_class
        self.gold = 0 # NOUVEAU: Portefeuille
        
        self.inventory = [
            {"name": "Potion Soin (15)", "type": "heal", "val": 15, "desc": "Rend 15 PV", "cat": "consommable", "base_price": 20},
            {"name": "Épée Rouillée", "cat": "equipment", "slot": "weapon", "atk": 5, "def": 0, "hp": 0, "desc": "+5 ATK", "base_price": 10}
        ]
        
        self.equipment = {
            "head": None, "chest": None, "legs": None, 
            "feet": None, "weapon": None, "ring": None
        }
        self.floor = 1; self.kills = 0

    @property
    def max_hp(self):
        bonus = sum(item.get("hp", 0) for item in self.equipment.values() if item)
        return self.base_max_hp + bonus

    @property
    def attack_value(self):
        bonus = sum(item.get("atk", 0) for item in self.equipment.values() if item)
        return self.base_attack + bonus

    @property
    def defense_value(self):
        bonus = sum(item.get("def", 0) for item in self.equipment.values() if item)
        return self.base_defense + bonus

    def is_alive(self): return self.hp > 0

    def take_damage(self, dmg):
        total_def = self.defense_value
        reduced_dmg = max(0, dmg - (total_def // 2))
        block_chance = min(60, total_def * 2)
        is_blocked = False
        if random.randint(0, 100) < block_chance:
            is_blocked = True; reduced_dmg //= 2
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
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return f"Soin: +{self.hp - old} PV"

    def equip_item(self, item_index):
        if 0 <= item_index < len(self.inventory):
            item = self.inventory[item_index]
            cat = item.get("cat", "unknown")
            if cat != "equipment" and "slot" not in item:
                return "Pas équipable"
            
            slot = item.get("slot", "weapon")
            new_hp_bonus = item.get("hp", 0)
            
            old_item = self.equipment.get(slot)
            if old_item:
                old_hp_bonus = old_item.get("hp", 0)
                self.hp = max(1, self.hp - old_hp_bonus)
                self.inventory.append(old_item)
            
            self.equipment[slot] = item
            self.inventory.pop(item_index)
            self.hp += new_hp_bonus
            return f"Équipé : {item['name']}"
        return "Erreur"

    def unequip_item(self, slot):
        item = self.equipment.get(slot)
        if item:
            hp_bonus = item.get("hp", 0)
            self.hp = max(1, self.hp - hp_bonus)
            self.inventory.append(item)
            self.equipment[slot] = None
            return "Déséquipé"
        return "Vide"

    def to_dict(self):
        return {
            "name": self.name, "base_max_hp": self.base_max_hp, "hp": self.hp,
            "base_attack": self.base_attack, "base_defense": self.base_defense,
            "inventory": self.inventory, "equipment": self.equipment,
            "floor": self.floor, "kills": self.kills, "job_class": self.job_class,
            "gold": self.gold
        }

    @classmethod
    def from_dict(cls, data):
        c = cls(
            data["name"], 
            data.get("base_max_hp", data.get("max_hp", 100)),
            data.get("base_attack", data.get("attack", 15)),
            data.get("base_defense", data.get("defense", 5)),
            data.get("job_class", "Aventurier")
        )
        c.hp = data["hp"]
        c.gold = data.get("gold", 0) # Charge l'or, sinon 0
        c.inventory = data.get("inventory", [])
        c.equipment = data.get("equipment", {k:None for k in ["head","chest","legs","feet","weapon","ring"]})
        c.floor = data.get("floor", 1); c.kills = data.get("kills", 0)

        # Migration forcée (Réparation)
        repaired_inventory = []
        for item in c.inventory:
            if isinstance(item, dict):
                if "cat" not in item:
                    if "slot" in item: item["cat"] = "equipment"
                    else: item["cat"] = "consommable"
                if "desc" not in item: item["desc"] = "Objet..."
                # Migration prix si absent
                if "base_price" not in item: item["base_price"] = 10
                repaired_inventory.append(item)
        c.inventory = repaired_inventory
        return c

class Enemy(Character):
    def __init__(self, name, hp, attack, defense, is_boss=False):
        super().__init__(name, hp, attack, defense, "Monstre")
        self.is_boss = is_boss
        self.inventory = []

class Button:
    def __init__(self, text, x, y, w, h, color, data=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text; self.color = color; self.data = data
        self.hover = False; self.disabled = False; self.selected = False

    def draw(self, surface, offset_y=0):
        adjusted_rect = self.rect.move(0, offset_y)
        if self.disabled: draw_col = GRAY
        elif self.hover: draw_col = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255))
        else: draw_col = self.color
        
        pygame.draw.rect(surface, draw_col, adjusted_rect, border_radius=8)
        border_col = GOLD if self.selected else WHITE
        border_width = 4 if self.selected else 2
        pygame.draw.rect(surface, border_col, adjusted_rect, border_width, border_radius=8)
        
        display_text = self.text
        if len(display_text) > 15: 
             display_text = display_text[:13] + ".."

        txt_surf = FONT_TEXT.render(display_text, True, WHITE)
        txt_rect = txt_surf.get_rect(center=adjusted_rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos, offset_y=0):
        adjusted_rect = self.rect.move(0, offset_y)
        if not self.disabled: self.hover = adjusted_rect.collidepoint(pos)

    def is_clicked(self, event, offset_y=0, check_bounds=False):
        adjusted_rect = self.rect.move(0, offset_y)
        if self.disabled: return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if adjusted_rect.collidepoint(event.pos):
                if check_bounds:
                    if adjusted_rect.bottom < 100 or adjusted_rect.top > 520: return False
                return True
        return False

# --- MOTEUR ---
class Game:
    def __init__(self):
        self.state = "MENU"
        self.player = None; self.enemy = None
        self.logs = ["Bienvenue !"]
        self.input_text = ""
        self.save_files_buttons = []; self.item_buttons = []
        self.shop_items = [] # Stock du marchand
        self.last_shop_floor = 0 # Pour rafraichir le shop
        self.next_rest_time = 0
        self.selected_class = "Guerrier"
        self.inv_scroll_y = 0
        self.is_fullscreen = False
        self.setup_ui()

    def add_log(self, msg):
        self.logs.insert(0, msg)
        if len(self.logs) > 6: self.logs.pop()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def generate_shop(self):
        # Ne génère un nouveau stock que si on a changé d'étage
        if self.player.floor != self.last_shop_floor:
            self.shop_items = []
            self.last_shop_floor = self.player.floor
            
            # 1. Ajouter les potions (toujours dispo)
            for pot in POSSIBLE_CONSUMABLES:
                item = pot.copy()
                # Prix augmente légèrement avec les étages (inflation)
                item["price"] = int(item["base_price"] * (1 + (self.player.floor * 0.1)))
                self.shop_items.append(item)
            
            # 2. Ajouter 3 équipements aléatoires (Mix Standard + Merchant Exclusive)
            possible_gears = POSSIBLE_EQUIPMENT + MERCHANT_GEAR
            for _ in range(3):
                gear = random.choice(possible_gears).copy()
                # Prix augmente avec l'étage
                gear["price"] = int(gear["base_price"] * (1 + (self.player.floor * 0.2)))
                # Stats scalées
                if gear["atk"] > 0: gear["atk"] += self.player.floor
                if gear["def"] > 0: gear["def"] += (self.player.floor // 2)
                
                self.shop_items.append(gear)

    def setup_ui(self):
        self.btn_new = Button("Nouvelle Partie", 300, 200, 200, 50, BLUE)
        self.btn_load_menu = Button("Charger Partie", 300, 270, 200, 50, GREEN)
        self.btn_quit = Button("Quitter", 300, 340, 200, 50, RED)
        
        self.btn_class_warrior = Button("Guerrier", 150, 300, 150, 100, RED, "Guerrier")
        self.btn_class_tank = Button("Tank", 325, 300, 150, 100, GRAY, "Tank")
        self.btn_class_mage = Button("Mage", 500, 300, 150, 100, BLUE, "Mage")
        self.class_buttons = [self.btn_class_warrior, self.btn_class_tank, self.btn_class_mage]

        self.btn_confirm_name = Button("Lancer l'aventure", 300, 450, 200, 50, GREEN)

        self.btn_resume = Button("Reprendre", 250, 430, 300, 50, GREEN)
        self.btn_back_stats = Button("Choisir un autre", 250, 490, 300, 40, GRAY)
        self.btn_delete = Button("💀 Mort Définitive", 550, 530, 180, 40, DARK_RED)

        self.btn_explore = Button("Explorer (Combat)", 50, 450, 200, 50, RED)
        self.btn_rest = Button("Se Reposer (+10PV)", 270, 450, 220, 50, GREEN)
        self.btn_inventory = Button("Sac à Dos", 270, 380, 150, 50, PURPLE)
        self.btn_equip_menu = Button("🛡️", 430, 380, 60, 50, GOLD)
        
        # NOUVEAU BOUTON MARCHAND
        self.btn_merchant = Button("Marchand 💰", 600, 380, 150, 50, CYAN)
        
        self.btn_save = Button("Sauvegarder", 510, 450, 200, 50, BLUE)
        self.btn_menu = Button("Menu Principal", 510, 20, 200, 40, GRAY)
        self.btn_fullscreen = Button("FS", 750, 20, 30, 30, GRAY)

        self.btn_back_inv = Button("Retour Camp", 300, 530, 200, 40, GRAY)
        self.btn_attack = Button("ATTAQUER", 200, 450, 200, 60, RED)
        self.btn_flee = Button("FUIR 🏃", 420, 450, 180, 60, ORANGE)
        self.btn_back_load = Button("Retour Menu", 300, 520, 200, 40, GRAY)
        
        self.equip_slots_buttons = {
            "head": Button("Tête", 350, 150, 100, 60, DARK_BLUE, "head"),
            "chest": Button("Plastron", 350, 220, 100, 60, DARK_BLUE, "chest"),
            "legs": Button("Jambes", 350, 290, 100, 60, DARK_BLUE, "legs"),
            "feet": Button("Pieds", 350, 360, 100, 60, DARK_BLUE, "feet"),
            "weapon": Button("Arme", 230, 220, 100, 60, RED, "weapon"),
            "ring": Button("Bague", 470, 220, 100, 60, GOLD, "ring")
        }

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
            # --- MENU SAC A DOS (Tout afficher) ---
            if self.state == "INVENTORY":
                start_x, start_y = 50, 100; col_width = 240; row_height = 100; cols = 3
                for i, item in enumerate(self.player.inventory):
                    row = i // cols; col = i % cols
                    x = start_x + (col * col_width); y = start_y + (row * row_height)
                    
                    cat = item.get("cat", "consommable")
                    col_btn = BLUE if cat == "consommable" else PURPLE
                    
                    btn = Button(item["name"], x, y, 220, 80, col_btn, data=(item, i))
                    self.item_buttons.append(btn)
            
            # --- MENU EQUIPEMENT (Filtrer equipement) ---
            elif self.state == "EQUIP_MENU":
                start_x = 50; start_y = 120; row = 0
                for i, item in enumerate(self.player.inventory):
                    cat = item.get("cat", "consommable")
                    if cat == "equipment":
                        x = start_x; y = start_y + (row * 60)
                        btn = Button(item["name"], x, y, 160, 50, PURPLE, data=(item, i))
                        self.item_buttons.append(btn); row += 1
            
            # --- MENU MARCHAND (Items à acheter) ---
            elif self.state == "MERCHANT":
                start_x, start_y = 50, 100; col_width = 240; row_height = 100; cols = 3
                self.generate_shop() # S'assure que le shop est généré
                for i, item in enumerate(self.shop_items):
                    row = i // cols; col = i % cols
                    x = start_x + (col * col_width); y = start_y + (row * row_height)
                    
                    price = item.get("price", 10)
                    can_afford = self.player.gold >= price
                    col_btn = CYAN if can_afford else GRAY
                    
                    btn_text = f"{item['name']} ({price} Or)"
                    btn = Button(btn_text, x, y, 220, 80, col_btn, data=(item, i))
                    if not can_afford: btn.disabled = True
                    
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
        floor = self.player.floor; kills = self.player.kills
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
                
                if event.type == pygame.MOUSEWHEEL and self.state in ["INVENTORY", "EQUIP_MENU", "MERCHANT"]:
                    self.inv_scroll_y += event.y * 30
                    if self.inv_scroll_y > 0: self.inv_scroll_y = 0

                # Boutons Globaux
                if self.state in ["CAMP", "STATS_VIEW", "INVENTORY", "EQUIP_MENU", "MERCHANT"]:
                    if self.btn_menu.is_clicked(event): self.state = "MENU"
                    if self.btn_fullscreen.is_clicked(event): self.toggle_fullscreen()

            screen.fill(BLACK)

            if self.state == "MENU":
                self.draw_text_centered("DONJON INFINI", FONT_TITLE, 100, GOLD)
                for btn in [self.btn_new, self.btn_load_menu, self.btn_quit]:
                    btn.check_hover(pos); btn.draw(screen)
                self.btn_fullscreen.check_hover(pos); self.btn_fullscreen.draw(screen)
                for event in events:
                    if self.btn_new.is_clicked(event):
                        self.state = "INPUT_NAME"; self.input_text = ""; self.selected_class = "Guerrier"
                    if self.btn_load_menu.is_clicked(event): self.refresh_save_list(); self.state = "LOAD_MENU"
                    if self.btn_quit.is_clicked(event): pygame.quit(); sys.exit()
                    if self.btn_fullscreen.is_clicked(event): self.toggle_fullscreen()

            elif self.state == "INPUT_NAME":
                self.draw_text_centered("Création du Personnage", FONT_TITLE, 50)
                self.draw_text_centered("Nom du Héros :", FONT_TEXT, 120)
                pygame.draw.rect(screen, WHITE, (250, 140, 300, 40), 2)
                txt_surf = FONT_TEXT.render(self.input_text, True, WHITE)
                screen.blit(txt_surf, (260, 150))
                self.draw_text_centered("Choisissez votre Classe :", FONT_TEXT, 250)
                for btn in self.class_buttons:
                    btn.selected = (btn.data == self.selected_class)
                    btn.check_hover(pos); btn.draw(screen)
                    if btn.data == "Guerrier":   desc = "PV:100 ATK:15 DEF:5"
                    elif btn.data == "Tank":     desc = "PV:120 ATK:10 DEF:12"
                    elif btn.data == "Mage":     desc = "PV:70 ATK:22 DEF:3"
                    screen.blit(FONT_SMALL.render(desc, True, WHITE), (btn.rect.x + 10, btn.rect.y + 110))
                self.btn_confirm_name.check_hover(pos); self.btn_confirm_name.draw(screen)
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
                        elif len(self.input_text) < 15 and event.unicode.isalnum(): self.input_text += event.unicode
                    for btn in self.class_buttons:
                        if btn.is_clicked(event): self.selected_class = btn.data
                    if self.btn_confirm_name.is_clicked(event) and self.input_text:
                        if self.selected_class == "Guerrier": hp=100; atk=15; defense=5
                        elif self.selected_class == "Tank":   hp=120; atk=10; defense=12
                        elif self.selected_class == "Mage":   hp=70;  atk=22; defense=3
                        self.player = Character(self.input_text, hp, atk, defense, self.selected_class)
                        self.state = "CAMP"; self.save_current_game()

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

            elif self.state == "STATS_VIEW":
                pygame.draw.rect(screen, DARK_BLUE, (100, 80, 600, 380), border_radius=15)
                pygame.draw.rect(screen, GOLD, (100, 80, 600, 380), 3, border_radius=15)
                self.draw_text_centered(f"FICHE DU HÉROS", FONT_TITLE, 130, GOLD)
                p = self.player
                self.draw_text_centered(f"{p.name} - {p.job_class}", FONT_SUBTITLE, 200)
                screen.blit(FONT_TEXT.render(f"❤️ Santé : {p.hp}/{p.max_hp}", True, WHITE), (250, 260))
                screen.blit(FONT_TEXT.render(f"⚔️ Attaque : {p.attack_value}", True, WHITE), (250, 300))
                block_pct = min(60, p.defense_value * 2)
                screen.blit(FONT_TEXT.render(f"🛡️ Défense : {p.defense_value} ({block_pct}%)", True, WHITE), (250, 340))
                screen.blit(FONT_TEXT.render(f"🏰 Étage : {p.floor}  |  💀 Kills : {p.kills}/10", True, ORANGE), (250, 380))
                screen.blit(FONT_TEXT.render(f"💰 Or : {p.gold}", True, GOLD), (250, 420)) # Affichage OR
                
                self.btn_resume.check_hover(pos); self.btn_resume.draw(screen)
                self.btn_back_stats.check_hover(pos); self.btn_back_stats.draw(screen)
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                self.btn_delete.check_hover(pos); self.btn_delete.draw(screen)

                for event in events:
                    if self.btn_resume.is_clicked(event): self.state = "CAMP"
                    if self.btn_back_stats.is_clicked(event): self.state = "LOAD_MENU"
                    if self.btn_delete.is_clicked(event):
                        self.delete_current_save(); self.player = None; self.refresh_save_list(); self.state = "LOAD_MENU"

            elif self.state == "INVENTORY":
                self.draw_text_centered("SAC À DOS", FONT_TITLE, 50, PURPLE)
                self.draw_text_centered(f"💰 Or: {self.player.gold}", FONT_TEXT, 90, GOLD)
                
                clip_rect = pygame.Rect(0, 100, SCREEN_WIDTH, 420)
                screen.set_clip(clip_rect)
                for btn in self.item_buttons:
                    btn.check_hover(pos, self.inv_scroll_y); btn.draw(screen, self.inv_scroll_y)
                    if btn.hover:
                         item, _ = btn.data
                         desc_txt = FONT_SMALL.render(item.get("desc",""), True, GOLD)
                         screen.blit(desc_txt, (btn.rect.x, btn.rect.y + 55 + self.inv_scroll_y))
                screen.set_clip(None)
                
                # Barre de scroll
                pygame.draw.rect(screen, GRAY, (780, 100, 10, 420))
                pygame.draw.rect(screen, WHITE, (780, 100 - (self.inv_scroll_y / 5), 10, 30))

                self.btn_back_inv.check_hover(pos); self.btn_back_inv.draw(screen)
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                self.btn_fullscreen.check_hover(pos); self.btn_fullscreen.draw(screen)
                for event in events:
                    if self.btn_back_inv.is_clicked(event): self.state = "CAMP"; self.inv_scroll_y = 0
                    for btn in self.item_buttons:
                        if btn.is_clicked(event, self.inv_scroll_y, check_bounds=True):
                            item, index = btn.data
                            cat = item.get("cat", "consommable")
                            if cat == "consommable":
                                if item["type"] == "heal": self.add_log(self.player.heal(item["val"]))
                                elif item["type"] == "atk": self.player.base_attack += item["val"]; self.add_log(f"+{item['val']} Base ATK")
                                elif item["type"] == "def": self.player.base_defense += item["val"]; self.add_log(f"+{item['val']} Base DEF")
                                self.player.inventory.pop(index); self.refresh_inventory_ui(); self.save_current_game()
                            else:
                                self.add_log("C'est un équipement, allez dans le menu 🛡️.")
                            break

            elif self.state == "EQUIP_MENU":
                self.draw_text_centered("ÉQUIPEMENT DU HÉROS", FONT_TITLE, 50, GOLD)
                
                clip_rect = pygame.Rect(0, 100, 250, 420)
                screen.set_clip(clip_rect)
                if not self.item_buttons:
                    screen.blit(FONT_SMALL.render("Pas d'équipement...", True, GRAY), (50, 120 + self.inv_scroll_y))
                
                for btn in self.item_buttons:
                    btn.check_hover(pos, self.inv_scroll_y); btn.draw(screen, self.inv_scroll_y)
                    if btn.hover:
                        item, _ = btn.data
                        desc = item.get("desc", "")
                        screen.blit(FONT_SMALL.render(desc, True, GOLD), (btn.rect.right + 10, btn.rect.y + 15 + self.inv_scroll_y))

                screen.set_clip(None)

                for slot_name, btn in self.equip_slots_buttons.items():
                    equipped_item = self.player.equipment.get(slot_name)
                    if equipped_item:
                        d_text = equipped_item["name"]
                        if len(d_text) > 10: d_text = d_text[:8] + ".."
                        btn.text = d_text
                        btn.color = GREEN
                    else:
                        btn.text = slot_name.upper()
                        btn.color = DARK_BLUE
                    btn.check_hover(pos); btn.draw(screen)

                self.btn_back_inv.check_hover(pos); self.btn_back_inv.draw(screen)
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                self.btn_fullscreen.check_hover(pos); self.btn_fullscreen.draw(screen)

                for event in events:
                    if self.btn_back_inv.is_clicked(event): self.state = "CAMP"; self.inv_scroll_y = 0
                    
                    for btn in self.item_buttons:
                         if btn.is_clicked(event, self.inv_scroll_y, check_bounds=True):
                            item, index = btn.data
                            msg = self.player.equip_item(index)
                            self.add_log(msg)
                            self.refresh_inventory_ui()
                            self.save_current_game()
                            break
                    
                    for slot_name, btn in self.equip_slots_buttons.items():
                        if btn.is_clicked(event):
                            msg = self.player.unequip_item(slot_name)
                            self.add_log(msg)
                            self.refresh_inventory_ui()
                            self.save_current_game()

            # --- NOUVEL ÉTAT : MARCHAND ---
            elif self.state == "MERCHANT":
                self.draw_text_centered("MARCHAND ITINÉRANT", FONT_TITLE, 50, CYAN)
                self.draw_text_centered(f"Votre Or: {self.player.gold} 💰", FONT_SUBTITLE, 90, GOLD)
                
                clip_rect = pygame.Rect(0, 120, SCREEN_WIDTH, 400)
                screen.set_clip(clip_rect)
                for btn in self.item_buttons:
                    btn.check_hover(pos, self.inv_scroll_y); btn.draw(screen, self.inv_scroll_y)
                    # Description
                    if btn.hover:
                         item, _ = btn.data
                         desc_txt = FONT_SMALL.render(item.get("desc","") + f" (Prix: {item['price']})", True, WHITE)
                         screen.blit(desc_txt, (btn.rect.x, btn.rect.y + 60 + self.inv_scroll_y))
                screen.set_clip(None)

                self.btn_back_inv.check_hover(pos); self.btn_back_inv.draw(screen)
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                self.btn_fullscreen.check_hover(pos); self.btn_fullscreen.draw(screen)

                for event in events:
                    if self.btn_back_inv.is_clicked(event): self.state = "CAMP"; self.inv_scroll_y = 0
                    for btn in self.item_buttons:
                        if btn.is_clicked(event, self.inv_scroll_y, check_bounds=True):
                            item, index = btn.data
                            price = item.get("price", 999)
                            if self.player.gold >= price:
                                self.player.gold -= price
                                # Copie l'objet pour l'inventaire
                                bought_item = item.copy()
                                self.player.inventory.append(bought_item)
                                self.add_log(f"Acheté : {item['name']}")
                                
                                # Si c'est un équipement unique (pas consommable), on peut l'enlever du shop
                                # Mais pour simplifier, on laisse le stock, le joueur peut en acheter plein s'il veut.
                                self.refresh_inventory_ui() # Met à jour les boutons (Griser si plus d'argent)
                                self.save_current_game()
                            else:
                                self.add_log("Pas assez d'or !")
            
            elif self.state == "CAMP":
                self.btn_menu.check_hover(pos); self.btn_menu.draw(screen)
                self.btn_fullscreen.check_hover(pos); self.btn_fullscreen.draw(screen)
                self.draw_text_centered(f"ÉTAGE {self.player.floor}", FONT_TITLE, 80)
                self.draw_text_centered(f"{self.player.name} (PV: {self.player.hp}/{self.player.max_hp})", FONT_SUBTITLE, 140, GREEN)
                self.draw_text_centered(f"💰 Or: {self.player.gold}", FONT_TEXT, 170, GOLD)
                
                prog = min(1.0, self.player.kills / 10)
                pygame.draw.rect(screen, GRAY, (250, 190, 300, 20))
                pygame.draw.rect(screen, ORANGE, (250, 190, 300 * prog, 20))
                screen.blit(FONT_SMALL.render(f"Boss: {self.player.kills}/10", True, WHITE), (350, 192))

                time_left = self.next_rest_time - current_time
                if time_left > 0: self.btn_rest.text = f"Repos ({time_left//1000}s)"; self.btn_rest.disabled = True
                else: self.btn_rest.text = "Se Reposer (+10PV)"; self.btn_rest.disabled = False
                
                for btn in [self.btn_explore, self.btn_rest, self.btn_inventory, self.btn_save, self.btn_equip_menu, self.btn_merchant]:
                    btn.check_hover(pos); btn.draw(screen)
                self.draw_logs()

                for event in events:
                    if self.btn_explore.is_clicked(event):
                        self.spawn_enemy(); self.state = "COMBAT"
                    if self.btn_rest.is_clicked(event):
                        self.add_log(self.player.heal(10)); self.next_rest_time = current_time + 60000 
                    if self.btn_save.is_clicked(event): self.save_current_game()
                    
                    if self.btn_inventory.is_clicked(event):
                        self.state = "INVENTORY"; self.refresh_inventory_ui()
                    if self.btn_equip_menu.is_clicked(event):
                        self.state = "EQUIP_MENU"; self.refresh_inventory_ui()
                    if self.btn_merchant.is_clicked(event):
                        self.state = "MERCHANT"; self.refresh_inventory_ui()

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
                            gold_gain = 5
                            # Chance de bourse rare
                            if random.random() < 0.2:
                                gold_gain += 15
                                self.add_log("💰 Bourse trouvée ! (+15 Or)")
                            
                            self.player.gold += gold_gain
                            self.add_log(f"Gain: +{gold_gain} Or")
                            
                            if self.enemy.is_boss:
                                self.player.floor += 1; self.player.kills = 0
                                self.add_log("🏆 BOSS VAINCU ! ÉTAGE SUIVANT !")
                                for loot in BOSS_LOOT:
                                    self.player.inventory.append(loot.copy())
                            else:
                                self.player.kills += 1
                                self.add_log(f"Ennemi vaincu ({self.player.kills}/10)")
                                if random.random() < 0.35:
                                    if random.random() < 0.7:
                                        loot_item = random.choice(POSSIBLE_CONSUMABLES).copy()
                                    else:
                                        loot_item = random.choice(POSSIBLE_EQUIPMENT).copy()
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