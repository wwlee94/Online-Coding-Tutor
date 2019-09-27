#-*- coding:utf-8 -*-
######################
#sys로 라인 정보 가져오기
######################
# import sys
# print dir(sys._getframe())
# print dir(sys._getframe().f_lineno)
# print sys._getframe().f_lineno
# print sys._getframe().f_lineno

import re
p = re.compile(".py[(]\d+[)]") #pdb current line 번호를 알기 위함
p_num = re.compile('\d+')
string =  "> /home/ubuntu/py_flask/pyfile/user_27.py(5)<module>()"

findall = p.findall(string)
print findall
out = p_num.search(findall[0])
print out.group()




