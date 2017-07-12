from flask import jsonify, request, abort
from v0_4.interact_db import open_db, close_db, force_close_db, column_name, insert_into, select_from, section_col, headline_col, article_col, TABLE_SECTIONS, TABLE_WHOLE_ARTS
import config as CONFIG


def db_sections():
    open_db()
    
    section_tuples = select_from(TABLE_SECTIONS)

    sections = []

    for section_tuple in section_tuples:
        section = {}
        for col_name in section_col:
            section[col_name] = section_tuple[section_col.index(col_name)]
        sections.append(section)
    
    return kor_jsonify({'sections': sections})

def db_headlines(section_id):
    open_db()

    headline_tuples = select_from(TABLE_WHOLE_ARTS, 'section_id="{}"'.format(section_id))
    whole_col = column_name(TABLE_WHOLE_ARTS)

    headlines = []

    for headline_tuple in headline_tuples:
        headline = {}
        for col_name in headline_col:
            headline[col_name] = headline_tuple[whole_col.index(col_name)]
        if headline['written_date'] is not None:
            headline['written_date'] = headline['written_date'].strftime('%Y-%m-%d %H:%M')
        headlines.append(headline)


    if len(headlines) == 0:
        abort(404)

    # Pagination. api?page=[page no.]
    page = request.args.get('page')

    headlines.reverse()

    if page is not None:
        return kor_jsonify({'headlines': headlines[int(page)*20:(int(page)+1)*20],'page':int(page)+1})
    else:
        return kor_jsonify({'headlines': headlines})

def db_whole_articles():
    open_db()
    
    article_tuples = select_from(TABLE_WHOLE_ARTS)
    whole_col = column_name(TABLE_WHOLE_ARTS)

    articles = []

    # ID querying
    id_list = request.args.getlist('id[]')

    # Entire articles
    if id_list == []:
        for article_tuple in article_tuples:
            article = {}
            for col_name in article_col:
                article[col_name] = article_tuple[whole_col.index(col_name)]
            articles.append(content_join(article))
    # Articles of specific ids
    else:
        for article_tuple in article_tuples:
            article = {}
            if str(article_tuple[0]) in id_list:
                for col_name in article_col:
                    article[col_name] = article_tuple[whole_col.index(col_name)]
                articles.append(content_join(article))

    articles.reverse()
    
    return kor_jsonify({'articles': articles})

def db_article(article_id):
    open_db()

    article_tuple = select_from(TABLE_WHOLE_ARTS, 'id="{}"'.format(article_id))[0]
    whole_col = column_name(TABLE_WHOLE_ARTS)

    article = {}
    for col_name in article_col:
        article[col_name] = article_tuple[whole_col.index(col_name)]

    if len(article_tuple) == 0:
        abort(404)
    return kor_jsonify({'article': content_join(article)})

def db_force_close():
    force_close_db()

def content_join(article_dict):
    res = { 
        'id': article_dict['id'],
        'journal': article_dict['journal'],
        'title': article_dict['title'],
    }   
    if article_dict['written_date'] is not None:
        res['written_date'] = article_dict['written_date'].strftime('%Y-%m-%d %H:%M')
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

