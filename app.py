from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import dateutil.parser
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)
CORS(app)

# Biến lưu cache RAM (luôn cập nhật mỗi phút)
news_cache = {
    "cnn": [],
    "cnbc": [],
    "fox": [],
    "yahoo": [],
    "cbsnews": [],
}

# ----------- Crawl Time Helper ----------
def get_article_time(article_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(article_url, headers=headers, timeout=5)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        time_tag = soup.find('time')
        if time_tag and time_tag.has_attr('datetime'):
            dt = dateutil.parser.isoparse(time_tag['datetime'])
            return dt.astimezone(timezone.utc)
    except:
        return None
    return None

# ---------- CNBC ----------
def fetch_cnbc_latest_news():
    url = "https://www.cnbc.com/world/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []
    for item in soup.select('a.LatestNews-headline'):
        title = item.get_text(strip=True)
        link = item.get('href')
        if not link.startswith('http'):
            link = 'https://www.cnbc.com' + link
        publishedAt = get_article_time(link) or datetime.now(timezone.utc)
        articles.append({
            'title': title,
            'link': link,
            'publishedAt': publishedAt.isoformat()
        })
    return articles

# ---------- CNN ----------
def fetch_cnn_latest_news_selenium():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    url = "https://edition.cnn.com/world"
    driver.get(url)

    articles = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.container__link--type-article"))
        )
        headline_links = driver.find_elements(By.CSS_SELECTOR, "a.container__link--type-article")
        now = datetime.now(timezone.utc).isoformat()
        for a in headline_links[:30]:
            title = a.get_attribute("data-zjs-card_name") or a.text
            link = a.get_attribute("href")
            if link.startswith("/"):
                link = "https://edition.cnn.com" + link
            articles.append({
                "title": title.strip(),
                "link": link,
                "publishedAt": now
            })
    except Exception as e:
        print("CNN error:", e)
    finally:
        driver.quit()
    return articles

# ---------- FOX ----------
def fetch_foxbusiness_latest_news():
    url = "https://www.foxbusiness.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []
    for item in soup.select('h2 a[href]'):
        title = item.get_text(strip=True)
        link = item['href']
        if not link.startswith('http'):
            link = 'https://www.foxbusiness.com' + link

        # Lọc bỏ các link chuyên mục, danh mục
        if "/category/" in link or "/tags/" in link:
            continue

        publishedAt = get_article_time(link) or datetime.now(timezone.utc)
        articles.append({
            'title': title,
            'link': link,
            'publishedAt': publishedAt.isoformat()
        })
    return articles

def get_cbs_news():
    try:
        url = "https://www.cbsnews.com/latest/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []

        for item in soup.select('article.item a'):
            title = item.get_text(strip=True)
            link = item.get('href')
            if link and not link.startswith("http"):
                link = "https://www.cbsnews.com" + link
            if title and link:
                articles.append({
                    'title': title,
                    'link': link
                })

        # Trả về danh sách 15 bài mới nhất
        return articles[:15]
    except Exception as e:
        print("Error fetching CBS News:", e)
        return []


def fetch_yahoo_finance_latest_news():
    url = 'https://finance.yahoo.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Cố gắng tìm khối Latest News (có thể thay đổi, bạn có thể debug lại nếu không lấy được)
    latest_section = soup.find('div', class_='hero-headlines hero-latest-news yf-36pijq')
    articles = []

    if latest_section:
        items = latest_section.find_all('li', class_='story-item')
        for item in items:
            title_tag = item.find('h3')
            link_tag = item.find('a', href=True)
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                link = link_tag['href']
                if link.startswith('/'):
                    link = 'https://finance.yahoo.com' + link

                publishedAt = get_article_time(link) or datetime.now(timezone.utc)
                articles.append({
                    'title': title,
                    'link': link,
                    'publishedAt': publishedAt.isoformat()
                })
    else:
        # Nếu không tìm thấy block, có thể fallback hoặc trả về rỗng
        print("Không tìm thấy khối 'Latest News' trên Yahoo Finance.")
    
    return articles




# ----------- Update thread mỗi phút -----------
def auto_update_news():
    while True:
        print("⏳ Đang crawl lại tin mới...")
        try:
            news_cache["cnn"] = fetch_cnn_latest_news_selenium()
            news_cache["cnbc"] = fetch_cnbc_latest_news()
            news_cache["fox"] = fetch_foxbusiness_latest_news()
            news_cache["yahoo"] = fetch_yahoo_finance_latest_news()
            news_cache["cbsnews"] = get_cbs_news()

            print("✅ Tin đã được cập nhật lúc", datetime.now().strftime('%H:%M:%S'))
        except Exception as e:
            print("❌ Lỗi khi cập nhật:", e)
        time.sleep(60)

# ----------- API Route trả về cache RAM ----------

@app.route('/api/cbs-news')
def api_cbsnews():
    return jsonify({
        "count": len(news_cache["cbsnews"]),
        "news": news_cache["cbsnews"]
    })

@app.route("/api/yahoo-news")
def api_yahoo():
    return jsonify({
        "count": len(news_cache["yahoo"]),
        "news": news_cache["yahoo"]
    })
@app.route("/api/cnn-news")
def api_cnn():
    return jsonify({
        "count": len(news_cache["cnn"]),
        "news": news_cache["cnn"]
    })

@app.route("/api/news")
def api_cnbc():
    return jsonify({
        "count": len(news_cache["cnbc"]),
        "news": news_cache["cnbc"]
    })

@app.route("/api/foxbusiness-news")
def api_fox():
    return jsonify({
        "count": len(news_cache["fox"]),
        "news": news_cache["fox"]
    })

# ----------- Chạy Flask và khởi động thread update ----------
if __name__ == "__main__":
    threading.Thread(target=auto_update_news, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
