import streamlit as st
import asyncio
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
try:
    from playwright_stealth import stealth_async
except ImportError:
    from playwright_stealth import Stealth
    async def stealth_async(page):
        await Stealth().apply_stealth_async(page)

import urllib.parse
import re
import subprocess
import os

# Streamlit Community Cloud 등 리눅스 환경에서 Playwright Chromium 브라우저 자동 설치 보장
@st.cache_resource
def ensure_playwright_browsers():
    try:
        # 이미 설치되어 있는지 확인하거나, 첫 기동 시 설치
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        pass

ensure_playwright_browsers()

# 페이지 기본 설정
st.set_page_config(
    page_title="얼마 - 최저가 가격 비교",
    page_icon="🛍️",
    layout="wide"
)

# ----------------- 100% 안전하고 완벽한 CSS 스타일 -----------------
st.markdown("""<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

html, body, [class*="css"] {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
}

.stApp {
    background-color: #F8F9FA;
}

.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px;
}

/* 상단 헤더 */
.header-box {
    text-align: center;
    margin-bottom: 2rem;
}
.main-logo-title {
    font-size: 3.2rem;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.04em;
    margin-bottom: 0.8rem;
}
.main-desc {
    font-size: 1.15rem;
    color: #374151;
    font-weight: 500;
    letter-spacing: -0.02em;
}

/* 검색창 & 버튼 스타일 */
div[data-testid="stTextInput"] {
    flex: 1;
    margin-bottom: 0px !important;
}
div[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border: 1px solid #D1D5DB !important;
    height: 48px !important;
    padding: 0 16px !important;
    font-size: 0.95rem !important;
    background-color: #FFFFFF !important;
    color: #111827 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #9CA3AF !important;
    font-weight: 400;
}

div[data-testid="stButton"] button {
    height: 48px !important;
    background-color: #1F2937 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 0 24px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
    transition: all 0.2s ease !important;
    white-space: nowrap !important;
}
div[data-testid="stButton"] button:hover {
    background-color: #111827 !important;
    transform: translateY(-1px) !important;
}

/* 4대 쇼핑몰 카드 컨테이너 */
.card-container {
    background: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
    border: 1px solid #E5E7EB;
    overflow: hidden;
    margin-bottom: 1.5rem;
}

/* 카드 상단 배너 헤더 */
.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 18px;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 1.15rem;
}
.header-danawa { background-color: #2D4C7F; }
.header-naver { background-color: #03C75A; }
.header-coupang { background-color: #E26829; }
.header-aliexpress { background: linear-gradient(135deg, #FF4747, #E62E04); }

.header-left {
    display: flex;
    align-items: center;
    gap: 8px;
}
.arrow-icon {
    font-size: 1.2rem;
    opacity: 0.85;
}

/* 카드 내부 상품 행(Row) */
.product-row {
    display: flex;
    align-items: center;
    padding: 14px 16px;
    border-bottom: 1px solid #F3F4F6;
    gap: 12px;
    background-color: #FFFFFF;
    transition: background-color 0.15s ease;
}
.product-row:last-child {
    border-bottom: none;
}
.product-row:hover {
    background-color: #FAFAFA;
}

/* 상품 썸네일 이미지 */
.prod-img {
    width: 64px;
    height: 64px;
    border-radius: 8px;
    object-fit: cover;
    background-color: #F3F4F6;
    border: 1px solid #E5E7EB;
    flex-shrink: 0;
}

/* 상품 상세 정보 */
.prod-info {
    flex: 1;
    min-width: 0;
}
.prod-title {
    font-size: 0.84rem;
    font-weight: 600;
    color: #1F2937;
    line-height: 1.35;
    margin-bottom: 5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.prod-price-box {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 3px;
}
.prod-price {
    font-size: 0.98rem;
    font-weight: 700;
    color: #111827;
}
.prod-badge {
    font-size: 0.75rem;
    color: #9CA3AF;
}
.prod-shipping {
    font-size: 0.72rem;
    color: #6B7280;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* 상품 보러가기 버튼 */
.btn-view {
    background-color: #F3F4F6;
    color: #374151 !important;
    text-decoration: none !important;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 7px 12px;
    border-radius: 6px;
    border: 1px solid #E5E7EB;
    white-space: nowrap;
    transition: all 0.15s ease;
    flex-shrink: 0;
}
.btn-view:hover {
    background-color: #E5E7EB;
    color: #111827 !important;
}

.empty-msg {
    padding: 30px 18px;
    text-align: center;
    color: #9CA3AF;
    font-size: 0.85rem;
}

/* 하단 푸터 */
.footer-divider {
    margin-top: 4rem;
    border-top: 1px solid #E5E7EB;
    padding-top: 1.5rem;
}
.footer-text {
    font-size: 0.85rem;
    color: #9CA3AF;
}

/* 합산 실구매가 뱃지 */
.prod-total-price {
    font-size: 0.75rem;
    font-weight: 700;
    color: #FFFFFF;
    background: linear-gradient(135deg, #E53E3E, #C53030);
    padding: 2px 6px;
    border-radius: 4px;
    margin-top: 4px;
    display: inline-block;
}

/* ── 카드 외곽: .card-header를 포함하는 column의 stVerticalBlock ── */
div[data-testid="column"]:has(.card-header) > div[data-testid="stVerticalBlock"] {
    background: white !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06) !important;
    border: 1px solid #E5E7EB !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin-bottom: 1.5rem !important;
}

div[data-testid="column"]:has(.card-header) > div[data-testid="stVerticalBlock"] > .element-container {
    padding: 0 !important;
    margin: 0 !important;
}
div[data-testid="column"]:has(.card-header) > div[data-testid="stVerticalBlock"] > .element-container > div {
    margin: 0 !important;
}

/* ── 상품 행: .prod-info-native를 포함하는 stHorizontalBlock ── */
div[data-testid="stHorizontalBlock"]:has(.prod-info-native) {
    background: white !important;
    padding: 8px 10px 8px 8px !important;
    border-bottom: 1px solid #F3F4F6 !important;
    align-items: flex-start !important;
    gap: 6px !important;
    margin: 0 !important;
}

div[data-testid="stHorizontalBlock"]:has(.prod-info-native) .element-container {
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stHorizontalBlock"]:has(.prod-info-native) > div[data-testid="column"] {
    padding: 0 !important;
    min-width: 0 !important;
}

/* 상품 썸네일 */
.native-prod-img {
    width: 58px;
    height: 58px;
    border-radius: 8px;
    object-fit: cover;
    border: 1px solid #E5E7EB;
    display: block;
    margin-top: 4px;
    flex-shrink: 0;
}

/* 상품 정보 래퍼 */
.prod-info-native { padding: 3px 0; min-width: 0; }

/* 상품명 (2줄 말줄임) */
.native-prod-title {
    font-size: 0.80rem;
    font-weight: 600;
    color: #1F2937;
    line-height: 1.35;
    margin-bottom: 3px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* 가격 */
.native-prod-price {
    font-size: 0.90rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 2px;
}

/* 배송비 */
.native-prod-shipping { font-size: 0.68rem; color: #6B7280; }

/* 버튼 컬럼 내 보러가기 링크 */
.native-link-btn {
    display: block !important;
    text-align: center !important;
    background-color: #F3F4F6 !important;
    color: #374151 !important;
    text-decoration: none !important;
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    padding: 5px 3px !important;
    border-radius: 6px !important;
    border: 1px solid #E5E7EB !important;
    margin-bottom: 4px !important;
    transition: background-color 0.15s !important;
}
.native-link-btn:hover { background-color: #E5E7EB !important; }

/* 🛒 담기 버튼 */
div[data-testid="stHorizontalBlock"]:has(.prod-info-native) div[data-testid="stButton"] button {
    height: 28px !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    padding: 0 2px !important;
    box-shadow: none !important;
    background-color: #ECFDF5 !important;
    color: #065F46 !important;
    border: 1px solid #A7F3D0 !important;
    transform: none !important;
}
div[data-testid="stHorizontalBlock"]:has(.prod-info-native) div[data-testid="stButton"] button:hover {
    background-color: #D1FAE5 !important;
    transform: none !important;
}
div[data-testid="stHorizontalBlock"]:has(.prod-info-native) div[data-testid="stButton"] button:disabled {
    background-color: #F9FAFB !important;
    color: #9CA3AF !important;
    border-color: #E5E7EB !important;
    opacity: 1 !important;
}

/* 비교 카드 스타일 */
.compare-card {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E5E7EB;
    padding: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.compare-mall-badge {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 6px;
}
.badge-danawa { background-color: #EBF5FF; color: #1D4ED8; }
.badge-naver { background-color: #ECFDF5; color: #047857; }
.badge-coupang { background-color: #FEF2F2; color: #B91C1C; }
.badge-ali { background-color: #FFF1F0; color: #E62E04; }
.badge-other { background-color: #F3F4F6; color: #374151; }

.compare-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #1F2937;
    margin-bottom: 6px;
    line-height: 1.35;
    height: 2.7em;
    overflow: hidden;
}
.compare-price-best {
    font-size: 1.1rem;
    font-weight: 800;
    color: #DC2626;
}
.compare-price-main {
    font-size: 1.05rem;
    font-weight: 700;
    color: #111827;
}
.compare-shipping {
    font-size: 0.72rem;
    color: #6B7280;
    margin-bottom: 6px;
}
.compare-total {
    font-size: 0.82rem;
    font-weight: 700;
    color: #1E293B;
    background: #F1F5F9;
    padding: 4px 8px;
    border-radius: 6px;
    margin-bottom: 10px;
}
.compare-link {
    display: block;
    text-align: center;
    background: #2563EB;
    color: white !important;
    text-decoration: none !important;
    padding: 6px 0;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 600;
}
.compare-link:hover {
    background: #1D4ED8;
}
</style>""", unsafe_allow_html=True)

