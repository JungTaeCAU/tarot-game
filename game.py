import pygame
import random
import sys
import os
from pygame.locals import *
import urllib.request
from tarot_data import tarot_cards

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
BACKGROUND = (20, 20, 50)

# 폰트 설정 (한글 지원)
try:
    font_large = pygame.font.SysFont('malgungothic', 48)
    font_medium = pygame.font.SysFont('malgungothic', 28)
    font_small = pygame.font.SysFont('malgungothic', 20)
except:
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 20)

# 이미지 디렉토리 확인 및 생성
if not os.path.exists('images'):
    os.makedirs('images')

# 카드 뒷면 이미지 생성
def create_card_back():
    card_back = pygame.Surface((120, 180))
    card_back.fill(DARK_BLUE)
    
    # 카드 뒷면 디자인
    pygame.draw.rect(card_back, GOLD, (10, 10, 100, 160), 2)
    pygame.draw.rect(card_back, GOLD, (20, 20, 80, 140), 1)
    
    # 별 모양 그리기 (간단한 버전)
    center_x, center_y = 60, 90
    pygame.draw.circle(card_back, GOLD, (center_x, center_y), 30, 1)
    
    # 대각선 그리기
    pygame.draw.line(card_back, GOLD, (center_x - 30, center_y - 30), (center_x + 30, center_y + 30), 1)
    pygame.draw.line(card_back, GOLD, (center_x - 30, center_y + 30), (center_x + 30, center_y - 30), 1)
    
    # 이미지 저장
    pygame.image.save(card_back, 'images/card_back.png')
    return card_back

# 카드 클래스
class Card:
    def __init__(self, x, y, width, height, card_data):
        self.rect = pygame.Rect(x, y, width, height)
        self.card_data = card_data
        self.revealed = False
        self.hover = False
        self.flip_progress = 0  # 0: 뒷면, 100: 앞면
        self.flipping = False
        self.original_pos = (x, y)
        self.target_pos = (x, y)
        self.move_progress = 0
        self.moving = False
        
        # 이미지 로드 또는 생성
        self.front_image = self.create_card_front()
        self.back_image = pygame.image.load('images/card_back.png') if os.path.exists('images/card_back.png') else create_card_back()
        
    def create_card_front(self):
        # 실제 이미지 파일이 있는지 확인
        image_path = os.path.join('images', self.card_data['image_file'])
        if os.path.exists(image_path):
            return pygame.image.load(image_path)
        
        # 이미지가 없으면 기본 카드 생성
        card_front = pygame.Surface((120, 180))
        card_front.fill(WHITE)
        pygame.draw.rect(card_front, BLACK, card_front.get_rect(), 2)
        
        # 카드 이름 렌더링
        try:
            name_font = pygame.font.SysFont('malgungothic', 16)
        except:
            name_font = pygame.font.Font(None, 16)
            
        name_text = name_font.render(self.card_data["name"], True, BLACK)
        name_rect = name_text.get_rect(center=(60, 30))
        card_front.blit(name_text, name_rect)
        
        # 구분선
        pygame.draw.line(card_front, BLACK, (20, 50), (100, 50), 1)
        
        # 카드 의미
        try:
            meaning_font = pygame.font.SysFont('malgungothic', 14)
        except:
            meaning_font = pygame.font.Font(None, 14)
            
        meaning_text = meaning_font.render(self.card_data["meaning"], True, PURPLE)
        meaning_rect = meaning_text.get_rect(center=(60, 70))
        card_front.blit(meaning_text, meaning_rect)
        
        # 이미지 저장
        pygame.image.save(card_front, image_path)
        return card_front
        
    def draw(self):
        # 카드 이동 애니메이션
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
        
        # 카드 뒤집기 애니메이션
        if self.flipping:
            self.flip_progress += 5
            if self.flip_progress >= 100:
                self.flip_progress = 100
                self.flipping = False
                self.revealed = True
        
        # 카드 그리기
        if self.flip_progress < 50:
            # 뒷면 그리기
            width_scale = 1 - (self.flip_progress / 50) * 0.9
            
            scaled_width = int(self.rect.width * width_scale)
            scaled_back = pygame.transform.scale(self.back_image, (scaled_width, self.rect.height))
            
            x = self.rect.x + (self.rect.width - scaled_width) // 2
            screen.blit(scaled_back, (x, self.rect.y))
            
            # 호버 효과
            if self.hover and not self.flipping and not self.revealed:
                # 더 두꺼운 테두리와 밝은 색상으로 강조
                pygame.draw.rect(screen, GOLD, (x-2, self.rect.y-2, scaled_width+4, self.rect.height+4), 4)
        else:
            # 앞면 그리기
            width_scale = (self.flip_progress - 50) / 50 * 0.9 + 0.1
            
            scaled_width = int(self.rect.width * width_scale)
            scaled_front = pygame.transform.scale(self.front_image, (scaled_width, self.rect.height))
            
            x = self.rect.x + (self.rect.width - scaled_width) // 2
            screen.blit(scaled_front, (x, self.rect.y))
    
    def check_hover(self, pos):
        was_hover = self.hover
        self.hover = self.rect.collidepoint(pos) and not self.revealed and not self.flipping
        return self.hover != was_hover
    
    def is_clickable(self, pos):
        # 클릭 가능 여부를 확인하는 함수 (영역을 약간 확장)
        # 카드 주변에 약간의 여유를 두어 클릭 감지 영역을 넓힘
        expanded_rect = self.rect.inflate(20, 20)  # 가로, 세로로 각각 20픽셀 확장
        return expanded_rect.collidepoint(pos) and not self.revealed and not self.flipping
        
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
        if self.hover:
            pygame.draw.rect(screen, self.hover_color, self.rect, border_radius=10)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        
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
    # 그라데이션 배경
    for y in range(SCREEN_HEIGHT):
        color_value = int(20 + (y / SCREEN_HEIGHT) * 30)
        pygame.draw.line(screen, (color_value, color_value, color_value + 10), (0, y), (SCREEN_WIDTH, y))
    
    # 별 그리기
    for i in range(50):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)

