import os
import sys
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup

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
    try:
        # set chrome options
        options = Options()
        options.add_argument("--headless")  # headless
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
        
        # initialize WebDriver
        driver = webdriver.Chrome(options=options)

        # access target url
        driver.get(url)

        # wait for page loading
        driver.implicitly_wait(5)

        # get html content
        html_content = driver.page_source

        # use BeautifulSoup to parse html content
        soup = BeautifulSoup(html_content, 'lxml')

        # get json data
        content = soup.find('pre').text

        # close WebDriver
        driver.quit()
        return content

    except WebDriverException as e:
        print(f"WebDriver Error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

raw_data = []

# generate folder :yyyy-mm-dd
parent_folder = time.strftime("%Y-%m", time.localtime())
if not os.path.exists(parent_folder):
    os.mkdir(parent_folder)

folder = parent_folder + '/' + time.strftime("%Y-%m-%d", time.localtime())
if not os.path.exists(folder):
    os.mkdir(folder)

content = f"""
# Today's Trending - {folder}\n
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
    print(f"get {target}")
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

# update README.md
content = \
"""# gpts-trending
Record everyday Top GPTs in ChatGPT GPTs Store\n""" \
     + content

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)
