import re
import requests
from lxml import html
from lxml.etree import tostring

from item import *

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'}

class Monster():
    def __init__(self, name, mtype, loc, act, mlvls, tc):
        self.name = name
        self.monster_type = mtype
        self.loc = loc
        self.act = act
        self.mlvls = {"normal": int(mlvls[0]), "nightmare": int(mlvls[1]), "hell": int(mlvls[2])}
        self.tc = tc
    
    def __str__(self):
        return "{}".format(self.name)
    
    def __repr__(self):
        return self.__str__()

def scrape_monster_levels():
    #monsters = []
    '''
    directory = "https://diablo.gamepedia.com/Monsters_(Diablo_II)"
    monster_link_xpath = "/html/body/div[2]/div[3]/div[1]/div[4]/div[4]/div/table[position() < 6]/tbody/tr/td/a/@href"
    superunique_link_xpath = "/html/body/div[2]/div[3]/div[1]/div[4]/div[4]/div/table[position() > 5 and position() < 11]/tbody/tr/td/a/@href"
    mlvl_xpath = "/html/body/div[2]/div[3]/div[1]/div[4]/div[4]/div/table[1]/tbody/tr/td[11]/text() | /html/body/div[2]/div[3]/div[1]/div[4]/div[4]/div/table[1]/tbody/tr/td[11]/a/text()"
    
    page = requests.get(directory, headers=headers)
    tree = html.fromstring(page.content)
    
    monster_links = set(list(tree.xpath(monster_link_xpath)))
    for link in monster_links:
        link = 'https://diablo.gamepedia.com' + link
        print(link)
        page = requests.get(link, headers=headers)
        tree = html.fromstring(page.content)
        
        mlvls = tree.xpath(mlvl_xpath)
        mlvls = [mlvl for mlvl in mlvls if len(mlvl.replace("\n", "")) > 0]
        print(mlvls)
        input("")
    return monsters, superuniques
    '''
    
    superuniques = []
    with open('raw/Super Unique Monsters.html', 'r') as lfile:
        page = lfile.read()
        tree = html.fromstring(page)
        rows = [row.text_content().replace("\n", "--") for row in tree.xpath("//tr")[1:]]
        #print(rows[-1])
        cur_act = None
        for row in rows:
            if 'Act ' in row and 'Act Boss' not in row:
                cur_act = row
                continue
            data = [r.strip() for r in row.split("--") if len(r.strip()) > 0]
            superuniques.append(Monster(data[0], data[1], data[5], cur_act, [data[2][-2:], data[3][-2:], data[4][-2:]], data[-1]))
            #print(x)
        #print(superuniques[-1])
    print(len(superuniques))
    return superuniques

def add_qlvls(items):
    with open('raw/TC 1.10 - Diablo Wiki.html', 'r') as lfile:
        page = lfile.read()
        matches = re.findall(r'\d\d\) ([^(\n<]*) \(qlvl (\d+)\)', page) + re.findall(r'<a href=[^\n<>]*>([^(\n<]*)<\/a> \(qlvl (\d+)\)', page)
        qlvls = {}
        for item, qlvl in matches:
            qlvls[item.lower().replace("'", "").replace(" ", "")] = int(qlvl)
        #print(qlvls)
    for item in items:
        if not isinstance(item, (WhiteItem, UniqueItem, SetItem)):
            continue
        if 'Rainbow Facet' in item.name:
            item.qlvl = 85
        elif 'Annihilus' in item.name or 'Hellfire Torch' in item.name:
            item.qlvl = 110
        else:
            item.qlvl = qlvls[item.name.lower().replace("'", "").replace(" ", "")]
            if item.eth_item is not None:
                item.eth_item.qlvl = item.qlvl

#add_qlvls([])