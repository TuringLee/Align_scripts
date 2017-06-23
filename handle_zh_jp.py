# -*- coding:utf-8 -*-

import os
import re

pattern_dot_zh = re.compile(u'[．\.]')
pattern_dot_jp = re.compile(u'[．\.]')
pattern_jp_s = re.compile(u'^[^a-zA-Z0-9０-９\'\u0800-\u9fa5\uac00-\ud7ff]*')
pattern_zh_s = re.compile(u'^[^0-9\u4e00-\u9fa5‘]*')
pattern_quot_zh = re.compile(u'[“”]')
pattern_quot_jp = re.compile(u'[「」]')
pattern_url = re.compile(u'')

input_path = '/raid/ltj/ZH_JP/zh_jp'
output_path = '/raid/ltj/ZH_JP/zh_jp_'
file_list = os.listdir(input_path)

for file in file_list:
    save_paras = []
    if file.split('_')[-1] == 'zh.txt':
        f_path = input_path +'/'+ file
        content = open(f_path).read()
        content = re.sub(pattern_dot_zh,u'@$',content.decode('utf8'))
        content = re.sub(pattern_quot_zh,u'',content)
        paras = content.split('\n')[:-1]
        if '@' in paras[-1]:
            paras = paras[:-1] 
        for para in paras:
            para_ = re.sub(pattern_zh_s,u'',para)
            save_paras.append(para_)
    elif file.split('_')[-1] == 'jp.txt':
        f_path = input_path +'/'+ file
        content = open(f_path).read()
        content = re.sub(pattern_dot_jp,u'@$',content.decode('utf8'))
        content = re.sub(pattern_quot_jp,u'',content)
        paras = content.split('\n')[:-1]
        if '@' in paras[-1]:
            paras = paras[:-1] 
        for para in paras:
            para_ = re.sub(pattern_jp_s,u'',para)
            save_paras.append(para_)
    f = open(output_path+'/'+file,'w')
    for para in save_paras:
        f.write(para.encode('utf8'))
        f.write('\n')
    f.close()

    

