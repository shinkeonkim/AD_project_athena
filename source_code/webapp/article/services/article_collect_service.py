import logging
from urllib.parse import urlparse

import requests
from article.models import Article
from bs4 import BeautifulSoup
from django.db import transaction
from duckduckgo_search import DDGS
from problem.models import Problem


class ArticleCollectService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.supported_sites = {
            "tistory.com": self.parse_tistory,
            "velog.io": self.parse_velog,
            "github.com": self.parse_github,
            "naver.com": self.parse_naver_blog,
            "notion.site": self.parse_notion,
            "medium.com": self.parse_medium,
        }

    def search_article_urls(self, problem_id: int, max_results: int = 30):
        query = f"백준 {problem_id} 해설 OR 풀이"
        logging.info(f"DuckDuckGo 검색 시작: query={query}, max_results={max_results}")
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                url = r.get("href")
                if url:
                    logging.info(f"DuckDuckGo 검색 결과 URL: {url}")
                    results.append(url)
        logging.info(f"DuckDuckGo 검색 결과 총 {len(results)}개 URL 수집 완료")
        return results

    def parse_tistory(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.select_one(".title") or soup.select_one("h1.entry-title")
        title_text = title.text.strip() if title else "Unknown Title"
        content_div = soup.select_one(".entry-content") or soup.select_one(".article")
        if not content_div:
            return None
        paragraphs = content_div.find_all(["p", "pre", "code", "h2", "h3"])
        content = "\n".join([p.text.strip() for p in paragraphs])
        code_blocks = content_div.find_all("pre")
        code = "\n\n".join([block.text for block in code_blocks])
        return {
            "title": title_text,
            "content": content,
            "code": code,
            "url": url,
            "source": "tistory",
            "author": "",
        }

    def parse_velog(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1")
        title_text = title.text.strip() if title else "Unknown Title"
        content_div = soup.find(class_="velog-content")
        if not content_div:
            # velog는 JS 렌더링이 필요한 경우가 많음
            return None
        paragraphs = content_div.find_all(["p", "pre", "code", "h2", "h3"])
        content = "\n".join([p.text.strip() for p in paragraphs])
        code_blocks = content_div.find_all("pre")
        code = "\n\n".join([block.text for block in code_blocks])
        author = soup.find("a", class_="username")
        author_text = author.text.strip() if author else ""
        return {
            "title": title_text,
            "content": content,
            "code": code,
            "url": url,
            "source": "velog",
            "author": author_text,
        }

    def parse_github(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.text.strip() if soup.title else "Unknown Title"
        # README나 코드 파일의 경우 전체 텍스트를 content로 저장
        content = soup.get_text()
        code = ""
        author = ""
        # github.com/{user}/{repo}/blob/{branch}/... 형태면 코드블록 추출
        file_blob = soup.find("table", class_="js-file-line-container")
        if file_blob:
            code = "\n".join([tr.text for tr in file_blob.find_all("tr")])
        return {
            "title": title,
            "content": content,
            "code": code,
            "url": url,
            "source": "github",
            "author": author,
        }

    def parse_naver_blog(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h3", class_="se_textarea")
        if not title:
            title = soup.find("title")
        title_text = title.text.strip() if title else "Unknown Title"
        content_div = soup.find("div", class_="se-main-container")
        if not content_div:
            content_div = soup.find("div", id="postViewArea")
        if not content_div:
            return None
        paragraphs = content_div.find_all(["p", "pre", "code", "h2", "h3"])
        content = "\n".join([p.text.strip() for p in paragraphs])
        code_blocks = content_div.find_all("pre")
        code = "\n\n".join([block.text for block in code_blocks])
        author = ""
        return {
            "title": title_text,
            "content": content,
            "code": code,
            "url": url,
            "source": "naver",
            "author": author,
        }

    def parse_notion(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("title")
        title_text = title.text.strip() if title else "Unknown Title"
        # Notion은 JS 렌더링이 필요한 경우가 많음
        content = soup.get_text()
        code = ""
        author = ""
        return {
            "title": title_text,
            "content": content,
            "code": code,
            "url": url,
            "source": "notion",
            "author": author,
        }

    def parse_medium(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1")
        title_text = (
            title.text.strip()
            if title
            else (soup.title.text.strip() if soup.title else "Unknown Title")
        )
        content_div = soup.find("article")
        if not content_div:
            return None
        paragraphs = content_div.find_all(["p", "pre", "code", "h2", "h3"])
        content = "\n".join([p.text.strip() for p in paragraphs])
        code_blocks = content_div.find_all("pre")
        code = "\n\n".join([block.text for block in code_blocks])
        author = ""
        return {
            "title": title_text,
            "content": content,
            "code": code,
            "url": url,
            "source": "medium",
            "author": author,
        }

    def generic_scrape(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.text.strip() if soup.title else "Unknown Title"
        content = soup.get_text()
        return {
            "title": title,
            "content": content,
            "code": "",
            "url": url,
            "source": urlparse(url).netloc,
            "author": "",
        }

    def scrape_article(self, url):
        domain = urlparse(url).netloc
        logging.info(f"게시글 파싱 시도: {url} (domain: {domain})")
        for site_domain, parser in self.supported_sites.items():
            if site_domain in domain:
                try:
                    result = parser(url)
                    if result:
                        logging.info(f"{site_domain} 파서 성공: {url}")
                    else:
                        logging.warning(f"{site_domain} 파서 실패: {url}")
                    return result
                except Exception as e:
                    logging.error(f"{site_domain} 파서 예외: {url} - {e}")
                    return None
        try:
            result = self.generic_scrape(url)
            if result:
                logging.info(f"generic_scrape 성공: {url}")
            else:
                logging.warning(f"generic_scrape 실패: {url}")
            return result
        except Exception as e:
            logging.error(f"generic_scrape 예외: {url} - {e}")
            return None

    @transaction.atomic
    def collect_articles_for_problem(self, problem_id: int, max_articles: int = 10):
        logging.info(
            f"문제 {problem_id}에 대한 게시글 수집 시작 (최대 {max_articles}개)"
        )
        problem = Problem.objects.get(boj_id=problem_id)
        urls = self.search_article_urls(problem_id, max_results=max_articles)
        articles = []
        for url in urls[:max_articles]:
            data = self.scrape_article(url)
            if not data:
                logging.warning(f"게시글 파싱 실패: {url}")
                continue
            article, created = Article.objects.update_or_create(
                full_url=data["url"],
                problem=problem,
                defaults={
                    "title": data["title"],
                    "content": data["content"],
                    "code": data.get("code", ""),
                    "source": data.get("source", ""),
                    "author": data.get("author", ""),
                },
            )
            if created:
                logging.info(f"새 Article 저장: {article.full_url}")
            else:
                logging.info(f"기존 Article 갱신: {article.full_url}")
            articles.append(article)
        logging.info(f"문제 {problem_id}에 대해 총 {len(articles)}개 Article 저장 완료")
        return articles
