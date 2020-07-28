#!/usr/local/bin/python3

import MySQLdb
import cgi, json, jsonpickle
from item import *
from guide import *
from utils import load_data
from collections import namedtuple
from config import *

form = cgi.FieldStorage(environ={'REQUEST_METHOD':'POST'})
vals = {}
for key in form.keys():
    vals[ key ] = form[ key ].value

item_types = [('Primary Weapon', 'weapon1', weapon_and_offhand_types), ('Shield/Other Weapon', 'weapon2', weapon_and_offhand_types), ('Off-hand Weapon', 'weapon3', weapon_and_offhand_types), ('Off-hand shield/Other Weapon', 'weapon4', weapon_and_offhand_types), ('Helm', 'helm', helm_types), ('Body armor', 'bodyarmor', body_armor_types), ('Belt', 'belt', belt_types), ('Gloves', 'gloves', glove_types), ('Boots', 'boots', boot_types), ('Amulet', 'amulet', amulet_types), ('Ring 1', 'ring1', ring_types), ('Ring 2', 'ring2', ring_types), ('Mercenary Weapon', 'mercweap', weapon_and_offhand_types), ('Mercenary Helm', 'merchelm', helm_types)]
#, ('Charms', 'charms', charm_types)

cur_charm = 0
while 'charm_charm_{0}'.format(cur_charm) in vals or 'attribute_charm_charm_{0}'.format(cur_charm) in vals:
    item_types.append(('Charms', 'charm_charm_{0}'.format(cur_charm), charm_types))
    cur_charm += 1

items, sets, attributes = load_data()

gear_pieces = []
for typename, typeid, typelist in item_types:
    gear_name = None
    custom_atts = [] # TODO - fix bug here, should be dict type with attr as key.(?)
    ethereal = False
    runeword_base = None
    desc = ""
    qty = 1
    
    if typeid in vals:
        gear_name = vals[typeid]
    else:
        #assert 'custom_item_{0}'.format(typeid) in vals
        # dealing with a custom item, parse its attributes with names: attribute_typeid_# // attribute_typeid_#_val
        cur_att = 0
        
        while 'attribute_{0}_{1}'.format(typeid, cur_att) in vals:
            att_name = vals['attribute_{0}_{1}'.format(typeid, cur_att)]
            att_val = vals['attribute_{0}_{1}_val'.format(typeid, cur_att)]
            if 'attribute_{0}_{1}_qty'.format(typeid, cur_att) in vals:
                qty = vals['attribute_{0}_{1}_qty'.format(typeid, cur_att)]
            
            # now match the att. name...
            for attr in attributes:
                if attr.name == att_name:
                    custom_atts.append(Attribute(attr.name, {'v': att_val}, att_val))
                    break
            cur_att += 1
        
        if 'attribute_{0}'.format(typeid) in vals:
            att_name = vals['attribute_{0}'.format(typeid)]
            att_val = vals['attribute_{0}_val'.format(typeid)]
            if 'attribute_{0}_qty'.format(typeid) in vals:
                qty = vals['attribute_{0}_qty'.format(typeid)]
            
            # now match the att. name...
            for attr in attributes:
                if attr.name == att_name:
                    custom_atts.append(Attribute(attr.name, {'v': att_val}, att_val))
                    break
            cur_att += 1
    
    sockets = []
    custom_socket_atts = []
    
    cur_soc = 0
    while 'sockets_{0}_{1}'.format(typeid, cur_soc) in vals:
        sockets.append(vals['sockets_{0}_{1}'.format(typeid, cur_soc)])
        cur_soc += 1
    
    cur_soc = 0
    while 'attribute_sockets_{0}_{1}'.format(typeid, cur_soc) in vals:
        att_name = vals['attribute_sockets_{0}_{1}'.format(typeid, cur_soc)]
        att_val = vals['attribute_sockets_{0}_{1}_val'.format(typeid, cur_soc)]
        
        # now match the att. name...
        for attr in attributes:
            if attr.name == att_name:
                custom_socket_atts.append(Attribute(attr.name, {'v': att_val}, att_val))
                break
        cur_soc += 1
    
    if 'ethereal_{0}'.format(typeid) in vals:
        ethereal = vals['ethereal_{0}'.format(typeid)]
    
    if 'runeword_base_{0}_field'.format(typeid) in vals:
        runeword_base = vals['runeword_base_{0}_field'.format(typeid)]
    
    if 'desc_{0}'.format(typeid) in vals:
        desc = vals['desc_{0}'.format(typeid)]
    
    gear_pieces.append(GearPiece(typename, typeid, gear_name, custom_atts, sockets, custom_socket_atts, ethereal, runeword_base, desc, qty))

guide = GearGuide(vals['name'], vals['author'], vals['link'] if 'link' in vals else '', vals['classname'], gear_pieces)
guide_json = jsonpickle.encode(guide)

db = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DBNAME)
cur = db.cursor()

cur.execute("INSERT INTO guides (data) VALUES (%s)", (guide_json,))

db.commit()
db.close()

print("Content-type:text/html\r\n\r\n")
print("<html><head>\
         <title>Gear Guide Creation</title>\
         <link rel='stylesheet' type='text/css' media='screen' href='/d2/css/style.css' />\
         <meta http-equiv='refresh' content='2;url=http://localhost/d2/' />\
       </head><body>")
print("<div id='container'>\n\
          <div id='headerContainer'>\n\
            <p id='headerText'><a href='/d2/index.html'>weizor's grimoire</a></p>\n\
          </div>\n\
          <div id='contentContainer'>\n\
            <h2>Guide saved successfully. Redirecting in 2 seconds.</h2>\n\
          </div>\n\
       </div>\n")
print("</body></html>")