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
    scraper = cloudscraper.create_scraper()
    url = "https://mabinogi.nexon.com/page/news/notice_list.asp"
    res = scraper.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("ul > li")

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
            
            if title in processed_titles:
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
    new_notices = []
    
    for notice in current_notices:
        if not any(p['title'] == notice['title'] for p in previous_notices):
            new_notices.append(notice)

    # 새로운 공지사항이 있으면 저장하고 메시지 반환
    if new_notices:
        save_notices(current_notices)
        messages.sort(key=lambda x: x['date'], reverse=True)
        sorted_messages = [msg['content'] for msg in messages]
        return "\n\n".join(sorted_messages)
    
    return None

def send_to_discord(content):
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    data = {"username": "📢 마비노기 알리미", "content": content}
    requests.post(webhook_url, json=data)

def main():
    try:
        msg = fetch_latest_notices()
        if msg:  # 새로운 공지사항이 있을 때만 메시지 전송
            send_to_discord(msg)
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
