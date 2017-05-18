import MySQLdb

USER = 'root'
DATABASE = 'news_digest'
PASSWORD = '101341'

TABLE_SECTIONS = 'news_sections'
TABLE_HEADLINES = 'section_headlines'
TABLE_ARTICLES = 'articles'

def play_with_db(query, cb_func=None):
    db = MySQLdb.connect(user=USER, passwd=PASSWORD, db=DATABASE, charset='utf8')
    c = db.cursor()

    c.execute(query)
    if cb_func is not None :
        cb_func(c)
    else:
        db.commit()

    c.close()
    db.close()

def print_fetchall(cursor):
    print(cursor.fetchall())

def query_key_value_builder(data_dict):
    key_q = '('
    value_q = '('

    for key in data_dict.keys():
        key_q += '{}, '.format(key)
        value_q += '"{}", '.format(data_dict[key])

    key_q = key_q[:-2] + ')'
    value_q = value_q[:-2] + ')'

    query = "{} VALUES {}".format(key_q, value_q)
    return query

def insert_into(table, data):
    query = 'INSERT INTO {} {};'.format(table, query_key_value_builder(data))
    print(query)
    play_with_db(query)

def select_from(table, rows=0):
    query = 'SELECT * FROM {}'.format(table)
    play_with_db(query, print_fetchall)

def main():
    select_from(TABLE_SECTIONS)
    dummy_dict = {'textbody': 'lorem ipsum어저고 저쩌고', 'img_urls': 'http://a.a/a'}
    insert_into(TABLE_ARTICLES, dummy_dict)
    select_from(TABLE_ARTICLES)

if __name__ == '__main__':
    main()
