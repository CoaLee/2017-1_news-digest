import MySQLdb

USER = 'root'
DATABASE = 'news_digest'
PASSWORD = '101341'

TABLE_SECTIONS = 'news_sections'
TABLE_HEADLINES = 'section_headlines'
TABLE_ARTICLES = 'articles'

_db = None
_cursor = None

def open_db():
    global _db, _cursor

    if _cursor != None or _db != None:
        close_db()

    _db = MySQLdb.connect(user=USER, passwd=PASSWORD, db=DATABASE, charset='utf8')
    _cursor = _db.cursor()

def close_db():
    global _db, _cursor

    if _cursor != None:
        _cursor.close()
        _cursor = None
    if _db != None:
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

    _db.commit()

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

def main():
    open_db()

    dummy_dict = {'textbody': 'lorem ipsum어저고 저쩌고', 'img_urls': 'http://a.a/a'}
    print(select_from(TABLE_ARTICLES))
    print(column_name(TABLE_HEADLINES))
    print(next_id(TABLE_ARTICLES))

    close_db()

if __name__ == '__main__':
    main()
