import pygame
import random
import sys
import os
from pygame.locals import *
import urllib.request
import json

# 초기화
pygame.init()
pygame.font.init()

# 화면 설정
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('타로 카드 리딩')

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
GOLD = (218, 165, 32)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)

# 폰트 설정 (한글 지원)
try:
    font_large = pygame.font.SysFont('malgungothic', 48)
    font_medium = pygame.font.SysFont('malgungothic', 28)
    font_small = pygame.font.SysFont('malgungothic', 20)
except:
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 20)

# 이미지 로딩 함수
def load_image(path):
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (120, 180))
    except:
        # 이미지 로드 실패시 기본 카드 생성
        surface = pygame.Surface((120, 180))
        surface.fill(WHITE)
        pygame.draw.rect(surface, BLACK, surface.get_rect(), 2)
        return surface

# 카드 클래스
class Card:
    def __init__(self, x, y, width, height, card_data):
        self.rect = pygame.Rect(x, y, width, height)
        self.card_data = card_data
        self.revealed = False
        self.hover = False
        self.flip_progress = 0
        self.flipping = False
        self.original_pos = (x, y)
        self.target_pos = (x, y)
        self.move_progress = 0
        self.moving = False
        
        # 이미지 로드
        self.front_image = load_image(os.path.join('images', card_data['image_file']))
        self.back_image = load_image('images/card_back.png')
        
    def draw(self):
        if self.moving:
            self.move_progress += 5
            if self.move_progress >= 100:
                self.move_progress = 100
                self.moving = False
                self.rect.x = self.target_pos[0]
                self.rect.y = self.target_pos[1]
            else:
                progress = self.move_progress / 100
                self.rect.x = self.original_pos[0] + (self.target_pos[0] - self.original_pos[0]) * progress
                self.rect.y = self.original_pos[1] + (self.target_pos[1] - self.original_pos[1]) * progress
        
        if self.flipping:
            self.flip_progress += 5
            if self.flip_progress >= 100:
                self.flip_progress = 100
                self.flipping = False
                self.revealed = True
        
        # 카드 그리기
        if self.flip_progress < 50:
            # 뒷면
            width_scale = abs(1 - (self.flip_progress / 50) * 0.9)
            scaled_width = int(self.rect.width * width_scale)
            scaled_back = pygame.transform.scale(self.back_image, (scaled_width, self.rect.height))
            
            x = self.rect.x + (self.rect.width - scaled_width) // 2
            screen.blit(scaled_back, (x, self.rect.y))
            
            if self.hover and not self.flipping and not self.revealed:
                pygame.draw.rect(screen, GOLD, (x, self.rect.y, scaled_width, self.rect.height), 3)
        else:
            # 앞면
            width_scale = (self.flip_progress - 50) / 50 * 0.9 + 0.1
            scaled_width = int(self.rect.width * width_scale)
            scaled_front = pygame.transform.scale(self.front_image, (scaled_width, self.rect.height))
            
            x = self.rect.x + (self.rect.width - scaled_width) // 2
            screen.blit(scaled_front, (x, self.rect.y))
    
    def check_hover(self, pos):
        was_hover = self.hover
        self.hover = self.rect.collidepoint(pos) and not self.revealed and not self.flipping
        return self.hover != was_hover
    
    def start_flip(self):
        if not self.revealed and not self.flipping:
            self.flipping = True
            self.flip_progress = 0
            return True
        return False
    
    def move_to(self, x, y):
        self.original_pos = (self.rect.x, self.rect.y)
        self.target_pos = (x, y)
        self.moving = True
        self.move_progress = 0

# 버튼 클래스
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hover = False
        
    def draw(self):
        color = self.hover_color if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        
        text = font_medium.render(self.text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
    
    def check_hover(self, pos):
        was_hover = self.hover
        self.hover = self.rect.collidepoint(pos)
        return self.hover != was_hover

# 게임 상태
class GameState:
    INTRO = 0
    SELECTING = 1
    READING = 2
    DETAILED_READING = 3

# 배경 그리기
def draw_background():
    screen.fill((245, 245, 255))
    for i in range(20):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 3)
        pygame.draw.circle(screen, GOLD, (x, y), size)

