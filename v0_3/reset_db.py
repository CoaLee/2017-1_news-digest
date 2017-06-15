import MySQLdb
import redis
import config as CONFIG

CACHE_SERVER = None 
if CONFIG.USING_CACHE is True:
    CACHE_SERVER = redis.Redis("localhost")

CACHE_SERVER.flushdb()

USER = 'root'
DATABASE = 'news_digest'
PASSWORD = '101341'

TABLE_SECTIONS = 'news_sections'
TABLE_HEADLINES = 'section_headlines'
TABLE_ARTICLES = 'articles'
TABLE_WHOLE_ARTS = 'whole_articles'

db = MySQLdb.connect(user=USER, passwd=PASSWORD, db=DATABASE, charset='utf8')
c = db.cursor()

def reset_query(table):
    return 'DELETE FROM {}; ALTER TABLE {} AUTO_INCREMENT=1;'.format(table, table)

c.execute(reset_query(TABLE_WHOLE_ARTS))
c.execute(reset_query(TABLE_SECTIONS))

section_name = u'네이버 정치'
base_url = u'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=100'
c.execute('INSERT INTO {} (section_name, base_url) VALUES ("{}", "{}");'\
        .format(TABLE_SECTIONS, section_name, base_url))

section_name = u'네이버 경제'
base_url = u'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=101'
c.execute('INSERT INTO {} (section_name, base_url) VALUES ("{}", "{}");'\
        .format(TABLE_SECTIONS, section_name, base_url))

c.close()
db.commit()
db.close()