# 게임 초기화
def init_game():
    random.shuffle(tarot_cards)
    cards = []
    
    # 3행 7열로 카드 배치
    card_width, card_height = 120, 180
    margin_x, margin_y = 30, 50
    
    for row in range(3):
        for col in range(7):
            idx = row * 7 + col
            if idx < len(tarot_cards):
                x = margin_x + col * (card_width + 10)
                y = margin_y + row * (card_height + 20)
                cards.append(Card(x, y, card_width, card_height, tarot_cards[idx]))
    
    return cards

# 메인 함수
def main():
    # 카드 뒷면 이미지 생성
    if not os.path.exists('images/card_back.png'):
        create_card_back()
    
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
                        if card.is_clickable(mouse_pos) and not card.revealed and not card.flipping:
                            if card.start_flip():
                                selected_cards.append(card)
                                # 클릭 피드백 추가
                                pygame.time.delay(100)  # 약간의 딜레이로 클릭 인식 확인
                                if len(selected_cards) == 3:  # 3장의 카드를 선택하면 리딩 단계로
                                    # 잠시 대기 후 리딩 화면으로 전환
                                    pygame.time.delay(1000)
                                    game_state = GameState.READING
                                    
                                    # 카드 위치 재배치
                                    positions = [
                                        (SCREEN_WIDTH//4 - 60, SCREEN_HEIGHT//2 - 90),
                                        (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 - 90),
                                        (3*SCREEN_WIDTH//4 - 60, SCREEN_HEIGHT//2 - 90)
                                    ]
                                    
                                    for i, card in enumerate(selected_cards):
                                        card.move_to(positions[i][0], positions[i][1])
                
                elif game_state == GameState.READING:
                    # 카드 클릭 시 상세 리딩으로
                    for i, card in enumerate(selected_cards):
                        if card.rect.collidepoint(mouse_pos):
                            detailed_card = card
                            game_state = GameState.DETAILED_READING
                    
                    # 다시 시작 버튼
                    if back_button.rect.collidepoint(mouse_pos):
                        game_state = GameState.INTRO
                        selected_cards = []
                
                elif game_state == GameState.DETAILED_READING:
                    # 아무 곳이나 클릭하면 리딩 화면으로 돌아감
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
            # 타이틀
            title = font_large.render("타로 카드 리딩", True, GOLD)
            subtitle = font_medium.render("당신의 과거, 현재, 미래를 알아보세요", True, WHITE)
            
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            
            screen.blit(title, title_rect)
            screen.blit(subtitle, subtitle_rect)
            
            # 시작 버튼
            start_button.draw()
            
        elif game_state == GameState.SELECTING:
            # 안내 텍스트
            title = font_medium.render("세 장의 카드를 선택하세요", True, WHITE)
            subtitle = font_small.render("첫 번째 카드는 과거, 두 번째는 현재, 세 번째는 미래를 나타냅니다", True, WHITE)
            
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 20))
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 50))
            
            screen.blit(title, title_rect)
            screen.blit(subtitle, subtitle_rect)
            
            # 선택 상태 표시
            status_text = font_small.render(f"선택한 카드: {len(selected_cards)}/3", True, WHITE)
            status_rect = status_text.get_rect(topleft=(20, SCREEN_HEIGHT - 30))
            screen.blit(status_text, status_rect)
            
            # 카드 그리기
            for card in cards:
                card.draw()
                
        elif game_state == GameState.READING:
            # 타이틀
            title = font_medium.render("당신의 타로 리딩 결과", True, GOLD)
            subtitle = font_small.render("카드를 클릭하면 더 자세한 해석을 볼 수 있습니다", True, WHITE)
            
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 20))
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 50))
            
            screen.blit(title, title_rect)
            screen.blit(subtitle, subtitle_rect)
            
            # 선택된 카드 표시
            labels = ["과거", "현재", "미래"]
            
            for i, card in enumerate(selected_cards):
                card.draw()
                
                # 라벨 표시
                label = font_medium.render(labels[i], True, GOLD)
                label_rect = label.get_rect(center=(card.rect.centerx, card.rect.y - 30))
                screen.blit(label, label_rect)
                
                # 카드 의미 표시
                meaning = font_small.render(card.card_data["meaning"], True, WHITE)
                meaning_rect = meaning.get_rect(center=(card.rect.centerx, card.rect.y + card.rect.height + 30))
                screen.blit(meaning, meaning_rect)
            
            # 다시 시작 버튼
            back_button.draw()
            
        elif game_state == GameState.DETAILED_READING:
            # 배경 어둡게
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            # 카드 상세 정보 표시
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
            
            # 카드 상세 설명 (여러 줄로 나누기)
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
            
            # 안내 텍스트
            instruction = font_small.render("아무 곳이나 클릭하여 돌아가기", True, WHITE)
            instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
            screen.blit(instruction, instruction_rect)
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
