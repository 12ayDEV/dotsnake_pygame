import pygame
import random
import time
import os
import math
import asyncio
import sys

# --- Konfigurasi Awal ---
GRID_SIZE = 20
GRID_WIDTH = 40   # Mengatur lebar ukuran layar
GRID_HEIGHT = 45  # Mengatur tinggi ukuran layar
HUD_HEIGHT = 80   # Tinggi area HUD
SCREEN_WIDTH = GRID_SIZE * GRID_WIDTH
SCREEN_HEIGHT = (GRID_SIZE * GRID_HEIGHT) + HUD_HEIGHT

# --- Event Timers ---
GAME_TICK = pygame.USEREVENT + 1      # Kecepatan Player
WORLD_TICK = pygame.USEREVENT + 2     # Kecepatan Musuh/Dunia
SPAWN_ENEMY = pygame.USEREVENT + 3    # Spawn Musuh
SPAWN_PICKUP = pygame.USEREVENT + 4   # Spawn Dot/Makanan

# --- Palet Warna Baru (Soft Bright & Distinct) ---
COLOR_BLACK = (10, 10, 15) # Slightly blueish black
COLOR_WHITE = (255, 255, 255)
COLOR_PLAYER_GREEN = (50, 255, 100)      # Bright Soft Green

# Warna Dot (Amunisi) - Soft Bright Colors
COLOR_DOT_RED = (255, 100, 100)       # Soft Red (Standard)
COLOR_DOT_YELLOW = (255, 255, 150)    # Soft Yellow (Charge)
COLOR_DOT_BLUE = (100, 200, 255)      # Soft Cyan/Blue (Shield)

# Warna Musuh & Rintangan - Distinct
COLOR_ENEMY_CHASER = (200, 50, 50)    # Deep Red/Maroon
COLOR_ENEMY_FOLLOWER = (200, 120, 0)  # Dark Orange
COLOR_WALL_CRACKED = (100, 100, 120)  # Blue-ish Grey

# Warna Peluru (Tinted)
COLOR_BULLET_STANDARD = (200, 255, 255) # Cyan tint
COLOR_BULLET_CHARGE = (255, 150, 200)   # Pink tint

# --- Asset Management ---
ASSETS = {}

def get_tinted_image(image, color):
    image = image.copy()
    # Fill with color using MULT to tint
    image.fill(color[0:3] + (255,), special_flags=pygame.BLEND_RGBA_MULT)
    return image

