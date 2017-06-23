# -*- coding:utf-8 -*-
import os
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-input_dir')
parser.add_argument('-output_dir')
parser.add_argument('-handled_ids_file')
parser.add_argument('-ids_file')
opt = parser.parse_args()

pattern_all_s = re.compile('^[^a-zA-Z0-9\u4e00-\u9fa5\"“]*')

def get_handled_ids(handled_ids_file):
    ids = open(handled_ids_file).read()
    ids = ids.split('\n')
    ids = list(set(ids))

    return ids

def get_ids(input_dir,handled_ids_file):
    handled_ids = get_handled_ids(handled_ids_file)
    ids = []
    file_list = os.listdir(input_dir)
    for file in file_list:
        id = file.split('_')[0]
        if id not in handled_ids:
            ids.append(id)
    ids = list(set(ids))

    return ids

def is_valid_id(id):
    path_zh = opt.input_dir+'/'+str(id)+'_zh.txt'    
    path_en = opt.input_dir+'/'+str(id)+'_en.txt'
    if os.path.exists(path_zh) and os.path.exists(path_en):
        return True
    else:
        return False

def get_first_last_sent(id):
    first_last_sents = []
    path_en = opt.input_dir+'/'+str(id)+'_en.txt'
    content = open(path_en).read()
    paras = content.split('\n\n')[:-1]
    paras_ = []
    for para in paras:
        if not para:
            continue
        sents = []
        sents_ = para.split('\n')[:-1]
        
        for sent in sents_:
            if re.sub(pattern_all_s,'',sent):
                sents.append(re.sub(pattern_all_s,'',sent))

        if len(sents) < 3:
            for sent in sents:
                #print sent
                first_last_sents.append(sent)
        else:
            #print sents[0]
            #print sents[-1]
            first_last_sents.append(sents[0])
            first_last_sents.append(sents[-1])
        first_last_sents.append('\n')
        paras_.append(sents)
    return first_last_sents,paras_

def save_file(id,first_last_sents):
    save_path = opt.output_dir+'/'+str(id)+'_en_first_last_sents.txt'
    f = open(save_path,'a+')
    for sent in first_last_sents:
        f.write(sent)
        f.write('\n')
    f.close()

def save_file_(id,paras_):
    save_path = opt.output_dir+'/'+str(id)+'_en_.txt'
    f = open(save_path,'a+')
    for para in paras_:
        for sent in para:
            f.write(sent)
            f.write('\n')
        f.write('\n')
    f.close()


def main():
    if opt.ids_file:
        ids = open(opt.ids_file).read()
        ids = ids.split('\n')[:-1]
    else:
        ids = get_ids(opt.input_dir,opt.handled_ids_file)
        f_ids = open('ids_without_mixture.txt','a+')
        for id in ids:
            f_ids.write(id)
            f_ids.write('\n')
        f_ids.close()

    for i,id in enumerate(ids):
        if is_valid_id(id):
            first_last_sents,paras_ = get_first_last_sent(id)
            save_file(id,first_last_sents)
            save_file_(id,paras_)
        if i % 100 == 0 :
            print str(i) + ' files has been handle'

if __name__ == '__main__':
    main()
