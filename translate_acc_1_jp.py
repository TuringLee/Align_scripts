# -*- coding:utf-8 -*-

import os
import re
import pickle
import numpy as np
import argparse
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

pattern_en_s = re.compile(u'^[^a-zA-Z0-9０-９\'\u0800-\u9fa5\uac00-\ud7ff]*')
pattern_zh_s = re.compile(u'^[^0-9\u4e00-\u9fa5‘]*')
pattern_dot = re.compile(u'@\$')

parser = argparse.ArgumentParser()
parser.add_argument('-input_dir')
parser.add_argument('-output_dir')
parser.add_argument('-ids_file')
opt = parser.parse_args()

miss_id = []

def get_ids():
    if opt.ids_file:
        ids = open(opt.ids_file).read().split('\n')[:-1]
    else:
        ids = []
        file_list = os.listdir(opt.input_dir)
        for file in file_list:
            id = file.split('_')[0]
            if id not in ids:
                ids.append(id)
        ids = list(set(ids))

    return ids

def get_input_path(id):
    en_path = os.path.join(opt.input_dir,str(id)+'_jp.txt')
    zh_path = os.path.join(opt.input_dir,str(id)+'_zh.txt')
    if os.path.exists(en_path) and os.path.exists(zh_path):
        return (en_path,zh_path)
    else:
        miss_id.append(id)
        return None

def get_paras(file_path,type = 'en'):
    content = open(file_path).read()
    content = unicode(content)
    content = re.sub(pattern_dot,u'.',content)
    paras = content.split('\n\n')[:-1]
    return paras

def main():
    EN_DICT = {}
    ZH_DICT = {}
    ids = get_ids()
    en_all_sents = []
    zh_all_sents = []
    en_sent_length = []
    for i_,id in enumerate(ids):
        ret = get_input_path(id)
        if not ret:
            continue
        en_path,zh_path = ret

        en_paras = get_paras(en_path)
        for i,para in enumerate(en_paras):
            sents = para.split('\n')[:-1]
            for j in range(len(sents)):
                tmp = re.sub(pattern_en_s,u'',sents[j])
                if not tmp:
                    continue
                EN_DICT[(id,i,j)] = len(en_all_sents)
                en_all_sents.append(tmp.encode('utf8'))
        
        zh_paras = get_paras(zh_path,'zh')
        for i,para in enumerate(zh_paras):
            sents = para.split('\n')[:-1]
            for j in range(len(sents)):
                tmp = re.sub(pattern_zh_s,u'',sents[j])
                if not tmp:
                    continue
                ZH_DICT[(id,i,j)] = len(zh_all_sents)
                zh_all_sents.append(tmp.encode('utf8'))

        if i_ % 100 == 0:
            print str(i_) + 'files has been handled'

    print 'step_1'
    print len(en_all_sents)
    for sent in en_all_sents:
        en_sent_length.append(len(sent))
        #en_all_sents_ = np.array(en_sent_length)
       
    en_sent_sorted_idx = sorted(range(len(en_sent_length)),key = lambda k:en_sent_length[k])
    f = open(opt.output_dir + '/sorted_sents.txt','w')
    print 'step_2'
    for k in en_sent_sorted_idx:
        f.write(en_all_sents[k])
        f.write('\n')
    f.close()
    print 'step_3'
    f = open(opt.output_dir + '/sorted_sents_index.txt','w')
    for k in en_sent_sorted_idx:
        f.write(str(k))
        f.write('\n')
    f.close()
    print 'step_4'
    f = open(opt.output_dir + '/densed_sents_en.txt','w')
    for sent in en_all_sents:
        f.write(sent)
        f.write('\n')
    f.close()
    
    f = open(opt.output_dir + '/en_dict_of_densed_sent.txt','w')
    pickle.dump(EN_DICT,f)
    f.close()
    f = open(opt.output_dir + '/zh_dict_of_densed_sent.txt','w')
    pickle.dump(ZH_DICT,f)
    f.close()
    '''
    #EN_DICT = sorted(EN_DICT.iteritems(),key = lambda d:d[1],reverse = False)
    f = open(opt.output_dir + '/en_dict_of_densed_sent.txt','w')
    for key_ in EN_DICT:
        f.write(str(key_))
        f.write(' : ')
        f.write(str(EN_DICT[key_]))
        f.write('\n')
    f.close()
    
    print 'step_5'
    f = open(opt.output_dir + '/zh_dict_of_densed_sent.txt','w')
    for key_ in ZH_DICT:
        f.write(str(key_))
        f.write(' : ')
        f.write(str(ZH_DICT[key_]))
        f.write('\n')
    f.close()
    '''
    
    print 'step_5'
    f = open(opt.output_dir + '/densed_sents_zh.txt','w')
    for sent in zh_all_sents:
        f.write(sent)
        f.write('\n')
    f.close()



if __name__ == '__main__':
    main()