# ----------------- 크롤링 로직 -----------------
COMMON_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
}

DEFAULT_IMG = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=120&auto=format&fit=crop&q=80"

async def search_danawa(page, keyword):
    """다나와 상위 5개 상품 수집 (기존 로직 100% 유지)"""
    url = f"https://search.danawa.com/dsearch.php?query={urllib.parse.quote(keyword)}"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=12000)
        items = await page.query_selector_all('li.prod_item:not(.product-pot)')
        results = []
        for item in items[:5]:
            title_el = await item.query_selector('.prod_name a')
            price_el = await item.query_selector('.price_sect strong')
            img_el = await item.query_selector('.thumb_image img')
            
            if title_el and price_el:
                title = await title_el.inner_text()
                price = await price_el.inner_text()
                link = await title_el.get_attribute("href")
                
                img_src = DEFAULT_IMG
                if img_el:
                    src = await img_el.get_attribute("src") or await img_el.get_attribute("data-original")
                    if src:
                        img_src = ("https:" + src) if src.startswith("//") else src

                results.append({
                    "mall": "다나와",
                    "title": title.strip(),
                    "price": price.strip() + "원",
                    "shipping": "🚚 배송 무료/별도",
                    "link": link,
                    "img": img_src
                })
        return results
    except Exception:
        return []

