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

# ----------------- 토스 / 당근마켓 감성 모던 앱 스타일 CSS -----------------
st.markdown("""<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

/* 1. 기본 Streamlit UI 숨기기 (모바일 앱 느낌 극대화) */
#MainMenu { visibility: hidden !important; display: none !important; }
header { visibility: hidden !important; display: none !important; }
footer { visibility: hidden !important; display: none !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
.viewerBadge_container__1QSob, .viewerBadge_link__1S137 { display: none !important; }

/* 2. 글로벌 폰트 및 부드러운 앱 배경색 */
*, html, body, [class*="css"], [class*="st-"] {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    box-sizing: border-box;
}

.stApp {
    background-color: #F2F4F6 !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1400px;
}

/* 사이드바 스타일링 */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E5E8EB !important;
}

/* 3. 상단 헤더 타이틀 */
.header-box {
    text-align: center;
    margin-bottom: 2.2rem;
}
.main-logo-title {
    font-size: 3.2rem;
    font-weight: 900;
    color: #191F28;
    letter-spacing: -0.04em;
    margin-bottom: 0.6rem;
}
.main-desc {
    font-size: 1.1rem;
    color: #4E5968;
    font-weight: 500;
    letter-spacing: -0.02em;
}

/* 4. 검색창 & 버튼 스타일 (토스 스타일) */
div[data-testid="stTextInput"] {
    flex: 1;
    margin-bottom: 0px !important;
}
div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    border: 1.5px solid #E5E8EB !important;
    height: 52px !important;
    padding: 0 20px !important;
    font-size: 1rem !important;
    background-color: #FFFFFF !important;
    color: #191F28 !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #3182F6 !important;
    box-shadow: 0 0 0 3px rgba(49, 130, 246, 0.12) !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #8B95A1 !important;
    font-weight: 400;
}

div[data-testid="stForm"] div[data-testid="stButton"] button {
    height: 52px !important;
    background-color: #3182F6 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    padding: 0 26px !important;
    box-shadow: 0 4px 14px rgba(49, 130, 246, 0.25) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    white-space: nowrap !important;
    letter-spacing: -0.02em !important;
}
div[data-testid="stForm"] div[data-testid="stButton"] button:hover {
    background-color: #1B64DA !important;
    box-shadow: 0 6px 20px rgba(49, 130, 246, 0.35) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stForm"] div[data-testid="stButton"] button:active {
    transform: scale(0.98) !important;
}

/* 일반 버튼 라운딩 */
div[data-testid="stButton"] button {
    border-radius: 10px !important;
    font-weight: 600 !important;
}

/* 5. 상품 카드 디자인 (둥둥 떠 있는 플로팅 카드) */
div[data-testid="column"]:has(.card-header) > div[data-testid="stVerticalBlock"] {
    background: #FFFFFF !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
    border: none !important;
    overflow: hidden !important;
    padding: 0 0 8px 0 !important;
    margin-bottom: 1.5rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="column"]:has(.card-header) > div[data-testid="stVerticalBlock"]:hover {
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08) !important;
}

div[data-testid="column"]:has(.card-header) > div[data-testid="stVerticalBlock"] > .element-container {
    padding: 0 !important;
    margin: 0 !important;
}
div[data-testid="column"]:has(.card-header) > div[data-testid="stVerticalBlock"] > .element-container > div {
    margin: 0 !important;
}

/* 카드 상단 배너 헤더 */
.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 18px;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 1.05rem;
    letter-spacing: -0.02em;
}
.header-danawa { background: linear-gradient(135deg, #1E3A8A, #2563EB); }
.header-naver { background: linear-gradient(135deg, #03C75A, #00A84D); }
.header-coupang { background: linear-gradient(135deg, #EA580C, #F97316); }
.header-aliexpress { background: linear-gradient(135deg, #E11D48, #F43F5E); }

.header-left {
    display: flex;
    align-items: center;
    gap: 8px;
}
.arrow-icon {
    font-size: 1.2rem;
    opacity: 0.8;
}

/* 카드 내부 상품 행(Row) */
div[data-testid="stHorizontalBlock"]:has(.prod-info-native) {
    background: #FFFFFF !important;
    padding: 12px 14px !important;
    border-bottom: 1px solid #F2F4F6 !important;
    align-items: center !important;
    gap: 10px !important;
    margin: 0 !important;
    transition: background-color 0.15s ease !important;
}
div[data-testid="stHorizontalBlock"]:has(.prod-info-native):hover {
    background-color: #F8FAFC !important;
}
div[data-testid="stHorizontalBlock"]:has(.prod-info-native):last-child {
    border-bottom: none !important;
}

div[data-testid="stHorizontalBlock"]:has(.prod-info-native) .element-container {
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stHorizontalBlock"]:has(.prod-info-native) > div[data-testid="column"] {
    padding: 0 !important;
    min-width: 0 !important;
}

/* 상품 썸네일 이미지 */
.native-prod-img {
    width: 64px !important;
    height: 64px !important;
    border-radius: 12px !important;
    object-fit: cover !important;
    border: 1px solid #F2F4F6 !important;
    background-color: #F8FAFC !important;
    display: block !important;
    flex-shrink: 0 !important;
    transition: transform 0.15s ease !important;
}
.native-prod-img:hover {
    transform: scale(1.04) !important;
}

/* 상품 정보 */
.prod-info-native {
    padding: 2px 0;
    min-width: 0;
}
.native-prod-title {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #191F28 !important;
    line-height: 1.38 !important;
    margin-bottom: 4px !important;
    display: -webkit-box !important;
    -webkit-line-clamp: 2 !important;
    -webkit-box-orient: vertical !important;
    overflow: hidden !important;
    letter-spacing: -0.02em !important;
}
.native-prod-price {
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    color: #191F28 !important;
    margin-bottom: 2px !important;
    letter-spacing: -0.02em !important;
}
.native-prod-shipping {
    font-size: 0.70rem !important;
    color: #8B95A1 !important;
    font-weight: 500 !important;
}
.prod-total-price {
    font-size: 0.70rem !important;
    font-weight: 700 !important;
    color: #3182F6 !important;
    background: #E8F3FF !important;
    padding: 3px 8px !important;
    border-radius: 6px !important;
    margin-top: 4px !important;
    display: inline-block !important;
}

/* 보러가기 링크 버튼 */
.native-link-btn {
    display: block !important;
    text-align: center !important;
    background-color: #F2F4F6 !important;
    color: #4E5968 !important;
    text-decoration: none !important;
    font-size: 0.70rem !important;
    font-weight: 600 !important;
    padding: 7px 4px !important;
    border-radius: 10px !important;
    border: none !important;
    margin-bottom: 6px !important;
    transition: all 0.15s ease !important;
}
.native-link-btn:hover {
    background-color: #E5E8EB !important;
    color: #191F28 !important;
}

/* 🛒 담기 버튼 */
div[data-testid="stHorizontalBlock"]:has(.prod-info-native) div[data-testid="stButton"] button {
    height: 32px !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    padding: 0 4px !important;
    box-shadow: none !important;
    background-color: #E8F3FF !important;
    color: #1B64DA !important;
    border: none !important;
    border-radius: 10px !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stHorizontalBlock"]:has(.prod-info-native) div[data-testid="stButton"] button:hover {
    background-color: #D2E7FF !important;
    color: #0E4DB7 !important;
    transform: none !important;
}
div[data-testid="stHorizontalBlock"]:has(.prod-info-native) div[data-testid="stButton"] button:disabled {
    background-color: #F2F4F6 !important;
    color: #B0B8C1 !important;
    border: none !important;
    opacity: 1 !important;
}

/* 비교 카드 및 토글 영역 */
.compare-card {
    background: #FFFFFF !important;
    border-radius: 16px !important;
    border: none !important;
    padding: 18px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
}
.compare-mall-badge {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 8px;
}
.badge-danawa { background-color: #EBF5FF; color: #1D4ED8; }
.badge-naver { background-color: #ECFDF5; color: #047857; }
.badge-coupang { background-color: #FFF7ED; color: #EA580C; }
.badge-ali { background-color: #FFF1F2; color: #E11D48; }
.badge-other { background-color: #F2F4F6; color: #4E5968; }

.compare-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #191F28;
    margin-bottom: 8px;
    line-height: 1.4;
    height: 2.8em;
    overflow: hidden;
}
.compare-price-best {
    font-size: 1.15rem;
    font-weight: 800;
    color: #E11D48;
}
.compare-price-main {
    font-size: 1.08rem;
    font-weight: 700;
    color: #191F28;
}
.compare-shipping {
    font-size: 0.72rem;
    color: #8B95A1;
    margin-bottom: 8px;
}
.compare-total {
    font-size: 0.82rem;
    font-weight: 700;
    color: #191F28;
    background: #F2F4F6;
    padding: 6px 10px;
    border-radius: 8px;
    margin-bottom: 12px;
}
.compare-link {
    display: block;
    text-align: center;
    background: #3182F6;
    color: white !important;
    text-decoration: none !important;
    padding: 8px 0;
    border-radius: 10px;
    font-size: 0.82rem;
    font-weight: 600;
    transition: background-color 0.15s ease;
}
.compare-link:hover {
    background: #1B64DA;
}

/* 하단 푸터 */
.footer-divider {
    margin-top: 4rem;
    border-top: 1px solid #E5E8EB;
    padding-top: 1.5rem;
    text-align: center;
}
.footer-text {
    font-size: 0.85rem;
    color: #8B95A1;
    font-weight: 500;
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

# ----------------- 광고 필터링 및 키워드 검증(검문소) 유틸 -----------------

def extract_keyword_tokens(keyword: str) -> list:
    """검색어에서 의미 있는 핵심 토큰 목록을 추출 (띄어쓰기 기준 단어 및 복합명사 서브토큰)"""
    if not keyword:
        return []
    kw = keyword.strip().lower()
    words = [w for w in re.split(r'[\s,+/_\-]+', kw) if w]
    
    tokens = set()
    for w in words:
        if len(w) >= 2:
            tokens.add(w)
        # 4글자 이상 한글 복합어일 경우 2~3글자 단위 서브토큰도 추가 (예: '무릎보호대' -> '무릎', '보호대')
        if len(w) >= 4 and re.match(r'^[가-힣]+$', w):
            tokens.add(w[:2])
            tokens.add(w[2:])
            if len(w) >= 5:
                tokens.add(w[-2:])
                tokens.add(w[:3])
                tokens.add(w[-3:])

    if not tokens:
        tokens = set(words) if words else {kw}
    return list(tokens)

def is_ad_text_or_class(text: str = "", class_attr: str = "") -> bool:
    """광고, 스폰서, AD 여부 판별 (단어 경계 및 독립 라벨 검사)"""
    combined = f"{text} {class_attr}".lower()
    
    # 영문 AD / Sponsored / Advertisement 단어 경계 매칭
    if re.search(r'\b(ad|sponsored|advertisement)\b', combined, re.I):
        return True
        
    # 한글 광고 / 스폰서 키워드 매칭
    if any(k in combined for k in ["스폰서", "광고상품", "[광고]", "(광고)", "추천상품", "파워상품"]):
        return True
        
    # 개별 라인에 독립된 '광고', 'AD'가 존재하는지 확인
    for line in text.split("\n"):
        line_s = line.strip()
        if line_s in ["광고", "AD", "Ad", "sponsored", "Sponsored"]:
            return True
            
    return False

def is_relevant_product(title: str, keyword: str) -> bool:
    """
    상품명(title)이 사용자가 입력한 검색어의 핵심 단어를 포함하는지 검증 (검문소)
    - 검색어 전체(공백 제거)가 상품명에 포함되어 있거나
    - 검색어의 핵심 토큰 중 최소 1개 이상이 상품명에 포함되어야 통과
    """
    if not title or not keyword:
        return False
        
    title_clean = title.lower()
    title_nospace = re.sub(r'[\s\-_]', '', title_clean)
    kw_clean = keyword.lower().strip()
    kw_nospace = re.sub(r'[\s\-_]', '', kw_clean)
    
    # 1. 공백 제거 검색어 자체가 상품명에 그대로 포함된 경우 (예: '무릎보호대' in '네오프렌무릎보호대')
    if len(kw_nospace) >= 2 and (kw_nospace in title_nospace or kw_clean in title_clean):
        return True
        
    # 2. 핵심 토큰 중 최소 1개 이상 포함 여부 검사
    tokens = extract_keyword_tokens(keyword)
    for token in tokens:
        if token in title_clean or token in title_nospace:
            return True
            
    return False

async def search_danawa(page, keyword):
    """다나와 상위 상품 수집: 광고/스폰서 제외 및 키워드 검증 후 상위 5개 선별"""
    url = f"https://search.danawa.com/dsearch.php?query={urllib.parse.quote(keyword)}"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=12000)
        # 광고 및 추천 배너 셀렉터 1차 제외
        items = await page.query_selector_all('li.prod_item:not(.product-pot):not(.ad_item)')
        results = []
        
        # 10~25개의 충분한 후보군을 탐색하여 광고 스킵 후 정상 상품 5개 확보
        for item in items[:25]:
            cls = (await item.get_attribute("class")) or ""
            if "ad_item" in cls or "product-pot" in cls:
                continue
                
            # 광고 아이콘/뱃지 검사
            ad_el = await item.query_selector('.ico_ad, .txt_ad, .badge_ad, [class*="ad_layer"], [class*="product-pot"]')
            if ad_el:
                continue

            title_el = await item.query_selector('.prod_name a')
            price_el = await item.query_selector('.price_sect strong')
            img_el = await item.query_selector('.thumb_image img')
            
            if title_el and price_el:
                title = await title_el.inner_text()
                price = await price_el.inner_text()
                link = await title_el.get_attribute("href")
                
                # 광고 텍스트 체크
                if is_ad_text_or_class(title, cls):
                    continue
                    
                # 핵심 키워드 일치 검증(검문소)
                if not is_relevant_product(title, keyword):
                    continue
                
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
                
                if len(results) >= 5:
                    break
                    
        return results
    except Exception:
        return []

def search_naver_sync(keyword):
    """
    모바일 네이버 쇼핑 검색 (requests + BeautifulSoup 방식):
    - 봇 탐지 없는 모바일 네이버 쇼핑 URL 사용
    - 모바일 스마트폰 User-Agent 헤더 적용
    - 광고(AD/스폰서) 상품 제외 및 키워드 검증(검문소) 통과한 정상 상품 상위 5개 선별
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

            # 1. 광고 URL 파라미터 제외
            if any(ad_param in href for ad_param in ["ad_mid", "adcr", "nad-", "/ad/"]):
                continue

            mid_match = re.search(r'nv_mid=(\d+)', href)
            mid = mid_match.group(1) if mid_match else href
            if mid in seen_mids:
                continue

            parent = a.find_parent("li") or a.find_parent("div")
            if not parent:
                continue

            # 2. 광고 뱃지 / 스폰서 태그 / 클래스 제외
            parent_classes = " ".join(parent.get("class", []))
            p_text = parent.get_text(separator=" | ", strip=True)
            if is_ad_text_or_class(p_text, parent_classes):
                continue
                
            ad_badge = parent.find(lambda el: el.name in ['span', 'em', 'strong', 'i', 'div'] and el.get_text(strip=True) in ['광고', 'AD'])
            if ad_badge:
                continue

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

            # 3. 광고 텍스트 및 키워드 일치 검증(검문소)
            if is_ad_text_or_class(title, ""):
                continue
            if not is_relevant_product(title, keyword):
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

            # 충분한 후보군 중 정상 상품 5개 채워지면 완료
            if len(results) >= 5:
                break

        return results
    except Exception:
        return []

async def search_naver(page, keyword):
    """search_naver를 비동기 이벤트 루프 내에서 requests_sync로 안전하게 호출"""
    return await asyncio.to_thread(search_naver_sync, keyword)

async def search_coupang(page, keyword):
    """폴센트(Fallcent) 연동 쿠팡 최저가 수집: 광고/스폰서 제외 및 키워드 검증 후 상위 5개 선별"""
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
            cls = (await a.get_attribute("class")) or ""
            
            # 1. 광고 및 스폰서 아이템 제외
            if is_ad_text_or_class(text, cls):
                continue
                
            ad_el = await a.query_selector('[class*="ad"], [class*="sponsor"], [class*="badge_ad"]')
            if ad_el:
                continue

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
            
            # 2. 광고 텍스트 및 키워드 일치 검증(검문소)
            if is_ad_text_or_class(title, ""):
                continue
            if not is_relevant_product(title, keyword):
                continue

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
                
            # 충분한 후보군 순회 후 정상 상품 5개 채워지면 완료
            if len(results) >= 5:
                break
                
        return results
    except Exception:
        return []

def search_aliexpress_sync(keyword):
    """
    알리익스프레스(AliExpress) 한국어 검색 결과 스크래핑:
    - 해외 IP(Streamlit Community Cloud) 환경에서도 지역(KR), 화폐(KRW), 한국어(ko_KR) 강제 고정
    - 쿠키: aep_usuc_f=region=KR&site=kor&b_locale=ko_KR&c_tp=KRW; xman_us_f=x_locale=ko_KR&x_l=0; intl_locale=ko_KR;
    - Referer: https://ko.aliexpress.com/
    - 봇 감지 우회 헤더 및 원화/달러 자동 환산 파싱
    """
    encoded = urllib.parse.quote(keyword)
    url = f"https://ko.aliexpress.com/w/wholesale-{encoded}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://ko.aliexpress.com/",
        "Cookie": "aep_usuc_f=region=KR&site=kor&b_locale=ko_KR&c_tp=KRW; xman_us_f=x_locale=ko_KR&x_l=0; intl_locale=ko_KR;",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
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
            parent_cls = " ".join(a.parent.get("class", [])) if a.parent else ""
            
            # 1. 광고 및 스폰서 추천 상품 제외
            if is_ad_text_or_class(text, parent_cls):
                continue
            
            # 2. 썸네일 이미지 추출
            img_tag = a.find("img")
            if not img_tag and a.parent:
                img_tag = a.parent.find("img")
            img_src = DEFAULT_IMG
            if img_tag:
                src = img_tag.get("src") or img_tag.get("data-src") or ""
                if src:
                    img_src = ("https:" + src) if src.startswith("//") else src
                    
            # 3. 가격 파싱 (한화 ₩ / KRW 기준, 해외 IP 달러 $ 폴백 지원)
            price_match = re.search(r'(?:₩|KRW)\s*(\d{1,3}(?:\s*,\s*\d{3})*)', text)
            usd_match = re.search(r'\$\s*(\d+(?:\.\d+)?)', text)
            price_str = ""
            
            if price_match:
                clean_num = re.sub(r'[\s,]', '', price_match.group(1))
                if clean_num.isdigit():
                    price_str = f"{int(clean_num):,}원"
            elif usd_match:
                # 해외 서버에서 달러로 표기될 경우 한화(1,350원 기준)로 친절하게 자동 환산
                usd_val = float(usd_match.group(1))
                krw_val = int(usd_val * 1350)
                price_str = f"약 {krw_val:,}원"
            
            if not price_str:
                continue
                
            # 4. 상품명 파싱
            cutoff_pos = price_match.start() if price_match else (usd_match.start() if usd_match else len(text))
            title_part = text[:cutoff_pos].strip()
            title_part = re.sub(r'-\d+%', '', title_part).strip()
            title = title_part if len(title_part) >= 4 else text[:50]
            
            # 5. 광고 텍스트 및 키워드 일치 검증(검문소) - 무관한 추천 상품(면도기 등) 완벽 배제
            if is_ad_text_or_class(title, ""):
                continue
            if not is_relevant_product(title, keyword):
                continue

            clean_title = re.sub(r'\s+', '', title)
            if clean_title in seen_titles:
                continue

            # 6. 배송 정보
            shipping = "🚚 배송 무료" if ("무료 배송" in text or "무료" in text or "Free Shipping" in text) else "🚚 배송비 별도"
            
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
            
            # 충분한 후보군 중 정상 상품 5개 채워지면 완료
            if len(results) >= 5:
                break
                
        return results
    except Exception:
        return []

async def search_aliexpress(page, keyword):
    """search_aliexpress를 비동기 이벤트 루프 내에서 requests_sync로 호출 (실패 시 Playwright 폴백)"""
    res = await asyncio.to_thread(search_aliexpress_sync, keyword)
    if res:
        return res
    
    # 2단계 폴백: 만약 해외 IP에서 requests가 빈 결과일 경우 Playwright로 쿠키 주입 후 직접 로드
    try:
        await page.context.add_cookies([
            {"name": "aep_usuc_f", "value": "region=KR&site=kor&b_locale=ko_KR&c_tp=KRW", "domain": ".aliexpress.com", "path": "/"},
            {"name": "intl_locale", "value": "ko_KR", "domain": ".aliexpress.com", "path": "/"}
        ])
        encoded = urllib.parse.quote(keyword)
        url = f"https://ko.aliexpress.com/w/wholesale-{encoded}.html"
        await page.goto(url, wait_until="domcontentloaded", timeout=12000)
        await page.wait_for_timeout(2000)
        
        links = await page.query_selector_all('a[href*="/item/"]')
        results = []
        seen_ids = set()
        for a in links:
            href = await a.get_attribute('href')
            text = await a.inner_text()
            cls = (await a.get_attribute("class")) or ""
            if not href or not text:
                continue
                
            # 광고 및 스폰서 아이템 제외
            if is_ad_text_or_class(text, cls):
                continue
                
            m_id = re.search(r'/item/(\d+)\.html', href)
            item_id = m_id.group(1) if m_id else href
            if item_id in seen_ids:
                continue
            
            price_m = re.search(r'(?:₩|KRW)\s*(\d{1,3}(?:\s*,\s*\d{3})*)', text)
            usd_m = re.search(r'\$\s*(\d+(?:\.\d+)?)', text)
            price_str = ""
            if price_m:
                clean_num = re.sub(r'[\s,]', '', price_m.group(1))
                if clean_num.isdigit():
                    price_str = f"{int(clean_num):,}원"
            elif usd_m:
                price_str = f"약 {int(float(usd_m.group(1)) * 1350):,}원"
                
            if not price_str:
                continue
                
            full_link = ("https:" + href) if href.startswith("//") else href
            img_el = await a.query_selector('img')
            img_src = DEFAULT_IMG
            if img_el:
                src = await img_el.get_attribute("src")
                if src and src.startswith("http"):
                    img_src = src
                    
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            title = lines[0] if lines else keyword
            
            # 광고 및 키워드 일치 검증(검문소)
            if is_ad_text_or_class(title, ""):
                continue
            if not is_relevant_product(title, keyword):
                continue
                
            shipping = "🚚 배송 무료" if ("무료" in text or "Free" in text) else "🚚 배송비 별도"
            
            seen_ids.add(item_id)
            results.append({
                "mall": "알리익스프레스",
                "title": title[:50],
                "price": price_str,
                "shipping": shipping,
                "link": full_link,
                "img": img_src
            })
            if len(results) >= 5:
                break
        return results
    except Exception:
        return []

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
        
        # 2차 최종 방어선: 화면 출력 직전 키워드 관련성 재검증 및 상위 5개 보장
        return {
            "다나와": [it for it in danawa_res if is_relevant_product(it.get("title", ""), keyword)][:5],
            "네이버": [it for it in naver_res if is_relevant_product(it.get("title", ""), keyword)][:5],
            "쿠팡": [it for it in coupang_res if is_relevant_product(it.get("title", ""), keyword)][:5],
            "알리익스프레스": [it for it in ali_res if is_relevant_product(it.get("title", ""), keyword)][:5]
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
        f"<span style='background:#3182F6;color:#fff;font-size:0.75rem;"
        f"padding:2px 8px;border-radius:12px;font-weight:700;'>{cart_count}</span>",
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
