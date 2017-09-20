import re
from attribute import *
from collections import namedtuple, defaultdict

class Category(object):
    def __init__(self, name, quality):
        self.name = name
        self.quality = quality
    
    def __hash__(self):
        return hash((self.name))
    
    def __eq__(self, other):
        return (self.name) == (other.name)
    
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
        
        self.can_spawn_ethereal = not self.spawns_ethereal
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