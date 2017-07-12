import MySQLdb
import config as CONFIG
import redis
from multiprocessing import Lock

CACHE_SERVER = None 
if CONFIG.USING_CACHE is True:
    CACHE_SERVER = redis.Redis("localhost")

USER = 'root'
DATABASE = 'news_digest'
PASSWORD = '101341'

TABLE_SECTIONS = 'news_sections'
TABLE_WHOLE_ARTS = 'whole_articles'

_db = None
_cursor = None
key_DB_request = "key_DB_request"
open_lock = Lock()
close_lock = Lock()

section_col = ('id', 'section_name', 'base_url')
headline_col = ('id', 'section_id', 'title', 'thumbnail', 'cached', 'article_id', 'article_url', 'written_date', 'journal')
article_col = ('id', 'written_date', 'modified_date', 'textbody', 'img_pos', 'img_urls', 'title', 'journal')

def open_db():
    global _db, _cursor

    open_lock.acquire()
    if CACHE_SERVER.incr(key_DB_request) == 1:
        if _db == None:
            _db = MySQLdb.connect(user=USER, passwd=PASSWORD, db=DATABASE, charset='utf8')
        if _cursor == None:
            _cursor = _db.cursor()
    open_lock.release()

def close_db():
    global _db, _cursor

    close_lock.acquire()
    if CACHE_SERVER.decr(key_DB_request) == 0:
        if _cursor != None:
            _cursor.close()
            _cursor = None
        if _db != None:
            _db.commit()
            _db.close()
            _db = None
    close_lock.release()

def force_close_db():
    global _db, _cursor

    CACHE_SERVER.set(key_DB_request, 0)

    if _cursor != None:
        _cursor.close()
        _cursor = None
    if _db != None:
        _db.commit()
        _db.close()
        _db = None

def query_key_value_builder(data_dict):
    key_q = '(' 
    value_tuple = ()

    for key in data_dict.keys():
        if data_dict[key] != None:
            key_q += '{}, '.format(key)
            value_tuple += (str(data_dict[key]), )

    key_q = key_q[:-2] + ')'

    query = '{} VALUES {};'.format(key_q, str(value_tuple))
    return query

def insert_into(table, data):
    query = "INSERT INTO {} {};".format(table, query_key_value_builder(data))
    _cursor.execute(query)

def query_key_values_builder(data_cols, data_dict_list):
    key_q = '(' 
    values_q = ""

    for key in data_cols:
        if key == 'id':
            continue
        key_q += '{}, '.format(key)

    for data_dict in data_dict_list:
        value_tuple = ()
        for key in data_cols:
            if key == 'id':
                continue
            if key in data_dict.keys():
                if data_dict[key] != None:
                    value_tuple += (str(data_dict[key]), )
                else:
                    value_tuple += ('', )
            else:
                value_tuple += ('', )

        values_q += '{}, '.format(str(value_tuple))

    key_q = key_q[:-2] + ')'
    values_q = values_q[:-2]

    query = '{} VALUES {}'.format(key_q, values_q)
    return query

def insert_into_many(table, cols, data_list):
    query = "INSERT INTO {} {};".format(table, query_key_values_builder(cols, data_list))
    _cursor.execute(query)

# TODO for rows
def select_from(table, cond=None):
    query = 'SELECT * FROM {}'.format(table)
    if cond != None:
        query += ' WHERE {};'.format(cond)

    _cursor.execute(query)

    result = _cursor.fetchall()
    return result

def column_name(table):
    query = 'SELECT column_name FROM information_schema.columns\
            WHERE table_name = "{}" AND table_schema = "{}";'\
            .format(table, DATABASE)

    _cursor.execute(query)

    # in type of (('column1', ), ('column2', ), ...)
    columns = _cursor.fetchall()
    result = ()

    for col_tuple in columns:
        result += col_tuple

    return result

def next_id(table):
    query = 'SELECT auto_increment FROM information_schema.tables\
            WHERE table_name = "{}" AND table_schema = "{}";'\
            .format(table, DATABASE)

    _cursor.execute(query)

    return _cursor.fetchone()[0]

def reset_table(table):
    query = 'DELETE FROM {}; ALTER TABLE {} AUTO_INCREMENT=1;'.format(table, table)
    _cursor.execute(query)

def main():
    open_db()

    dummy_dict = {'textbody': 'lorem ipsum어저고 저쩌고', 'img_urls': 'http://a.a/a'}
    print(select_from(TABLE_ARTICLES))
    print(column_name(TABLE_HEADLINES))
    print(next_id(TABLE_ARTICLES))

    close_db()

if __name__ == '__main__':
    main()
