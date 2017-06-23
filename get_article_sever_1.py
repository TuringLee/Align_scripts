# -*- coding:utf-8 -*-

import os
import re
import MySQLdb
import cPickle as pickle
import HTMLParser
from bs4 import BeautifulSoup
import argparse
from MySQLdb import cursors

DB_USER = 'root'
DB_PASSWD = 'ltj123'
DB_NAME = 'YEEYAN'
TB_NAME = 'translations'

parser = argparse.ArgumentParser()
parser.add_argument('output_file_path')
args = parser.parse_args()
PARSED_SAVE_DIR = args.output_file_path

miss_trans_ids = []
miss_origi_ids = []

parser = HTMLParser.HTMLParser()

pattern_tags = re.compile(u'</?span.*?>|</?b>|</?strong>|</?font.*?>|</?em>|</?a.*?>|</?u>|</?i>|</?sup>|</?option>')
#pattern_space = re.compile(u'&nbsp;')
#pattern_newline = re.compile(u'\n|\r')
pattern_dash_1 = re.compile(u'--')
pattern_dash_2 = re.compile(u' - | -|- ')
pattern_dash_3 = re.compile(u'-')
pattern_special = re.compile(u'\u2028|\u0008|\u0009|\u000A|\u000B|\u000C|\u000D|\u0022|\u005C|\u00A0|\u2029|\uFEFF')
pattern_annotations = re.compile(u'\[.*?\]')
pattern_bra = re.compile(u'\(.*?\)|（.*?）|【.*?】')
pattern_quot = re.compile(u'"|“|”')
pattern_dot = re.compile(u'\.')
pattern_quop_hk = re.compile(u'[」』]')
pattern_quob_hk = re.compile(u'[「『]')
pattern_slash = re.compile(ur'\\')

def connect_db(user, passwd, db, host='localhost', port=3306):
    return MySQLdb.connect(
            host=host,
            user=user,
            passwd=passwd,
            db=db,
            port=port,
            cursorclass=cursors.SSCursor,
            charset='utf8')

def select_cursor(conn):
    cur = conn.cursor()
    # conn.cursor(cursors.SSCursor)
    cur.execute('select * from '+TB_NAME)
    return cur

def close_all(conn, cur):
    cur.close()
    conn.close()
    
def parse_row(row):
    article_id = row[0]
    translation_content = row[1]
    original_content = row[2]
    if len(translation_content) < 2:
        miss_trans_ids.append(article_id)
    elif len(original_content) < 2:
        miss_origi_ids.append(article_id)
    else:
        paras_zh = parse_html(translation_content,'zh')
        paras_en = parse_html(original_content)
        zh_path = os.path.join(PARSED_SAVE_DIR, str(article_id)+'_zh.txt')
        en_path = os.path.join(PARSED_SAVE_DIR, str(article_id)+'_en.txt')
        save_parse(zh_path, paras_zh, article_id)
        save_parse(en_path, paras_en, article_id)

def parse_row_1(row):                                #对数据库中缺少一域的单独处理
    article_id = row[0]
    translation_content = row[1]
    original_content = row[2]
    if len(translation_content) < 2 and len(original_content) > 2:
        paras_en = parse_html(original_content)
        en_path = os.path.join(PARSED_SAVE_DIR, str(article_id)+'_en.txt')
        save_parse(en_path, paras_en, article_id)
        re_handle_en.append(article_id)
    elif len(original_content) < 2 and len(translation_content) > 2:
        paras_zh = parse_html(translation_content,'zh')
        zh_path = os.path.join(PARSED_SAVE_DIR, str(article_id)+'_zh.txt')
        save_parse(zh_path, paras_zh, article_id)
        re_handle_zh.append(article_id)

def save_parse(path, paras, article_id):
    if os.path.exists(path):
        os.remove(path)
    try:
        with open(path, 'a+') as fw:
            fw.writelines(paras)
    except IOError:
        print 'open file {} error!'.format(article_id)


def parse_html(html,lang='en'):
    html = unicode(html)
    if lang == 'zh':
        html = re.sub(pattern_dot, u'@$', html)
    #html = re.sub(pattern_space, u'', html)
    html = decode_html_entities(html)
    html = re.sub(pattern_tags, u'', html)
    html = re.sub(pattern_special, u' ', html)
    html = re.sub(pattern_annotations, u'', html)
    html = re.sub(pattern_bra, u'', html)
    html = re.sub(pattern_quop_hk, u'“', html)
    html = re.sub(pattern_quob_hk, u'”', html)
    html = re.sub(pattern_quot, u'', html)
    html = re.sub(pattern_dash_1, u',', html)
    html = re.sub(pattern_dash_2,u' , ', html)
    html = re.sub(pattern_dash_3,u' ', html)
    html = re.sub(pattern_slash,u'',html)
    paras = get_paras(html)

    return paras

def decode_html_entities(text):
    return parser.unescape(text)

def get_paras(html):
    soup = BeautifulSoup(html)
    paras = soup.get_text('\n')
    paras = paras.encode('utf8')
    paras = paras.split('\n')
    t = []
    for para in paras:
        if para.strip():
            t.append(str(para.strip())+'\n')
    return t

def save_miss():
    try:
        with open(PARSED_SAVE_DIR+'/miss.pkl', 'wb') as fp:
            miss = {'miss_origi_ids': miss_origi_ids, 'miss_trans_ids': miss_trans_ids}
            pickle.dump(miss, fp, True)
    except IOError:
        print 'save miss error!'

# main field
if __name__ == '__main__':

    i = 1
    conn = connect_db(DB_USER, DB_PASSWD, DB_NAME)
    cur = select_cursor(conn)

    row = cur.fetchone()

    while row is not None:
        parse_row(row)
        row = cur.fetchone()
        i += 1

        if i % 100 == 0:
            print str(i)+' files has been parsered!'
    save_miss()
    close_all(conn, cur)
    print 'ALL DONE'