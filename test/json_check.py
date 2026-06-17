"Validating that a newly added token doesn't break the JSON format."


import json


def valid_len(s: str) -> int:
    "Get the length up to where a string is considered valid JSON."
    for i in range(1, len(s) + 1):
        try:
            json.loads(f'["{s[:i]}"]')
        except json.JSONDecodeError:
            try:
                json.loads(f'["{s[:i + 1]}"]')
                continue
            except (json.JSONDecodeError, IndexError):
                return i - 1
    return i


vocab = ('((Hello', ' World!', '))\\\\')
result = []
for t in vocab:
    result.append(t[:valid_len(t)])
print("".join(result))
