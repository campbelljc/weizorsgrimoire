import MySQLdb
import os, dill, json, jsonpickle
from item import *
from data import *
from config import *

def load_data():
    if not os.path.exists("items.dll"):
        from get_items import get_items_from_summit
        items = get_items_from_summit()
        with open("items.dll", 'wb') as output:
            dill.dump(items, output, protocol=2)
    else:
        items = dill.load(open("items.dll", 'rb'))
    
    #print("Num items:", len(items))
    
    items = fill_in_tiers(items)
    sets, items = get_sets_from_items(items)
    attributes = get_global_attr_dict(items, sets)
    
    return items, sets, attributes

def load_guides():
    db = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DBNAME)
    cur = db.cursor()

    cur.execute("SELECT * FROM guides")
    
    guides = []
    for row in cur.fetchall():
        guide_json = row[1]
        guide = jsonpickle.decode(guide_json)
        guides.append(guide)
    
    db.close()
    
    return guides

def fix_ormus():
    ormus_str = ""
    sorc_skills = class_skills[-1][1]
    for skill_tree, skills in sorc_skills:
        for skill in skills:
            ormus_str += """
<TR>
<TD align=center>
<a name="twitchthroe"></a>
<font face="arial,helvetica" size=-1><span>
<img src="/diablo2exp/images/items/elite/ormusrobes.gif" width=56 height="78">
<center><font face="arial,helvetica" color=908858 size=-1><SPAN><b>Ormus' Robes</b></font></center>
<center>Dusk Shroud</center>
<br Clear=left>
</span></font>
</td>
<TD>
<font face="arial,helvetica" size=-1><SPAN>
Defense: <font color=4850B8>371-487</font> (varies) (Base Defense: 361-467)<BR>
Required Level: 75<BR>
Required Strength: 77<BR>
Durability: 20<BR>
<font color=4850B8>+10-20 Defense</font> (varies)<BR>
<font color=4850B8>20% Faster Cast Rate</font><BR>
<font color=4850B8>+10-15% To Cold Skill Damage</font> (varies)<BR>
<font color=4850B8>+10-15% To Fire Skill Damage</font> (varies)<BR>
<font color=4850B8>+10-15% To Lightning Skill Damage</font> (varies)<BR>
<font color=4850B8>+3 to {0} (Sorceress Only)</font>*<BR>
<font color=4850B8>Regenerate Mana 10-15%</font> (varies)<BR>
(Only Spawns In Patch 1.10 or later)
</font></td>
</TR>\n
""".format(skill.title())
    print(ormus_str)

class dotdict(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError
