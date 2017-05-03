import re
from collections import namedtuple

class Item():
    def __init__(self, name, imagepath, quality, tier, itype, stype, attr_dict):
        self.name = name
        self.imagepath = imagepath
        self.quality = quality
        self.tier = tier
        self.type = (itype[:-1] if itype[-1] == 's' else itype) if len(itype) > 0 else None
        self.stype = stype
        self.attr_dict = attr_dict
