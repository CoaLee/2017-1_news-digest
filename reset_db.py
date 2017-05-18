import MySQLdb

USER = 'root'
DATABASE = 'news_digest'
PASSWORD = '101341'

TABLE_SECTIONS = 'news_sections'
TABLE_HEADLINES = 'section_headlines'
TABLE_ARTICLES = 'articles'

db = MySQLdb.connect(user=USER, passwd=PASSWORD, db=DATABASE, charset='utf8')
c = db.cursor()

def reset_query(table):
    return 'DELETE FROM {}; ALTER TABLE {} AUTO_INCREMENT=1;'.format(table, table)

c.execute(reset_query(TABLE_SECTIONS))
c.execute(reset_query(TABLE_HEADLINES))
c.execute(reset_query(TABLE_ARTICLES))

def_section_name = u'네이버 정치'
def_base_url = u'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=100'
c.execute('INSERT INTO {} (section_name, base_url) VALUES ("{}", "{}");'\
        .format(TABLE_SECTIONS, def_section_name, def_base_url))

c.close()
db.commit()
db.close()

