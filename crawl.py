import sys
import requests
from bs4 import BeautifulSoup

session = requests.Session()

if len(sys.argv) > 1:
    username = sys.argv[1]
    password = sys.argv[2]
else:
    print('You can specify username and password as arguments as well.')
    username=input('enter username:')
    password=input('enter password:')

URL_login_get = 'https://elearning.uni-regensburg.de/login/index.php'
page_login_get = session.get(URL_login_get)
soup = BeautifulSoup(page_login_get.text,'html.parser')
token = soup.find_all(attrs={'name':'logintoken'})[0]['value']

URL_login_post = 'https://elearning.uni-regensburg.de/login/index.php'
files=dict(anchor='', logintoken=token, realm='hs', username=username, password=password)
data={'anchor':'', 'logintoken':token, 'realm':'hs', 'username':username, 'password':password}
page_login_post = session.post(URL_login_post, data=data)
soup = BeautifulSoup(page_login_post.text,'html.parser')
print(f'logged in as {soup.select("span.usertext")[0].text}\n\n')

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

URL_course_get = course_chosen.contents[0]['href']
print(URL_course_get)
page_dashboard_get = session.get(URL_course_get)
soup = BeautifulSoup(page_dashboard_get.text,'html.parser')
resources = soup.select('li.activity.resource a')
for resource in resources:
    print(resource['href'])