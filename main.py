import cloudscraper
from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime
import json

def load_previous_notices():
    try:
        with open('previous_notices.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_notices(notices):
    with open('previous_notices.json', 'w', encoding='utf-8') as f:
        json.dump(notices, f, ensure_ascii=False, indent=2)

def fetch_latest_notices():
    print("Starting to fetch notices...")
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    
    # User-Agent 추가
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
    }
    
    url = "https://mabinogi.nexon.com/page/news/notice_list.asp"
    try:
        res = scraper.get(url, headers=headers)
        print(f"Response status code: {res.status_code}")
        print(f"Response content length: {len(res.text)}")
        
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("ul > li")
        print(f"Found {len(items)} total items")
        
        # HTML 내용 일부 출력하여 디버깅
        print("First few items HTML:")
        for item in items[:2]:
            print(item.prettify())
            
        messages = []
        processed_titles = set()
        current_notices = []

        for item in items:
            if 'icon_new.gif' not in str(item):
                continue

            a_tag = item.select_one("dt > a")
            date_tag = item.select_one("span.date")
            if a_tag and date_tag:
                title = a_tag.text.strip()
                print(f"Processing notice: {title}")
                
                if title in processed_titles:
                    print(f"Skipping duplicate: {title}")
                    continue
                    
                link = "https://mabinogi.nexon.com/page/news/" + a_tag['href']
                date = date_tag.text.strip()
                
                notice_info = {
                    'title': title,
                    'date': date,
                    'link': link
                }
                current_notices.append(notice_info)
                
                messages.append({
                    'date': date,
                    'content': f"🗓️ **{date}**\n🔹 {title}\n{link}"
                })
                processed_titles.add(title)

            if len(messages) >= 4:
                break

        # 이전 공지사항과 비교
        previous_notices = load_previous_notices()
        print(f"Loaded {len(previous_notices)} previous notices")
        
        new_notices = []
        for notice in current_notices:
            if not any(p['title'] == notice['title'] for p in previous_notices):
                new_notices.append(notice)
                print(f"Found new notice: {notice['title']}")

        # 새로운 공지사항이 있으면 저장하고 메시지 반환
        if new_notices:
            print(f"Saving {len(current_notices)} notices")
            save_notices(current_notices)
            messages.sort(key=lambda x: x['date'], reverse=True)
            sorted_messages = [msg['content'] for msg in messages]
            return "\n\n".join(sorted_messages)
        else:
            print("No new notices found")
        
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def send_to_discord(content):
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL is not set")
        return
        
    data = {"username": "📢 마비노기 알리미", "content": content}
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()  # HTTP 에러 체크
        print(f"Successfully sent message to Discord. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Discord: {e}")

def main():
    try:
        print("Starting to fetch notices...")
        msg = fetch_latest_notices()
        if msg:
            print("New notices found, sending to Discord...")
            send_to_discord(msg)
        else:
            print("No new notices found")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
