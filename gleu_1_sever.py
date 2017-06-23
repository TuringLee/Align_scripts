# -*- coding:utf-8 -*-
# implementation of GLEU as defined in https://arxiv.org/abs/1609.08144
from __future__ import division
import os
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('-input_dir')
parser.add_argument('-output_dir')
parser.add_argument('-ids_file')
opt = parser.parse_args()

n_1_en = []
n_1_zh = []

def get_ngrams(s,maxn):
    ngrams = {}
    size = 0
    for n in range(1,maxn+1):
        for i in range(0,len(s)):
            for j in range(i+1,min(i+n+1,len(s)+1)):
                ngram = ''
                for word in s[i:j]:
                    ngram += word
                    ngram += ' '
                ngram = ngram.strip()
                if ngram not in ngrams:
                    ngrams[ngram] = 1
                    size += 1
    return size,ngrams

def get_gleu(orig,pred,n=4):
    orig_ = orig.split(' ')
    pred_ = pred.split(' ')
    n_orig,ngrams_orig = get_ngrams(orig_,n)
    n_pred,ngrams_pred = get_ngrams(pred_,n)
    count_match = 0
    for v in ngrams_orig:
        if v in ngrams_pred:
            count_match += 1
    return min(count_match/n_orig,count_match/n_pred)


def get_ids(dir_path):
    ids = []
    file_list = os.listdir(dir_path)
    for file in file_list:
        id = file.split('_')[0]
        if id not in ids:
            ids.append(id)
    return list(set(ids))

def get_input_path(id):
    input_orig_path = os.path.join(opt.input_dir,str(id)+'_resumed_zh.txt')
    input_pred_path = os.path.join(opt.input_dir,str(id)+'_resumed_pred.txt')
    input_en_path = os.path.join(opt.input_dir,str(id)+'_resumed_en.txt')

    return (input_orig_path,input_pred_path,input_en_path)

def get_output_path(id):
    output_orig_path = os.path.join(opt.output_path,str(id)+'_orig_en2zh.txt')
    output_pred_path = os.path.join(opt.output_path,str(id)+'_pred_en2zh.txt')

    return (output_orig_path,output_pred_path)

def get_paras(input_path):
    input_orig_path,input_pred_path,input_en_path = input_path
    content_orig = open(input_orig_path).read()
    content_pred = open(input_pred_path).read()
    content_en = open(input_en_path).read()
    paras_orig = content_orig.split('\n\n')
    paras_pred = content_pred.split('\n\n')
    paras_en = content_en.split('\n\n')

    return paras_orig,paras_pred,paras_en

def get_align_sents(lines_o,lines_p,lines_e):      #每个orig句子与各个pred句子计算gleu，取最大。
    lines_al_o = []
    lines_al_e = []
    for line_o in lines_o:
        max_gleu = 0
        t = lines_e[0]
        for line_p ,line_e in zip(lines_p,lines_e):
            cur_gleu = get_gleu(line_o,line_p)
            if cur_gleu > max_gleu:
                max_gleu = cur_gleu
                t = line_e
        lines_al_o.append(line_o)
        lines_al_e.append(t)

    return lines_al_o,lines_al_e

def get_align_sents_1(lines_o,lines_p,lines_e):    #每个pred句子与各个orig计算gleu，取最大。
    lines_al_o = []
    lines_al_e = []
    for line_p,line_e in zip(lines_p,lines_e):
        max_gleu = 0
        t = None
        for line_o in lines_o:
            cur_gleu = get_gleu(line_o,line_p)
            if cur_gleu > max_gleu:
                max_gleu = cur_gleu
                t = line_o
        if not t:
            continue 
        lines_al_o.append(t)
        lines_al_e.append(line_e)

    return lines_al_o,lines_al_e

def get_align_sents_2(lines_o,lines_p,lines_e):    #len(lines_o) > len(lines_p)
    lines_al_o = []
    lines_al_e = []
    flag = False
    for line_p,line_e in zip(lines_p,lines_e):
        max_gleu = 0
        t = None
        for i in range(len(lines_o)):                          #与每个单句计算
            line_o = lines_o[i]
            cur_gleu = get_gleu(line_o,line_p)
            if cur_gleu > max_gleu:
                max_gleu = cur_gleu
                t = line_o
        for i in range(len(lines_o)-1):                        #与两两合并计算
            line_o = lines_o[i]+' '+lines_o[i+1]
            cur_gleu = get_gleu(line_o,line_p)
            if cur_gleu > max_gleu:
                if flag == False:
                    flag = True
                max_gleu = cur_gleu
                t = line_o  
        for i in range(len(lines_o)-2):
            line_o = lines_o[i]+' '+lines_o[i+1]+' '+lines_o[i+2]   #与三三合并计算
            cur_gleu = get_gleu(line_o,line_p)
            if cur_gleu > max_gleu:
                if flag == False:
                    flag = True
                max_gleu = cur_gleu
                t = line_o
        if t and max_gleu > 0.03:
            lines_al_o.append(t)
            lines_al_e.append(line_e)
        if flag:
            n_1_en.append(line_e)
            n_1_zh.append(t)

    return lines_al_o,lines_al_e

