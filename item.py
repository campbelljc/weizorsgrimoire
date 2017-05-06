import re
from attribute import *
from collections import namedtuple, defaultdict

class Item():
    def __init__(self, name, imagepath, quality, tier, itype, stype, attr_dict):
        self.name = name
        self.imagepath = imagepath
        self.quality = quality # "Unique"
        self.tier = tier # "Elite"
        self.type = (itype[:-1] if itype[-1] == 's' else itype) if len(itype) > 0 else None # "Armor"
        self.stype = stype # "Balrog Skin"
        self.attr_dict = attr_dict

class WhiteItem(Item):
    def __init__(self, name, imagepath, tier, item_type):
        super().__init__(name, imagepath, 'White', tier, item_type, name, dict())

class Rune(Item):
    def __init__(self, name, imagepath, rlvl, attr_dict):
        self.attr_dict_weap, self.attr_dict_armor, self.attr_dict_helm, self.attr_dict_shield, rlvl_dict = attr_dict
        self.rlvl = rlvl
        attr_dict_expanded = {**self.attr_dict_weap, **self.attr_dict_armor, **self.attr_dict_helm, **self.attr_dict_shield, **rlvl_dict}
        super().__init__(name + " Rune", imagepath, 'Rune', '', 'socketable', '', attr_dict_expanded)

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
        self.allowed_items = allowed_items
        self.runes = rune_string.split(" + ")
        super().__init__(name, '', 'Runeword', '', '', '', attr_dict)

class ItemSet():
    def __init__(self, name, set_items, set_bonuses):
        self.quality = 'set'
        self.name = name
        self.set_items = set_items
        self.set_bonuses = set_bonuses

def fill_in_tiers(items):
    white_items = [item for item in items if item.quality == 'White']
    print([w.name for w in white_items])
    
    for item in items:
        if isinstance(item, Runeword) or isinstance(item, Rune): continue
        
        print(item.name)
        assert len(item.quality) > 0
        assert len(item.stype) > 0
        
        if item.tier == "" or item.type == "":
            # find item tier by scanning through white items.
            found = False
            for white_item in white_items:
                if item.stype.lower() == white_item.name.lower():
                    found = True
                    item.tier = white_item.tier
                    item.type = white_item.type
                    break
            if not found:
                if item.stype.lower() in ['ring', 'amulet', 'small charm', 'large charm', 'grand charm', 'jewel']:
                    item.type = 'Jewelry/Charms'
                else:
                    print("Couldn't find <", item.stype, ">")
                    assert False
    
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