import MySQLdb
from interact_db import open_db, close_db, insert_into, query_key_value_builder, TABLE_SECTIONS, TABLE_WHOLE_ARTS

USER = 'root'
DATABASE = 'news_digest'
PASSWORD = '101341'

db = MySQLdb.connect(user=USER, passwd=PASSWORD, db=DATABASE, charset='utf8')
c = db.cursor()

cmd = 0

while cmd != -1:
    cmd = int(input("기능 입력(1:컨텐츠 섹션 추가, -1: 종료) "))
    enzyme = {}
    if cmd == -1:
        continue
    elif cmd == 1:
        enzyme['section_name'] = input("섹션 이름: ")
        enzyme['base_url'] = input("Base URL 주소: ")
        enzyme['links_body'] = input("기사 링크가 있는 위치: ")
        enzyme['title'] = input("글의 제목 위치: ")
        enzyme['article_body'] = input("글의 본문 위치: ")
        enzyme['written_date'] = input("글의 일시 위치: ")
        enzyme['journal'] = input("글의 신문사 위치: ")
        enzyme['image'] = input("글에 포함된 사진 태그: ")

    enzyme['section_name'] = '다음 정치'
    enzyme['base_url'] = 'http://media.daum.net/politics/'
    enzyme['links_body'] = 'mArticle'
    enzyme['title'] = 'tit_view'
    enzyme['article_body'] = 'news_view'
    enzyme['written_date'] = 'txt_info'
    enzyme['journal'] = 'link_cp'
    enzyme['image'] = 'origin_fig'
    
    print(enzyme)

    query = "INSERT INTO {} {};".format(TABLE_SECTIONS, query_key_value_builder(enzyme))
    c.execute(query)

c.close()
db.commit()
db.close()
