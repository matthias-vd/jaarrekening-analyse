import os
import sys

sys.path.insert(0, '/var/www/html')
sys.path.insert(0, '/var/www/html/web')

os.chdir('/var/www/html/web')

from app import app as application
