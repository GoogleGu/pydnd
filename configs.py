import os

ROOT = os.path.abspath(os.sep.join(__file__.split(os.sep)[:-1]))
FILE_ROOT = os.path.join(ROOT, 'files')
BESTIARY_FILE_ROOT = os.path.join(FILE_ROOT, 'bestiary')
INBOX_FILE_ROOT = os.path.join(FILE_ROOT, 'inbox')

class DevMysql:
    user_name = 'root'
    password = '8g9g4qvj'
    host = 'localhost'
    port = '3306'
    database = 'dnd'

TIMEOUT = 10
BESTIARY_INDEX = "http://www.goddessfantasy.net/bbs/index.php?topic=56571.0"
