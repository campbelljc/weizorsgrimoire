import os, dill
import requests
import mimetypes
from lxml import html
from lxml.etree import tostring
from collections import namedtuple

from item import *
from attribute import *

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'}

start_links = [('http://classic.battle.net/diablo2exp/items/runes.shtml', '', ''), ('http://classic.battle.net/diablo2exp/items/uniques.shtml', '//tr/td//span//a/@href', 'http://classic.battle.net'), ('http://classic.battle.net/diablo2exp/items/sets/index.shtml', '//tr/td/font/span//table//tr/td//span/a/@href', 'http://classic.battle.net/diablo2exp/items/sets/'), ('http://classic.battle.net/diablo2exp/items/runewords-original.shtml', '', ''), ('http://classic.battle.net/diablo2exp/items/runewords-110.shtml', '', ''), ('http://classic.battle.net/diablo2exp/items/runewords-111.shtml', '', '')]

def get_items_from_summit():
    links = []
    for start_link, link_xpath, root_path in start_links:
        links.append(start_link)
        print(start_link)
        page = requests.get(start_link, headers=headers)
        tree = html.fromstring(page.content)
        
        if len(link_xpath) > 0:
            hrefs = tree.xpath(link_xpath)
            links.extend([root_path + href.split("#")[0] for href in hrefs if ('items' in href and '/u' in href) or 'sets' in href])
        links = list(set(links))        
        
    items = []
    for link in links:
        print(link)
        rel_link = link.replace("http://classic.battle.net/", "")
        
        if not os.path.exists('raw/' + rel_link):
            print("Fetching", link)
            page = requests.get(link, headers=headers)        
            rel_dir = 'raw/' + '/'.join(rel_link.split("/")[:-1])
            if not os.path.exists(rel_dir):
                os.makedirs(rel_dir)
            with open('raw/' + rel_link, 'wb') as lfile:
                lfile.write(page.content)
            tree = html.fromstring(page.content)
        else:
            with open('raw/' + rel_link, 'rb') as lfile:
                page = lfile.read()
                tree = html.fromstring(page)
        
        if 'sets' in link:
            set_names = tree.xpath('//span[contains(@class, "setname")]/text()')
            if len(set_names) == 0: continue
            set_bonuses_set = tree.xpath('//table//tr/td[3]/font/span')
            
            set_bonus_attrs = []
            for set_bonus in set_bonuses_set:
                attrs = set_bonus.text_content().replace("\r", "").split("\n")
                attrs = [attr for attr in attrs if len(attr) > 0]
                assert len(attrs) > 0

                attr_dict = {}
            
                discard_attr_indices = []
                for i, attr in enumerate(attrs):
                    attr = attr.replace(" (varies)", "").replace("*", "")
                    if len(attr) == 0 or 'set bonus' in attr.lower():
                        discard_attr_indices.append(i)
                        continue
                    attr_lower = attr.lower()
                    for attr_index, attr_matcher in enumerate(attribute_matches):
                        m = re.match(attr_matcher.regex, attr_lower)
                        if m:
                            discard_attr_indices.append(i)
                            attr_dict[attr_matcher] = Attribute(attr_matcher.name, m.groupdict(), attr)
                            break
        
                attrs = [attr for i, attr in enumerate(attrs) if i not in discard_attr_indices]
                if len(attrs) > 0:
                    print("Remaining:", attrs)
                    input("")
                set_bonus_attrs.append(attr_dict)
            
            #duplicate bonuses,1 copy for each item in set...
            set_bonuses = []
            cur_setname = set_names[0]
            j = 0
            for i in range(len(set_names)):
                if cur_setname != set_names[i]:
                    cur_setname = set_names[i]
                    j += 1
                set_bonuses.append(set_bonus_attrs[j])
            assert len(set_names) == len(set_bonuses)
            print(set_bonuses)
            
            item_tier = ''
            item_type = ''
            quality = 'Set'
            
            types = [typ for typ in tree.xpath('//tr/td//font//center//font/span/text()[normalize-space()]') if len(typ) > 0]
        
        elif 'runewords' in link:
            quality = 'Runeword'
            types = tree.xpath('//table//tr/td[2]/font/span/text()')
        
        elif 'runes' in link:
            quality = 'Rune'
        
        else:
            general_type = tree.xpath('//tr/td/font/span/center[1]/font/b')
            if len(general_type) == 0:
                continue
            else:
                general_type = general_type[0].text_content().split("Unique ")

            if len(general_type) > 1:
                item_tier = general_type[0][:-1]
                item_type = general_type[1]
            else:
                item_tier = None
                item_type = general_type[0]
            print(item_tier, item_type)
        
            quality = tree.xpath('//tr/td/font/span/center[1]/font/b')[0].text_content().split()
            assert 'Unique' in quality
            quality = 'Unique'
            
            types = [typ.text_content() for typ in tree.xpath('//tr/td//font//center[2]')[:-1]]
        
        if 'runes' in link:
            names = tree.xpath('//tr/td[2]/font')[1:]
            
            weap_descs = [typ.text_content() for typ in tree.xpath('//tr/td[3]/font')]
            ahs_descs = [typ.text_content() for typ in tree.xpath('//tr/td[4]/font')]
            assert len(weap_descs) == len(ahs_descs)
            
            descs = []
            for weap_desc, ahs_desc in zip(weap_descs, ahs_descs):
                rune_desc = weap_desc.replace(",", "\n") + " (weapons)\n"
                
                temp = ahs_desc.split("/")
                if len(temp) == 1:
                    rune_desc += ahs_desc.replace(",", "\n") + " (armor/helms/shields)\n"
                elif len(temp) == 2 and 'Shields' in temp[1]:
                    rune_desc += temp[0] + " (armor/helms)\n" + temp[1] + "\n"
                descs.append(rune_desc)
            
            images = [typ.text_content() for typ in tree.xpath('//tr/td[1]/font//img')[:-2]]
            types = [typ.text_content() for typ in tree.xpath('//tr/td[5]/font')] # rlvls
        else:
            names = tree.xpath('//tr/td//font//center//span/b')
        
            if 'runewords' in link:
                descs = [typ.text_content() for typ in tree.xpath('//tr/td[4]/font/span')]
                images = [typ.text_content() for typ in tree.xpath('//tr/td[3]/font/span')]
            else:
                descs = [typ.text_content() for typ in tree.xpath('//tr/td[2]/font/span')[1:]]
                images = [img for img in tree.xpath('//tr/td[1]/font/span//img/@src') if '/diablo2exp/images' in img and ('jewels' in img or 'items' in img)]
            if len(descs) == 0: descs = [typ.text_content() for typ in tree.xpath('//tr/td[3]/font/span')]
                
        print(link)
        print(len(names), len(types), len(descs), len(images))

        assert len(names) > 0
        assert len(names) == len(types) == len(descs) == len(images)
        if 'sets' in link:
            print(len(set_names))
            assert len(names) == len(set_names)

        for item_index, (iname, itype, idesc, image) in enumerate(zip(names, types, descs, images)):
            iname = iname.text_content().replace("*", "")
            print(iname)
            
            attrs = idesc.replace("\r", "").split("\n")
            attrs = [attr for attr in attrs if len(attr) > 0]
            assert len(attrs) > 0

            attr_dict = {}
            
            discard_attr_indices = []
            for i, attr in enumerate(attrs):
                attr = attr.replace(" (varies)", "").replace("*", "")
                if len(attr) == 0:
                    discard_attr_indices.append(i)
                    continue
                attr_lower = attr.lower()
                for attr_index, attr_matcher in enumerate(attribute_matches):
                    m = re.match(attr_matcher.regex, attr_lower)
                    if m:
                        discard_attr_indices.append(i)
                        attr_dict[attr_matcher] = Attribute(attr_matcher.name, m.groupdict(), attr)
                        break
        
            attrs = [attr for i, attr in enumerate(attrs) if i not in discard_attr_indices]
            if len(attrs) > 0:
                print("Remaining:", attrs)
                input("")
            
            if quality == 'Unique':
                item = UniqueItem(iname, 'http://classic.battle.net'+image, item_tier, item_type, itype, attr_dict)
            elif quality == 'Set':
                item = SetItem(iname, 'http://classic.battle.net'+image, item_tier, item_type, itype, attr_dict, set_names[item_index], set_bonuses[item_index])
            elif quality == 'Runeword':
                item = Runeword(iname, itype, image, attr_dict)
            elif quality == 'Rune':
                item = Rune(iname, image, itype, attr_dict)
            else:
                raise Exception(quality)
            items.append(item)
    
    return items