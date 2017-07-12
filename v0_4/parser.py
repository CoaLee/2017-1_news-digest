import requests
import re
from bs4 import BeautifulSoup, Comment
import logging

handler_crawllog = logging.FileHandler("log_crawl.log")
handler_crawllog.setFormatter(logging.Formatter("%(asctime)s| %(message)s"))
mylogger = logging.getLogger('mylogger')
mylogger.setLevel(logging.DEBUG)
mylogger.addHandler(handler_crawllog)

mylogger.debug("[PARSER] logging start in parser.py")

IMG_TMP_TAG = '[<img]>'

def get_title(soup, enzyme):
    title = ''
    for item in soup.find_all(id=enzyme['title']):
        title = item.text
    return title

def get_date(soup, enzyme):
    date = ''
    # TODO datetime object
    for tmp_date in soup.find_all(class_='t11'):
        date = tmp_date.text
        break
    return date

def get_journal(soup, enzyme):
    journal = ''
    for item in soup.find_all(class_=enzyme['journal']):
        journal = item.find('img')['title']
    return journal

def get_textbody_and_imgs(soup, enzyme):
    text = ''
    img_pos = ''
    img_urls = ''
    
    for item in soup.find_all('div', id=enzyme['article_body']):
        # remove <script> tag
        for script in item.find_all('script'):
            script.extract()
        # remove comments: <!-- -->
        for comment in item.find_all(string = lambda text:isinstance(text, Comment)):
            comment.extract()
        # operation for photos. TODO 
        for img in item.find_all('img'):
            img_url = img['src']

            # find possible caption-containing parent
            second_grand_parent = img
            for parent in img.parents:
                if parent == item:
                    break
                second_grand_parent = parent

            # if it has strings in int add up them to a caption
            caption = ''
            if second_grand_parent == img:
                pass
            else: 
                if second_grand_parent.stripped_strings is not None:
                    for partial_text in second_grand_parent.stripped_strings:
                        caption += partial_text

            tmp_string = IMG_TMP_TAG + img_url + ' ' + caption
            second_grand_parent.replace_with(tmp_string)

        for partial_text in item.stripped_strings:
            # skipping new line character
            #if partial_text == '\n':
            #   continue
            #text += partial_text.rstrip() + '\n\n'
            if partial_text.startswith(IMG_TMP_TAG):
                img_pos += str(len(text)) + ' '
                img_urls += partial_text[len(IMG_TMP_TAG):] + '\n'
            else:
                text += partial_text + '\n\n'

    body_dict = {
        'textbody': text,
        'img_pos': img_pos,
        'img_urls': img_urls
    }
    return body_dict 

def parse_article(article_URL, enzyme):
    req = requests.get(article_URL) 
    soup = BeautifulSoup(req.text, 'lxml')
    data = {}
    data['title'] = get_title(soup, enzyme)
    # TODO in case of failure, return None. It will be taken care 
    if data['title'] == '':
        return None
    data['written_date'] = get_date(soup, enzyme)
    data['journal'] = get_journal(soup, enzyme)

    body_dict = get_textbody_and_imgs(soup, enzyme)
    data['textbody'] = body_dict['textbody']
    data['img_pos'] = body_dict['img_pos']
    data['img_urls'] = body_dict['img_urls']
    return data

def get_not_cached_title(base_url, url):
    req = requests.get(base_url) 
    soup = BeautifulSoup(req.text, 'lxml')
    title = soup.findAll('a', href=url)[0]
    return title.text.strip()

def main():
    article_URL = \
        'http://news.naver.com/main/read.nhn?mode=LSD&mid=shm&sid1=100&oid=022&aid=0003174397'
    mylogger.info("[PARSER] requests.get(article_URL)")
    req = requests.get(article_URL) 
    mylogger.info("[PARSER] soup = BeautifulSoup(req.text, 'lxml') ")
    soup = BeautifulSoup(req.text, 'lxml') 
    data = {}
    mylogger.info("[PARSER] data['title'] = get_title(soup)")
    data['title'] = get_title(soup)
    mylogger.info("[PARSER] data['written_date'] = get_date(soup)")
    data['written_date'] = get_date(soup)

    mylogger.info("[PARSER] body_dict = get_textbody_and_imgs(soup)")
    body_dict = get_textbody_and_imgs(soup)
    data['textbody'] = body_dict['textbody']
    data['img_pos'] = body_dict['img_pos']
    data['img_urls'] = body_dict['img_urls']
    mylogger.info("[PARSER] ends")
    print(data)

if __name__ == '__main__':
    main()
