import re
import requests
from lxml import html
from lxml.etree import tostring

from item import *

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'}

class Monster():
    def __init__(self, name, act, mlvls, tcs):
        self.name = name
        #self.monster_type = mtype
        #self.loc = loc
        self.act = act
        self.mlvls = {"normal": int(mlvls[0]), "nightmare": int(mlvls[1]), "hell": int(mlvls[2])}
        self.tcs = {"normal": int(tcs[0]), "nightmare": int(tcs[1]), "hell": int(tcs[2])}
    
    def __str__(self):
        return "{}".format(self.name)
    
    def __repr__(self):
        return self.__str__()

def scrape_monster_levels():
    superuniques = []
    with open('raw/d2jsp_tcs.txt', 'r') as lfile:
        cur_act = None
        i = 0
        for line in lfile:
            #print("Line:", line)
            #print(len(line.strip()))
            if i == 0 or len(line.strip()) == 0:
                i += 1
                continue
            if 'Act ' in line and 'Act Boss' not in line:
                cur_act = line[:10].strip()
                #print(cur_act)
                continue
            line = line.replace("(Act Boss)", "")
            data = re.match(r'([a-zA-Z ]+)[\s]*(\d+)[\s]*\((\d+)\)[\s]*(\d+)[\s]*\((\d+)\)[\s]*(\d+)[\s]*\((\d+)\)', line)
            #print(data)
            if data is None:
                #input("")
                continue

            #print(data.group(1))
            lvls = [data.group(i) for i in range(2, 8)]
            #print(lvls)
            superuniques.append(Monster(data.group(1).strip(), cur_act, [lvls[0], lvls[2], lvls[4]], [lvls[1], lvls[3], lvls[5]]))
            #print(x)
        print(superuniques[-1])
    print(len(superuniques))
    return superuniques

def add_qlvls(items):
    qlvls = {}
    tcs = {}
    with open('raw/TC 1.10 - Diablo Wiki.html', 'r') as lfile:
        cur_tc = None
        
        for line in lfile:
            tc_match = re.findall(r'TC (\d+)', line)
            if len(tc_match) > 0:
                print("Cur tc:", tc_match)
                cur_tc = int(tc_match[0])
                continue
            
            matches = re.findall(r'\d\d\) ([^(\n<]*) \(qlvl (\d+)\)', line) + re.findall(r'<a href=[^\n<>]*>([^(\n<]*)<\/a> \(qlvl (\d+)\)', line)
            
            #page = lfile.read()
            #matches = re.findall(r'\d\d\) ([^(\n<]*) \(qlvl (\d+)\)', page) + re.findall(r'<a href=[^\n<>]*>([^(\n<]*)<\/a> \(qlvl (\d+)\)', page)
            for item, qlvl in matches:
                qlvls[item.lower().replace("'", "").replace(" ", "")] = int(qlvl)
                tcs[item.lower().replace("'", "").replace(" ", "")] = cur_tc
            
            #print(qlvls)
    for item in items:
        if not isinstance(item, (WhiteItem, UniqueItem, SetItem)):
            continue
        if 'Rainbow Facet' in item.name:
            item.qlvl = 85
            item.tc = 0
        elif 'Annihilus' in item.name or 'Hellfire Torch' in item.name:
            item.qlvl = 110
            item.tc = 110
        else:
            item.qlvl = qlvls[item.name.lower().replace("'", "").replace(" ", "")]
            item.tc = tcs[item.name.lower().replace("'", "").replace(" ", "")]
            if item.eth_item is not None:
                item.eth_item.qlvl = item.qlvl
                item.eth_item.tc = item.tc
            print(item.name, item.qlvl, item.tc)

if __name__ == '__main__':
    add_qlvls([])