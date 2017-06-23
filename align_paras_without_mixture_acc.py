# -*- coding:utf-8 -*-
# implementation of GLEU as defined in https://arxiv.org/abs/1609.08144
from __future__ import division
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-input_dir')
parser.add_argument('-output_dir')
parser.add_argument('-ids_file')
opt = parser.parse_args()

miss_id = []
aligned_paras_less_than_50 = []

def get_ngrams(s,maxn=4):
    s = s.split(' ')
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

def get_gleu_1(orig,pred,n=4):
    orig_ = orig.split(' ')
    pred_ = pred.split(' ')
    n_orig,ngrams_orig = get_ngrams(orig_,n)
    n_pred,ngrams_pred = get_ngrams(pred_,n)
    count_match = 0
    for v in ngrams_orig:
        if v in ngrams_pred:
            count_match += 1
    return min(count_match/n_orig,count_match/n_pred)

def get_gleu_2(i,j,ngrams_orig,ngrams_pred,idx):
    print i,j,idx
    n_orig,ngrams_orig = ngrams_orig[i][idx]
    n_pred,ngrams_pred = ngrams_pred[j][idx]
    count_match = 0
    for v in ngrams_orig:
        if v in ngrams_pred:
            count_match += 1
    return min(count_match/n_orig,count_match/n_pred)

def get_ngrams_f_l_sent(paras):
    ngrams = []
    for i,para in enumerate(paras):
        sents = para.split('\n')
        ngrams.append([])
        ngrams[i].append(get_ngrams(sents[0]))
        ngrams[i].append(get_ngrams(sents[-1]))
    return ngrams

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
    if os.path.exists(input_orig_path) and os.path.exists(input_pred_path) and os.path.exists(input_en_path):
        return (input_orig_path,input_pred_path,input_en_path)
    else:
        miss_id.append(id)
        return None

def get_paras(input_path):
    input_orig_path,input_pred_path,input_en_path = input_path
    content_orig = open(input_orig_path).read()
    content_orig = content_orig.decode('utf8').encode('utf8')
    content_pred = open(input_pred_path).read()
    content_en = open(input_en_path).read()
    paras_orig = content_orig.split('\n\n')
    paras_pred = content_pred.split('\n\n')
    paras_en = content_en.split('\n\n')

    return paras_orig,paras_pred,paras_en

def get_aligned_paras(paras_orig,paras_pred,paras_en):
    alignd_paras_zh = []
    alignd_paras_en = []

    len_en = len(paras_en)
    len_pred = len(paras_pred)
    len_orig = len(paras_orig)
    if len_en != len_pred:
        return False

    for i in range(len_pred):
        max_gleu = 0
        t_o = None
        t_p = None
        for j in range(len_orig):
            for k in range(j-2,j+2):
                if k < 0:
                    continue
                elif k >= len(paras_orig):
                    break
                else:
                    gleu_f = get_gleu(paras_pred[0],paras_orig[0])
                    gleu_l = get_gleu(paras_pred[-1],paras_orig[-1])
                    if not (gleu_f +  gleu_l > 0.1):
                        continue
                    else:
                        if gleu_f + gleu_l > max_gleu:
                            max_gleu = gleu_f + gleu_l
                            t_o = j
                            t_p = i
        if t_o != None and t_p != None:
            alignd_paras_en.append(paras_en[t_p])
            alignd_paras_zh.append(paras_orig[t_o])
    if alignd_paras_zh and alignd_paras_en:
        return (alignd_paras_zh,alignd_paras_en)
    else:
        return False

