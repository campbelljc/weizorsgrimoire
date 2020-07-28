import re
from attribute import *
from collections import namedtuple, defaultdict

eth_attr_match = None

class Category(object):
    def __init__(self, name, quality):
        self.name = name
        self.quality = quality
    
    def __hash__(self):
        return hash((self.name))
    
    def __eq__(self, other):
        if isinstance(other, Category):
            return (self.name) == (other.name)
        return self.name == other
    
    def __repr__(self):
        return self.name

def get_cat_dict(items, cat_name):
    items_per_cat = defaultdict(list)
    for item in items:
        cat_obj = getattr(item, cat_name)
        if cat_obj is not None:
            if isinstance(cat_obj, list):
                for c_obj in cat_obj:
                    items_per_cat[c_obj].append(item)
            else:
                items_per_cat[cat_obj].append(item)
    for cat in items_per_cat:
        items_per_cat[cat].sort(key=lambda tup: tup.name)
    return items_per_cat

class Item(object):
    def __init__(self, name, imagepath, quality, tier, itype, stype, attr_dict):
        
        global eth_attr_match
        if eth_attr_match is None:
            for attr_match in attribute_matches:
                if attr_match.name == 'Ethereal':
                    eth_attr_match = attr_match
                    break
            assert eth_attr_match is not None
        
        self.name = name
        self.imagepath = imagepath
        self.quality = quality # "Unique"
        self.tier = Category(tier, 'tier') if len(tier) > 0 else None # "Elite"
        if isinstance(itype, list):
            self.type = [Category(t[:-1] if t[-1] == 's' else t, 'type') for t in itype]
        else:
            self.type = Category(itype[:-1] if itype[-1] == 's' else itype, 'type') if len(itype) > 0 else None # "Armor"
        self.stype = Category(stype, 'subtype') # "Balrog Skin"
        self.attr_dict = attr_dict
        
        self.num_possible_sockets = 0
        self.class_restriction = None
        self.spawns_ethereal = False
        self.can_spawn_ethereal = False
        self.ethereal = False
        self.eth_item = None
    
    def create_ethereal_version(self):
        assert self.can_spawn_ethereal
        #print("Creating ethereal version of", self.name, self.type, self.stype)
        new_item = Item(self.name + " (ethereal)", self.imagepath, self.quality, self.tier.name, self.type.name, self.stype.name, self.attr_dict.copy())
        new_item.ethereal = True
        new_item.update_info()
        
        for i, attr in enumerate(new_item.attr_dict):
            item_attr = new_item.attr_dict[attr]
            if attr.name == "Defense":
                values = item_attr.value_dict
                text = item_attr.text

                keys_to_update = ['r1', 'r2', 'r3', 'r4', 'base_min', 'base_max']
                for key in keys_to_update:
                    if key in values and values[key] is not None:
                        values[key] = str(int(int(values[key]) * 1.5))
                
                # TODO: Make this work with straight +Def attributes.
                if 'r3' in values and values['r3'] is not None:
                    text = "Defense: (" + values['r1'] + "-" + values['r2'] + ") - (" + values['r3'] + "-" + values['r4'] + ")"
                else:
                    text = "Defense: " + str(values['r1'])
                    if 'r2' in values and values['r2'] is not None:
                        text += "-" + str(values['r2'])
                
                if 'base_min' in values and values['base_min'] is not None:
                    text += " (Base Defense: " + str(values['base_min'])
                    if 'base_max' in values and values['base_max'] is not None:
                        text += "-" + str(values['base_max'])
                    text += ")"
            elif attr.name in ['Damage', 'Throw Damage', 'One-Hand Damage', 'Two-Hand Damage']:
                values = item_attr.value_dict
                text = item_attr.text
                
                #print(text, values)
                
                # TODO
                keys_to_update = ['r11', 'r12', 'r21', 'r22', 'ravg1', 'ravg2']
                for key in keys_to_update:
                    if key in values and values[key] is not None:
                        values[key] = str(float(float(values[key]) * 1.5))
                
                damages = ['Damage', 'Throw Damage', 'One-Hand Damage', 'Two-Hand Damage']
                
                text = attr.name + ': '
                if values['r12'] is not None:
                    text += '({}-{})'.format(values['r11'], values['r12'])
                else:
                    text += '({})'.format(values['r11'])
                text += ' to '
                if values['r22'] is not None:
                    text += '({}-{})'.format(values['r21'], values['r22'])
                else:
                    text += '({})'.format(values['r21'])
                
                text += ' ({}-{} avg)'.format(values['ravg1'], values['ravg2'])
                
                #print(text, values)
                #input("")
            elif attr.name == "Durability":
                assert len(item_attr.value_dict) == 1
                values = item_attr.value_dict
                values['v'] = str((int(item_attr.value_dict['v'])//2) + 1)
                text = "Durability: " + values['v']
            elif attr.name == "Required Strength":
                values = item_attr.value_dict
                values['v'] = str(max(int(item_attr.value_dict['v']) - 10, 0))
                text = "Required Strength: " + values['v']
            elif attr.name == "Required Dexterity":
                values = item_attr.value_dict
                values['v'] = str(max(int(item_attr.value_dict['v']) - 10, 0))
                text = "Required Dexterity: " + values['v']
            else:
                continue
        
            new_item.attr_dict[attr] = Attribute(item_attr.name, values, text, item_attr.varies)
        
        new_item.attr_dict[eth_attr_match] = Attribute(eth_attr_match.name, {}, "ethereal (cannot be repaired)", False)
        
        self.eth_item = new_item
    
    def update_info(self):
        for classname, item_type in class_specific_item_types:
            if isinstance(self.type.name, str) and self.type.name == item_type:
                self.class_restriction = classname
                break
        
        for attr in self.attr_dict:
            if 'Socket' in attr.name:
                self.num_possible_sockets = self.attr_dict[attr].max_value
        if self.num_possible_sockets == 0 and self.quality in ['Unique', 'Set'] and self.type is not None and self.type.name in SOCKETABLE_TYPES:
            self.num_possible_sockets = 1
        
        self.spawns_ethereal = False
        if any('Ethereal' in attr.name for attr in self.attr_dict):
            self.spawns_ethereal = True
            self.ethereal = True
        
        self.can_spawn_ethereal = not self.spawns_ethereal and self.quality != 'Set' and self.stype != 'Phase Blade' and self.type not in ['Amulet', 'Ring', 'Arrows', 'Bolts', 'Bow', 'Crossbow', 'Jewel', 'Charm']
        if any('Indestructible' in attr.name for attr in self.attr_dict):
            self.can_spawn_ethereal = False

class WhiteItem(Item):
    def __init__(self, name, imagepath, tier, item_type):
        super().__init__(name, imagepath, 'White', tier, item_type, name, dict())

class Socketable(Item):
    def __init__(self, name, imagepath, socketable_type, rlvl, attr_dict):
        self.attr_dict_weap, self.attr_dict_armor, self.attr_dict_helm, self.attr_dict_shield, rlvl_dict = attr_dict
        self.rlvl = rlvl
        #attr_dict_expanded = {**self.attr_dict_weap, **self.attr_dict_armor, **self.attr_dict_helm, **self.attr_dict_shield, **rlvl_dict}
        attr_dict_expanded = {}
        attr_dict_expanded.update(self.attr_dict_weap)
        attr_dict_expanded.update(self.attr_dict_armor)
        attr_dict_expanded.update(self.attr_dict_helm)
        attr_dict_expanded.update(self.attr_dict_shield)
        attr_dict_expanded.update(rlvl_dict)
        super().__init__(name, imagepath, socketable_type, '', 'Socketable', '', attr_dict_expanded)

class Rune(Socketable):
    def __init__(self, name, imagepath, rlvl, attr_dict):
        super().__init__(name + " Rune", imagepath, 'Rune', rlvl, attr_dict)

class Gem(Socketable):
    def __init__(self, name, imagepath, rlvl, attr_dict):
        super().__init__(name, imagepath, 'Gem', rlvl, attr_dict)

class UniqueItem(Item):
    def __init__(self, name, imagepath, tier, itype, stype, attr_dict):
        super().__init__(name, imagepath, 'Unique', tier, itype, stype, attr_dict)

class SetItem(Item):
    def __init__(self, name, imagepath, tier, itype, stype, attr_dict, set_name, set_bonuses):
        self.set_name = set_name
        self.set_bonuses = set_bonuses
        super().__init__(name, imagepath, 'Set', '', '', stype, attr_dict)

class Runeword(Item):
    def __init__(self, name, allowed_items, rune_string, attr_dict):
        types = allowed_items.split("Socket ")[1].split("/")
        self.runes = rune_string.split(" + ")
        super().__init__(name, '', 'Runeword', '', types, '', attr_dict)

class ItemSet(object):
    def __init__(self, name, set_items, set_bonuses):
        self.quality = 'set'
        self.name = name
        self.set_items = set_items
        self.set_bonuses = set_bonuses
        self.type = 'Set Bonus'

def fill_in_tiers(items):
    white_items = [item for item in items if item.quality == 'White']
        
    for item in items:
        if isinstance(item, Runeword) or isinstance(item, Socketable): continue
        
        assert len(item.quality) > 0
        assert len(item.stype.name) > 0
        
        if item.tier is None or item.type is None:
            # find item tier by scanning through white items.
            found = False
            for white_item in white_items:
                if item.stype.name.lower() == white_item.name.lower():
                    found = True
                    item.tier = white_item.tier
                    item.type = white_item.type
                    break
            if not found:
                if item.stype.name.lower() in ['ring', 'amulet', 'jewel']:
                    item.type = item.stype
                elif item.stype.name.lower() in ['small charm', 'large charm', 'grand charm']:
                    item.type = Category('Charm', 'type')
                else:
                    print("Couldn't find <", item.stype.name, ">")
                    assert False
        item.update_info()
        
        if item.can_spawn_ethereal:
            #print(item, "can spawn eth")
            item.create_ethereal_version()
            items.append(item.eth_item)
    
    return items

def get_sets_from_items(items):
    items_per_set = defaultdict(list)
    for item in items:
        if isinstance(item, SetItem):
            items_per_set[item.set_name].append(item)
    
    sets = []
    for set_name in items_per_set:
        sets.append(ItemSet(set_name, items_per_set[set_name], items_per_set[set_name][0].set_bonuses))
    
    for item in items:
        if isinstance(item, SetItem):
            for itemset in sets:
                if item.set_name == itemset.name:
                    item.set = itemset
                    break
    
    return sets, items