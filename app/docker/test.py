import re
result = re.findall(r'\d', 'hello 123 world')
print("".join(result))
