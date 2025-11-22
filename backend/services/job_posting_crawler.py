"""
Job Posting Crawler Service
직무 공고 URL을 크롤링하여 정보를 추출하는 서비스
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from urllib.parse import urlparse
import re


def detect_platform(url: str) -> Optional[str]:
    """
    URL로부터 크롤링 플랫폼을 감지합니다.
    
    Returns:
        'wanted', 'saramin', 'jobkorea', 'incruit', 'linkedin', 'indeed', None
    """
    domain = urlparse(url).netloc.lower()
    
    if 'wanted.co.kr' in domain or 'wanted' in domain:
        return 'wanted'
    elif 'saramin.co.kr' in domain or 'saramin' in domain:
        return 'saramin'
    elif 'jobkorea.co.kr' in domain or 'jobkorea' in domain:
        return 'jobkorea'
    elif 'incruit.com' in domain or 'incruit' in domain:
        return 'incruit'
    elif 'linkedin.com' in domain or 'linkedin' in domain:
        return 'linkedin'
    elif 'indeed.com' in domain or 'indeed' in domain:
        return 'indeed'
    
    return None


def crawl_job_posting(url: str) -> Dict[str, Optional[str]]:
    """
    직무 공고 URL을 크롤링하여 정보를 추출합니다.
    
    Args:
        url: 크롤링할 직무 공고 URL
    
    Returns:
        {
            'company_name': 회사명,
            'title': 직무명/제목,
            'raw_text': 전체 공고 텍스트,
            'source_url': 원본 URL,
            'platform': 플랫폼명
        }
    """
    try:
        # User-Agent 설정 (일부 사이트에서 차단 방지)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 플랫폼 감지
        platform = detect_platform(url)
        
        # 플랫폼별 크롤링 로직
        if platform == 'wanted':
            return crawl_wanted(soup, url)
        elif platform == 'saramin':
            return crawl_saramin(soup, url)
        elif platform == 'jobkorea':
            return crawl_jobkorea(soup, url)
        elif platform == 'incruit':
            return crawl_incruit(soup, url)
        elif platform == 'linkedin':
            return crawl_linkedin(soup, url)
        elif platform == 'indeed':
            return crawl_indeed(soup, url)
        else:
            # 플랫폼을 감지하지 못한 경우 일반 크롤링
            return crawl_generic(soup, url)
            
    except requests.RequestException as e:
        raise Exception(f"URL 크롤링 실패: {str(e)}")
    except Exception as e:
        raise Exception(f"크롤링 중 오류 발생: {str(e)}")


def crawl_wanted(soup: BeautifulSoup, url: str) -> Dict[str, Optional[str]]:
    """Wanted 크롤링"""
    # Wanted는 보통 JSON-LD나 특정 클래스를 사용
    company_name = None
    title = None
    raw_text = None
    
    # 회사명 추출
    company_elem = soup.find('div', class_=re.compile(r'company', re.I)) or \
                   soup.find('span', class_=re.compile(r'company', re.I)) or \
                   soup.find('a', class_=re.compile(r'company', re.I))
    if company_elem:
        company_name = company_elem.get_text(strip=True)
    
    # 제목 추출
    title_elem = soup.find('h1') or soup.find('h2', class_=re.compile(r'title|position', re.I))
    if title_elem:
        title = title_elem.get_text(strip=True)
    
    # 본문 추출
    content_elem = soup.find('div', class_=re.compile(r'content|description|detail', re.I)) or \
                   soup.find('section', class_=re.compile(r'content|description', re.I))
    if content_elem:
        raw_text = content_elem.get_text(separator='\n', strip=True)
    
    # 메타 태그에서 정보 추출 (fallback)
    if not company_name:
        meta_company = soup.find('meta', property='og:site_name') or \
                       soup.find('meta', attrs={'name': re.compile(r'company', re.I)})
        if meta_company:
            company_name = meta_company.get('content', '')
    
    if not title:
        meta_title = soup.find('meta', property='og:title') or soup.find('title')
        if meta_title:
            title = meta_title.get('content') or meta_title.get_text(strip=True)
    
    # 전체 텍스트가 없으면 body에서 추출
    if not raw_text:
        body = soup.find('body')
        if body:
            # 스크립트와 스타일 제거
            for script in body(['script', 'style', 'nav', 'header', 'footer']):
                script.decompose()
            raw_text = body.get_text(separator='\n', strip=True)
    
    return {
        'company_name': company_name or '알 수 없음',
        'title': title or '알 수 없음',
        'raw_text': raw_text or '',
        'source_url': url,
        'platform': 'wanted'
    }


def crawl_saramin(soup: BeautifulSoup, url: str) -> Dict[str, Optional[str]]:
    """사람인 크롤링"""
    company_name = None
    title = None
    raw_text = None
    
    # 사람인 특정 구조
    company_elem = soup.find('div', class_=re.compile(r'company', re.I)) or \
                   soup.find('strong', class_=re.compile(r'company', re.I))
    if company_elem:
        company_name = company_elem.get_text(strip=True)
    
    title_elem = soup.find('h1', class_=re.compile(r'title|position', re.I)) or soup.find('h1')
    if title_elem:
        title = title_elem.get_text(strip=True)
    
    content_elem = soup.find('div', class_=re.compile(r'content|description|detail', re.I)) or \
                   soup.find('div', id=re.compile(r'content|description', re.I))
    if content_elem:
        raw_text = content_elem.get_text(separator='\n', strip=True)
    
    # Fallback
    if not raw_text:
        body = soup.find('body')
        if body:
            for script in body(['script', 'style', 'nav', 'header', 'footer']):
                script.decompose()
            raw_text = body.get_text(separator='\n', strip=True)
    
    return {
        'company_name': company_name or '알 수 없음',
        'title': title or '알 수 없음',
        'raw_text': raw_text or '',
        'source_url': url,
        'platform': 'saramin'
    }


def crawl_jobkorea(soup: BeautifulSoup, url: str) -> Dict[str, Optional[str]]:
    """잡코리아 크롤링"""
    company_name = None
    title = None
    raw_text = None
    
    company_elem = soup.find('div', class_=re.compile(r'company', re.I)) or \
                   soup.find('a', class_=re.compile(r'company', re.I))
    if company_elem:
        company_name = company_elem.get_text(strip=True)
    
    title_elem = soup.find('h1') or soup.find('div', class_=re.compile(r'title', re.I))
    if title_elem:
        title = title_elem.get_text(strip=True)
    
    content_elem = soup.find('div', class_=re.compile(r'content|description|detail', re.I))
    if content_elem:
        raw_text = content_elem.get_text(separator='\n', strip=True)
    
    if not raw_text:
        body = soup.find('body')
        if body:
            for script in body(['script', 'style', 'nav', 'header', 'footer']):
                script.decompose()
            raw_text = body.get_text(separator='\n', strip=True)
    
    return {
        'company_name': company_name or '알 수 없음',
        'title': title or '알 수 없음',
        'raw_text': raw_text or '',
        'source_url': url,
        'platform': 'jobkorea'
    }


def crawl_incruit(soup: BeautifulSoup, url: str) -> Dict[str, Optional[str]]:
    """인크루트 크롤링"""
    return crawl_generic(soup, url, 'incruit')


def crawl_linkedin(soup: BeautifulSoup, url: str) -> Dict[str, Optional[str]]:
    """LinkedIn 크롤링"""
    company_name = None
    title = None
    raw_text = None
    
    # LinkedIn은 보통 JSON-LD를 사용
    json_ld = soup.find('script', type='application/ld+json')
    if json_ld:
        try:
            import json
            data = json.loads(json_ld.string)
            if isinstance(data, dict):
                company_name = data.get('hiringOrganization', {}).get('name', '')
                title = data.get('title', '')
                raw_text = data.get('description', '')
        except:
            pass
    
    # Fallback
    if not company_name:
        company_elem = soup.find('a', class_=re.compile(r'company', re.I))
        if company_elem:
            company_name = company_elem.get_text(strip=True)
    
    if not title:
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            title = title_elem.get_text(strip=True)
    
    if not raw_text:
        content_elem = soup.find('div', class_=re.compile(r'description|content', re.I))
        if content_elem:
            raw_text = content_elem.get_text(separator='\n', strip=True)
    
    return {
        'company_name': company_name or '알 수 없음',
        'title': title or '알 수 없음',
        'raw_text': raw_text or '',
        'source_url': url,
        'platform': 'linkedin'
    }


def crawl_indeed(soup: BeautifulSoup, url: str) -> Dict[str, Optional[str]]:
    """Indeed 크롤링"""
    return crawl_generic(soup, url, 'indeed')


def crawl_generic(soup: BeautifulSoup, url: str, platform: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    일반적인 크롤링 (플랫폼별 특화 로직이 없는 경우)
    """
    company_name = None
    title = None
    raw_text = None
    
    # 메타 태그에서 정보 추출
    meta_company = soup.find('meta', property='og:site_name') or \
                   soup.find('meta', attrs={'name': re.compile(r'company|organization', re.I)})
    if meta_company:
        company_name = meta_company.get('content', '')
    
    # 제목 추출
    meta_title = soup.find('meta', property='og:title')
    if meta_title:
        title = meta_title.get('content', '')
    else:
        title_elem = soup.find('title') or soup.find('h1')
        if title_elem:
            title = title_elem.get_text(strip=True)
    
    # 본문 추출
    content_elem = soup.find('main') or \
                   soup.find('article') or \
                   soup.find('div', class_=re.compile(r'content|description|detail|body', re.I))
    
    if content_elem:
        # 불필요한 요소 제거
        for elem in content_elem(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            elem.decompose()
        raw_text = content_elem.get_text(separator='\n', strip=True)
    else:
        # body에서 추출
        body = soup.find('body')
        if body:
            for script in body(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                script.decompose()
            raw_text = body.get_text(separator='\n', strip=True)
    
    return {
        'company_name': company_name or '알 수 없음',
        'title': title or '알 수 없음',
        'raw_text': raw_text or '',
        'source_url': url,
        'platform': platform or 'generic'
    }

