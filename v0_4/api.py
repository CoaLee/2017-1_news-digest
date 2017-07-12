from flask import Flask, abort
from v0_4.db_process import db_sections, db_headlines, db_whole_articles, db_article, db_force_close

app = Flask(__name__)

# to ensure unicode transmitted unbroken
app.config['JSON_AS_ASCII'] = False

usage_string = """\n
    <h2>Available requests:</h2>
    <p>GET '[api_root]/sections'</p>
    <p>GET '[api_root]/sections/[section_id]'</p>
    <p>GET '[api_root]/sections/[section_id]?page=[page_num]'</p>
    <p>GET '[api_root]/articles'<p>
    <p>GET '[api_root]/articles?id[]=1&id[]=3&id[]=7...'<p>
    <p>GET '[api_root]/articles/[article_id]'</p>
    """ 

@app.route('/')
def usage_notice():
    return usage_string 

@app.errorhandler(404)
def error_notice(error):
    return """\n
    <h2>Invalid request.</h2>
    """ + usage_string

@app.route('/sections', methods=['GET'])
def get_sections():
    return db_sections()

@app.route('/sections/<int:section_id>', methods=['GET'])
def get_headlines(section_id):
    return db_headlines(section_id)

@app.route('/articles', methods=['GET'])
def get_whole_articles():
    return db_whole_articles() 

@app.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    return db_article(article_id)

@app.teardown_appcontext
def force_close(exception):
    db_force_close()

if __name__ == '__main__':
    app.run(debug=True)