def search_naver_sync(keyword):
    """
    모바일 네이버 쇼핑 검색 (requests + BeautifulSoup 방식):
    - 봇 탐지 없는 모바일 네이버 쇼핑 URL 사용
    - 모바일 스마트폰 User-Agent 헤더 적용
    - 상위 5개 본품 상품명, 가격, 썸네일, 링크 정확 파싱 (기존 로직 100% 유지)
    """
    url = f"https://m.search.naver.com/search.naver?where=m_shopping&query={urllib.parse.quote(keyword)}"
    mobile_headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://m.naver.com/"
    }

    try:
        res = requests.get(url, headers=mobile_headers, timeout=10)
        if res.status_code != 200:
            return []

        soup = BeautifulSoup(res.text, "html.parser")
        shop_links = soup.find_all("a", href=re.compile(r"shopping\.naver\.com/v2/bridge|cr3\.shopping\.naver\.com|cr\.shopping\.naver\.com"))
        
        results = []
        seen_mids = set()
        seen_titles = set()

        for a in shop_links:
            href = a.get("href", "")
            if not href:
                continue

            mid_match = re.search(r'nv_mid=(\d+)', href)
            mid = mid_match.group(1) if mid_match else href
            if mid in seen_mids:
                continue

            parent = a.find_parent("li") or a.find_parent("div")
            if not parent:
                continue

            p_text = parent.get_text(separator=" | ", strip=True)
            lines = [l.strip() for l in p_text.split("|") if l.strip()]

            price = ""
            for i, line in enumerate(lines):
                if "배송" in line:
                    continue
                if i > 0 and "배송" in lines[i-1]:
                    continue
                if "최저" in line:
                    m = re.search(r'(\d{1,3}(?:,\d{3})+)', line)
                    if m:
                        price = f"최저 {m.group(1)}원"
                        break
                    if i + 1 < len(lines):
                        m2 = re.search(r'(\d{1,3}(?:,\d{3})+)', lines[i+1])
                        if m2:
                            price = f"최저 {m2.group(1)}원"
                            break
                m_won = re.search(r'(\d{1,3}(?:,\d{3})+)\s*원', line)
                if m_won and "배송" not in line and "적립" not in line:
                    price = f"{m_won.group(1)}원"
                    break
                m_only_num = re.match(r'^(\d{1,3}(?:,\d{3})+)$', line)
                if m_only_num and i + 1 < len(lines) and "원" in lines[i+1]:
                    price = f"{m_only_num.group(1)}원"
                    break

            if not price:
                continue

            title = a.get_text(strip=True)
            if not title or len(title) < 4 or title in ["전체 상품 보기", "법적고지 및 안내", "쿠팡", "11번가", "G마켓"]:
                for l in lines:
                    if len(l) >= 5 and not any(skip in l for skip in ["최저", "원", "배송비", "무료", "할인", "등록일", "리뷰", "평점"]):
                        title = l
                        break

            if not title or len(title) < 4:
                continue

            clean_title = re.sub(r'\s+', '', title)
            if clean_title in seen_titles:
                continue

            img_tag = parent.find("img")
            img_src = DEFAULT_IMG
            if img_tag and img_tag.get("src"):
                src = img_tag.get("src")
                if src.startswith("http"):
                    img_src = src

            shipping = "🚚 배송 무료" if "무료" in p_text else "🚚 배송 3,000원"

            seen_mids.add(mid)
            seen_titles.add(clean_title)

            results.append({
                "mall": "네이버 쇼핑",
                "title": title.strip(),
                "price": price.strip(),
                "shipping": shipping,
                "link": href.strip(),
                "img": img_src
            })

            if len(results) >= 5:
                break

        return results
    except Exception:
        return []

async def search_naver(page, keyword):
    """search_naver를 비동기 이벤트 루프 내에서 requests_sync로 안전하게 호출"""
    return await asyncio.to_thread(search_naver_sync, keyword)

