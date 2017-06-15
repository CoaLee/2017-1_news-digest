from flask import jsonify, request, abort
from v0_3.interact_db import open_db, close_db, next_id, insert_into, select_from, column_name, TABLE_SECTIONS, TABLE_HEADLINES, TABLE_ARTICLES
import config
#import redis


'''
CACHE_SERVER = None 
if config.USING_CACHE is True:
    CACHE_SERVER = redis.Redis("localhost")
'''

def db_sections():
    open_db()
    
    section_col = column_name(TABLE_SECTIONS)
    section_tuples = select_from(TABLE_SECTIONS)

    sections = []

    for section_tuple in section_tuples:
        section = {}
        for col_name in section_col:
            section[col_name] = section_tuple[section_col.index(col_name)]
        sections.append(section)
    
    close_db()
    return kor_jsonify({'sections': sections})
'''
def db_sections():
    if CACHE_SERVER is None:
        return _db_sections()
    return "hah"
'''

def db_headlines(section_id):
    open_db()

    headline_col = column_name(TABLE_HEADLINES)
    headline_tuples = select_from(TABLE_HEADLINES, 'section_id="{}"'.format(section_id))

    headlines = []

    for headline_tuple in headline_tuples:
        headline = {}
        for col_name in headline_col:
            headline[col_name] = headline_tuple[headline_col.index(col_name)]
        if headline['written_date'] is not None:
            headline['written_date'] = headline['written_date'].strftime('%Y-%m-%d %H:%M')
        headlines.append(headline)

    close_db()

    if len(headlines) == 0:
        abort(404)

    # Pagination. api?page=[page no.]
    page = request.args.get('page')

    if page is not None:
        return kor_jsonify({'headlines': headlines[int(page)*20:(int(page)+1)*20],'page':int(page)+1})
    else:
        return kor_jsonify({'headlines': headlines})

def db_whole_articles():
    open_db()
    
    article_col = column_name(TABLE_ARTICLES)
    article_tuples = select_from(TABLE_ARTICLES)

    articles = []

    # ID querying
    id_list = request.args.getlist('id[]')

    # Entire articles
    if id_list == []:
        for article_tuple in article_tuples:
            article = {}
            for col_name in article_col:
                article[col_name] = article_tuple[article_col.index(col_name)]
            articles.append(content_join(article))
    # Articles of specific ids
    else:
        for article_tuple in article_tuples:
            article = {}
            if str(article_tuple[0]) in id_list:
                for col_name in article_col:
                    article[col_name] = article_tuple[article_col.index(col_name)]
                articles.append(content_join(article))

    close_db()
    
    return kor_jsonify({'articles': articles})

def db_article(article_id):
    open_db()

    article_col = column_name(TABLE_ARTICLES)
    article_tuple = select_from(TABLE_ARTICLES, 'id="{}"'.format(article_id))[0]

    article = {}
    for col_name in article_col:
        article[col_name] = article_tuple[article_col.index(col_name)]

    close_db()

    if len(article_tuple) == 0:
        abort(404)
    return kor_jsonify({'article': content_join(article)})

#TODO need to optimize & fix in case of img_pos at 0
def content_join(article_dict):
    res = { 
        'id': article_dict['id'],
        'journal': article_dict['journal'],
        'title': article_dict['title'],
        'written_date': article_dict['written_date'].strftime('%Y-%m-%d %H:%M')
    }   
    if article_dict['img_pos'] == '' :
        res['content'] = [{'type': 0, 'text': article_dict['textbody']}]
    else:
        img_pos_list = article_dict['img_pos'].split(' ')
        img_urls_list = article_dict['img_urls'].split('\n')
        img_pos_list.remove('')
        img_urls_list.remove('')
        text = article_dict['textbody']
        content = []
        i_prev = 0 
        cnt = 0 
        for i in img_pos_list:
            i_int = int(i)
            if i_prev != i_int:
                content.append({'type': 0, 'text': text[i_prev:i_int]})
            tmp_dict = {} 
            tmp_dict['type'] = 1
            tmp_idx = img_urls_list[cnt].find(' ')
            if tmp_idx != -1:
                tmp_dict['url'] = img_urls_list[cnt][:tmp_idx]
                tmp_dict['caption'] = img_urls_list[cnt][tmp_idx+1:]
            else:
                tmp_dict['url'] = img_urls_list[cnt]
            content.append(tmp_dict)
            i_prev = i_int
            cnt += 1
        content.append({'type': 0, 'text': text[i_int:]})
        res['content'] = content
    return res 

# to ensure unicode transmitted unbroken
def kor_jsonify(somedict):
    res = jsonify(somedict)
    res.headers['Content-Type'] += '; charset=utf-8'
    return res 

