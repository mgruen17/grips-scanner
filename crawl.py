import sys
import requests
from tqdm import tqdm
from time import time
import os
from bs4 import BeautifulSoup

session = requests.Session()
invalid = '<>:"/\|?*'

def download_file(link, path, filename = None):
    URL_resource_get = link
    resource_result = session.get(URL_resource_get, stream=True)
    if filename == None:
        filename = resource_result.url.split('/')[-1].split('?')[0]

    for char in invalid:
        filename = filename.replace(char, '_')
    
    fullpath = path + '/' + filename.strip()

    print('Downloading "' + filename + '" to "' + path + '"')
    if 'content-length' not in resource_result.headers:
        total_size = 0
    else:
        total_size = int(resource_result.headers['content-length'])
    chunk_size = 1024
    with open(fullpath, "wb") as file:
        for data in tqdm(iterable=resource_result.iter_content(chunk_size=chunk_size), total = total_size/chunk_size, unit='KB'):
            file.write(data)
    print('complete')

if len(sys.argv) > 1:
    username = sys.argv[1]
    password = sys.argv[2]
else:
    print('You can specify username and password as arguments as well.')
    username=input('enter username:')
    password=input('enter password:')

URL_grips_login_get = 'https://elearning.uni-regensburg.de/login/index.php'
page_grips_login_get = session.get(URL_grips_login_get)
soup = BeautifulSoup(page_grips_login_get.text,'html.parser')
token = soup.find_all(attrs={'name':'logintoken'})[0]['value']

URL_grips_login_post = 'https://elearning.uni-regensburg.de/login/index.php'
files=dict(anchor='', logintoken=token, realm='hs', username=username, password=password)
data={'anchor':'', 'logintoken':token, 'realm':'hs', 'username':username, 'password':password}

page_grips_login_post = session.post(URL_grips_login_post, data=data)
soup = BeautifulSoup(page_grips_login_post.text,'html.parser')
print(f'\nGRIPS: logged in as {soup.select("span.usertext")[0].text}')

URL_vimp_login_get = 'https://vimp.oth-regensburg.de/login'
page_vimp_login_get = session.get(URL_vimp_login_get)
soup = BeautifulSoup(page_vimp_login_get.text,'html.parser')
token = soup.find_all(attrs={'name':'signin[_csrf_token]'})[0]['value']

URL_vimp_login_post = 'https://vimp.oth-regensburg.de/login'
files=dict(anchor='', logintoken=token, realm='hs', username=username, password=password)
data={'signin[username]': username, 'signin[password]': password, 'signin[position]': 'content', 'signin[_csrf_token]': token}
page_vimp_login_post = session.post(URL_vimp_login_post, data=data)
soup = BeautifulSoup(page_vimp_login_post.text,'html.parser')
print(f'VIMP: logged in as {soup.select(".linkToProfile a")[0].text}\n\n')

URL_dashboard_get = 'https://elearning.uni-regensburg.de/my'
page_dashboard_get = session.get(URL_dashboard_get)
soup = BeautifulSoup(page_dashboard_get.text,'html.parser')
courses = soup.select('li.qa-course')
course_i = 0
for course in courses:
    print(f'[{course_i}] {course.text}')
    course_i = course_i+1

course_chosen_index = input('choose course:')
course_chosen = courses[int(course_chosen_index)]
print(f'\ncrawling {course_chosen.text}')

timestamp = str(int(time()))
course_directory = course_chosen.text.strip()
for char in invalid:
	course_directory = course_directory.replace(char, '_')
path = 'Downloads/' + timestamp + '/' + course_directory
os.makedirs(path,mode = 0o777, exist_ok=True)

URL_course_get = course_chosen.contents[0]['href']
page_course_get = session.get(URL_course_get)
soup = BeautifulSoup(page_course_get.text,'html.parser')

# directly linked files
# resources = soup.select('li.activity.resource a')
# for resource in resources:
#     download_file(resource['href'], path)

# URLs
# all_urls = soup.select('li.activity.url a')

# for url in all_urls:
#     url.span.span.decompose()
#     print(url.text)
#     url_result = session.get(url['href'])
#     url_soup = BeautifulSoup(url_result.text,'html.parser')
#     final_url = url_soup.select('.urlworkaround a')[0]['href']

#     with open(path + '/URLs.txt', 'a') as url_txt_file:
#         url_txt_file.write(url.text + '\n' + final_url + '\n\n')

#     if final_url.startswith('https://vimp.oth-regensburg.de/'):
#         final_url_result = session.get(final_url)
#         final_url_soup = BeautifulSoup(final_url_result.text,'html.parser')
#         download_url = final_url_soup.select('meta[property="og:video:url"]')[0]['content']
#         download_file(download_url, path, url.text.strip() + '.' + download_url.split('.')[-1])

# grips pages
# VIDEOS ONLY
# TODO: save content as HTML and find and download media referenced in content
all_pages = soup.select('li.activity.page a')
for page in all_pages:
    page.span.span.decompose()
    page_result = session.get(page['href'])
    page_soup = BeautifulSoup(page_result.text, 'html.parser')
    key = page_soup.select('iframe')[0]['src'].split('key=')[-1].split('&')[0]
    download_url = f'https://vimp.oth-regensburg.de/getMedium/{key}.mp4'
    download_file(download_url, path, page.text)

# TODO: download folders
# TODO: download user-submitted files