def load_assets():
    asset_dir = os.path.join(os.path.dirname(__file__), 'assets')
    
    def load_img(name, scale=None):
        path = os.path.join(asset_dir, name)
        try:
            img = pygame.image.load(path).convert_alpha()
            if scale:
                img = pygame.transform.scale(img, scale)
            return img
        except Exception as e:
            print(f"Error loading {name}: {e}")
            s = pygame.Surface(scale if scale else (GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
            s.fill((255, 0, 255))
            return s

    ASSETS['dot'] = load_img('dotsnake_dot.png', (GRID_SIZE, GRID_SIZE))
    ASSETS['virus'] = load_img('dotsnake_virus.png', (GRID_SIZE, GRID_SIZE))
    ASSETS['barrier'] = load_img('dotsnake_barrier.png', (GRID_SIZE, GRID_SIZE))
    
    # Load Font
    font_path = os.path.join(asset_dir, 'PressStart2P-Regular.ttf')
    try:
        ASSETS['font'] = pygame.font.Font(font_path, 16) # 16px for 8-bit look
        ASSETS['font_large'] = pygame.font.Font(font_path, 32)
    except Exception as e:
        print(f"Error loading font: {e}")
        ASSETS['font'] = pygame.font.Font(None, 24)
        ASSETS['font_large'] = pygame.font.Font(None, 48)

    # Pre-tint assets for performance
    ASSETS['dot_head'] = get_tinted_image(ASSETS['dot'], COLOR_PLAYER_GREEN)
    ASSETS['dot_standard'] = get_tinted_image(ASSETS['dot'], COLOR_DOT_RED)
    ASSETS['dot_charge'] = get_tinted_image(ASSETS['dot'], COLOR_DOT_YELLOW)
    ASSETS['dot_shield'] = get_tinted_image(ASSETS['dot'], COLOR_DOT_BLUE)
    
    ASSETS['virus_chaser'] = get_tinted_image(ASSETS['virus'], COLOR_ENEMY_CHASER)
    ASSETS['virus_follower'] = get_tinted_image(ASSETS['virus'], COLOR_ENEMY_FOLLOWER)
    
    ASSETS['bullet_standard'] = get_tinted_image(ASSETS['dot'], COLOR_BULLET_STANDARD)
    ASSETS['bullet_charge'] = get_tinted_image(ASSETS['dot'], COLOR_BULLET_CHARGE)

    # Create a background texture
    bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg.fill((10, 10, 20)) # Dark blue-ish black
    # Draw faint grid
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(bg, (20, 20, 40), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(bg, (20, 20, 40), (0, y), (SCREEN_WIDTH, y))
    ASSETS['background'] = bg

# --- Konfigurasi Gameplay ---

# Kecepatan Player (berbasis delay)
FAST_SPEED_DELAY = 70
SLOW_SPEED_DELAY = 250
MAX_LENGTH_FOR_SPEED = 15

import pygame
import random
import time
import os
import math
import asyncio

# --- Konfigurasi Awal ---
GRID_SIZE = 20
GRID_WIDTH = 40   # Mengatur lebar ukuran layar
GRID_HEIGHT = 45  # Mengatur tinggi ukuran layar
HUD_HEIGHT = 80   # Tinggi area HUD
SCREEN_WIDTH = GRID_SIZE * GRID_WIDTH
SCREEN_HEIGHT = (GRID_SIZE * GRID_HEIGHT) + HUD_HEIGHT

# --- Event Timers ---
GAME_TICK = pygame.USEREVENT + 1      # Kecepatan Player
WORLD_TICK = pygame.USEREVENT + 2     # Kecepatan Musuh/Dunia
SPAWN_ENEMY = pygame.USEREVENT + 3    # Spawn Musuh
SPAWN_PICKUP = pygame.USEREVENT + 4   # Spawn Dot/Makanan

# --- Palet Warna Baru (Soft Bright & Distinct) ---
COLOR_BLACK = (10, 10, 15) # Slightly blueish black
COLOR_WHITE = (255, 255, 255)
COLOR_PLAYER_GREEN = (50, 255, 100)      # Bright Soft Green

# Warna Dot (Amunisi) - Soft Bright Colors
COLOR_DOT_RED = (255, 100, 100)       # Soft Red (Standard)
COLOR_DOT_YELLOW = (255, 255, 150)    # Soft Yellow (Charge)
COLOR_DOT_BLUE = (100, 200, 255)      # Soft Cyan/Blue (Shield)

# Warna Musuh & Rintangan - Distinct
COLOR_ENEMY_CHASER = (200, 50, 50)    # Deep Red/Maroon
COLOR_ENEMY_FOLLOWER = (200, 120, 0)  # Dark Orange
COLOR_WALL_CRACKED = (100, 100, 120)  # Blue-ish Grey

# Warna Peluru (Tinted)
COLOR_BULLET_STANDARD = (200, 255, 255) # Cyan tint
COLOR_BULLET_CHARGE = (255, 150, 200)   # Pink tint

# --- Asset Management ---
ASSETS = {}

def get_tinted_image(image, color):
    image = image.copy()
    # Fill with color using MULT to tint
    image.fill(color[0:3] + (255,), special_flags=pygame.BLEND_RGBA_MULT)
    return image

def load_assets():
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(__file__)
        
    asset_dir = os.path.join(base_path, 'assets')
    
    def load_img(name, scale=None):
        path = os.path.join(asset_dir, name)
        try:
            img = pygame.image.load(path).convert_alpha()
            if scale:
                img = pygame.transform.scale(img, scale)
            return img
        except Exception as e:
            print(f"Error loading {name}: {e}")
            s = pygame.Surface(scale if scale else (GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
            s.fill((255, 0, 255))
            return s

    ASSETS['dot'] = load_img('dotsnake_dot.png', (GRID_SIZE, GRID_SIZE))
    ASSETS['head'] = load_img('dotsnake_head.png', (GRID_SIZE, GRID_SIZE))
    ASSETS['shield'] = load_img('dotsnake_shield.png', (GRID_SIZE, GRID_SIZE))
    ASSETS['charge'] = load_img('dotsnake_dot_charge.png', (GRID_SIZE, GRID_SIZE))
    ASSETS['virus'] = load_img('dotsnake_virus.png', (GRID_SIZE, GRID_SIZE))
    ASSETS['barrier'] = load_img('dotsnake_barrier.png', (GRID_SIZE, GRID_SIZE))
    
    # Load Font
    font_path = os.path.join(asset_dir, 'PressStart2P-Regular.ttf')
    try:
        ASSETS['font'] = pygame.font.Font(font_path, 16) # 16px for 8-bit look
        ASSETS['font_large'] = pygame.font.Font(font_path, 32)
    except Exception as e:
        print(f"Error loading font: {e}")
        ASSETS['font'] = pygame.font.Font(None, 24)
        ASSETS['font_large'] = pygame.font.Font(None, 48)

    # Pre-tint assets for performance
    # Use specific sprites if available, otherwise tint the base dot
    ASSETS['dot_head'] = ASSETS['head'] # Use the new head sprite directly
    ASSETS['dot_standard'] = get_tinted_image(ASSETS['dot'], COLOR_DOT_RED)
    ASSETS['dot_charge'] = ASSETS['charge'] # Use the new charge sprite directly
    ASSETS['dot_shield'] = ASSETS['shield'] # Use the new shield sprite directly
    
    ASSETS['virus_chaser'] = get_tinted_image(ASSETS['virus'], COLOR_ENEMY_CHASER)
    ASSETS['virus_follower'] = get_tinted_image(ASSETS['virus'], COLOR_ENEMY_FOLLOWER)
    
    ASSETS['bullet_standard'] = get_tinted_image(ASSETS['dot'], COLOR_BULLET_STANDARD)
    ASSETS['bullet_charge'] = get_tinted_image(ASSETS['dot'], COLOR_BULLET_CHARGE)

    # Create a background texture
    bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg.fill((10, 10, 20)) # Dark blue-ish black
    # Draw faint grid
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(bg, (20, 20, 40), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(bg, (20, 20, 40), (0, y), (SCREEN_WIDTH, y))
    ASSETS['background'] = bg

# --- Konfigurasi Gameplay ---

# Kecepatan Player (berbasis delay)
FAST_SPEED_DELAY = 70
SLOW_SPEED_DELAY = 250
MAX_LENGTH_FOR_SPEED = 15

# Kecepatan Dunia (Musuh/Rintangan)
INITIAL_WORLD_SPEED = 500 # Delay awal (Slower start)
MIN_WORLD_SPEED = 60      # Delay tercepat
SCORE_MILESTONE = 50      # Percepat setiap 50 tick dunia
SPEED_INCREASE_AMOUNT = 5 # Pengurangan delay

# --- Helper for Interpolation ---
def lerp(start, end, t):
    return start + (end - start) * t

# --- Particle System ---
class Particle:
    def __init__(self, x, y, color, size, speed_range=(1, 4), life_range=(20, 40)):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(*life_range)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1) 
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0: return
        alpha = int((self.life / self.max_life) * 255)
        s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=10, size=4):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, size))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

# --- Class untuk Player (Dotsnake) ---
class Player:
    def __init__(self, particle_system):
        self.particle_system = particle_system
        start_y = GRID_HEIGHT - 5
        
        # Logical Body (Grid Coordinates)
        self.body = [
            {"type": "head", "rect": pygame.Rect(GRID_WIDTH // 2, start_y, 1, 1)},
            {"type": "standard", "rect": pygame.Rect(GRID_WIDTH // 2, start_y + 1, 1, 1)},
            {"type": "standard", "rect": pygame.Rect(GRID_WIDTH // 2, start_y + 2, 1, 1)},
        ]
        
        # Visual Body (Pixel Coordinates for Interpolation)
        # Initialize visual positions to match logical positions
        self.visual_body = []
        for segment in self.body:
            self.visual_body.append({
                "x": segment["rect"].x * GRID_SIZE,
                "y": segment["rect"].y * GRID_SIZE,
                "prev_x": segment["rect"].x * GRID_SIZE,
                "prev_y": segment["rect"].y * GRID_SIZE
            })

        self.lives = 3
        self.shields = 0 # New shield mechanic
        self.dx = 0
        self.dy = -1 
        
        self.last_move_time = 0
        self.move_delay = SLOW_SPEED_DELAY # Current speed delay
        self.respawn_timer = 0 # Timestamp when respawn invulnerability ends
        self.recoil_end_time = 0 # Timestamp when recoil ends
        
        self.is_aiming = False
        self.trail = [] # List of (x, y, type) for trail
        
        self.set_speed()

    def set_speed(self):
        length = len(self.body)
        if length >= MAX_LENGTH_FOR_SPEED:
            delay = SLOW_SPEED_DELAY
        elif length <= 2: 
            delay = FAST_SPEED_DELAY
        else:
            ratio = (length - 2) / (MAX_LENGTH_FOR_SPEED - 2)
            delay = int(FAST_SPEED_DELAY + (SLOW_SPEED_DELAY - FAST_SPEED_DELAY) * ratio)
        
        self.move_delay = delay
        
        # Only set timer if not currently in recoil
        # IMPORTANT: We MUST set the timer initially or if it's not running.
        # But to avoid "stopping" during gameplay, we don't reset it here if it's already running.
        # However, for the FIRST call (init), we need to start it.
        # We can check if it's the first call by checking if move_delay was previously set?
        # Or just rely on the main loop to keep it going.
        
        # The issue "snake cannot move at all" is likely because I removed the initial set_timer call
        # AND I removed the self.move_delay assignment in the previous botched edit.
        
        # Let's restore the assignment and add a check to start the timer if it's the first time.
        # Since we can't easily check if the timer is active, we can just set it if it's the __init__ phase.
        # But set_speed is called in __init__.
        
        if pygame.time.get_ticks() < 500: # Increased startup window check
             pygame.time.set_timer(GAME_TICK, delay)
        elif pygame.time.get_ticks() > self.recoil_end_time:
             pass

    def get_visual_head_pos(self):
        now = pygame.time.get_ticks()
        time_since_move = now - self.last_move_time
        t = min(1.0, time_since_move / self.move_delay) if self.move_delay > 0 else 1.0
        
        head_idx = 0
        if head_idx >= len(self.visual_body):
             return self.body[0]["rect"].x * GRID_SIZE, self.body[0]["rect"].y * GRID_SIZE

        prev_x = self.visual_body[head_idx]["prev_x"]
        prev_y = self.visual_body[head_idx]["prev_y"]
        target_x = self.body[head_idx]["rect"].x * GRID_SIZE
        target_y = self.body[head_idx]["rect"].y * GRID_SIZE
        
        x = lerp(prev_x, target_x, t)
        y = lerp(prev_y, target_y, t)
        return x, y

    def get_head(self):
        return self.body[0]["rect"]
    
    def get_body_length(self):
        return len(self.body) - 1

    def move(self):
        # Check respawn timer - Allow movement but logic handled in hit()
        # if pygame.time.get_ticks() < self.respawn_timer:
        #    return

        # Check recoil reset
        if self.recoil_end_time > 0 and pygame.time.get_ticks() > self.recoil_end_time:
            self.recoil_end_time = 0
            self.set_speed()

        # Store previous positions for interpolation
        for i, segment in enumerate(self.body):
            if i < len(self.visual_body):
                self.visual_body[i]["prev_x"] = segment["rect"].x * GRID_SIZE
                self.visual_body[i]["prev_y"] = segment["rect"].y * GRID_SIZE
        
        self.last_move_time = pygame.time.get_ticks()

        head = self.get_head()
        new_head_rect = pygame.Rect(head.x + self.dx, head.y + self.dy, 1, 1)

        # Check bounds
        if (new_head_rect.x < 0 or new_head_rect.x >= GRID_WIDTH or
            new_head_rect.y < 0 or new_head_rect.y >= GRID_HEIGHT):
            return self.hit() # Return the result of hit()

        # Check self collision
        for segment in self.body[1:]:
            if new_head_rect.colliderect(segment["rect"]):
                return self.hit()

        # Update body segments (Shift positions)
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i]["rect"] = self.body[i-1]["rect"]
        
        self.body[0]["rect"] = new_head_rect

        # Update visual body targets
        for i, segment in enumerate(self.body):
            if i < len(self.visual_body):
                self.visual_body[i]["x"] = segment["rect"].x * GRID_SIZE
                self.visual_body[i]["y"] = segment["rect"].y * GRID_SIZE
            else:
                # If visual body is smaller (e.g. just grew), append new
                self.visual_body.append({
                    "x": segment["rect"].x * GRID_SIZE,
                    "y": segment["rect"].y * GRID_SIZE,
                    "prev_x": segment["rect"].x * GRID_SIZE, # Start from new pos to avoid flying in
                    "prev_y": segment["rect"].y * GRID_SIZE
                })

    def get_next_ammo(self):
        for i in range(1, len(self.body)):
            segment_type = self.body[i]["type"]
            if segment_type != "shield":
                return segment_type
        return None

    def shoot(self, all_sprites_group, standard_bullet_group, charge_bullet_group, all_bullets_group):
        if self.get_body_length() < 1: return 

        fired_dot_type = None
        fired_dot_index = -1

        for i in range(1, len(self.body)):
            segment_type = self.body[i]["type"]
            if segment_type != "shield":
                fired_dot_type = segment_type
                fired_dot_index = i
                break 

        if fired_dot_type is None: return
        
        self.body.pop(fired_dot_index)
        if fired_dot_index < len(self.visual_body):
            self.visual_body.pop(fired_dot_index)
        
        head_rect = self.get_head()
        vis_head_x, vis_head_y = self.get_visual_head_pos()
        spawn_x = vis_head_x + (GRID_SIZE // 2)
        spawn_y = vis_head_y + (GRID_SIZE // 2)

        if fired_dot_type == "charge":
            bullet = Bullet(spawn_x, spawn_y, self.dx, self.dy, "charge")
            charge_bullet_group.add(bullet)
        else: 
            bullet = Bullet(spawn_x, spawn_y, self.dx, self.dy, "standard")
            standard_bullet_group.add(bullet)

        all_sprites_group.add(bullet)
        all_bullets_group.add(bullet)
        
        # Apply Recoil
        RECOIL_DURATION = 200 # ms
        RECOIL_DELAY_ADD = 100 # ms
        
        self.recoil_end_time = pygame.time.get_ticks() + RECOIL_DURATION
        # Set temporary slow speed
        pygame.time.set_timer(GAME_TICK, self.move_delay + RECOIL_DELAY_ADD)
        
        self.set_speed()

    def grow(self, dot_type):
        if dot_type == "shield":
            if self.shields < 3:
                self.shields += 1
                print(f"Shield added! Total: {self.shields}")
            return

        if self.get_body_length() > 0:
            last_segment_rect = self.body[-1]["rect"]
        else:
            last_segment_rect = self.get_head()
            
        new_segment = {
            "type": dot_type,
            "rect": pygame.Rect(last_segment_rect.x, last_segment_rect.y, 1, 1)
        }
        self.body.append(new_segment)
        # Visual body update handled in move() or next frame
        
        self.set_speed()

    def hit(self):
        # Ignore hits if invincible (respawning)
        if pygame.time.get_ticks() < self.respawn_timer:
            return

        if self.shields > 0:
            self.shields -= 1
            print(f"Shield protected! Remaining: {self.shields}")
            return

        # Trigger Explosion
        for i, segment in enumerate(self.body):
            # Get position from visual body if available for smoothness
            if i < len(self.visual_body):
                x = self.visual_body[i]["x"] + GRID_SIZE // 2
                y = self.visual_body[i]["y"] + GRID_SIZE // 2
            else:
                x = segment["rect"].x * GRID_SIZE + GRID_SIZE // 2
                y = segment["rect"].y * GRID_SIZE + GRID_SIZE // 2
            
            color = COLOR_PLAYER_GREEN
            if segment["type"] == "head": color = COLOR_DOT_RED # Head explodes red
            elif segment["type"] == "standard": color = COLOR_DOT_RED
            elif segment["type"] == "charge": color = COLOR_DOT_YELLOW
            elif segment["type"] == "shield": color = COLOR_DOT_BLUE
            
            self.particle_system.emit(x, y, color, count=8, size=5)

        self.lives -= 1
        print(f"Nyawa tersisa: {self.lives}")
        
        if self.lives <= 0:
            return "GAME_OVER"
        
        # Respawn Logic
        start_y = GRID_HEIGHT - 5
        self.body = [
            {"type": "head", "rect": pygame.Rect(GRID_WIDTH // 2, start_y, 1, 1)},
            {"type": "standard", "rect": pygame.Rect(GRID_WIDTH // 2, start_y + 1, 1, 1)},
            {"type": "standard", "rect": pygame.Rect(GRID_WIDTH // 2, start_y + 2, 1, 1)},
        ]
        # Reset visual body
        self.visual_body = []
        for segment in self.body:
            self.visual_body.append({
                "x": segment["rect"].x * GRID_SIZE,
                "y": segment["rect"].y * GRID_SIZE,
                "prev_x": segment["rect"].x * GRID_SIZE,
                "prev_y": segment["rect"].y * GRID_SIZE
            })

        self.dx = 0
        self.dy = -1 
        self.set_speed()
        
        # Set Respawn Timer (3 seconds invulnerability)
        self.respawn_timer = pygame.time.get_ticks() + 3000

    def draw(self, surface):
        # Calculate interpolation progress
        now = pygame.time.get_ticks()
        time_since_move = now - self.last_move_time
        t = min(1.0, time_since_move / self.move_delay) if self.move_delay > 0 else 1.0
        
        is_invincible = now < self.respawn_timer
        show_body = True
        
        if is_invincible:
            # Blink effect: Hide body on odd intervals
            if (now // 100) % 2 != 0:
                show_body = False
            
            # Draw Shield Aura (Always visible when invincible)
            head_x, head_y = self.get_visual_head_pos()
            center_x = int(head_x + GRID_SIZE // 2)
            center_y = int(head_y + GRID_SIZE // 2)
            radius = int(GRID_SIZE // 2) + 6
            
            shield_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            # Pulsing alpha for aura
            aura_alpha = int(100 + (math.sin(now * 0.01) + 1) * 50)
            pygame.draw.circle(shield_surf, (200, 200, 255, aura_alpha), (radius, radius), radius, 2)
            surface.blit(shield_surf, (center_x - radius, center_y - radius))

        # --- Draw Trail (Behind Body) ---
        for i, (tx, ty, t_type) in enumerate(self.trail):
            # Alpha based on index (older = more transparent)
            # Reduced opacity as requested
            alpha = int(10 + (i / len(self.trail)) * 20) 
            if alpha > 255: alpha = 255
            
            ghost_img = None
            if t_type == "head": ghost_img = ASSETS.get('dot_head')
            elif t_type == "standard": ghost_img = ASSETS.get('dot_standard')
            elif t_type == "charge": ghost_img = ASSETS.get('dot_charge')
            elif t_type == "shield": ghost_img = ASSETS.get('dot_shield')
            
            if ghost_img:
                ghost_img = ghost_img.copy()
                ghost_img.set_alpha(alpha)
                surface.blit(ghost_img, (tx, ty))

        # --- Draw Body ---
        if show_body:
            for i, segment in enumerate(self.body):
                if i >= len(self.visual_body): continue
                
                seg_type = segment["type"]
                
                # Interpolate position
                prev_x = self.visual_body[i]["prev_x"]
                prev_y = self.visual_body[i]["prev_y"]
                target_x = segment["rect"].x * GRID_SIZE
                target_y = segment["rect"].y * GRID_SIZE
                
                draw_x = lerp(prev_x, target_x, t)
                draw_y = lerp(prev_y, target_y, t)
                
                img = None
                if seg_type == "head": img = ASSETS.get('dot_head')
                elif seg_type == "standard": img = ASSETS.get('dot_standard')
                elif seg_type == "charge": img = ASSETS.get('dot_charge')
                elif seg_type == "shield": img = ASSETS.get('dot_shield')
                
                if img:
                    if seg_type == "head":
                        # Rotate head based on direction
                        angle = 0
                        if self.dx == 1: angle = -90
                        elif self.dx == -1: angle = 90
                        elif self.dy == 1: angle = 180
                        elif self.dy == -1: angle = 0
                        
                        # Rotate image
                        img = pygame.transform.rotate(img, angle)
                        
                    surface.blit(img, (draw_x, draw_y))
                    
                    # Visual Shield Indicator on Head
                    if seg_type == "head" and self.shields > 0:
                        center_x = int(draw_x + GRID_SIZE // 2)
                        center_y = int(draw_y + GRID_SIZE // 2)
                        radius = int(GRID_SIZE // 2) + 3
                        # Draw pulsing shield aura
                        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2 # 0 to 1
                        alpha = int(100 + pulse * 155)
                        
                        shield_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                        # Draw ring (width=2)
                        pygame.draw.circle(shield_surf, (*COLOR_DOT_BLUE, alpha), (radius, radius), radius, 2)
                        surface.blit(shield_surf, (center_x - radius, center_y - radius))
                else:
                    pygame.draw.rect(surface, COLOR_WHITE, (draw_x, draw_y, GRID_SIZE, GRID_SIZE))

        # Update Trail (Keep last 5 frames)
        if len(self.visual_body) > 0:
            # Determine which segment to trail from
            # If body length > 1, trail from tail (last segment)
            # If body length == 1, trail from head (first segment)
            trail_idx = len(self.visual_body) - 1
            
            prev_x = self.visual_body[trail_idx]["prev_x"]
            prev_y = self.visual_body[trail_idx]["prev_y"]
            target_x = self.body[trail_idx]["rect"].x * GRID_SIZE
            target_y = self.body[trail_idx]["rect"].y * GRID_SIZE
            
            trail_x = lerp(prev_x, target_x, t)
            trail_y = lerp(prev_y, target_y, t)
            trail_type = self.body[trail_idx]["type"]
            
            self.trail.append((trail_x, trail_y, trail_type))
            if len(self.trail) > 5:
                self.trail.pop(0)

    def draw_reticle_raycast(self, surface, enemies, obstacles):
         if not self.is_aiming or self.get_body_length() < 1: return

         # Use visual head position for smoother aiming origin
         vis_x, vis_y = self.get_visual_head_pos()
         start_x = vis_x + GRID_SIZE // 2
         start_y = vis_y + GRID_SIZE // 2
         
         head_rect = self.get_head() # Still need logical rect for raycast start
         
         bullet_type = "standard"
         next_ammo = self.get_next_ammo()
         if next_ammo: bullet_type = next_ammo
         
         # Raycast
         ray_x, ray_y = head_rect.x, head_rect.y
         
         # Max steps
         max_steps = max(GRID_WIDTH, GRID_HEIGHT)
         
         hit_x, hit_y = -1, -1
         target_obj = None
         
         for _ in range(max_steps):
             ray_x += self.dx
             ray_y += self.dy
             
             # Bounds check
             if ray_x < 0 or ray_x >= GRID_WIDTH or ray_y < 0 or ray_y >= GRID_HEIGHT:
                 hit_x = (ray_x - self.dx) * GRID_SIZE + GRID_SIZE // 2
                 hit_y = (ray_y - self.dy) * GRID_SIZE + GRID_SIZE // 2
                 # Adjust to edge
                 if self.dx > 0: hit_x = SCREEN_WIDTH
                 elif self.dx < 0: hit_x = 0
                 elif self.dy > 0: hit_y = SCREEN_HEIGHT
                 elif self.dy < 0: hit_y = 0
                 break
             
             # Check collision
             check_rect = pygame.Rect(ray_x * GRID_SIZE, ray_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
             
             # Obstacles (Walls) - Always stop
             hit_obstacle = False
             for obs in obstacles:
                 if obs.rect.colliderect(check_rect):
                     hit_obstacle = True
                     target_obj = obs
                     break
             if hit_obstacle:
                 hit_x = check_rect.centerx
                 hit_y = check_rect.centery
                 break
                 
             # Enemies - Stop if standard
             if bullet_type == "standard":
                 hit_enemy = False
                 for enemy in enemies:
                     if enemy.rect.colliderect(check_rect):
                         hit_enemy = True
                         target_obj = enemy
                         break
                 if hit_enemy:
                     hit_x = check_rect.centerx
                     hit_y = check_rect.centery
                     break
        
         if hit_x == -1: # Should have hit bounds at least
             hit_x = start_x + self.dx * 1000
             hit_y = start_y + self.dy * 1000
             
         # Draw Moving Arrows
         vec_x = hit_x - start_x
         vec_y = hit_y - start_y
         dist = math.sqrt(vec_x**2 + vec_y**2)
         
         color = COLOR_DOT_RED if bullet_type == "standard" else COLOR_DOT_YELLOW

         if dist > 0:
            norm_x = vec_x / dist
            norm_y = vec_y / dist
            
            arrow_spacing = 20 
            anim_speed = 0.1 # Faster pixel movement
            offset = (pygame.time.get_ticks() * anim_speed) % arrow_spacing
            
            current_dist = offset
            while current_dist < dist - 5: # Don't draw on top of target
                ax = start_x + norm_x * current_dist
                ay = start_y + norm_y * current_dist
                
                # Draw Arrow Head (Chevron)
                size = 3
                points = []
                if self.dx != 0: # Horizontal
                    points = [(ax - self.dx*size, ay - size), (ax + self.dx*size, ay), (ax - self.dx*size, ay + size)]
                else: # Vertical
                    points = [(ax - size, ay - self.dy*size), (ax, ay + self.dy*size), (ax + size, ay - self.dy*size)]
                
                if points:
                    pygame.draw.lines(surface, color, False, points, 2)
                
                current_dist += arrow_spacing

         # Draw Impact Marker
         if target_obj and hasattr(target_obj, 'get_draw_pos'):
             # Draw bracket around target
             tx, ty = target_obj.get_draw_pos()
             
             # Corner brackets
             bracket_len = 5
             # Top-left
             pygame.draw.line(surface, color, (tx, ty), (tx + bracket_len, ty), 2)
             pygame.draw.line(surface, color, (tx, ty), (tx, ty + bracket_len), 2)
             # Top-right
             pygame.draw.line(surface, color, (tx + GRID_SIZE, ty), (tx + GRID_SIZE - bracket_len, ty), 2)
             pygame.draw.line(surface, color, (tx + GRID_SIZE, ty), (tx + GRID_SIZE, ty + bracket_len), 2)
             # Bottom-left
             pygame.draw.line(surface, color, (tx, ty + GRID_SIZE), (tx + bracket_len, ty + GRID_SIZE), 2)
             pygame.draw.line(surface, color, (tx, ty + GRID_SIZE), (tx, ty + GRID_SIZE - bracket_len), 2)
             # Bottom-right
             pygame.draw.line(surface, color, (tx + GRID_SIZE, ty + GRID_SIZE), (tx + GRID_SIZE - bracket_len, ty + GRID_SIZE), 2)
             pygame.draw.line(surface, color, (tx + GRID_SIZE, ty + GRID_SIZE), (tx + GRID_SIZE, ty + GRID_SIZE - bracket_len), 2)
             
         else:
             # Hit wall or bounds - Draw X
             pygame.draw.line(surface, color, (hit_x - 4, hit_y - 4), (hit_x + 4, hit_y + 4), 2)
             pygame.draw.line(surface, color, (hit_x - 4, hit_y + 4), (hit_x + 4, hit_y - 4), 2)

# --- Class untuk Musuh & Rintangan (Interpolated) ---

class InterpolatedSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.grid_x = 0
        self.grid_y = 0
        self.prev_x = 0
        self.prev_y = 0
        self.last_move_time = 0
        self.move_delay = INITIAL_WORLD_SPEED # Default, updated by main loop
        self.trail = [] # List of (x, y) for trailing effect

    def update_logical_pos(self):
        # Called when grid position changes
        self.prev_x = self.rect.x
        self.prev_y = self.rect.y
        self.rect.x = self.grid_x * GRID_SIZE
        self.rect.y = self.grid_y * GRID_SIZE
        self.last_move_time = pygame.time.get_ticks()

    def get_draw_pos(self):
        now = pygame.time.get_ticks()
        time_since_move = now - self.last_move_time
        t = min(1.0, time_since_move / self.move_delay) if self.move_delay > 0 else 1.0
        
        draw_x = lerp(self.prev_x, self.rect.x, t)
        draw_y = lerp(self.prev_y, self.rect.y, t)
        return draw_x, draw_y

    def draw(self, surface):
        draw_x, draw_y = self.get_draw_pos()
        
        # Update Trail
        self.trail.append((draw_x, draw_y))
        if len(self.trail) > 5:
            self.trail.pop(0)
            
        # Draw Trail
        for i, (tx, ty) in enumerate(self.trail):
            # Reduced opacity for enemies too
            alpha = int(20 + (i / len(self.trail)) * 60)
            if alpha > 255: alpha = 255
            
            ghost_img = self.image.copy()
            ghost_img.set_alpha(alpha)
            surface.blit(ghost_img, (tx, ty))
            
        # Draw Self
        surface.blit(self.image, (draw_x, draw_y))

class Chaser(InterpolatedSprite):
    def __init__(self, player): 
        super().__init__()
        if 'virus_chaser' in ASSETS:
            self.image = ASSETS['virus_chaser'].copy()
        else:
            self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
            self.image.fill(COLOR_ENEMY_CHASER)
            
        self.player = player 
        self.grid_x = random.randint(0, GRID_WIDTH - 1)
        self.grid_y = -1
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.grid_x * GRID_SIZE, self.grid_y * GRID_SIZE)
        self.prev_x = self.rect.x
        self.prev_y = self.rect.y
        
        self.move_counter = 0
        self.chase_delay = 2

    def update(self, move=False):
        if move:
            self.grid_y += 1
            self.move_counter += 1
            
            if self.move_counter >= self.chase_delay:
                player_head_rect = self.player.get_head()
                dx = player_head_rect.x - self.grid_x
                
                if dx > 0: self.grid_x += 1
                elif dx < 0: self.grid_x -= 1
                self.move_counter = 0
                
            self.update_logical_pos()
            
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()

class Follower(InterpolatedSprite):
    def __init__(self, player):
        super().__init__()
        if 'virus_follower' in ASSETS:
            self.image = ASSETS['virus_follower'].copy()
        else:
            self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
            self.image.fill(COLOR_ENEMY_FOLLOWER)
            
        self.player = player 
        self.grid_x = random.randint(0, GRID_WIDTH - 1)
        self.grid_y = -1 
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.grid_x * GRID_SIZE, self.grid_y * GRID_SIZE)
        self.prev_x = self.rect.x
        self.prev_y = self.rect.y
        
        self.move_counter = 0
        self.chase_delay = 3

    def update(self, move=False):
        if move:
            self.move_counter += 1
            
            if self.move_counter >= self.chase_delay:
                player_head_rect = self.player.get_head()
                dx = player_head_rect.x - self.grid_x
                dy = player_head_rect.y - self.grid_y
                
                if abs(dx) > abs(dy):
                    if dx > 0: self.grid_x += 1
                    elif dx < 0: self.grid_x -= 1
                else:
                    if dy > 0: self.grid_y += 1
                    elif dy < 0: self.grid_y -= 1
                self.move_counter = 0
            
            self.update_logical_pos()
            
            if (self.rect.bottom < -GRID_SIZE or 
                self.rect.top > SCREEN_HEIGHT + GRID_SIZE or
                self.rect.right < -GRID_SIZE or
                self.rect.left > SCREEN_WIDTH + GRID_SIZE):
                self.kill()

class CrackedWall(InterpolatedSprite):
    def __init__(self, grid_x, grid_y):
        super().__init__()
        if 'barrier' in ASSETS:
            self.image = ASSETS['barrier'].copy()
        else:
            self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
            self.image.fill(COLOR_WALL_CRACKED)
            
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.rect = self.image.get_rect()
        self.rect.x = grid_x * GRID_SIZE
        self.rect.y = grid_y * GRID_SIZE
        self.prev_x = self.rect.x
        self.prev_y = self.rect.y
        self.trail = [] # Ensure trail exists

    def update(self, move=False):
        if move:
            self.grid_y += 1
            self.update_logical_pos()
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()

# --- Class untuk Pickups (Makanan/Dot) ---
class DotPickup(InterpolatedSprite):
    def __init__(self, x=None, y=None, dot_type=None):
        super().__init__()
        
        if dot_type:
            self.dot_type = dot_type
            if dot_type == "standard": color = COLOR_DOT_RED
            elif dot_type == "charge": color = COLOR_DOT_YELLOW
            else: color = COLOR_DOT_BLUE
        else:
            rand_val = random.random()
            if rand_val < 0.90: 
                self.dot_type = "standard"
                color = COLOR_DOT_RED
            elif rand_val < 0.98: 
                self.dot_type = "charge"
                color = COLOR_DOT_YELLOW
            else: 
                self.dot_type = "shield"
                color = COLOR_DOT_BLUE
        
        key = None
        if self.dot_type == "standard": key = 'dot_standard'
        elif self.dot_type == "charge": key = 'dot_charge'
        elif self.dot_type == "shield": key = 'dot_shield'
        
        if key and key in ASSETS:
            self.base_image = ASSETS[key]
            self.image = self.base_image.copy()
        else:
            self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
            self.image.fill(color)
            self.base_image = self.image.copy()
            
        if x is not None and y is not None:
            self.grid_x = x
            self.grid_y = y
            self.rect = self.image.get_rect(center=(x * GRID_SIZE + GRID_SIZE//2, y * GRID_SIZE + GRID_SIZE//2))
        else:
            self.grid_x = random.randint(0, GRID_WIDTH - 1)
            self.grid_y = -1
            self.rect = self.image.get_rect()
            self.rect.x = self.grid_x * GRID_SIZE
            self.rect.y = self.grid_y * GRID_SIZE
            
        self.prev_x = self.rect.x
        self.prev_y = self.rect.y
        
        self.move_accum = 0
        self.move_threshold = 2 
        self.trail = []
        self.magnetized = False

    def update(self, move=False, player_head_pos=None):
        # Magnetic Logic
        if player_head_pos:
            px, py = player_head_pos
            # Center of pickup
            cx, cy = self.rect.centerx, self.rect.centery
            dx = px - cx
            dy = py - cy
            dist = math.sqrt(dx*dx + dy*dy)
            
            magnet_radius = GRID_SIZE * 3.0 # Slightly increased for better feel
            if dist < magnet_radius:
                self.magnetized = True
                
            if self.magnetized:
                # Retro "snap" movement - move in larger pixel chunks or accelerate
                # Simple ease-in
                speed = 4 + (magnet_radius - dist) * 0.1 
                
                if dist > 0:
                    self.rect.x += (dx / dist) * speed
                    self.rect.y += (dy / dist) * speed
                    # Update logical grid pos roughly for cleanup check
                    self.grid_y = self.rect.y // GRID_SIZE
                return # Skip normal movement if magnetized

        if move:
            self.move_accum += 1
            if self.move_accum >= self.move_threshold:
                self.move_accum = 0
                self.grid_y += 1
                self.update_logical_pos()
                
                if self.rect.top > SCREEN_HEIGHT:
                    self.kill()
            return

        # Animation: Continuous smooth pulse
        now = pygame.time.get_ticks()
        pulse_speed = 0.005
        pulse = (math.sin(now * pulse_speed) + 1) / 2 # 0 to 1 
        
        scale = 0.85 + (pulse * 0.3) # 0.85 to 1.15
        
        # Scale image from center
        new_size = (int(GRID_SIZE * scale), int(GRID_SIZE * scale))
        if new_size[0] < 1: new_size = (1, 1)
        
        self.image = pygame.transform.scale(self.base_image, new_size)
        # Note: Rect position is handled by draw logic, but collision needs rect
        # We don't update rect center here to avoid fighting with interpolation logic for drawing

# --- Class untuk Peluru ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, center_x, center_y, dir_x, dir_y, bullet_type):
        super().__init__()
        
        self.bullet_type = bullet_type
        
        if self.bullet_type == "charge":
            if 'bullet_charge' in ASSETS:
                self.image = ASSETS['bullet_charge'].copy()
            else:
                self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
                self.image.fill(COLOR_BULLET_CHARGE)
            self.penetration = 999 
        else: # standard
            if 'bullet_standard' in ASSETS:
                self.image = pygame.transform.scale(ASSETS['bullet_standard'], (GRID_SIZE//2, GRID_SIZE//2))
            else:
                self.image = pygame.Surface((GRID_SIZE // 2, GRID_SIZE // 2))
                self.image.fill(COLOR_BULLET_STANDARD)
            self.penetration = 1 

        self.rect = self.image.get_rect(center=(center_x, center_y))
        
        self.x = float(center_x)
        self.y = float(center_y)
        self.base_speed = 900
        self.vx = dir_x * self.base_speed
        self.vy = dir_y * self.base_speed

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (int(self.x), int(self.y))

        if (self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or
            self.rect.right < 0 or self.rect.left > SCREEN_WIDTH):
            self.kill()

# --- Class untuk Score & Visual Effects ---

class FloatingText:
    def __init__(self, text, x, y, color=(255, 255, 255), duration=1000, size=24):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.creation_time = pygame.time.get_ticks()
        self.duration = duration
        self.alpha = 255
        self.font = pygame.font.Font(None, size)
        if 'font' in ASSETS:
             self.font = ASSETS['font']

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.creation_time
        if elapsed > self.duration:
            return False
        
        # Float up
        self.y -= 0.5
        # Fade out
        self.alpha = max(0, 255 - (elapsed / self.duration) * 255)
        return True

    def draw(self, surface):
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        surface.blit(text_surf, (self.x, self.y))

class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_duration = 3000 # 3 seconds to keep combo
        self.floating_texts = []
        self.splash_messages = [] # For top right

    def add_score(self, points, enemy_type, pos):
        now = pygame.time.get_ticks()
        
        # Combo Logic
        if now < self.combo_timer:
            self.combo_count += 1
        else:
            self.combo_count = 1
        
        self.combo_timer = now + self.combo_duration
        
        # Calculate Points
        multiplier = 1 + (self.combo_count - 1) * 0.2 # 20% bonus per combo
        final_points = int(points * multiplier)
        self.score += final_points
        
        # Add Floating Text at position
        combo_text = f" x{self.combo_count}" if self.combo_count > 1 else ""
        self.floating_texts.append(FloatingText(f"+{final_points}{combo_text}", pos[0], pos[1], COLOR_WHITE))
        
        # Add Splash Message
        if enemy_type == "WALL":
            msg = "WALL BROKEN"
        else:
            msg = f"{enemy_type} DEFEATED"

        if self.combo_count > 1:
            pass # msg += f" (COMBO x{self.combo_count}!)"
        
        print(f"Splash added: {msg}") # Debug print
        # Add to splash (stacking)
        self.splash_messages.append(FloatingText(msg, SCREEN_WIDTH - 20, 20, (255, 255, 100), 2000))

    def update(self):
        # Update Floating Texts
        self.floating_texts = [ft for ft in self.floating_texts if ft.update()]
        
        # Update Splash Messages
        active_splashes = []
        for i, ft in enumerate(self.splash_messages):
            if ft.update():
                # Stack from top right
                target_y = 20 + i * 25
                ft.y = target_y 
                
                # Right align calculation
                text_width = ft.font.size(ft.text)[0]
                ft.x = SCREEN_WIDTH - 20 - text_width
                
                active_splashes.append(ft)
        self.splash_messages = active_splashes

    def draw(self, surface, font):
        for ft in self.floating_texts:
            ft.draw(surface)
        for ft in self.splash_messages:
            ft.draw(surface)
            
        # Draw Combo Bar/Timer if active
        if pygame.time.get_ticks() < self.combo_timer:
            time_left = self.combo_timer - pygame.time.get_ticks()
            ratio = time_left / self.combo_duration
            
            # Draw combo bar at top left
            bar_width = 150
            margin_left = 20
            margin_top = 20
            
            combo_surf = font.render(f"COMBO x{self.combo_count}!", True, (255, 255, 0))
            surface.blit(combo_surf, (margin_left, margin_top))
            
            pygame.draw.rect(surface, (50, 50, 50), (margin_left, margin_top + 25, bar_width, 8))
            pygame.draw.rect(surface, (255, 200, 0), (margin_left, margin_top + 25, bar_width * ratio, 8))

# --- Fungsi Game Utama ---
async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("DOTSNAKE - Project Edition")
    clock = pygame.time.Clock()
    
    load_assets()
    
    font = ASSETS.get('font', pygame.font.Font(None, 24))
    font_large = ASSETS.get('font_large', pygame.font.Font(None, 48))
    
    particle_system = ParticleSystem()
    player = Player(particle_system)
    
    # --- Grup Sprite ---
    all_sprites = pygame.sprite.Group() # For logical updates
    
    # Separate lists for custom drawing
    enemies_list = []
    obstacles_list = []
    pickups_list = []
    
    enemies = pygame.sprite.Group()     
    obstacles = pygame.sprite.Group()   
    pickups = pygame.sprite.Group()     

    standard_bullets = pygame.sprite.Group() 
    charge_bullets = pygame.sprite.Group() 
    all_bullets = pygame.sprite.Group()

    # --- PENGATURAN LEVEL & KESULITAN ---
    world_ticks_elapsed = 0
    current_level = 1
    LEVEL_DURATION_TICKS = 250 

    level_definitions = {
        1: {"spawn_delay": 1500, "chances": {"chaser": 0.6, "wall": 0.4, "follower": 0.0}},
        2: {"spawn_delay": 1300, "chances": {"chaser": 0.4, "wall": 0.3, "follower": 0.3}},
        3: {"spawn_delay": 1100, "chances": {"chaser": 0.3, "wall": 0.2, "follower": 0.5}},
        4: {"spawn_delay": 900,  "chances": {"chaser": 0.4, "wall": 0.1, "follower": 0.5}},
        5: {"spawn_delay": 750,  "chances": {"chaser": 0.3, "wall": 0.1, "follower": 0.6}}
    }
    max_level = len(level_definitions)

    initial_spawn_delay = level_definitions[current_level]["spawn_delay"]
    pygame.time.set_timer(SPAWN_ENEMY, initial_spawn_delay)
    pygame.time.set_timer(SPAWN_PICKUP, 4000) # Reduced drop rate

    current_world_speed = INITIAL_WORLD_SPEED 
    pygame.time.set_timer(WORLD_TICK, current_world_speed)

    running = True
    game_state = "PLAYING"
    score_system = ScoreSystem()
    bg_y = 0
    
    game_over_timer = 0
    
    dt = 0
    while running:
        dt_ms = clock.tick(60)
        dt = dt_ms / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.is_aiming = True
                    elif event.key == pygame.K_LEFT and player.dx != 1:
                        player.dx = -1; player.dy = 0
                    elif event.key == pygame.K_RIGHT and player.dx != -1:
                        player.dx = 1; player.dy = 0
                    elif event.key == pygame.K_UP and player.dy != 1:
                        player.dx = 0; player.dy = -1
                    elif event.key == pygame.K_DOWN and player.dy != -1:
                        player.dx = 0; player.dy = 1
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        if player.is_aiming:
                            player.shoot(all_sprites, standard_bullets, charge_bullets, all_bullets)
                            player.is_aiming = False

                if event.type == GAME_TICK:
                    game_result = player.move() 
                    # Reset timer to current speed (in case it changed due to growth/recoil end)
                    # This ensures the next tick happens at the correct interval from NOW.
                    pygame.time.set_timer(GAME_TICK, player.move_delay)
                    
                    if game_result == "GAME_OVER":
                        game_state = "DYING"
                        game_over_timer = pygame.time.get_ticks() + 1500 # 1.5s delay

                if event.type == WORLD_TICK:
                    world_ticks_elapsed += 1
                    
                    # Update World Entities with move=True
                    for e in enemies_list: e.update(move=True)
                    for o in obstacles_list: o.update(move=True)
                    for p in pickups_list: p.update(move=True)
                    
                    score_system.score += (1 * player.get_body_length())
                    
                    if world_ticks_elapsed % SCORE_MILESTONE == 0 and world_ticks_elapsed > 0:
                        if current_world_speed > MIN_WORLD_SPEED:
                            current_world_speed -= SPEED_INCREASE_AMOUNT
                            if current_world_speed < MIN_WORLD_SPEED:
                                current_world_speed = MIN_WORLD_SPEED
                            pygame.time.set_timer(WORLD_TICK, current_world_speed)
                            print(f"SPEED UP! New world delay: {current_world_speed}ms")
                            
                            # Update delay for interpolation
                            for e in enemies_list: e.move_delay = current_world_speed
                            for o in obstacles_list: o.move_delay = current_world_speed
                            for p in pickups_list: p.move_delay = current_world_speed * p.move_threshold

                    if world_ticks_elapsed % LEVEL_DURATION_TICKS == 0 and world_ticks_elapsed > 0:
                        if current_level < max_level:
                            current_level += 1
                            print(f"--- LEVEL UP! MENCAPAI LEVEL {current_level} ---")
                            new_spawn_delay = level_definitions[current_level]["spawn_delay"]
                            pygame.time.set_timer(SPAWN_ENEMY, new_spawn_delay)

                if event.type == SPAWN_ENEMY:
                    chances = level_definitions[current_level]["chances"]
                    enemy_type = random.choices(
                        ["chaser", "wall", "follower"],
                        weights=[chances["chaser"], chances["wall"], chances["follower"]],
                        k=1
                    )[0]
                    
                    new_entities = []
                    
                    if enemy_type == "chaser":
                        new_entities.append(Chaser(player))
                    elif enemy_type == "follower":
                        new_entities.append(Follower(player))
                    elif enemy_type == "wall":
                        # Advanced Wall Patterns (Short Rows & Clusters)
                        pattern = random.choice(["short_row", "cluster", "scattered_small"])
                        
                        if pattern == "short_row":
                            # Horizontal row, max length 10
                            row_len = random.randint(3, 10)
                            start_x = random.randint(1, GRID_WIDTH - row_len - 1)
                            for x in range(row_len):
                                new_entities.append(CrackedWall(start_x + x, -1))
                                    
                        elif pattern == "cluster":
                            # Spawn a block of walls
                            cluster_w = random.randint(3, 6)
                            cluster_h = random.randint(2, 4)
                            start_x = random.randint(1, GRID_WIDTH - cluster_w - 1)
                            
                            for y_off in range(cluster_h):
                                for x_off in range(cluster_w):
                                    new_entities.append(CrackedWall(start_x + x_off, -1 - y_off))
                                    
                        elif pattern == "scattered_small":
                             # A few random walls in a small area
                             center_x = random.randint(5, GRID_WIDTH - 6)
                             count = random.randint(3, 8)
                             for _ in range(count):
                                 off_x = random.randint(-4, 4)
                                 off_y = random.randint(0, 3)
                                 nx = center_x + off_x
                                 if 0 <= nx < GRID_WIDTH:
                                     new_entities.append(CrackedWall(nx, -1 - off_y))

                    for entity in new_entities:
                        entity.move_delay = current_world_speed
                        all_sprites.add(entity)
                        if isinstance(entity, CrackedWall):
                            obstacles.add(entity)
                            obstacles_list.append(entity)
                        else:
                            enemies.add(entity)
                            enemies_list.append(entity)

                if event.type == SPAWN_PICKUP:
                    new_pickup = DotPickup()
                    new_pickup.move_delay = current_world_speed * new_pickup.move_threshold
                    pickups.add(new_pickup)
                    pickups_list.append(new_pickup)
                    all_sprites.add(new_pickup)

        if game_state == "PLAYING":
            all_bullets.update(dt)
            # Update animations (no movement)
            # Update animations (no movement)
            head_pos_px = (player.get_head().x * GRID_SIZE + GRID_SIZE//2, player.get_head().y * GRID_SIZE + GRID_SIZE//2)
            for p in pickups_list: p.update(move=False, player_head_pos=head_pos_px)
            
            # Cleanup dead sprites from lists
            enemies_list = [e for e in enemies_list if e.alive()]
            obstacles_list = [o for o in obstacles_list if o.alive()]
            pickups_list = [p for p in pickups_list if p.alive()]

            # --- Collision Detection ---
            # Standard Bullets vs Enemies
            hits_standard = pygame.sprite.groupcollide(enemies, standard_bullets, True, True)
            for enemy, bullets in hits_standard.items():
                points = 100
                e_type = "ENEMY"
                if isinstance(enemy, Chaser): 
                    points = 150
                    e_type = "CHASER"
                elif isinstance(enemy, Follower): 
                    points = 100
                    e_type = "FOLLOWER"
                score_system.add_score(points, e_type, enemy.rect.center)
                
                # Drop Bullet Logic
                drop_type = None
                if isinstance(enemy, Chaser): drop_type = "standard"
                elif isinstance(enemy, Follower): drop_type = "charge"
                
                if drop_type and random.random() < 0.3: # 30% chance to drop
                    # Convert pixel pos to grid pos for init
                    gx = enemy.rect.centerx // GRID_SIZE
                    gy = enemy.rect.centery // GRID_SIZE
                    new_pickup = DotPickup(gx, gy, drop_type)
                    new_pickup.move_delay = current_world_speed * new_pickup.move_threshold
                    pickups.add(new_pickup)
                    pickups_list.append(new_pickup)
                    all_sprites.add(new_pickup)

            # Standard Bullets vs Obstacles
            hits_obstacles = pygame.sprite.groupcollide(obstacles, standard_bullets, True, True)
            for obs, bullets in hits_obstacles.items():
                score_system.add_score(10, "WALL", obs.rect.center)

            # Charge Bullets vs Enemies (Penetrate)
            hits_charge = pygame.sprite.groupcollide(enemies, charge_bullets, True, False)
            for enemy, bullets in hits_charge.items():
                points = 100
                e_type = "ENEMY"
                if isinstance(enemy, Chaser): 
                    points = 150
                    e_type = "CHASER"
                elif isinstance(enemy, Follower): 
                    points = 100
                    e_type = "FOLLOWER"
                score_system.add_score(points, e_type, enemy.rect.center)

                # Drop Bullet Logic (Charge)
                drop_type = None
                if isinstance(enemy, Chaser): drop_type = "standard"
                elif isinstance(enemy, Follower): drop_type = "charge"
                
                if drop_type and random.random() < 0.3: # 30% chance to drop
                    gx = enemy.rect.centerx // GRID_SIZE
                    gy = enemy.rect.centery // GRID_SIZE
                    new_pickup = DotPickup(gx, gy, drop_type)
                    new_pickup.move_delay = current_world_speed * new_pickup.move_threshold
                    pickups.add(new_pickup)
                    pickups_list.append(new_pickup)
                    all_sprites.add(new_pickup)

            # Charge Bullets vs Obstacles (Penetrate)
            hits_charge_obs = pygame.sprite.groupcollide(obstacles, charge_bullets, True, False)
            for obs, bullets in hits_charge_obs.items():
                score_system.add_score(10, "WALL", obs.rect.center)

            player_head_rect_px = pygame.Rect(
                player.get_head().x * GRID_SIZE, player.get_head().y * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            
            # Inflate head rect for pickup detection to make it easier
            pickup_hitbox = player_head_rect_px.inflate(5, 5)
            
            collided_enemies = [s for s in enemies if s.rect.colliderect(player_head_rect_px)]
            if collided_enemies:
                for enemy in collided_enemies: enemy.kill() 
                if player.hit() == "GAME_OVER": 
                    game_state = "DYING"
                    game_over_timer = pygame.time.get_ticks() + 1500
            
            collided_obstacles = [s for s in obstacles if s.rect.colliderect(player_head_rect_px)]
            if collided_obstacles:
                for obstacle in collided_obstacles: obstacle.kill()
                if player.hit() == "GAME_OVER": 
                    game_state = "DYING"
                    game_over_timer = pygame.time.get_ticks() + 1500

            collided_pickups = [s for s in pickups if s.rect.colliderect(pickup_hitbox)]
            if collided_pickups:
                for pickup in collided_pickups:
                    player.grow(pickup.dot_type)
                    pickup.kill()
            
            score_system.update()
            particle_system.update()

        if game_state == "DYING":
            # Only update particles
            particle_system.update()
            if pygame.time.get_ticks() > game_over_timer:
                game_state = "GAME_OVER"

        # --- Drawing (Interpolated) ---
        screen.fill(COLOR_BLACK)
        
        if 'background' in ASSETS:
            bg_y = (bg_y + 2) % SCREEN_HEIGHT
            screen.blit(ASSETS['background'], (0, bg_y))
            screen.blit(ASSETS['background'], (0, bg_y - SCREEN_HEIGHT))
            
        if game_state == "PLAYING" or game_state == "DYING":
            # Draw Bullets (Standard sprite draw)
            all_bullets.draw(screen)
            
            # Draw Interpolated Entities
            for e in enemies_list:
                e.draw(screen)
            for o in obstacles_list:
                o.draw(screen)
            for p in pickups_list:
                p.draw(screen)
                
            if game_state == "PLAYING":
                player.draw(screen)
                player.draw_reticle_raycast(screen, enemies, obstacles)
            
            score_system.draw(screen, font)
            particle_system.draw(screen)
            
            # --- HUD ---
            # Background HUD
            pygame.draw.rect(screen, (20, 20, 30), (0, SCREEN_HEIGHT - HUD_HEIGHT, SCREEN_WIDTH, HUD_HEIGHT))
            pygame.draw.line(screen, (50, 50, 100), (0, SCREEN_HEIGHT - HUD_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT), 2)

            # Left: Score & Level
            score_text = font.render(f"SCORE: {score_system.score}", True, COLOR_WHITE)
            screen.blit(score_text, (40, SCREEN_HEIGHT - HUD_HEIGHT + 25))
            
            level_text = font.render(f"LVL: {current_level}", True, COLOR_WHITE)
            screen.blit(level_text, (40, SCREEN_HEIGHT - HUD_HEIGHT + 50))

            # Center: Lives & Shield
            # Lives
            lives_label = font.render("LIVES:", True, COLOR_WHITE)
            screen.blit(lives_label, (300, SCREEN_HEIGHT - HUD_HEIGHT + 25))
            for i in range(player.lives):
                pygame.draw.circle(screen, COLOR_PLAYER_GREEN, (420 + (i * 25), SCREEN_HEIGHT - HUD_HEIGHT + 33), 8)

            # Shield
            shield_label = font.render("SHIELD:", True, COLOR_WHITE)
            screen.blit(shield_label, (300, SCREEN_HEIGHT - HUD_HEIGHT + 50))
            for i in range(player.shields):
                pygame.draw.circle(screen, COLOR_DOT_BLUE, (420 + (i * 25), SCREEN_HEIGHT - HUD_HEIGHT + 58), 6)

            # Right: Next Ammo
            ammo_label = font.render("NEXT:", True, COLOR_WHITE)
            screen.blit(ammo_label, (600, SCREEN_HEIGHT - HUD_HEIGHT + 38))
            
            next_ammo = player.get_next_ammo()
            if next_ammo:
                icon = None
                label = ""
                if next_ammo == "standard": 
                    icon = ASSETS.get('dot_standard')
                    label = "STD"
                elif next_ammo == "charge": 
                    icon = ASSETS.get('dot_charge')
                    label = "CHG"
                
                if icon:
                    screen.blit(icon, (680, SCREEN_HEIGHT - HUD_HEIGHT + 28))
                    label_text = font.render(label, True, (200, 200, 200))
                    screen.blit(label_text, (710, SCREEN_HEIGHT - HUD_HEIGHT + 38))
            else:
                empty_text = font.render("EMPTY", True, (100, 100, 100))
                screen.blit(empty_text, (680, SCREEN_HEIGHT - HUD_HEIGHT + 38))

        elif game_state == "GAME_OVER":
            game_over_text = font_large.render("GAME OVER", True, (255, 50, 50))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            screen.blit(game_over_text, text_rect)
            
            final_score_text = font.render(f"Final Score: {score_system.score}", True, COLOR_WHITE)
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(final_score_text, score_rect)
            
            restart_text = font.render("Press R to Restart", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
            screen.blit(restart_text, restart_rect)
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                # Reset Game
                particle_system.particles.clear()
                player = Player(particle_system)
                enemies.empty()
                obstacles.empty()
                pickups.empty()
                standard_bullets.empty()
                charge_bullets.empty()
                all_bullets.empty()
                all_sprites.empty()
                
                enemies_list.clear()
                obstacles_list.clear()
                pickups_list.clear()
                
                score_system = ScoreSystem()
                current_level = 1
                world_ticks_elapsed = 0
                current_world_speed = INITIAL_WORLD_SPEED
                pygame.time.set_timer(WORLD_TICK, current_world_speed)
                pygame.time.set_timer(SPAWN_ENEMY, level_definitions[1]["spawn_delay"])
                
                game_state = "PLAYING"

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
