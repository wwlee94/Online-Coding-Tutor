#-*- coding:utf-8 -*-
# 리스트 선언 및 추가, 함수 선언 및 호출
x = [1, 2, 3]
y = [4, 5, 6]
z = y
y = x
x = z

x = [1, 2, 3] # a different [1, 2, 3] list!
y = x
x.append(4)
y.append(5)
z = [1, 2, 3, 4, 5] # a different list!
x.append(6)
y.append(7)
y = "hello"


def foo(lst):
    lst.append("hello")
    bar(lst)

def bar(myLst):
    print(myLst)

foo(x)
foo(z)
