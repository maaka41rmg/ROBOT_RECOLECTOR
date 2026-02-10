import asyncio  # <--- VITAL PARA WEB
import pygame
import sys
from interfaz.botones import BotonTactil

# --- FUNCIÓN AUXILIAR DE TEXTO ---
def draw_text_simple(WIN, txt, size, color, x, y):
    font = pygame.font.SysFont("consolas", size, True)
    img = font.render(txt, True, color)
    rect = img.get_rect(center=(x, y))
    WIN.blit(img, rect)

# --- FUNCIÓN DE CRÉDITOS (AHORA ASYNC) ---
async def show_credits(WIN, WIDTH, HEIGHT, CYBER_BG, CYAN, WHITE, clock, turbo_time=15000):
    waiting = True
    font_title = pygame.font.SysFont("consolas", 50, True)
    font_text = pygame.font.SysFont("consolas", 20, True)

    while waiting:
        WIN.fill(CYBER_BG)
        
        txt_cap = font_title.render("CONFIG & CRÉDITOS", True, CYAN)
        line_turbo = font_text.render(f"DURACIÓN TURBO: {turbo_time/1000} SEG", True, (255, 211, 25))
        line1 = font_text.render("Desarrollado por: Gladis Mercedes / Dylan", True, WHITE)
        line2 = font_text.render("Para: ♥Mi Girl of Dylan I love You♥ ", True, WHITE)
        line3 = font_text.render("Motor: Pygame 2.6.1", True, WHITE)
        txt_back = font_text.render("Presiona ESC o toca para volver", True, (150, 150, 150))

        WIN.blit(txt_cap, (WIDTH//2 - txt_cap.get_width()//2, HEIGHT//4))
        WIN.blit(line_turbo, (WIDTH//2 - line_turbo.get_width()//2, HEIGHT//2 - 80))
        WIN.blit(line1, (WIDTH//2 - line1.get_width()//2, HEIGHT//2))
        WIN.blit(line2, (WIDTH//2 - line2.get_width()//2, HEIGHT//2 + 40))
        WIN.blit(line3, (WIDTH//2 - line3.get_width()//2, HEIGHT//2 + 80))
        WIN.blit(txt_back, (WIDTH//2 - txt_back.get_width()//2, HEIGHT - 100))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        await asyncio.sleep(0) # <--- PERMITE QUE EL NAVEGADOR DIBUJE
        clock.tick(30)

# --- FUNCIÓN DE PAUSA (AHORA ASYNC) ---
async def pause_game(WIN, WIDTH, HEIGHT, CYAN, WHITE, clock, CYBER_BG):
    paused = True
    
    btn_continuar = BotonTactil(WIDTH//2 - 150, HEIGHT//2 - 60, 300, 60, "CONTINUAR", (50, 50, 50, 200), CYAN)
    btn_creditos = BotonTactil(WIDTH//2 - 150, HEIGHT//2 + 20, 300, 60, "CRÉDITOS", (50, 50, 50, 200), WHITE)
    btn_menu = BotonTactil(WIDTH//2 - 150, HEIGHT//2 + 100, 300, 60, "IR AL MENÚ", (50, 50, 50, 200), (255, 45, 85))

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((10, 5, 25)) 
    
    while paused:
        WIN.blit(overlay, (0, 0))
        draw_text_simple(WIN, "SISTEMA EN PAUSA", 50, CYAN, WIDTH//2, HEIGHT//4)

        btn_continuar.dibujar(WIN)
        btn_creditos.dibujar(WIN)
        btn_menu.dibujar(WIN)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_continuar.esta_presionado(): paused = False
                if btn_creditos.esta_presionado():
                    await show_credits(WIN, WIDTH, HEIGHT, CYBER_BG, CYAN, WHITE, clock, 15000)
                if btn_menu.esta_presionado(): return "MENU"
        
        await asyncio.sleep(0) # <--- EVITA PANTALLA NEGRA
        clock.tick(30)
    
    return "CONTINUAR"

# --- FUNCIÓN DEL MENÚ PRINCIPAL (AHORA ASYNC) ---
async def main_menu(WIN, WIDTH, HEIGHT, CYBER_BG, CYAN, WHITE, RED, clock):
    menu_running = True
    
    btn_jugar = BotonTactil(WIDTH//2 - 150, HEIGHT//2 - 40, 300, 60, "INICIAR MISIÓN", (40, 40, 40), CYAN)
    btn_ver_creditos = BotonTactil(WIDTH//2 - 150, HEIGHT//2 + 40, 300, 60, "CRÉDITOS", (40, 40, 40), WHITE)
    btn_salir = BotonTactil(WIDTH//2 - 150, HEIGHT//2 + 120, 300, 60, "DESCONECTAR", (40, 40, 40), RED)

    while menu_running:
        WIN.fill(CYBER_BG)
        
        font_title = pygame.font.SysFont("consolas", 70, True)
        txt_title = font_title.render("ROBO COLLECTOR", True, CYAN)
        WIN.blit(txt_title, (WIDTH//2 - txt_title.get_width()//2, HEIGHT//3))
        
        btn_jugar.dibujar(WIN)
        btn_ver_creditos.dibujar(WIN)
        btn_salir.dibujar(WIN)
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return True
                if event.key == pygame.K_c: 
                    await show_credits(WIN, WIDTH, HEIGHT, CYBER_BG, CYAN, WHITE, clock, 15000)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_jugar.esta_presionado(): return True
                if btn_ver_creditos.esta_presionado():
                    await show_credits(WIN, WIDTH, HEIGHT, CYBER_BG, CYAN, WHITE, clock, 15000)
                if btn_salir.esta_presionado(): pygame.quit(); sys.exit()
        
        await asyncio.sleep(0) # <--- CLAVE PARA QUE EL MENÚ SE VEA EN WEB
        clock.tick(30)