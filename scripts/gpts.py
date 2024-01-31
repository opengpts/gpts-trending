import os
import json
import time
import requests


targets = ['https://chat.openai.com/public-api/gizmos/discovery/trending',
'https://chat.openai.com/public-api/gizmos/discovery/research',
'https://chat.openai.com/public-api/gizmos/discovery/dalle',
'https://chat.openai.com/public-api/gizmos/discovery/writing',
'https://chat.openai.com/public-api/gizmos/discovery/productivity',
'https://chat.openai.com/public-api/gizmos/discovery/programming',
'https://chat.openai.com/public-api/gizmos/discovery/education',
'https://chat.openai.com/public-api/gizmos/discovery/lifestyle']

title_desc = {"Top Picks": "Most popular GPTs by GPT Store community",
"Research & Analysis": "Find, evaluate, interpret, and visualize information",
"DALL·E": "Transform your ideas into amazing images",
"Writing": "Enhance your writing with tools for creation, editing, and style refinement",
"Productivity": "Increase your efficiency",
"Programming": "Write code, debug, test, and learn",
"Education": "Explore new ideas, revisit existing skills",
"Lifestyle": "Get tips on travel, workouts, style, food, and more"}

featured = r"https://chat.openai.com/public-api/gizmos/discovery"

def get_trending_data(url):
    time.sleep(5)
    params = {
        'cursor': '0',
        'limit': '10',
        'locale': 'global'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.text
    else:
        return None

raw_data = []

content = """
# Today's Trending\n
- [Featured](#featured)
- [Top Picks](#top-picks)
- [Research \& Analysis](#research--analysis)
- [DALL·E](#dalle)
- [Writing](#writing)
- [Productivity](#productivity)
- [Programming](#programming)
- [Education](#education)
- [Lifestyle](#lifestyle)\n\n
"""

# generate folder :yyyy-mm-dd
folder = time.strftime("%Y-%m-%d", time.localtime())
if not os.path.exists(folder):
    os.mkdir(folder)

# get featured data
data = get_trending_data(featured)

if data:
    json_data = json.loads(data)
    gpts = json_data['cuts'][0]
    # maintain raw data
    gpts['type'] = 'Featured'
    raw_data.append(gpts)

    # tranfsorm to markdown format
    content += '## Featured\n'
    content += '> Curated top picks from this week\n'
    for item in gpts['list']['items']:
        name = item['resource']['gizmo']['display']['name']
        url = f"https://chat.openai.com/g/{item['resource']['gizmo']['short_url']}" 
        description = item['resource']['gizmo']['display']['description']
        content += f'- [{name}]({url}) {description}\n'
    content += '\n'

for target in targets:
    time.sleep(10)
    data = get_trending_data(target)

    if not data:
        print(f"error in get {target}")
        continue 
    json_data = json.loads(data)
    gpt_type = json_data['info']['display_group']

    # maintain raw data
    json_data['type'] = gpt_type
    raw_data.append(json_data)

    # tranfsorm to markdown format
    content += '## ' + gpt_type + '\n'
    content += '> ' + title_desc[gpt_type] + '\n'
    for item in json_data['list']['items']:
        name = item['resource']['gizmo']['display']['name']
        url = f"https://chat.openai.com/g/{item['resource']['gizmo']['short_url']}" 
        description = item['resource']['gizmo']['display']['description']
        content += f'- [{name}]({url}) {description}\n'
    content += '\n'

# save markdown file
with open(folder + '/README.md', 'w', encoding='utf-8') as f:
    f.write(content)
    

# save raw data
with open(folder + '/raw_data.json', 'w', encoding='utf-8') as f:
    json.dump(raw_data, f, ensure_ascii=False, indent=4)
