import requests
from bs4 import BeautifulSoup

username=input('enter username:')
password=input('enter password:')

URL_login_get = 'https://elearning.uni-regensburg.de/login/index.php'
page_login_get = requests.get(URL_login_get)
soup = BeautifulSoup(page_login_get.text,'html.parser')
token = soup.find_all(attrs={'name':'logintoken'})[0]['value']

URL_login_post = 'https://elearning.uni-regensburg.de/login/index.php'
# URL_login_post = 'http://httpbin.org/post'
files=dict(anchor='', logintoken=token, realm='hs', username=username, password=password)
data={'anchor':'', 'logintoken':token, 'realm':'hs', 'username':username, 'password':password}
page_login_post = requests.post(URL_login_post, data=data)
soup = BeautifulSoup(page_login_post.text,'html.parser')
print(soup.findAll('span','usertext'))

URL_dashboard_get = 'https://elearning.uni-regensburg.de/my'
page_dashboard_get = requests.get(URL_dashboard_get,cookies=page_login_get.cookies)
soup = BeautifulSoup(page_login_post.text,'html.parser')
courses = soup.findAll('li','qa-course')
course_i = 0
for course in courses:
    print(f'[{course_i}] {course.text}')
    course_i = course_i+1