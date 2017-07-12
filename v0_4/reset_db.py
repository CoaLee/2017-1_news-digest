import MySQLdb
import redis
from interact_db import query_key_value_builder, TABLE_SECTIONS, TABLE_WHOLE_ARTS
import config as CONFIG

CACHE_SERVER = None 
if CONFIG.USING_CACHE is True:
    CACHE_SERVER = redis.Redis("localhost")

CACHE_SERVER.flushdb()

USER = 'root'
DATABASE = 'news_digest'
PASSWORD = '101341'

db = MySQLdb.connect(user=USER, passwd=PASSWORD, db=DATABASE, charset='utf8')
c = db.cursor()

def reset_query(table):
    return 'DELETE FROM {}; ALTER TABLE {} AUTO_INCREMENT=1;'.format(table, table)

c.execute(reset_query(TABLE_WHOLE_ARTS))
c.execute(reset_query(TABLE_SECTIONS))

enzyme = {
    'section_name': u'네이버 정치',
    'base_url': u'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=100',
    'title': 'articleTitle',
    'article_body': 'articleBodyContents',
    'written_date': 't11',
    'journal': 'press_logo',
    'image': 'end_photo_org',
    'links_body': 'main_content'
}

query = "INSERT INTO {} {};".format(TABLE_SECTIONS, query_key_value_builder(enzyme))
c.execute(query)

enzyme['section_name'] = u'네이버 경제'
enzyme['base_url'] = u'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=101'

query = "INSERT INTO {} {};".format(TABLE_SECTIONS, query_key_value_builder(enzyme))
c.execute(query)

c.close()
db.commit()
db.close()
