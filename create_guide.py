#!/usr/bin/env python

import cgi
from item import *
from items import load_data
from collections import namedtuple

form = cgi.FieldStorage()

vals = {}
for key in form.keys():
    assert key not in params
    vals[ key ] = form[ key ].value
return vals

item_types = [('Primary Weapon', 'weapon1', weapon_and_offhand_types), ('Shield/Other Weapon', 'weapon2', weapon_and_offhand_types), ('Off-hand Weapon', 'weapon3', weapon_and_offhand_types), ('Off-hand shield/Other Weapon', 'weapon4', weapon_and_offhand_types), ('Helm', 'helm', helm_types), ('Body armor', 'bodyarmor', body_armor_types), ('Belt', 'belt', belt_types), ('Gloves', 'gloves', glove_types), ('Boots', 'boots', boot_types), ('Amulet', 'amulet', amulet_types), ('Ring 1', 'ring1', ring_types), ('Ring 2', 'ring2', ring_types), ('Charms', 'charms', charm_types), ('Sockets', 'sockets', ['Socketable'])]

Socket = namedtuple('Socket', 'socket_name, custom_atts')
GearPiece = namedtuple('GearPiece', 'type shorttype gear_name custom_atts sockets ethereal desc')
GearGuide = namedtuple('GearGuide', 'name link class gear_pieces')

items, sets, attributes = load_data()

gear_pieces = []
for typename, typeid, typelist in item_types:
    gear_name = None
    custom_atts = []
    socket_name = None
    custom_socket_atts = []
    ethereal = False
    desc = ""
    
    if typeid in vals:
        gear_name = vals[typeid]
    else:
        assert 'custom_item_{0}'.format(typeid) in vals
        # dealing with a custom item, parse its attributes with names: attribute_typeid_# // attribute_typeid_#_val
        cur_att = 0
        
        while 'attribute_{0}_{1}'.format(typeid, cur_att) in vals:
            att_name = vals['attribute_{0}_{1}'.format(typeid, cur_att)]
            att_val = vals['attribute_{0}_{1}_val'.format(typeid, cur_att)]
            
            # now match the att. name...
            for attr in attributes:
                if attr.name == att_name:
                    custom_atts.append(Attribute(attr.name, [att_val], att_val))
                    break
    
    if 'ethereal_{0}'.format(typeid) in vals:
        ethereal = vals['ethereal_{0}'.format(typeid)]
    
    if 'desc_{0}'.format(typeid) in vals:
        desc = vals['desc_{0}'.format(typeid)]
    
    gear_pieces.append(GearPiece(typename, typeid, gear_name, custom_atts, socket_name, custom_socket_atts))

guide = GearGuide(vals['name'], vals['link'], vals['classname'], gear_pieces)

print("Content-type:text/html\r\n\r\n")
print("<html><head>\
         <title>Gear Guide Creation</title>\
         <link rel='stylesheet' type='text/css' media='screen' href='/d2/style.css' />\
       </head><body>")
print("<h2> Entered Text Content is {0}</h2>".format(form))
print("</body></html>")