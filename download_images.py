import os
import urllib.request
import json
from tarot_data import tarot_cards

def download_tarot_images():
    """
    타로 카드 이미지를 다운로드하는 함수
    
    User-Agent와 Referer 헤더를 추가하여 403 Forbidden 오류 방지
    """
    # 이미지 디렉토리 확인 및 생성
    if not os.path.exists('images'):
        os.makedirs('images')
        print("'images' 디렉토리를 생성했습니다.")
    
    # 다운로드할 이미지 목록
    download_list = []
    
    # 타로 카드 데이터에서 이미지 URL 추출
    for card in tarot_cards:
        image_file = card['image_file']
        image_url = card['image_url']
        
        # 샘플 URL인지 확인
        if 'example.com' in image_url:
            print(f"경고: {card['name']}의 URL이 샘플 URL입니다. 실제 URL로 교체해주세요.")
            continue
        
        download_list.append((image_url, image_file))
    
    # 이미지 다운로드
    for url, filename in download_list:
        try:
            print(f"{filename} 다운로드 중...")
            
            # 헤더 추가
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://www.google.com/',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8',
                'Connection': 'keep-alive'
            }
            
            # 요청 객체 생성
            req = urllib.request.Request(url, headers=headers)
            
            # 이미지 다운로드
            with urllib.request.urlopen(req) as response, open(os.path.join('images', filename), 'wb') as out_file:
                data = response.read()
                out_file.write(data)
                
            print(f"{filename} 다운로드 완료!")
        except Exception as e:
            print(f"{filename} 다운로드 실패: {e}")
    
    print("\n다운로드 프로세스 완료!")

def download_single_image(url, filename):
    """
    단일 이미지를 다운로드하는 함수
    
    Args:
        url (str): 이미지 URL
        filename (str): 저장할 파일 이름
    """
    try:
        # 이미지 디렉토리 확인 및 생성
        if not os.path.exists('images'):
            os.makedirs('images')
        
        print(f"{filename} 다운로드 중...")
        
        # 헤더 추가
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.google.com/',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
        
        # 요청 객체 생성
        req = urllib.request.Request(url, headers=headers)
        
        # 이미지 다운로드
        with urllib.request.urlopen(req) as response, open(os.path.join('images', filename), 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            
        print(f"{filename} 다운로드 완료!")
        return True
    except Exception as e:
        print(f"{filename} 다운로드 실패: {e}")
        return False

if __name__ == "__main__":
    print("타로 카드 이미지 다운로더")
    print("=" * 30)
    print("1. 모든 카드 이미지 다운로드")
    print("2. 단일 이미지 다운로드")
    print("=" * 30)
    
    choice = input("선택하세요 (1/2): ")
    
    if choice == '1':
        download_tarot_images()
    elif choice == '2':
        url = input("이미지 URL을 입력하세요: ")
        filename = input("저장할 파일 이름을 입력하세요 (예: 00_fool.jpg): ")
        download_single_image(url, filename)
    else:
        print("잘못된 선택입니다.")
