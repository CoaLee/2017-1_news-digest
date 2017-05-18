import requests
import re
from bs4 import BeautifulSoup, Comment

enzyme = {
    'title': 'articleTitle',
    'article_body': 'articleBodyContents',
    'written_date': 't11'
}

def get_title(soup):
    title = ''
    for item in soup.find_all(id='articleTitle'):
        title = item.text
    return title

def get_date(soup):
    date = ''
    for tmp_date in soup.find_all(class_='t11'):
        date = tmp_date.text
        break
    return date

def get_textbody(soup):
    text = ''
    
    for item in soup.find_all('div', id='articleBodyContents'):
        # remove <script> tag
        for script in item.find_all('script'):
            script.extract()
        # remove comments: <!-- -->
        for comment in item.find_all(string = lambda text:isinstance(text, Comment)):
            comment.extract()
        # operation for <table> tag, that is photos TODO 
        for photo in item.find_all('table'):
            photo.extract()
        for partial_text in item.find_all(text=True):
            # skipping new line character
            if partial_text == '\n':
                continue
            text += partial_text.rstrip() + '\n\n'

    """
    # Trimming after the email address of the author
    #not working r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)" from http://emailregex.com/
    email_regex = r'[\w\.-]+@[\w\.-]+'
    end_pos = re.search(email_regex, text).end()

    # TODO: need to locate the last occurence of email. consider the case for parentheses
    text = text[:end_pos+1]  
    """
    return text

def parse_article(article_URL):
    req = requests.get(article_URL) 
    soup = BeautifulSoup(req.text, 'lxml')
    data = {}
    data['title'] = get_title(soup)
    data['written_date'] = get_date(soup)
    data['textbody'] = get_textbody(soup)
    return data

def main():
    article_URL = \
        'http://news.naver.com/main/read.nhn?mode=LSD&mid=shm&sid1=100&oid=022&aid=0003174397'
    req = requests.get(article_URL) 
    soup = BeautifulSoup(req.text, 'lxml')
    data = {}
    data['title'] = get_title(soup)
    data['written_date'] = get_date(soup)
    data['textbody'] = get_textbody(soup)
    print(data)

if __name__ == '__main__':
    main()
