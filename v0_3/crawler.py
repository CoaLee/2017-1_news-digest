from url_crawl import extract_article_urls
from parser import parse_article, get_not_cached_title, mylogger
from interact_db import open_db, close_db, next_id, insert_into, insert_into_many, select_from, column_name, TABLE_SECTIONS, TABLE_HEADLINES, TABLE_ARTICLES, TABLE_WHOLE_ARTS, CACHE_SERVER
import config as CONFIG
import threading

class spiderWorker(threading.Thread):
    def __init__(self, spiderID, section_id, urls, enzyme, article_cols, result_list, base_url):
        threading.Thread.__init__(self)
        self.spiderID = spiderID
        self.section_id = section_id
        self.urls = urls
        self.enzyme = enzyme
        self.article_cols = article_cols
        self.result_list = result_list
        self.base_url = base_url

    def run(self):
        crawling(self.spiderID, self.section_id, self.urls, self.enzyme,\
                self.article_cols, self.result_list, self.base_url)

def crawling(spiderID, section_id, urls, enzyme, article_cols, result_list, base_url):
    mylogger.info("[CRAWLER] Spider {} Working on section #{}".format(str(spiderID), str(section_id)))
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
            article['title'] = get_not_cached_title(base_url, url)

        article['section_id'] = section_id
        article['article_url'] = url
        articles.append(article)

    th_lock.acquire()
    result_list.append(articles)
    th_lock.release()

th_lock = threading.Lock()

def main():
    open_db()
    mylogger.info("[CRAWLER] ======== DB opened ========")

    sections = select_from(TABLE_SECTIONS)
    article_cols = column_name(TABLE_WHOLE_ARTS)

    for (section_id, section_name, base_url) in sections:
        article_urls = extract_article_urls(base_url)
        article_urls = list_remove_duplicates(article_urls)

        mylogger.info("[CRAWLER] url duplication check Starts")
        # redis use bytes format for data. so need to convert when comparing.
        key_prev_urls = "prev_urls_of {}".format(section_id)
        prev_urls = CACHE_SERVER.lrange(key_prev_urls, 0, -1)

        if prev_urls != None:
            cur_urls = [bytes(x, 'utf-8') for x in article_urls]
            cur_urls_set = set(cur_urls)
            prev_urls_set = set(prev_urls)
            common_set = cur_urls_set & prev_urls_set
            # every elements already exist
            if len(common_set) == len(cur_urls_set):
                mylogger.info("[CRAWLER] nothing new")
                continue
            # some remains. need update
            else:
                for existing in common_set:
                    article_urls.remove(existing.decode('utf-8'))
                mylogger.info("[CRAWLER] remain urls: {}".format(len(article_urls)))

        # lpush 'reversely', and maintain list length less than 500
        CACHE_SERVER.lpush(key_prev_urls, *article_urls[::-1])
        CACHE_SERVER.ltrim(key_prev_urls, 0, CONFIG.MAX_CACHED_URLS)

        mylogger.info("[CRAWLER] url duplication check Finished")

        capa = CONFIG.CRAWL_CAPACITY
        spider_cnt = -(-len(article_urls) // capa)
        result_list = []
        threads = []

        mylogger.info("[CRAWLER] urls in section #{}: {}. Required spiders: {}. Now starting."\
                .format(section_id, len(article_urls), spider_cnt))

        for i in range(spider_cnt):
            thread = spiderWorker(i, section_id, article_urls[i*capa:(i+1)*capa], 1, article_cols, result_list, base_url)
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

        # result_list.sort(key = lambda row:row['written_date'])
        # flattening list of lists into a list
        flat_result = [item for sublist in result_list for item in sublist]
        mylogger.info("[CRAWLER] {} articles digested, now storing into DB".format(len(flat_result)))

        insert_into_many(TABLE_WHOLE_ARTS, article_cols, flat_result)
        mylogger.info("[CRAWLER] Successfully stored.")

    close_db()
    mylogger.info("[CRAWLER] ======== DB closed ========")

def filter_dict_with_tuple(key_tuple, dict_data):
    result = {}
    for key in key_tuple:
        result[key] = dict_data.get(key)
    return result

# from a SO answer here. https://stackoverflow.com/questions/480214
def list_remove_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

if __name__ == '__main__':
    main()
