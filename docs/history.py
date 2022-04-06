from os import environ, remove
from sqlite3 import connect
from shutil import copyfile
from urllib.parse import urlparse

copyfile(environ['APPDATA'] + '/../Local/Google/Chrome/User Data/Default/History', 'history.db')
conn = connect('history.db')
cursor = conn.cursor()
cursor.execute("SELECT url FROM urls ORDER BY last_visit_time DESC")
urls = []
for url in cursor.fetchall():
	url = urlparse(url[0]).hostname
	if url not in urls and url and '.' in url:
		urls.append(url)
print('\n'.join(urls[:100]))
cursor.close()
conn.close()
remove('history.db')