async def search_coupang(page, keyword):
    """폴센트(Fallcent) 연동 쿠팡 최저가 상위 5개 수집 (기존 로직 100% 유지)"""
    encoded = urllib.parse.quote(keyword)
    url = f"https://fallcent.com/product/search/?keyword={encoded}"
    
    try:
        headers = dict(COMMON_HEADERS)
        headers["Referer"] = "https://fallcent.com/"
        await page.set_extra_http_headers(headers)
        
        await page.goto(url, wait_until="domcontentloaded", timeout=12000)
        
        try:
            await page.wait_for_selector('a[href*="fcnt.link"]', timeout=5000)
        except Exception:
            await page.wait_for_timeout(2000)
            
        links = await page.query_selector_all('a[href*="fcnt.link"]')
        results = []
        
        for a in links:
            href = await a.get_attribute('href')
            text = await a.inner_text()
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            
            if not lines:
                continue
                
            price = ""
            for l in reversed(lines):
                if "원" in l and any(ch.isdigit() for ch in l):
                    price = l
                    break
            
            ignore_keywords = ["로켓", "배송", "원", "할인", "품절", "%"]
            title_candidates = [l for l in lines if not any(k in l for k in ignore_keywords)]
            title = title_candidates[0] if title_candidates else lines[0]
            
            img_el = await a.query_selector('img')
            img_src = DEFAULT_IMG
            if img_el:
                src = await img_el.get_attribute("src")
                if src and src.startswith("http"):
                    img_src = src

            shipping = "🚚 로켓배송" if "로켓" in text else "🚚 배송 무료/별도"

            if title and price and href:
                results.append({
                    "mall": "쿠팡",
                    "title": title.strip(),
                    "price": price.strip(),
                    "shipping": shipping,
                    "link": href.strip(),
                    "img": img_src
                })
                
            if len(results) >= 5:
                break
                
        return results
    except Exception:
        return []

def search_aliexpress_sync(keyword):
    """
    알리익스프레스(AliExpress) 한국어 검색 결과 스크래핑:
    - URL: https://ko.aliexpress.com/w/wholesale-{keyword}.html
    - 봇 차단 없는 안정적인 헤더 및 requests 요청
    - 상품명, 한화(원) 가격, 썸네일, 링크 상위 5개 추출
    """
    encoded = urllib.parse.quote(keyword)
    url = f"https://ko.aliexpress.com/w/wholesale-{encoded}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return []

        soup = BeautifulSoup(res.text, "html.parser")
        item_links = soup.find_all("a", href=re.compile(r"/item/\d+\.html"))
        
        results = []
        seen_ids = set()
        seen_titles = set()
        
        for a in item_links:
            href = a.get("href", "")
            if not href:
                continue
                
            m_id = re.search(r'/item/(\d+)\.html', href)
            item_id = m_id.group(1) if m_id else href
            if item_id in seen_ids:
                continue
                
            full_link = ("https:" + href) if href.startswith("//") else href
            text = a.get_text(separator=" ", strip=True)
            
            # 1. 썸네일 이미지 추출
            img_tag = a.find("img")
            if not img_tag and a.parent:
                img_tag = a.parent.find("img")
            img_src = DEFAULT_IMG
            if img_tag:
                src = img_tag.get("src") or img_tag.get("data-src") or ""
                if src:
                    img_src = ("https:" + src) if src.startswith("//") else src
                    
            # 2. 가격 파싱 (한화 ₩ 기준: 공백/콤마 정규화)
            price_match = re.search(r'₩\s*(\d{1,3}(?:\s*,\s*\d{3})*)', text)
            price_str = ""
            if price_match:
                clean_num = re.sub(r'[\s,]', '', price_match.group(1))
                if clean_num.isdigit():
                    price_str = f"{int(clean_num):,}원"
            
            if not price_str:
                continue
                
            # 3. 상품명 파싱
            title_part = text[:price_match.start()].strip()
            title_part = re.sub(r'-\d+%', '', title_part).strip()
            title = title_part if len(title_part) >= 4 else text[:50]
            
            clean_title = re.sub(r'\s+', '', title)
            if clean_title in seen_titles:
                continue

            # 4. 배송 정보
            shipping = "🚚 배송 무료" if ("무료 배송" in text or "무료" in text) else "🚚 배송비 별도"
            
            seen_ids.add(item_id)
            seen_titles.add(clean_title)
            
            results.append({
                "mall": "알리익스프레스",
                "title": title.strip(),
                "price": price_str.strip(),
                "shipping": shipping,
                "link": full_link.strip(),
                "img": img_src
            })
            if len(results) >= 5:
                break
                
        return results
    except Exception:
        return []

async def search_aliexpress(page, keyword):
    """search_aliexpress를 비동기 이벤트 루프 내에서 requests_sync로 안전하게 호출"""
    return await asyncio.to_thread(search_aliexpress_sync, keyword)

async def crawl_all(keyword):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        await stealth_async(page)
        
        # 다나와, 네이버 쇼핑, 쿠팡(폴센트), 알리익스프레스 병렬/순차 수집
        danawa_res = await search_danawa(page, keyword)
        naver_res = await search_naver(page, keyword)
        coupang_res = await search_coupang(page, keyword)
        ali_res = await search_aliexpress(page, keyword)
        
        await browser.close()
        return {
            "다나와": danawa_res,
            "네이버": naver_res,
            "쿠팡": coupang_res,
            "알리익스프레스": ali_res
        }

