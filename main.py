import asyncio 
import pygame
import random
import os
import sys
from herramientas import pause_game, main_menu, show_credits
from interfaz.botones import BotonTactil

# 1. RUTA DE RECURSOS
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 2. INICIALIZACIÓN
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robo Collector: Edición Hardcore")
clock = pygame.time.Clock()

# CONSTANTES
TILE = 64  
GRAVITY = 0.8
JUMP_FORCE = -16
BASE_PLAYER_SPEED = 7
WHITE, BLACK = (240, 240, 240), (5, 5, 15)
CYBER_BG = (10, 5, 25)
RED, YELLOW, CYAN = (255, 45, 85), (255, 211, 25), (0, 255, 255)
GRAY, PURPLE = (40, 40, 50), (150, 0, 255)

# 3. CARGA DE SONIDOS
def load_sound(path, volume):
    full_path = resource_path(path)
    if os.path.exists(full_path):
        s = pygame.mixer.Sound(full_path)
        s.set_volume(volume)
        return s
    return None

sfx_jump = load_sound("assets/sounds/jump.mp3", 0.1)
sfx_pickup = load_sound("assets/sounds/pickup.mp3", 0.3)
sfx_gameover = load_sound("assets/sounds/gameover.mp3", 0.2)
sfx_powerup = load_sound("assets/sounds/powerup.mp3", 0.15)
sfx_victory = load_sound("assets/sounds/victory.mp3", 0.2)

music_path = resource_path("assets/sounds/music.mp3")
if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

def play_sfx(sound):
    if sound: sound.play()

# 4. CARGA DE IMÁGENES
def get_surface(color, w, h, alpha=255):
    s = pygame.Surface((w, h)); s.set_alpha(alpha); s.fill(color)
    return s

try:
    player_img = pygame.transform.scale(pygame.image.load(resource_path("assets/sprites/robot_img.png")), (TILE, TILE))
    enemy_img = pygame.transform.scale(pygame.image.load(resource_path("assets/sprites/enemy_img.png")), (TILE, TILE))
    battery_img = pygame.transform.scale(pygame.image.load(resource_path("assets/sprites/battery_img.png")), (TILE, TILE))
    door_img = pygame.transform.scale(pygame.image.load(resource_path("assets/sprites/door.png")), (TILE, TILE * 2))
    floor_tile = pygame.transform.scale(pygame.image.load(resource_path("assets/tiles/floor.png")), (TILE, TILE))
    platform_tile = pygame.transform.scale(pygame.image.load(resource_path("assets/tiles/plataform.png")), (TILE, TILE))
except:
    player_img = get_surface((0, 255, 150), TILE, TILE)
    enemy_img = get_surface(RED, TILE, TILE)
    battery_img = get_surface(YELLOW, TILE, TILE)
    door_img = get_surface(PURPLE, TILE, TILE*2)
    floor_tile = get_surface((60, 60, 80), TILE, TILE)
    platform_tile = get_surface((100, 100, 130), TILE, TILE)

