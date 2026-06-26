"Show off different JSON data types."


from pathlib import Path
import json


data = [1, 3, 3.0, "5", float('inf'), float('-inf'), float('nan')]
Path('data/output').mkdir(exist_ok=True)
with open("data/output/data_types.json", 'w') as f:
    json.dump(data, f, indent='\t')
