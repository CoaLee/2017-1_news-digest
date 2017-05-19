from flask import Flask, jsonify, abort, json, make_response
# from dummy_db import sections, headlines, articles
from interact_db import open_db, close_db, next_id, insert_into, select_from, column_name, TABLE_SECTIONS, TABLE_HEADLINES, TABLE_ARTICLES

app = Flask(__name__)

API_ADDRESS = '/news_digest/api/'
API_VERSION = 'v0.1'
CURRENT_API = API_ADDRESS + API_VERSION + '/' 

# to ensure unicode transmitted unbroken
app.config['JSON_AS_ASCII'] = False
def kor_jsonify(somedict):
    res = jsonify(somedict)
    res.headers['Content-Type'] += '; charset=utf-8'
    return res 

@app.route(API_ADDRESS)
def version_notice():
    return "Latest API version is {}. Try 'GET [root]{}'\n".format(API_VERSION, CURRENT_API)

@app.route(CURRENT_API)
def usage_notice():
    return """\n
    <h2>Available request</h2>
    <p>GET '{}sections'</p>
    <p>GET '{}sections/[section_id]'</p>
    <p>GET '{}sections/articles/[article_id]'</p>
    """.format(CURRENT_API, CURRENT_API, CURRENT_API)

@app.route(CURRENT_API+'sections', methods=['GET'])
def get_sections():
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

@app.route(CURRENT_API+'sections/<int:section_id>', methods=['GET'])
def get_headlines(section_id):
    #TODO this part will be done by database query, not in python
    open_db()

    headline_col = column_name(TABLE_HEADLINES)
    headline_tuples = select_from(TABLE_HEADLINES, 'section_id="{}"'.format(section_id))

    headlines = []

    for headline_tuple in headline_tuples:
        headline = {}
        for col_name in headline_col:
            headline[col_name] = headline_tuple[headline_col.index(col_name)]
        headlines.append(headline)

    close_db()

    if len(headlines) == 0:
        abort(404)

    return kor_jsonify({'headlines': headlines})

#TODO need to optimize & fix in case of img_pos at 0
def content_join(article_dict):
    res = { 
        'id': article_dict['id'],
        'author': article_dict['author'],
        'written_date': article_dict['written_date']
    }   
    if(article_dict['img_pos'] is None):
        res['content'] = article_dict['textbody']
    else:
        img_pos_list = article_dict['img_pos'].split(' ')
        img_urls_list = article_dict['img_urls'].split(' ')
        text = article_dict['textbody']
        content = []
        i_prev = 0 
        cnt = 0 
        for i in img_pos_list:
            i_int = int(i)
            content.append(text[i_prev:i_int])
            content.append(img_urls_list[cnt])
            i_prev = i_int
            cnt += 1
        content.append(text[i_int:])
        res['content'] = content
    return res 

@app.route(CURRENT_API+'sections/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    #TODO this part will be done by database query, not in python
    open_db()

    article_col = column_name(TABLE_ARTICLES)
    article_tuple = select_from(TABLE_ARTICLES, 'id="{}"'.format(article_id))[0]

    article = {}
    for col_name in article_col:
        article[col_name] = article_tuple[article_col.index(col_name)]
    #TODO need to implement author extraction
    article['author'] = 'Best Author in the World(need to fix)'

    close_db()

    if len(article_tuple) == 0:
        abort(404)
    return kor_jsonify({'article': content_join(article)})

if __name__ == '__main__':
    app.run(debug=True)