red_battery_img = get_surface(RED, TILE // 2, TILE // 2)

# 5. UI Y SISTEMA DE PUNTOS
def save_high_score(score):
    try:
        with open("highscore.txt", "w") as f: f.write(str(score))
    except: pass

def load_high_score():
    path = resource_path("highscore.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            try: return int(f.read())
            except: return 0
    return 0

high_score = load_high_score()

def draw_text(txt, size, color, x, y, center=True, align_right=False):
    font = pygame.font.SysFont("consolas", size, True)
    img = font.render(txt, True, color)
    rect = img.get_rect()
    if center: rect.center = (x, y)
    elif align_right: rect.topright = (x, y)
    else: rect.topleft = (x, y)
    WIN.blit(img, rect)

def draw_hud(level, score, lives, h_score, t_ms, t_max):
    hud_bg = pygame.Surface((380, 110)); hud_bg.set_alpha(180); hud_bg.fill(BLACK)
    WIN.blit(hud_bg, (20, 20))
    pygame.draw.rect(WIN, CYAN, (20, 20, 380, 110), 2, border_radius=8)
    draw_text(f"NIVEL: {level}", 22, CYAN, 40, 35, center=False)
    draw_text(f"PUNTOS: {score}", 20, WHITE, 40, 60, center=False)
    draw_text(f"VIDAS:  {'♥' * lives}", 20, RED, 40, 85, center=False)
    draw_text(f"RÉCORD: {h_score}", 24, YELLOW, WIDTH - 40, 35, center=False, align_right=True)

    if t_ms > 0:
        b_w, b_h = 450, 20
        x_bar, y_bar = WIDTH // 2 - b_w // 2, 30
        fill = (t_ms / t_max) * b_w
        color_bar = RED if pygame.time.get_ticks() % 400 < 200 else CYAN
        pygame.draw.rect(WIN, GRAY, (x_bar, y_bar, b_w, b_h), border_radius=5)
        pygame.draw.rect(WIN, color_bar, (x_bar, y_bar, fill, b_h), border_radius=5)
        draw_text("MODO TURBO ACTIVADO", 14, color_bar, WIDTH//2, 60)

# 6. BUCLE DE JUEGO
async def game(level=1, total_score=0, total_lives=3):
    global high_score
    
    # Generar Nivel
    level_length = 70 + (level * 20)
    enemy_freq = max(7, 18 - (level // 2))
    floors, platforms, enemies = [], [], []
    for i in range(level_length):
        if i > 5 and i < level_length - 5 and random.random() < 0.08: continue
        px, py = i * TILE, HEIGHT - TILE
        floors.append(pygame.Rect(px, py, TILE, TILE))
        if i % 14 == 0: platforms.append(pygame.Rect(px, py - TILE * 3, TILE, TILE))
        if i % enemy_freq == 0 and i > 12: enemies.append(pygame.Rect(px, py - TILE, TILE, TILE))
    door = pygame.Rect(floors[-1].x, floors[-1].y - TILE * 2, TILE, TILE * 2)

    player_hitbox = pygame.Rect(100, 100, TILE * 0.6, TILE * 0.9)
    score, lives = total_score, total_lives
    y_vel, jump_count, camera_x = 0, 0, 0
    t_max, t_end = 15000, 0
    trail, batteries, s_batteries = [], [], []
    e_speed = 3.0 + (level * 0.5)
    e_dir = {id(e): 1 for e in enemies}

    btn_izq = BotonTactil(50, HEIGHT - 150, 120, 120, "<", (100, 100, 100, 150), CYAN)
    btn_der = BotonTactil(200, HEIGHT - 150, 120, 120, ">", (100, 100, 100, 150), CYAN)
    btn_salto = BotonTactil(WIDTH - 170, HEIGHT - 150, 120, 120, "^", (100, 100, 100, 150), RED)

    while True:
        clock.tick(60)
        curr_t = pygame.time.get_ticks()
        if score > high_score:
            high_score = score
            save_high_score(high_score)

        t_ms = max(0, t_end - curr_t)
        player_speed = BASE_PLAYER_SPEED * 1.6 if t_ms > 0 else BASE_PLAYER_SPEED

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    res = await pause_game(WIN, WIDTH, HEIGHT, CYAN, WHITE, clock, CYBER_BG)
                    if res == "MENU": return 
                if (event.key in [pygame.K_SPACE, pygame.K_UP]) and jump_count < 2:
                    y_vel = JUMP_FORCE; jump_count += 1; play_sfx(sfx_jump)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_salto.rect.collidepoint(event.pos) and jump_count < 2:
                    y_vel = JUMP_FORCE; jump_count += 1; play_sfx(sfx_jump)

        # Movimiento
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
        if btn_der.esta_presionado(): dx = player_speed
        if btn_izq.esta_presionado(): dx = -player_speed

        y_vel += GRAVITY
        player_hitbox.x += dx
        for s in floors + platforms:
            if player_hitbox.colliderect(s):
                if dx > 0: player_hitbox.right = s.left
                else: player_hitbox.left = s.right
        
        player_hitbox.y += y_vel
        for s in floors + platforms:
            if player_hitbox.colliderect(s):
                if y_vel > 0: player_hitbox.bottom = s.top; jump_count = 0
                else: player_hitbox.top = s.bottom
                y_vel = 0

        if player_hitbox.y > HEIGHT:
            lives -= 1; play_sfx(sfx_gameover)
            player_hitbox.x, player_hitbox.y = 100, 100
            if lives <= 0: return await game_over(score)

        camera_x += (player_hitbox.x - camera_x - WIDTH//2) * 0.1

      # --- LÓGICA DE ENEMIGOS ---
        for e in enemies[:]:
            # Aplicamos la velocidad que aumenta por nivel
            e.x += e_dir[id(e)] * e_speed
            
            # IA básica: Si el enemigo va a caerse de la plataforma, cambia de dirección
            # Creamos un pequeño sensor debajo de él
            sensor_suelo = pygame.Rect(e.x + (e_dir[id(e)] * 20), e.bottom, 10, 5)
            hay_suelo = any(sensor_suelo.colliderect(f) for f in floors)
            
            if not hay_suelo:
                e_dir[id(e)] *= -1

            # Colisión con el jugador
            if player_hitbox.colliderect(e):
                # Si tienes el Turbo (t_ms > 0), los destruyes al tocarlos
                if t_ms > 0:
                    enemies.remove(e)
                    score += 60
                    play_sfx(sfx_pickup)
                # Si saltas sobre ellos (caes desde arriba)
                elif y_vel > 0 and player_hitbox.bottom < e.centery + 10:
                    y_vel = JUMP_FORCE // 1.2
                    score += 45
                    # Probabilidad de soltar batería roja (vida) o normal
                    if random.random() < 0.2:
                        s_batteries.append(pygame.Rect(e.x, e.y, TILE//2, TILE//2))
                    else:
                        batteries.append(pygame.Rect(e.x, e.y, TILE, TILE))
                    enemies.remove(e)
                    play_sfx(sfx_jump)
                else:
                    # Daño al jugador
                    lives -= 1
                    play_sfx(sfx_gameover)
                    player_hitbox.x -= 200 # Empujón hacia atrás
                    if lives <= 0: return await game_over(score)
        # Items
        for b in batteries[:]:
            if player_hitbox.colliderect(b): batteries.remove(b); score += 25; play_sfx(sfx_pickup)
        for sb in s_batteries[:]:
            if player_hitbox.colliderect(sb):
                s_batteries.remove(sb); lives += 1; play_sfx(sfx_powerup)
                t_end = max(pygame.time.get_ticks(), t_end) + t_max

        if player_hitbox.colliderect(door):
            play_sfx(sfx_victory); return await game(level + 1, score, lives)

        # Dibujado
        WIN.fill(CYBER_BG)
        if t_ms > 0: trail.append([player_hitbox.centerx, player_hitbox.centery, 14])
        for p in trail[:]:
            p[2] -= 1.0
            pygame.draw.circle(WIN, CYAN, (int(p[0]-camera_x), p[1]), int(p[2]))
            if p[2] <= 0: trail.remove(p)

        for f in floors: WIN.blit(floor_tile, (f.x - camera_x, f.y))
        for p in platforms: WIN.blit(platform_tile, (p.x - camera_x, p.y))
        for b in batteries: WIN.blit(battery_img, (b.x - camera_x, b.y))
        for sb in s_batteries: WIN.blit(red_battery_img, (sb.x - camera_x, sb.y))
        for e in enemies: WIN.blit(enemy_img, (e.x - camera_x, e.y))
        WIN.blit(door_img, (door.x - camera_x, door.y))
        WIN.blit(player_img, (player_hitbox.x - 10 - camera_x, player_hitbox.y - 5))

        btn_izq.dibujar(WIN); btn_der.dibujar(WIN); btn_salto.dibujar(WIN)
        draw_hud(level, score, lives, high_score, t_ms, t_max)
        
        pygame.display.update()
        await asyncio.sleep(0)

# 7. GAME OVER
async def game_over(final_score):
    pygame.mixer.music.stop()
    play_sfx(sfx_gameover) # Sonido de derrota
    
    while True:
        WIN.fill(BLACK)
        # Dibujamos los textos
        draw_text("NÚCLEO DAÑADO", 50, RED, WIDTH//2, HEIGHT//3)
        draw_text(f"PUNTUACIÓN FINAL: {final_score}", 30, WHITE, WIDTH//2, HEIGHT//2)
        draw_text("PRESIONA ENTER O TOCA PARA REINTENTAR", 20, CYAN, WIDTH//2, HEIGHT - 150)
        
        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN: 
                    pygame.mixer.music.play(-1)
                    return await game() # Reinicia el juego
            if e.type == pygame.MOUSEBUTTONDOWN:
                pygame.mixer.music.play(-1)
                return await game()

        # ESTA LÍNEA ES LA QUE HACE QUE CARGUE EN LA WEB
        await asyncio.sleep(0)
# 8. ARRANQUE
async def main():
    while True:
        if await main_menu(WIN, WIDTH, HEIGHT, CYBER_BG, CYAN, WHITE, RED, clock):
            await game()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())