def get_align_sents_3(lines_o,lines_p,lines_e):      #len(lines_p) > len(lines_o)
    lines_al_o = []
    lines_al_e = []
    flag = False
    for line_o in lines_o:
        max_gleu = 0
        t = None
        for i in range(len(lines_p)):
            line_p = lines_p[i]
            cur_gleu = get_gleu(line_o,line_p)
            if cur_gleu > max_gleu:
                max_gleu = cur_gleu
                t = lines_e[i]
        for i in range(len(lines_p)-1):
            line_p = lines_p[i] +' '+ lines_p[i+1]
            cur_gleu = get_gleu(line_o,line_p)
            if cur_gleu > max_gleu:
                if flag == False:
                    flag = True
                max_gleu = cur_gleu
                t = lines_e[i] +' '+ lines_e[i+1]
        for i in range(len(lines_p)-2):
            line_p = lines_p[i] +' '+ lines_p[i+1] +' '+ lines_p[i+2]
            cur_gleu = get_gleu(line_o,line_p)
            if cur_gleu > max_gleu:
                if flag == False:
                    flag = True
                max_gleu = cur_gleu
                t = lines_e[i] +' '+ lines_e[i+1] +' '+ lines_e[i+2]

        if t and max_gleu > 0.03:
            lines_al_o.append(line_o)
            lines_al_e.append(t)
        if flag:
            n_1_en.append(t)
            n_1_zh.append(line_o)

    return lines_al_o,lines_al_e

def save_sents(lines_o,lines_e):
    f = open(opt.output_dir+'/aligned_result.txt','a+')
    for line_o,line_e in zip(lines_o,lines_e):
        f.write(line_o)
        f.write('\n')
        f.write(line_e)
        f.write('\n\n')
    f.close()

def save_sents_1(id,lines_o,lines_e):
    f = open(opt.output_dir+'/'+str(id)+'_aligned.txt','a+')
    for line_o,line_e in zip(lines_o,lines_e):
        f.write(line_o)
        f.write('\n')
        f.write(line_e)
        f.write('\n\n')
    f.close()

def save_less_than_50(aligned_sents_less_than_50):
    try:
        with open(opt.output_dir+'/align_sents_less_than_50.txt', 'wb') as fp:
            for id in aligned_sents_less_than_50:
                fp.write(id)
                fp.write('\n')
    except IOError:
        print 'save miss error!'

def save_1_n_sents():
    try:
        with open(opt.output_dir+'/1_n.txt', 'wb') as fp:
            for sent_en,sent_zh in zip(n_1_en,n_1_zh):
                fp.write(sent_en)
                fp.write('\n')
                fp.write(sent_zh)
                fp.write('\n\n')
    except IOError:
        print 'save 1toN error!'



def main():
    miss_id = []
    aligned_sents_less_than_50 = []
    if opt.ids_file:
        ids = open(opt.ids_file).read()
        ids = ids.split('\n')[:-1]
    else:
        ids = get_ids(opt.input_dir)
    for id in ids:
        count_sents = 0
        count_aligned_sents = 0
        print id
        input_path = get_input_path(id)
        if not (os.path.exists(input_path[0]) and os.path.exists(input_path[1]) and os.path.exists(input_path[2])):
            miss_id.append(id)
            continue
        paras_orig,paras_pred,paras_en = get_paras(input_path)
        if not (len(paras_orig) == len(paras_pred) == len(paras_en)):
            continue
        for para_orig , para_pred ,para_en in zip(paras_orig,paras_pred,paras_en):
            lines_o = para_orig.split('\n')
            lines_p = para_pred.split('\n')
            lines_e = para_en.split('\n')
            count_sents += len(lines_o)
            if len(lines_o) == len(lines_p):
                print len(lines_p),'    ',len(lines_p)
                count_aligned_sents += len(lines_o)
                save_sents(lines_o,lines_e)  #存放到一个文件中
                #save_sents_1(id,lines_o,lines_e)
            elif len(lines_o) > len(lines_p):
                lines_al_o,lines_al_e = get_align_sents_2(lines_o,lines_p,lines_e)
                count_aligned_sents += len(lines_al_o)
                save_sents(lines_al_o,lines_al_e)   #存放到一个文件中
                print len(lines_o),'    ',len(lines_al_e)
                #save_sents_1(id,lines_al_o,lines_al_e)
            else:
                lines_al_o,lines_al_e = get_align_sents_3(lines_o,lines_p,lines_e)
                count_aligned_sents += len(lines_al_o)
                save_sents(lines_al_o,lines_al_e)   #存放到一个文件中
                print len(lines_o),'    ',len(lines_al_e)
                #save_sents_1(id,lines_al_o,lines_al_e)

        if count_sents == 0:
            continue
        if count_aligned_sents / count_sents <= 0.5:
            aligned_sents_less_than_50.append(id)

    f = open('miss_id.txt','w')
    for id_ in miss_id:
        f.write(id_)
        f.write('\n')
    f.close()           
    print "down"
    save_less_than_50(aligned_sents_less_than_50)
    save_1_n_sents()

if __name__ == '__main__':
    main()



