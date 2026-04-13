import json
with open('data.json', 'r', encoding='utf-8-sig', errors='ignore') as f:
    data = json.load(f)
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print('Done!')	