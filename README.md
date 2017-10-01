# Align_scripts
align code...

作其他语言需要注意一下需对齐文件的名字，以及分段、分句后是否取[：-1]。

步骤：
对齐脚本

第一步（optional）：从数据库中取出数据并进行一定的预处理（比如，去除各种tag）。
get_article_sever_1.py

第二步：对其中缺失数据进行过滤，比如某个ID只有中文没有英文，丢掉。并去空行。
get_pretty_para.py

第三步：分句
test.rb

第四步：翻译加速步骤，将所有文章中的句子合并到一个大文件中并按长度排序。
translate_acc_1.py

第五步：翻译，需要相应的模型

第六步：恢复翻译前文章的格式，即将翻译后的整个文本按之前的文章ID分离。
translate_acc_2.py translate_acc_3.py 分别对应回复中文和英文

第七步：段落对齐
align_paras_without_mixture_acc.py

第七步：利用glue值来对齐，并存储。
align_paras_without_mixture_acc.py
