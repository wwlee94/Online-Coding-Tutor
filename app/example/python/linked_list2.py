#-*- coding:utf-8 -*-
# Linked List 예제 2

myList = (1, (2, (3, (4, (5, None)))))

def sumList(node, subtotal):
    if not node:
        return subtotal
    else:
        return sumList(node[1], subtotal + node[0])
        
total = sumList(myList, 0)
