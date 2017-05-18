from url_crawl import extract_article_urls
from parser import parse_article  

BASE_URL = 'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=100'

def main():
    article_urls = extract_article_urls(BASE_URL)
    i = 0
    for url in article_urls:
        data = parse_article(url)
        print(data['textbody'])
        i += 1
        if i>=3:
            break

if __name__ == '__main__':
    main()
