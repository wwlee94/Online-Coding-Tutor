#-*- coding:utf-8 -*-
# Linked List 예제

# use lists
x = None
for i in range(6, 0, -1):
  x = [i, x]

# use tuples
y = None
for i in range(6, 0, -1):
  y = (i, y)

z = None
for i in range(6, 0, -1):
    z = [i, z]

x[1][0]=y[1][1] # courtesy of John DeNero!
z[1][0]=y[1][1]