def _run_crawler_sync(keyword):
    """실제 크롤링 실행 (캐시 없음 - 내부 전용)"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(crawl_all(keyword))
    finally:
        loop.close()

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_results(keyword: str) -> dict:
    """캐싱 래퍼: 동일 검색어는 1시간 동안 메모리에서 즉시 반환."""
    return _run_crawler_sync(keyword)

# ----------------- 가격 파싱 유틸 -----------------

def parse_price_int(price_text: str) -> int:
    """가격 텍스트에서 숫자만 추출하여 정수로 반환. 파싱 실패 시 0 반환."""
    if not price_text:
        return 0
    nums = re.findall(r'\d[\d,]*', price_text.replace(',', ''))
    if nums:
        return int(nums[0])
    return 0

def parse_shipping_int(shipping_text: str) -> int:
    """배송비 텍스트에서 숫자 추출. 무료/로켓배송 등은 0원 반환."""
    if not shipping_text:
        return 0
    if any(kw in shipping_text for kw in ["무료", "로켓배송", "무료배송"]):
        return 0
    nums = re.findall(r'\d[\d,]*', shipping_text.replace(',', ''))
    if nums:
        return int(nums[0])
    return 0

def calc_total_price(item: dict) -> int:
    """상품 dict에서 가격 + 배송비 합산 실구매가 계산."""
    return parse_price_int(item.get("price", "")) + parse_shipping_int(item.get("shipping", ""))

def format_price(n: int) -> str:
    """정수를 '123,456원' 형식으로 포맷."""
    return f"{n:,}원"

# ----------------- 장바구니 Session State 초기화 -----------------

if "cart" not in st.session_state:
    st.session_state["cart"] = []
if "compare_items" not in st.session_state:
    st.session_state["compare_items"] = []

# ----------------- 사이드바: 장바구니 -----------------

with st.sidebar:
    cart = st.session_state["cart"]
    cart_count = len(cart)

    st.markdown(
        f"### 🛒 내 장바구니 "
        f"<span style='background:#1F2937;color:#fff;font-size:0.75rem;"
        f"padding:1px 8px;border-radius:10px;'>{cart_count}</span>",
        unsafe_allow_html=True
    )
    st.divider()

    if cart_count == 0:
        st.caption("아직 담긴 상품이 없습니다.\n검색 후 상품을 담아보세요!")
    else:
        if st.button("🗑️ 전체 비우기", use_container_width=True):
            st.session_state["cart"] = []
            st.session_state["compare_items"] = []
            st.rerun()

        selected_indices = []

        for idx, item in enumerate(cart):
            mall_label = item.get("mall", "?")
            title_short = item["title"][:28] + "…" if len(item["title"]) > 28 else item["title"]

            cb_col, info_col, del_col = st.columns([0.5, 6, 1])
            with cb_col:
                checked = st.checkbox("선택", key=f"cart_cb_{idx}", label_visibility="collapsed")
                if checked:
                    selected_indices.append(idx)
            with info_col:
                st.markdown(
                    f"<div style='font-size:0.75rem;font-weight:700;color:#374151;'>"
                    f"[{mall_label}] {title_short}</div>"
                    f"<div style='font-size:0.8rem;font-weight:700;color:#111827;'>{item['price']}</div>"
                    f"<div style='font-size:0.7rem;color:#9CA3AF;'>{item.get('shipping','')}</div>",
                    unsafe_allow_html=True
                )
            with del_col:
                if st.button("❌", key=f"del_{idx}", help="삭제"):
                    st.session_state["cart"].pop(idx)
                    st.rerun()

            st.markdown("<hr style='margin:4px 0;border-color:#F3F4F6;'>", unsafe_allow_html=True)

        st.write("")

        if st.button("☑️ 선택한 상품 비교하기", use_container_width=True, type="primary"):
            if len(selected_indices) < 2:
                st.warning("비교하려면 상품을 2개 이상 선택하세요.")
            else:
                st.session_state["compare_items"] = [cart[i] for i in selected_indices]
                st.rerun()

# ----------------- UI 렌더링 -----------------

# 1. 상단 타이틀 & 설명
st.markdown("""<div class="header-box">
<div class="main-logo-title">얼마</div>
<div class="main-desc">다나와 · 네이버 쇼핑 · 쿠팡몰 · 알리익스프레스의 최신 가격 정보를 한번에 검색하고 비교하세요.</div>
</div>""", unsafe_allow_html=True)

# 2. 검색창 & 버튼
with st.form(key="search_form", clear_on_submit=False):
    search_col1, search_col2, search_col3 = st.columns([1.5, 7, 2])
    with search_col2:
        keyword = st.text_input(
            "검색어",
            placeholder="검색할 상품명을 입력하세요 (예: 에어팟 프로 2, 비레디 블루쿠션 4호, 아이폰 16)",
            label_visibility="collapsed"
        )
    with search_col3:
        search_submitted = st.form_submit_button("최저가 비교하기", use_container_width=True)

# 3. 배송비 포함 토글 + 새로고침 버튼
toggle_col1, toggle_col2, toggle_col3, toggle_col4 = st.columns([1.5, 6, 2, 1])
with toggle_col2:
    sort_by_total = st.toggle("🚚 배송비 포함 실구매가로 정렬", value=False)
with toggle_col3:
    refresh_clicked = st.button("🔄 최신 데이터로 새로고침", use_container_width=True)

st.write("")

# 새로고침 버튼 클릭 시 캐시 초기화
if refresh_clicked:
    fetch_results.clear()
    if "last_keyword" in st.session_state:
        st.session_state["force_refresh"] = True
    st.rerun()

# 검색 제출 시 크롤링 실행
if search_submitted and keyword.strip():
    kw = keyword.strip()
    cached = (
        st.session_state.get("last_keyword") == kw
        and "search_results" in st.session_state
        and not st.session_state.pop("force_refresh", False)
    )
    if cached:
        results_data = fetch_results(kw)
        st.session_state["search_results"] = results_data
        st.session_state["last_keyword"] = kw
    else:
        with st.spinner(f"'{kw}' 상품을 다나와, 네이버 쇼핑, 쿠팡, 알리익스프레스에서 검색 중입니다..."):
            results_data = fetch_results(kw)
            st.session_state["search_results"] = results_data
            st.session_state["last_keyword"] = kw

if st.session_state.pop("force_refresh", False) and "last_keyword" in st.session_state:
    kw = st.session_state["last_keyword"]
    with st.spinner(f"'{kw}' 최신 데이터를 가져오는 중입니다..."):
        results_data = fetch_results(kw)
        st.session_state["search_results"] = results_data

# 5개 샘플 데이터 정의 (미리보기 화면용)
SAMPLE_DANAWA = [
    {"title": "APPLE 에어팟 프로 2세대 USB-C MTJV3KH/A", "price": "316,690원", "shipping": "🚚 배송 무료", "link": "https://danawa.com", "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=120&auto=format&fit=crop&q=80"},
    {"title": "APPLE 에어팟 프로 2세대 라이트닝 MQD83KH/A", "price": "318,190원", "shipping": "🚚 배송 무료", "link": "https://danawa.com", "img": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=120&auto=format&fit=crop&q=80"},
    {"title": "APPLE 에어팟 맥스 USB-C", "price": "545,190원", "shipping": "🚚 배송 무료", "link": "https://danawa.com", "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=120&auto=format&fit=crop&q=80"},
    {"title": "APPLE 에어팟 4세대 ANC 액티브 노이즈 캔슬링", "price": "219,000원", "shipping": "🚚 배송 2,500원", "link": "https://danawa.com", "img": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=120&auto=format&fit=crop&q=80"},
    {"title": "APPLE 에어팟 4세대 일반 모델", "price": "179,000원", "shipping": "🚚 배송 무료", "link": "https://danawa.com", "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=120&auto=format&fit=crop&q=80"}
]
SAMPLE_NAVER = [
    {"title": "Apple 에어팟 프로 2세대 C타입 MTJV3KH/A", "price": "최저 204,700원", "shipping": "🚚 배송 무료", "link": "https://shopping.naver.com", "img": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=120&auto=format&fit=crop&q=80"},
    {"title": "에어팟 프로 2세대 MQD83KH/A C타입 카탈로그", "price": "최저 399,000원", "shipping": "🚚 배송 3,000원", "link": "https://shopping.naver.com", "img": "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=120&auto=format&fit=crop&q=80"},
    {"title": "에어팟 프로 3세대 MFHP4KH/A USB-C 노이즈캔슬링", "price": "최저 290,000원", "shipping": "🚚 배송 무료", "link": "https://shopping.naver.com", "img": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=120&auto=format&fit=crop&q=80"},
    {"title": "에어팟 4세대 ANC MXP93KH/A 액티브 노이즈 캔슬링", "price": "최저 180,000원", "shipping": "🚚 배송 무료", "link": "https://shopping.naver.com", "img": "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=120&auto=format&fit=crop&q=80"},
    {"title": "에어팟 2세대 유선충전 모델 MV7N2KH/A", "price": "최저 299,000원", "shipping": "🚚 배송 무료", "link": "https://shopping.naver.com", "img": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=120&auto=format&fit=crop&q=80"}
]
SAMPLE_COUPANG = [
    {"title": "Apple 정품 에어팟 프로 2세대 USB-C 타입", "price": "312,000원", "shipping": "🚚 로켓배송", "link": "https://coupang.com", "img": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=120&auto=format&fit=crop&q=80"},
    {"title": "Apple 정품 에어팟 맥스 헤드폰 실버", "price": "670,000원", "shipping": "🚚 로켓배송", "link": "https://coupang.com", "img": DEFAULT_IMG},
    {"title": "Apple 에어팟 4세대 무선 이어폰 일반형", "price": "189,000원", "shipping": "🚚 로켓배송", "link": "https://coupang.com", "img": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=120&auto=format&fit=crop&q=80"},
    {"title": "Apple 에어팟 4세대 ANC 노이즈 캔슬링 모델", "price": "245,000원", "shipping": "🚚 로켓배송", "link": "https://coupang.com", "img": DEFAULT_IMG},
    {"title": "Apple 정품 에어팟 3세대 MagSafe 충전 케이스", "price": "239,000원", "shipping": "🚚 로켓배송", "link": "https://coupang.com", "img": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=120&auto=format&fit=crop&q=80"}
]
SAMPLE_ALIEXPRESS = [
    {"title": "프로 2 3 4 무선 블루투스 이어버드 액티브 노이즈 캔슬링", "price": "31,900원", "shipping": "🚚 배송 무료", "link": "https://ko.aliexpress.com", "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=120&auto=format&fit=crop&q=80"},
    {"title": "진정한 무선 블루투스 이어폰 HiFi 사운드 저지연 소음 감소", "price": "7,757원", "shipping": "🚚 배송 무료", "link": "https://ko.aliexpress.com", "img": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=120&auto=format&fit=crop&q=80"},
    {"title": "TWS 블루투스 헤드셋 HiFi 무선 헤드폰 마이크 소음 감소", "price": "14,500원", "shipping": "🚚 배송 무료", "link": "https://ko.aliexpress.com", "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=120&auto=format&fit=crop&q=80"},
    {"title": "Airs Pro TWS 무선 블루투스 이어버드 팝업 터치 컨트롤", "price": "16,600원", "shipping": "🚚 배송 무료", "link": "https://ko.aliexpress.com", "img": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=120&auto=format&fit=crop&q=80"},
    {"title": "TWS 무선 블루투스 헤드셋 LED 디스플레이 마이크 포함", "price": "11,500원", "shipping": "🚚 배송 무료", "link": "https://ko.aliexpress.com", "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=120&auto=format&fit=crop&q=80"}
]

# 데이터 소스 결정 (실제 검색 결과 vs 초기 샘플 5개)
if "search_results" in st.session_state and st.session_state["search_results"]:
    data = st.session_state["search_results"]
    if isinstance(data, dict):
        danawa_items = data.get("다나와", [])
        naver_items = data.get("네이버", [])
        coupang_items = data.get("쿠팡", [])
        ali_items = data.get("알리익스프레스", [])
    else:
        danawa_items, naver_items, coupang_items, ali_items = [], [], [], []
else:
    danawa_items = SAMPLE_DANAWA
    naver_items = SAMPLE_NAVER
    coupang_items = SAMPLE_COUPANG
    ali_items = SAMPLE_ALIEXPRESS

# 각 아이템 리스트가 list of dict 형태인지 검증 및 정제
danawa_items  = [it for it in danawa_items if isinstance(it, dict)] if isinstance(danawa_items, list) else []
naver_items   = [it for it in naver_items if isinstance(it, dict)] if isinstance(naver_items, list) else []
coupang_items = [it for it in coupang_items if isinstance(it, dict)] if isinstance(coupang_items, list) else []
ali_items     = [it for it in ali_items if isinstance(it, dict)] if isinstance(ali_items, list) else []

# 토글 ON 시 합산 실구매가 기준 오름차순 정렬
if sort_by_total:
    danawa_items  = sorted(danawa_items,  key=calc_total_price)
    naver_items   = sorted(naver_items,   key=calc_total_price)
    coupang_items = sorted(coupang_items, key=calc_total_price)
    ali_items     = sorted(ali_items,     key=calc_total_price)

# ── 쇼핑몰 섹션 렌더러 (완전 네이티브 레이아웃) ─────────────
def render_mall_section(col, header_class, logo_html, items, mall_name, show_total):
    """
    각 쇼핑몰 컬럼을 st.columns()로 렌더링.
    상품 이미지 · 정보 · 장바구니 버튼이 하나의 행(row)에 나란히 배치됨.
    CSS :has() 선택자로 외곽 카드 박스와 행 스타일을 자동 적용.
    """
    with col:
        # ① 컬러 헤더
        st.markdown(
            f'<div class="card-header {header_class}">'
            f'<div class="header-left">{logo_html}</div>'
            f'<span class="arrow-icon">›</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        if not items or not isinstance(items, list):
            st.markdown(
                '<div style="padding:30px 18px;text-align:center;'
                'color:#9CA3AF;font-size:0.85rem;">검색된 상품이 없습니다.</div>',
                unsafe_allow_html=True
            )
            return

        valid_items = [it for it in items if isinstance(it, dict)]
        if not valid_items:
            st.markdown(
                '<div style="padding:30px 18px;text-align:center;'
                'color:#9CA3AF;font-size:0.85rem;">검색된 상품이 없습니다.</div>',
                unsafe_allow_html=True
            )
            return

        for idx, item in enumerate(valid_items[:5]):
            # 4열 레이아웃에 맞춰 열 비율 조정: 이미지(1.2) | 정보(4.5) | 버튼(1.5)
            c_img, c_info, c_btn = st.columns([1.2, 4.5, 1.5], gap="small")

            # 이미지 열
            with c_img:
                img_src = item.get('img', DEFAULT_IMG)
                st.markdown(
                    f'<img src="{img_src}" class="native-prod-img" '
                    f'onerror="this.src=\'{DEFAULT_IMG}\'" alt="상품이미지" />',
                    unsafe_allow_html=True
                )

            # 정보 열
            with c_info:
                title = (item['title']
                         .replace('&', '&amp;').replace('<', '&lt;')
                         .replace('>', '&gt;').replace('"', '&quot;'))
                price = item['price']
                ship  = item.get('shipping', '🚚 배송 무료/별도')

                total_html = ''
                if show_total:
                    t = calc_total_price(item)
                    total_html = (
                        f'<div style="margin-top:3px;">'
                        f'<span class="prod-total-price">실구매가: {format_price(t)}</span>'
                        f'</div>'
                    )

                st.markdown(
                    f'<div class="prod-info-native">'
                    f'  <div class="native-prod-title" title="{title}">{title}</div>'
                    f'  <div class="native-prod-price">{price}</div>'
                    f'  <div class="native-prod-shipping">{ship}</div>'
                    f'  {total_html}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # 버튼 열 — 보러가기 링크 + 🛒 담기 버튼
            with c_btn:
                link = item.get('link', '#')
                already_in = any(
                    c['title'] == item['title'] and c.get('mall') == item.get('mall')
                    for c in st.session_state["cart"]
                )

                # 보러가기 (HTML <a>)
                st.markdown(
                    f'<a href="{link}" target="_blank" class="btn-view native-link-btn">'
                    f'보러가기</a>',
                    unsafe_allow_html=True
                )

                # 🛒 담기 버튼
                btn_key = f'cart_{mall_name}_{idx}'
                if already_in:
                    st.button(
                        '✅ 담김',
                        key=btn_key,
                        disabled=True,
                        use_container_width=True,
                    )
                else:
                    if st.button(
                        '🛒 담기',
                        key=btn_key,
                        use_container_width=True,
                    ):
                        st.session_state['cart'].append({
                            'mall':     item.get('mall', mall_name),
                            'title':    item['title'],
                            'price':    item['price'],
                            'shipping': item.get('shipping', ''),
                            'link':     item.get('link', ''),
                            'img':      item.get('img', DEFAULT_IMG),
                        })
                        st.toast(
                            f'장바구니에 담겼습니다!\n{item["title"][:25]}',
                            icon='✅'
                        )
                        st.rerun()

# ── 4대 쇼핑몰 컬럼 배치 (st.columns(4)) ────────────────────────────
col_danawa, col_naver, col_coupang, col_ali = st.columns(4)

danawa_logo  = '<span style="font-weight:800;color:#FF4B4B;">d</span><span style="font-weight:800;">anawa</span>'
naver_logo   = '<span style="background:white;color:#03C75A;font-weight:900;font-size:0.8rem;padding:1px 5px;border-radius:2px;">N</span><span>네이버 쇼핑</span>'
coupang_logo = '<span>coupang</span>'
ali_logo     = '<span style="font-weight:800;color:#FFFFFF;">Ali</span><span style="font-weight:800;color:#FFF700;">Express</span>'

render_mall_section(col_danawa,  "header-danawa",     danawa_logo,  danawa_items,  "danawa",      sort_by_total)
render_mall_section(col_naver,   "header-naver",      naver_logo,   naver_items,   "naver",       sort_by_total)
render_mall_section(col_coupang, "header-coupang",    coupang_logo, coupang_items, "coupang",     sort_by_total)
render_mall_section(col_ali,     "header-aliexpress", ali_logo,     ali_items,     "aliexpress",  sort_by_total)

# ── 비교 뷰 ───────────────────────────────────────────────
compare_items = st.session_state.get("compare_items", [])
if compare_items:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        f"### ☑️ 선택 상품 비교 · {len(compare_items)}개",
    )

    totals = [calc_total_price(it) for it in compare_items]
    min_total = min(totals) if totals else 0

    compare_cols = st.columns(len(compare_items))
    for col, item, total in zip(compare_cols, compare_items, totals):
        mall = item.get("mall", "")
        badge_cls = (
            "badge-danawa"  if "다나와" in mall else
            "badge-naver"   if "네이버" in mall else
            "badge-coupang" if "쿠팡"  in mall else
            "badge-ali"     if "알리"  in mall else
            "badge-other"
        )
        price_cls = "compare-price-best" if total == min_total else "compare-price-main"
        crown = " 👑 최저가" if total == min_total else ""

        with col:
            st.markdown(
                f'<div class="compare-card">'
                f'<span class="compare-mall-badge {badge_cls}">{mall}</span>'
                f'<div class="compare-title">{item["title"]}</div>'
                f'<div class="{price_cls}">{item["price"]}</div>'
                f'<div class="compare-shipping">{item.get("shipping","")}</div>'
                f'<div class="compare-total">합산 실구매가: {format_price(total)}{crown}</div>'
                f'<a href="{item.get("link","#")}" target="_blank" class="compare-link">상품 보러가기 →</a>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.write("")
    if st.button("✖ 비교 닫기", key="close_compare"):
        st.session_state["compare_items"] = []
        st.rerun()

# ── 하단 푸터 ─────────────────────────────────────────────
st.markdown("""<div class="footer-divider"><span class="footer-text">다나와 &nbsp;&nbsp; 네이버 쇼핑 &nbsp;&nbsp; 쿠팡 &nbsp;&nbsp; 알리익스프레스</span></div>""", unsafe_allow_html=True)
