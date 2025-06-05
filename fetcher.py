import requests
from bs4 import BeautifulSoup

# URL của Yahoo Finance
url = 'https://finance.yahoo.com/'

# Tạo header để giả lập trình duyệt
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# Gửi request
response = requests.get(url, headers=headers)

# Kiểm tra status
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Tìm khối chứa "Latest" news
    latest_section = soup.find('div', class_='hero-headlines hero-latest-news yf-36pijq')
    if latest_section:
        items = latest_section.find_all('li', class_='story-item')
        print(f'Tìm thấy {len(items)} tin mới nhất:\n')
        for item in items:
            title_tag = item.find('h3')
            link_tag = item.find('a', href=True)
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                link = 'https://finance.yahoo.com' + link_tag['href'] if link_tag['href'].startswith('/') else link_tag['href']
                print(f"- {title}\n  Link: {link}\n")
    else:
        print("Không tìm thấy khối 'Latest News'. Có thể cấu trúc HTML đã thay đổi.")
else:
    print(f"Lỗi khi gửi request: {response.status_code}")
