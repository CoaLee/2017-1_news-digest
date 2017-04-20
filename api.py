from flask import Flask, jsonify, abort, json, make_response
from dummy_db import sections, headlines, articles

app = Flask(__name__)

# to ensure unicode transmitted unbroken
app.config['JSON_AS_ASCII'] = False
def kor_jsonify(somedict):
    res = jsonify(somedict)
    res.headers['Content-Type'] += '; charset=utf-8'
    return res

@app.route('/news_digest/api/')
def version_notice():
    return "Latest API version is v0.1. Try '.../api/[version]'"

@app.route('/news_digest/api/v0.1/')
def usage_notice():
    return """\n
    <h2>Available request</h2>
    <p>GET '/news_digest/api/v0.1/sections'</p>
    <p>GET '/news_digest/api/v0.1/sections/[section_id]'</p>
    <p>GET '/news_digest/api/v0.1/sections/articles/[article_id]'</p>
    """

@app.route('/news_digest/api/v0.1/sections', methods=['GET'])
def get_sections():
    return kor_jsonify({'sections': sections})

@app.route('/news_digest/api/v0.1/sections/<int:section_id>', methods=['GET'])
def get_headlines(section_id):
    #TODO this part will be done by database query, not in python
    sec_headlines = [headline for headline in headlines if headline['section_id'] == section_id]
    if len(sec_headlines) == 0:
        abort(404)
    return kor_jsonify({'headlines': sec_headlines})

#TODO need to optimize & fix in case of img_pos at 0
def content_join(article_dict):
    res = {
        'id': article_dict['id'],
        'section_id': article_dict['section_id'],
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

@app.route('/news_digest/api/v0.1/sections/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    #TODO this part will be done by database query, not in python
    article = [article for article in articles if article['id'] == article_id]
    if len(article) == 0:
        abort(404)
    return kor_jsonify({'article': content_join(article[0])})

if __name__ == '__main__':
    app.run(debug=True)
