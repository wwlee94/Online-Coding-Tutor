# -*- coding:utf-8 -*-
# 함수 호출, 링크 전환 기본예제
def func(a,b,c):
    return a+b+c
# 메인함수
if __name__ == '__main__':
    result = func(10,20,30)
    array = [100, 200, 300, 400]
    x = array
    z = func
    func = array
    print(result)
    print(array)
    print(z(1,2,3))
