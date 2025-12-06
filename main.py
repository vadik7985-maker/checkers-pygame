"""
Главный файл для запуска игры в шашки
"""

import sys
import pygame

def main():
    """Основная функция запуска игры"""
    try:
        pygame.init()
        pygame.font.init()
        print("Игра в шашки - Профессиональная версия")
        print("Инициализация завершена успешно")
        
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Шашки")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            screen.fill((30, 30, 40))
            pygame.display.flip()
            
    except Exception as e:
        print(f"Ошибка при запуске игры: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()