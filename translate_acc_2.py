# -*- coding:utf-8 -*-

import os
import re
import pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-input_dir')
parser.add_argument('-output_dir')
opt = parser.parse_args()

#pred_sents = open(opt.input_dir + '/pred_en2zh.txt').read().split('\n')[:-1]
orig_sents = open(opt.input_dir + '/merged_pred.txt').read().split('\n')[:-1]
sorted_sents_index = open(opt.input_dir + '/sorted_sents_index.txt').read().split('\n')[:-1]

orig_resume_sents = [None]*len(sorted_sents_index)
pred_resume_sents = [None]*len(sorted_sents_index)

for o_sent,j in zip(orig_sents,sorted_sents_index):
    orig_resume_sents[int(j)] = o_sent
    #pred_resume_sents[j] = p_sent
f = open(opt.output_dir+'/resumed_merged_sents.txt','w')
for sent in orig_resume_sents:
	f.write(sent)
	f.write('\n')
f.close()

f = open(opt.input_dir+'/en_dict_of_densed_sent.txt')
EN_DICT = pickle.load(f)
f.close()
EN_DICT_ = sorted(EN_DICT.items(),key = lambda d : d[1],reverse = False)

pre_arti_id = EN_DICT_[0][0][0]
pre_para_id = EN_DICT_[0][0][1]
sents_list = []
for item in EN_DICT_:
    cur_arti_id = item[0][0]
    cur_para_id = item[0][1]
    print cur_arti_id
    if cur_arti_id  != pre_arti_id :
        f = open(opt.output_dir+'/'+str(pre_arti_id)+'_resumed_en.txt','w')
        f.writelines(sents_list)
        f.close()
        pre_arti_id = cur_arti_id
        pre_para_id = cur_para_id
        sents_list = []
        if orig_resume_sents[item[1]]:
            sents_list.append(orig_resume_sents[item[1]])
            sents_list.append('\n')
        else:
            continue
    else:
        if cur_para_id != pre_para_id :
            sents_list.append('\n')
            pre_para_id = cur_para_id
            if orig_resume_sents[item[1]]:
                sents_list.append(orig_resume_sents[item[1]])
                sents_list.append('\n')
                continue
        else:
            if orig_resume_sents[item[1]]:
                sents_list.append(orig_resume_sents[item[1]])
            else:
                continue
            sents_list.append('\n')

f = open(opt.output_dir+'/'+str(cur_arti_id)+'_resumed_en.txt','w')
f.writelines(sents_list)
f.close()