def get_aligned_paras_1(id,paras_orig,paras_pred,paras_en,ngrams_orig,ngrams_pred):
    alignd_paras_zh = []
    alignd_paras_en = []
    alignd_paras_pred = [] 
    
    len_en = len(paras_en)
    len_pred = len(paras_pred)
    len_orig = len(paras_orig)
    
    if len_en != len_pred:
        return False

    for i in range(len_pred):
        max_gleu = 0
        t_o = None
        t_p = None
        for j in range(len_orig):
            para_pred = paras_pred[i].split('\n')
            para_orig = paras_orig[j].split('\n')
            gleu_f = get_gleu_2(j,i,ngrams_orig,ngrams_pred,0)
            gleu_l = get_gleu_2(j,i,ngrams_orig,ngrams_pred,-1)
            if not (gleu_f + gleu_l > 0.1):
                    continue
            else:
                if gleu_f + gleu_l > max_gleu:
                    max_gleu = gleu_f + gleu_l
                    t_o = j
                    t_p = i
        if t_o != None and t_p != None:
            alignd_paras_en.append(paras_en[t_p])
            alignd_paras_zh.append(paras_orig[t_o])
            alignd_paras_pred.append(paras_pred[t_p])
    if len(alignd_paras_zh) / len_orig <= 0.5:
        aligned_paras_less_than_50.append(id)
    if alignd_paras_zh and alignd_paras_en:
        return (alignd_paras_zh,alignd_paras_en,alignd_paras_pred)
    else:
        return False

def get_num_sent(paras):
    count = 0
    for para in paras:
        count += len(para.split('\n'))
    return count

def save_paras(id,paras_zh,paras_en,paras_pred):
    f_zh = open(opt.output_dir+'/'+str(id)+'_zh_.txt','w')
    f_en = open(opt.output_dir+'/'+str(id)+'_en_.txt','w')
    f_pred = open(opt.output_dir+'/'+str(id)+'_pred_.txt','w')
    for para_zh,para_en,para_pred in zip(paras_zh,paras_en,paras_pred):
        f_zh.write(para_zh)
        f_zh.write('\n\n')
        f_en.write(para_en)
        f_en.write('\n\n')
        f_pred.write(para_pred)
        f_pred.write('\n\n')
    f_zh.close()
    f_en.close()

def save_miss():
    try:
        with open(opt.output_path+'/miss_ids_align_paras.txt', 'wb') as fp:
            for id in miss_id:
                fp.write(id)
                fp.write('\n')
    except IOError:
        print 'save miss error!'

def save_less_than_50():
    try:
        with open(opt.output_dir+'/align_paras_less_than_50.txt', 'wb') as fp:
            for id in aligned_paras_less_than_50:
                fp.write(id)
                fp.write('\n')
    except IOError:
        print 'save miss error!'


def main():
    count = 0
    count_orig = 0
    if opt.ids_file :
        ids = open(opt.ids_file).read()
        ids = ids.split('\n')[:-1]
    else:
        ids = get_ids(opt.input_dir)
    
    for id in ids:
        print id
        l_align = 0
        input_path = get_input_path(id)
        if not input_path:
            continue
        paras_orig,paras_pred,paras_en = get_paras(input_path)
        count_orig += len(paras_orig)
        sents_orig = get_num_sent(paras_orig)
        sents_en = get_num_sent(paras_en)
        ngrams_orig = get_ngrams_f_l_sent(paras_orig)
        ngrams_pred = get_ngrams_f_l_sent(paras_pred)
        ret = get_aligned_paras_1(id,paras_orig,paras_pred,paras_en,ngrams_orig,ngrams_pred)
        if ret:
            #print id
            alignd_paras_zh,alignd_paras_en,alignd_paras_pred = ret
            count += len(alignd_paras_zh)
            sents_align = get_num_sent(alignd_paras_en)
            save_paras(id,alignd_paras_zh,alignd_paras_en,alignd_paras_pred)
            print id
            print "%-8d%-8d%-8d"%(len(paras_en),len(alignd_paras_en),len(paras_orig))
            print "%-8d%-8d%-8d"%(sents_en,sents_align,sents_orig)
        else:
            print id
            print "%-8d%-8s%-8d"%(len(paras_en),'0',len(paras_orig))
            print "%-8d%-8s%-8d"%(sents_en,'0',sents_orig)
    save_miss()
    save_less_than_50()
    print 'done'
    print count,'  ',count_orig

if __name__ == '__main__':
    main()






