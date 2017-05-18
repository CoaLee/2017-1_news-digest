# modifed from http://m.blog.naver.com/htk1019

import re
import requests

def get_html(target_date, page_num):
    page_url = "http://news.naver.com/main/list.nhn?sid2=258&sid1=101&mid=shm&mode=LS2D&date=" + \
    str(target_date) + "&page=" + str(page_num) + ""

    response = requests.get(page_url)
    html = response.text

    return html

def ext_news_urls(html):
    url_frags = re.findall('<a href="(.*?)"', html)
    news_urls=[]

    for url_frag in url_frags:
        if "aid" in url_frag:
            news_urls.append(url_frag)
        else :
            continue

    return news_urls

def extract_article_urls(base_url):
    article_urls = []

    response = requests.get(base_url)
    base_html = response.text

    urls = ext_news_urls(base_html)
    article_urls += urls

    return article_urls

def main():
    # 네이버 정치
    base_url = 'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=100'
    page_num = 1
    max_page_num = 20

    article_urls = []

    # first get the article urls here
    response = requests.get(base_url)
    base_html = response.text

    urls = ext_news_urls(base_html)
    article_urls += urls

    # TODO if there is paging, follow the paging
    print(re.findall('class="paging"', base_html))

    """
    while page_num<=max_page_num:
        html = get_html(target_date, page_num)
        urls = ext_news_urls(html)
        article_urls.append(urls)
        page_num+=1
    """

    print(article_urls)

if __name__ == '__main__':
    main()