def main():
    clock = pygame.time.Clock()
    game_state = GameState.INTRO
    cards = []
    selected_cards = []
    detailed_card = None
    
    # 버튼 생성
    start_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50, "시작하기", LIGHT_BLUE, GOLD)
    back_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 50, "다시 시작", LIGHT_BLUE, GOLD)
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                
            if event.type == MOUSEBUTTONDOWN:
                if game_state == GameState.INTRO:
                    if start_button.rect.collidepoint(mouse_pos):
                        game_state = GameState.SELECTING
                        cards = init_game()
                    
                elif game_state == GameState.SELECTING:
                    for card in cards:
                        if card.check_hover(mouse_pos) and not card.revealed and not card.flipping:
                            if card.start_flip():
                                selected_cards.append(card)
                                if len(selected_cards) == 3:
                                    pygame.time.delay(1000)
                                    game_state = GameState.READING
                                    
                                    positions = [
                                        (SCREEN_WIDTH//4 - 60, SCREEN_HEIGHT//2 - 90),
                                        (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 - 90),
                                        (3*SCREEN_WIDTH//4 - 60, SCREEN_HEIGHT//2 - 90)
                                    ]
                                    
                                    for i, card in enumerate(selected_cards):
                                        card.move_to(positions[i][0], positions[i][1])
                
                elif game_state == GameState.READING:
                    for card in selected_cards:
                        if card.rect.collidepoint(mouse_pos):
                            detailed_card = card
                            game_state = GameState.DETAILED_READING
                    
                    if back_button.rect.collidepoint(mouse_pos):
                        game_state = GameState.INTRO
                        selected_cards = []
                
                elif game_state == GameState.DETAILED_READING:
                    game_state = GameState.READING
        
        # 마우스 호버 체크
        if game_state == GameState.INTRO:
            start_button.check_hover(mouse_pos)
        elif game_state == GameState.SELECTING:
            for card in cards:
                card.check_hover(mouse_pos)
        elif game_state == GameState.READING:
            back_button.check_hover(mouse_pos)
        
        # 화면 그리기
        draw_background()
        
        if game_state == GameState.INTRO:
            title = font_large.render("타로 카드 리딩", True, PURPLE)
            subtitle = font_medium.render("당신의 과거, 현재, 미래를 알아보세요", True, BLACK)
            
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            
            screen.blit(title, title_rect)
            screen.blit(subtitle, subtitle_rect)
            start_button.draw()
            
        elif game_state == GameState.SELECTING:
            title = font_medium.render("세 장의 카드를 선택하세요", True, BLACK)
            subtitle = font_small.render("첫 번째 카드는 과거, 두 번째는 현재, 세 번째는 미래를 나타냅니다", True, BLACK)
            
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 20))
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 50))
            
            screen.blit(title, title_rect)
            screen.blit(subtitle, subtitle_rect)
            
            status_text = font_small.render(f"선택한 카드: {len(selected_cards)}/3", True, BLACK)
            status_rect = status_text.get_rect(topleft=(20, SCREEN_HEIGHT - 30))
            screen.blit(status_text, status_rect)
            
            for card in cards:
                card.draw()
                
        elif game_state == GameState.READING:
            title = font_medium.render("당신의 타로 리딩 결과", True, PURPLE)
            subtitle = font_small.render("카드를 클릭하면 더 자세한 해석을 볼 수 있습니다", True, BLACK)
            
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 20))
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 50))
            
            screen.blit(title, title_rect)
            screen.blit(subtitle, subtitle_rect)
            
            labels = ["과거", "현재", "미래"]
            
            for i, card in enumerate(selected_cards):
                card.draw()
                label = font_medium.render(labels[i], True, PURPLE)
                label_rect = label.get_rect(center=(card.rect.centerx, card.rect.y - 30))
                screen.blit(label, label_rect)
            
            back_button.draw()
            
        elif game_state == GameState.DETAILED_READING:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            card_width, card_height = 240, 360
            card_x = SCREEN_WIDTH//2 - card_width//2
            card_y = 100
            
            # 큰 카드 이미지 표시
            scaled_image = pygame.transform.scale(detailed_card.front_image, (card_width, card_height))
            screen.blit(scaled_image, (card_x, card_y))
            pygame.draw.rect(screen, GOLD, (card_x, card_y, card_width, card_height), 3)
            
            # 카드 설명
            desc_y = card_y + card_height + 20
            name_text = font_medium.render(detailed_card.card_data["name"], True, WHITE)
            meaning_text = font_medium.render(detailed_card.card_data["meaning"], True, GOLD)
            
            name_rect = name_text.get_rect(center=(SCREEN_WIDTH//2, desc_y))
            meaning_rect = meaning_text.get_rect(center=(SCREEN_WIDTH//2, desc_y + 40))
            
            screen.blit(name_text, name_rect)
            screen.blit(meaning_text, meaning_rect)
            
            description = detailed_card.card_data["description"]
            words = description.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if font_small.size(test_line)[0] < card_width + 100:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            for i, line in enumerate(lines):
                desc_text = font_small.render(line, True, WHITE)
                desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, desc_y + 80 + i * 25))
                screen.blit(desc_text, desc_rect)
            
            instruction = font_small.render("아무 곳이나 클릭하여 돌아가기", True, WHITE)
            instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
            screen.blit(instruction, instruction_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
