from url_crawl import extract_article_urls
from parser import parse_article, get_not_cached_title
from interact_db import open_db, close_db, next_id, insert_into, insert_into_many, select_from, column_name, TABLE_SECTIONS, TABLE_HEADLINES, TABLE_ARTICLES, TABLE_WHOLE_ARTS
import config as CONFIG
import threading
import logging

logging.basicConfig(filename = 'crawler_log.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.debug("[CRAWLER] logging start")

caching_file = 

class spiderWorker(threading.Thread):
    def __init__(self, spiderID, section_id, urls, enzyme, article_cols, result_list):
        threading.Thread.__init__(self)
        self.spiderID = spiderID
        self.section_id = section_id
        self.urls = urls
        self.enzyme = enzyme
        self.article_cols = article_cols
        self.result_list = result_list

    def run(self):
        crawling(self.spiderID, self.section_id, self.urls, self.enzyme, self.article_cols, self.result_list)

def crawling(spiderID, section_id, urls, enzyme, article_cols, result_list):
    logging.info("[CRAWLER] Spider {} Working on section #{}".format(str(spiderID), str(section_id)))
    articles = []
    for url in urls:
        article = {}
        try:
            data = parse_article(url)
            article = filter_dict_with_tuple(article_cols, data)
            article['cached'] = 1
        # parsing fail -> Cache fail
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            article['cached'] = 0

        article['section_id'] = section_id
        article['article_url'] = url
        article['title'] = get_not_cached_title(base_url, url)
        articles.append(article)

    lock_q.acquire()
    result_list.append(articles)
    lock_q.release()

lock_q = threading.Lock()

def main():
    open_db()
    logging.info("[CRAWLER] DB opened")

    sections = select_from(TABLE_SECTIONS)
    article_cols = column_name(TABLE_WHOLE_ARTS)

    for (section_id, section_name, base_url) in sections:
        article_urls = extract_article_urls(base_url)
        cnt = 0 

        capa = CONFIG.CRAWL_CAPACITY
        spider_cnt = -(-len(article_urls) // capa)
        result_list = []
        threads = []

        logging.info("[CRAWLER] urls in section #{}: {}. spider capacity: {}.\nRequired spiders: {}. Now starting threads.".format(section_id, len(article_urls), capa, spider_cnt))

        for i in range(spider_cnt):
            thread = spiderWorker(i, section_id, article_urls[i*capa:(i+1)*capa], 1, article_cols, result_list)
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

        #result_list.sort(key = lambda row:row['written_date'])
        # flattening
        flat_result = [item for sublist in result_list for item in sublist]
        logging.info("[CRAWLER] Articles digested, now storing into DB")

        insert_into_many(TABLE_WHOLE_ARTS, article_cols, flat_result)
        logging.info("[CRAWLER] Successfully stored.")

    close_db()
    logging.info("[CRAWLER] DB closed")

def filter_dict_with_tuple(key_tuple, dict_data):
    result = {}
    for key in key_tuple:
        result[key] = dict_data.get(key)
    return result

if __name__ == '__main__':
    main()
