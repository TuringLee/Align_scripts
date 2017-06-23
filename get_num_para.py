# -*- coding:utf-8 -*-
import os
import re
import langid
import argparse

miss_ids = []

parser = argparse.ArgumentParser()
parser.add_argument('input_file_path')
parser.add_argument('output_file_path')
args = parser.parse_args()
FILE_DIR = args.input_file_path
SAVE_DIR = args.output_file_path
'''
FILE_DIR = '/Users/lee/Documents/YEEYAN/parser_result'
SAVE_DIR = '/Users/lee/Documents/YEEYAN/pretty_para'
'''
pattern_blankline = re.compile('\s\s+')

def lang_det(file_path):
    f = open(file_path)
    content = f.read()
    f.close()
    lang_id = langid.classify(content)
    
    return lang_id[0]

def remove_bline(file_path):
    t = []
    f = open(file_path)
    lines = f.readlines()
    f.close()
    for line in lines:
        line = re.sub(pattern_blankline,' ',line)
        if line.decode('utf8').strip():
            t.append(line.decode('utf8').strip().encode('utf8')+'\n')
    
    return t

def save_miss():
    try:
        with open(SAVE_DIR+'/miss_step_2.txt', 'wb') as fp:
            for id in miss_ids:
                fp.write(id)
                fp.write('\n')
    except IOError:
        print 'save miss error!'

if __name__ == '__main__':

    ids = []

    file_list = os.listdir(FILE_DIR)

    for file in file_list:
        id = file.split('_')[0]
        if id in ids:
            continue
        ids.append(id)
    
    ids = list(set(ids))

    for i,id in enumerate(ids):

        file_path_zh = os.path.join(FILE_DIR,str(id)+'_zh.txt')
        file_path_en = os.path.join(FILE_DIR,str(id)+'_en.txt')

        if not ( os.path.exists(file_path_zh) and os.path.exists(file_path_en) ):
            miss_ids.append(id)
            continue

        if lang_det(file_path_zh) != 'zh' or lang_det(file_path_en) != 'en':
            miss_ids.append(id)
            continue

        t_zh = remove_bline(file_path_zh)
        t_en = remove_bline(file_path_en)

        save_path_zh = os.path.join(SAVE_DIR,str(id)+'_zh.txt')
        save_path_en = os.path.join(SAVE_DIR,str(id)+'_en.txt')

        f_zh = open(save_path_zh,'a+')
        f_en = open(save_path_en,'a+')

        f_zh.writelines(t_zh)
        f_en.writelines(t_en)

        f_zh.close()
        f_en.close()

        if i % 100 == 0:
            print str(i)+' files has been pretteied!'

    save_miss()
    print "Done"

    



