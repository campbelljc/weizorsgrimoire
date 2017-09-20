from utils import load_data
items, sets, attributes = load_data()

class GearPiece(object):
    def __init__(self, type, shorttype, gear_name, custom_atts, sockets, custom_socket_atts, ethereal, runeword_base, desc):
        self.type = type
        self.shorttype = shorttype
        self.gear_name = gear_name
        self.custom_atts = custom_atts
        self.sockets = sockets
        self.custom_socket_atts = custom_socket_atts
        self.ethereal = ethereal
        self.runeword_base = runeword_base
        self.desc = desc
        
        self.matched_item = None
        if len(self.custom_atts) == 0:
            # match gear name to item.
            for item in items:
                if item.name == self.gear_name:
                    self.matched_item = item
                    break
        
        self.matched_sockets = []
        for socket in self.sockets:
            for item in items:
                if item.name == socket:
                    self.matched_sockets.append(socket)
                    break
        
        for item in items:
            if item.name == runeword_base:
                self.runeword_base = item
                break

class GearGuide(object):
    def __init__(self, name, link, classname, gear_pieces):
        self.name = name
        self.link = link
        self.classname = classname
        self.gear_pieces = gear_pieces
        self.quality = 'guide'

#GearPiece = namedtuple('GearPiece', 'type shorttype gear_name custom_atts sockets custom_socket_atts ethereal runeword_base desc')
#GearGuide = namedtuple('GearGuide', 'name link classname gear_pieces')
