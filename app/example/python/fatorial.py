#-*- coding:utf-8 -*-
#  팩토리얼 예제 - 재귀함수 이용
def fact(n):
    if (n <= 1):
        return 1
    else:
        return n * fact(n - 1)

print(fact(6))
