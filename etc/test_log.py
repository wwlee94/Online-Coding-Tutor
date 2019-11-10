#-*- coding:utf-8 -*-
import re
# 정규식 테스트 1
# result = re.findall(r'\d', 'hello 123 world')
# print "".join(result)

# 정규식 테스트 2
reg = re.compile("^import\s(os|sys|subprocess)$") # os,sys 방지
print(reg.match("import sys"))
