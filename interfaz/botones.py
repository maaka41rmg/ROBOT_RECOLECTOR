import pygame

class BotonTactil:
    def __init__(self, x, y, ancho, alto, texto, color_base, color_click):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_base = color_base
        self.color_click = color_click
        self.color_actual = color_base
        self.fuente = pygame.font.SysFont("consolas", 40, True)

    def dibujar(self, ventana):
        # Dibujamos el cuerpo del botón
        pygame.draw.rect(ventana, self.color_actual, self.rect, border_radius=15)
        # Dibujamos el borde brillante
        pygame.draw.rect(ventana, (255, 255, 255), self.rect, 3, border_radius=15)
        
        # Renderizar y centrar el texto
        img_texto = self.fuente.render(self.texto, True, (255, 255, 255))
        rect_texto = img_texto.get_rect(center=self.rect.center)
        ventana.blit(img_texto, rect_texto)

    def esta_presionado(self):
        # Detecta si el mouse o el dedo están sobre el botón y presionando
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]:
                self.color_actual = self.color_click
                return True
        self.color_actual = self.color_base
        return False