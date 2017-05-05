import re
from collections import namedtuple, defaultdict

class Item():
    def __init__(self, name, imagepath, quality, tier, itype, stype, attr_dict):
        self.name = name
        self.imagepath = imagepath
        self.quality = quality
        self.tier = tier
        self.type = (itype[:-1] if itype[-1] == 's' else itype) if len(itype) > 0 else None
        self.stype = stype
        self.attr_dict = attr_dict

class Rune(Item):
    def __init__(self, name, imagepath, rlvl, attr_dict):
        self.rlvl = rlvl
        super().__init(name, imagepath, 'Rune', '', 'Socketable', '', attr_dict)

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