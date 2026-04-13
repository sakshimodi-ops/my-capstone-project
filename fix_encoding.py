with open('data.json', 'rb') as f:
    content = f.read()

content = content.decode('latin-1')

with open('data.json', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')