import sys
import requests
from tqdm import tqdm
from time import time
import os
from bs4 import BeautifulSoup

session = requests.Session()
invalid = '<>:"/\|?*'
username = ''
password = ''
path = ''

# download
def download_file(link, path, filename = None):
    URL_resource_get = link
    resource_result = session.get(URL_resource_get, stream=True)
    if filename == None:
        filename = resource_result.url.split('/')[-1].split('?')[0]

    for char in invalid:
        filename = filename.replace(char, '_')
    
    fullpath = path + '/' + filename.strip()

    if os.path.exists(fullpath):
        print('file exists. skipping...')
        return

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

# logins
def gripsLogin():
    URL_grips_login_get = 'https://elearning.uni-regensburg.de/login/index.php'
    page_grips_login_get = session.get(URL_grips_login_get)
    soup = BeautifulSoup(page_grips_login_get.text,'html.parser')
    if 'Sie sind angemeldet' in soup.text:
        print('GRIPS: already logged in')
        return
    token = soup.find_all(attrs={'name':'logintoken'})[0]['value']

    URL_grips_login_post = 'https://elearning.uni-regensburg.de/login/index.php'
    data={'anchor':'', 'logintoken':token, 'realm':'hs', 'username':username, 'password':password}
    page_grips_login_post = session.post(URL_grips_login_post, data=data)
    soup = BeautifulSoup(page_grips_login_post.text,'html.parser')
    print(f'\nGRIPS: logged in as {soup.select("span.usertext")[0].text}')

def vimpLogin():
    URL_vimp_login_get = 'https://vimp.oth-regensburg.de/login'
    page_vimp_login_get = session.get(URL_vimp_login_get)
    soup = BeautifulSoup(page_vimp_login_get.text,'html.parser')
    profileLink = soup.select(".linkToProfile a")
    if len(profileLink) > 0 and username == profileLink[0].text:
        print('VIMP: already logged in')
        return
    token = soup.find_all(attrs={'name':'signin[_csrf_token]'})[0]['value']

    URL_vimp_login_post = 'https://vimp.oth-regensburg.de/login'
    data={'signin[username]': username, 'signin[password]': password, 'signin[position]': 'content', 'signin[_csrf_token]': token}
    page_vimp_login_post = session.post(URL_vimp_login_post, data=data)
    soup = BeautifulSoup(page_vimp_login_post.text,'html.parser')
    print(f'VIMP: logged in as {soup.select(".linkToProfile a")[0].text}\n\n')

def login():
    gripsLogin()
    vimpLogin()
    
# process activity
def processActivity(activity):
    if any(x in activity['class'] for x in ['forum', 'label', 'assign', 'feedback']):
        return
    a_element = activity.select('a')[0]
    if a_element.span.span is not None:
        a_element.span.span.decompose()
    print(a_element.text)

    # directly linked files
    if 'resource' in activity['class']:
        print('resource')
        # return
        download_file(a_element['href'], path)

    # URLs
    elif 'url' in activity['class']:
        print('url')
        # return
        url_result = session.get(a_element['href'])
        url_soup = BeautifulSoup(url_result.text,'html.parser')
        final_url = url_soup.select('.urlworkaround a')[0]['href']

        with open(path + f'/URLs_{timestamp}.txt', 'a') as url_txt_file:
            url_txt_file.write(a_element.text + '\n' + final_url + '\n\n')

        if final_url.startswith('https://vimp.oth-regensburg.de/'):
            final_url_result = session.get(final_url)
            final_url_soup = BeautifulSoup(final_url_result.text,'html.parser')
            download_url = final_url_soup.select('meta[property="og:video:url"]')[0]['content']
            download_file(download_url, path, a_element.text.strip() + '.' + download_url.split('.')[-1])

    # grips pages
    # VIDEOS ONLY
    # TODO: save content as HTML and find and download media referenced in content
    elif 'page' in activity['class']:
        print('page')
        # return
        page_result = session.get(a_element['href'])
        page_soup = BeautifulSoup(page_result.text, 'html.parser')
        iframes = page_soup.select('iframe')
        if len(iframes) == 0:
            print('no video found -> skipping...')
            return
        key = iframes[0]['src'].split('key=')[-1].split('&')[0]
        download_url = f'https://vimp.oth-regensburg.de/getMedium/{key}.mp4'
        download_file(download_url, path, a_element.text)

    # grips file folders
    elif 'folder' in activity['class']:
        print('folder')
        # return
        folder_id = a_element['href'].split('id=')[-1].split('&')[0]
        download_url = f'https://elearning.uni-regensburg.de/mod/folder/download_folder.php?id={folder_id}'
        download_file(download_url, path, a_element.text)

# read arguments
if len(sys.argv) > 1:
    username = sys.argv[1]
    password = sys.argv[2]
    path = sys.argv[3]
else:
    print('You can specify username and password as arguments as well.')
    username=input('enter username:')
    password=input('enter password:')

login()

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
# path = path + 'Downloads/' + timestamp + '/' + course_directory
path = path + 'Downloads/' + course_directory
os.makedirs(path,mode = 0o777, exist_ok=True)

URL_course_get = course_chosen.contents[0]['href']
page_course_get = session.get(URL_course_get)
soup = BeautifulSoup(page_course_get.text,'html.parser')

activities = soup.select('li.activity')
for activity in activities:
    retry = True
    retry_count = 0
    max_retry_count = 1
    while retry and retry_count <= max_retry_count:
        retry = False
        try:
            processActivity(activity)
        except Exception as e:
            retry = True
            retry_count = retry_count + 1
            if retry_count > max_retry_count:
                print(f'error:{repr(e)}\nprocessing next item...0')
            else:
                print(f'error:{repr(e)}\nretrying...')
                login()

# TODO: download user-submitted files