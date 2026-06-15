import json

vocab = ('Hello', ' World!', '\\')
result = []
for t in vocab:
    print("".join(result))
    result.append(t)
    try:
        json.loads(f'{{"a":"{"".join(result)}"}}')
    except json.JSONDecodeError:
        result.pop()
        result.append('[END]')
print("".join(result))
