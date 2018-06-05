# Weizor's Grimoire
A cool looking Diablo 2 item info site. You can access a (live version here)[http://campbelljc.com/d2/index.html].

### Requirements
* Python3
* pip3 install --user requests lxml dill cgi json jsonpickle MySQL-python
* MySQL (for gear guides database)

### How to build
* Create config.py and define DBHOST, DBUSER, DBPASSWORD and DBNAME.
* Edit items.py lines 10-13 (follow the comments).
* python3 items.py

Site will be created within 'html' directory.
Builds will go faster after the first time when the items cache is created.
