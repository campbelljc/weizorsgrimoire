import re
from data import *
from collections import defaultdict

class Attribute():
    def __init__(self, name, values, text):
        self.quality = 'attribute'
        self.name = name
        self.value_dict = values
        self.text = text
        
        self.sort_value = None
        self.max_value = None
        if len(values) == 0:
            self.sort_value = True
            self.value_text = ""
        elif 'v' in self.value_dict and self.value_dict['v'] is not None:
            self.sort_value = float(self.value_dict['v'])
            self.value_text = self.value_dict['v']
            if 'd' in self.value_dict and self.value_dict['d'] is not None:
                self.sort_value *= float(self.value_dict['d'])
                self.value_text += " over " + self.value_dict['d'] + " seconds"
        else:
            self.value_text = ""
            if 'r11' in self.value_dict and self.value_dict['r11'] is not None and 'r12' in self.value_dict and self.value_dict['r12'] is not None:
                self.value_text += "(" + self.value_dict['r11'] + "-" + self.value_dict['r12'] + ")"
            elif 'r11' in self.value_dict and self.value_dict['r11'] is not None:
                self.value_text += self.value_dict['r11']
            elif 'r1' in self.value_dict and self.value_dict['r1'] is not None:
                self.value_text += self.value_dict['r1']
            
            if 'r21' in self.value_dict and self.value_dict['r21'] is not None and 'r22' in self.value_dict and self.value_dict['r22'] is not None:
                self.value_text += "-(" + self.value_dict['r21'] + "-" + self.value_dict['r22'] + ")"
            elif 'r21' in self.value_dict and self.value_dict['r21'] is not None:
                self.value_text += "-" + self.value_dict['r21']
            elif 'r2' in self.value_dict and self.value_dict['r2'] is not None:
                self.value_text += "-" + self.value_dict['r2']
            
            if 'perclvl2' in self.value_dict and self.value_dict['perclvl2'] is not None:
                self.value_text += " (" + self.value_dict['perclvl'] + "-" + self.value_dict['perclvl2'] + " per clvl)"                
            elif 'perclvl' in self.value_dict and self.value_dict['perclvl'] is not None:
                self.value_text += " (" + self.value_dict['perclvl'] + " per clvl)"
            
            if 'r22' in self.value_dict and self.value_dict['r22'] is not None:
                self.sort_value = float(self.value_dict['r22']) - 0.0001
            elif 'r21' in self.value_dict and self.value_dict['r21'] is not None:
                self.sort_value = float(self.value_dict['r21']) - 0.0001
            elif 'r2' in self.value_dict and self.value_dict['r2'] is not None:
                self.sort_value = float(self.value_dict['r2']) - 0.0001
            elif 'r1' in self.value_dict and self.value_dict['r1'] is not None:
                self.sort_value = float(self.value_dict['r1'])
            elif 'r11' in self.value_dict and self.value_dict['r11'] is not None:
                self.sort_value = float(self.value_dict['r11'])
            else:
                print("value dict:", self.value_dict)
                raise Exception
            self.max_value = int(self.sort_value+0.0001)

class AttributeMatch():
    def __init__(self, attr_name, regex, highlight_regex):
        self.quality = 'attribute'
        self.name = attr_name
        self.regex = re.compile(regex)
        self.highlight_regex = re.compile(highlight_regex)

def match_attributes(idesc):
    attrs = idesc.replace("\r", "").split("\n")
    attrs = [attr for attr in attrs if len(attr) > 0]
    assert len(attrs) > 0
    
    attr_dict = {}
    unmatched_strs = []
    for i, attr in enumerate(attrs):
        attr = attr.replace(" (varies)", "").replace("*", "")
        if len(attr) == 0:
            continue
        attr_lower = attr.lower()
        
        matched = False
        for attr_index, attr_matcher in enumerate(attribute_matches):
            m = re.match(attr_matcher.regex, attr_lower)
            if m:
                matched = True
                attr_dict[attr_matcher] = Attribute(attr_matcher.name, m.groupdict(), attr)
                break
        if not matched:
            unmatched_strs.append(attr)
    return attr_dict, unmatched_strs

def get_global_attr_dict(items, sets):
    items_per_attribute = defaultdict(list)
    for item in items:
        for attr in item.attr_dict:
            items_per_attribute[attr].append((item, item.attr_dict[attr]))
    
    for itemset in sets:
        for attr in itemset.set_bonuses:
            items_per_attribute[attr].append((itemset, itemset.set_bonuses[attr]))
    
    for attribute in items_per_attribute:        
        has_val_text = []
        for item, item_attr in items_per_attribute[attribute]:
            has_val_text.append(len(item_attr.value_text) > 0)
        display_value_column = sum(has_val_text) > 0
        
        if not display_value_column:
            items_per_attribute[attribute].sort(key=lambda tup: tup[0].name)
        else:
            items_per_attribute[attribute].sort(key=lambda tup: tup[1].sort_value, reverse=True)
    
    return items_per_attribute

start_atts = ['Damage', 'Throw Damage', 'One-Hand Damage', 'Two-Hand Damage', 'Defense', 'Required Level', 'Required Strength', 'Required Dexterity', 'Max Stack', 'Range', 'Durability', 'Weapon Speed', 'Boxes', 'Chance to Block', 'Chance to Block (Pal)', 'Chance to Block (Ama/Asn/Bar)', 'Chance to Block (Dru/Nec/Sor)', 'Kick Damage', 'Smite Damage']

attribute_matches = [
    AttributeMatch('Damage', r'damage: [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]* to [\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* \([\(]*(?P<ravg1>[\d\.]+)[\-]*(?P<ravg2>[\d\.]+)*[\)]* avg\)', 'damage'),
    AttributeMatch('Throw Damage', r'throw damage: [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]* to [\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* \([\(]*(?P<ravg1>[\d\.]+)[\-]*(?P<ravg2>[\d\.]+)*[\)]* avg\)', 'throw damage'),
    AttributeMatch('One-Hand Damage', r'one-hand damage: [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]* to [\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* \([\(]*(?P<ravg1>[\d\.]+)[\-]*(?P<ravg2>[\d\.]+)*[\)]* avg\)', 'one-hand damage'),
    AttributeMatch('One-Hand Damage', r'two-hand damage: [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]* to [\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* \([\(]*(?P<ravg1>[\d\.]+)[\-]*(?P<ravg2>[\d\.]+)*[\)]* avg\)', 'two-hand damage'),
    AttributeMatch('Defense', r'defense: [\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*( \(base defense: [\(]*(?P<br1>\d+)[\-]*(?P<br2>\d+)*[\)]*\))*', 'defense'),
    AttributeMatch('Required Level', r'required level: (?P<v>\d+)', 'required level'),
    AttributeMatch('Required Strength', r'required strength: (?P<v>\d+)', 'required strength'),
    AttributeMatch('Required Dexterity', r'required dexterity: (?P<v>\d+)', 'required dexterity'),
    AttributeMatch('Max Stack', r'max stack \((?P<v>\d+)\)', 'max stack'),
    AttributeMatch('Range', r'range: (?P<v>\d+)', 'range'),
    AttributeMatch('Durability', r'durability: (?P<v>\d+)', 'durability'),
    AttributeMatch('Weapon Speed', r'(base )*weapon speed: \[(?P<v>[\d\-]+)\]', r'(base )*weapon speed'),
    AttributeMatch('Boxes', r'(?P<v>\d+) boxes', 'boxes'),
    AttributeMatch('Chance to Block', r'chance to block: (?P<v>\d+)%', 'chance to block'),
    AttributeMatch('Chance to Block (Pal)', r'chance to block: pal: (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'chance to block: pal'),
    AttributeMatch('Chance to Block (Ama/Asn/Bar)', r'chance to block: ama/asn/bar: (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'chance to block: ama/asn/bar'),
    AttributeMatch('Chance to Block (Dru/Nec/Sor)', r'chance to block: dru/nec/sor: (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'chance to block: dru/nec/sor'),
    AttributeMatch('Kick Damage', r'assassin kick damage: (?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'assassin kick damage'),
    AttributeMatch('Smite Damage', r'(paladin )*smite damage: [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]* to [\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]*', r'(paladin )*smite damage'),
]

for classname in classes:
    attribute_matches.append(AttributeMatch(classname+' Only', r'\('+classname+' only\)', r'\('+classname+' only\)'))

for classname, trees in class_skills:
    for treename, tree in trees:
        for skill in tree:
            for proc_type in proc_types:
                attribute_matches.append(AttributeMatch('Chance to Cast '+skill.replace(" ", "_")+' '+proc_type.replace(" ", "_"), r'(?P<p>\d+)% chance to cast level (?P<r1>\d+)[\-]*(?P<r2>\d+)* '+skill+' '+proc_type, r'chance to cast level (?P<r1>\d+)[\-]*(?P<r2>\d+)* '+skill+' '+proc_type))

attribute_matches += [
    AttributeMatch('Firestorm', r'1% chance to cast level 50 delirium when struck', r'1% chance to cast level 50 delirium when struck'),
    AttributeMatch('Delirium', r'5% chance to cast level 10 firestorm on striking', r'5% chance to cast level 10 firestorm on striking'),
    AttributeMatch('% Enhanced Damage', r'\+[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% enhanced damage', 'enhanced damage'),
    AttributeMatch('% Enhanced Maximum Damage', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)*% enhanced maximum damage( \(based on character level\))*', 'enhanced maximum damage'),
    AttributeMatch('% Damage to Demons', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>[\d\.]+)[\-]*(?P<r2>[\d\.]+)*% damage to demons( \(based on character level\))*', 'damage to demons'),
    AttributeMatch('% Damage to Undead', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)*% damage to undead( \(based on character level\))*', 'damage to undead'),
    AttributeMatch('+ Minimum Damage', r'\+(?P<v>\d+) to minimum damage', 'minimum damage'),
    AttributeMatch('+ Maximum Damage', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* to maximum damage( \(based on character level\))*', 'maximum damage'),
    AttributeMatch('+ Maximum Fire Damage', r'\+(?P<v>\d+) to maximum fire damage', 'maximum fire damage'),

    AttributeMatch('Ignore Target\'s Defense', r"ignore target's defense", r"ignore target's defense"),    
    AttributeMatch('% Increased Chance of Blocking', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% increased chance of blocking', 'increased chance of blocking'),
    AttributeMatch('Faster Block Rate', r'(?P<v>\d+)% faster block rate', 'faster block rate'),
    
    AttributeMatch('Adds Damage', r'adds [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]*-[\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* damage', 'damage'),
    AttributeMatch('Adds Magic Damage', r'adds (?P<r1>\d+)[\-]*[\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* magic damage', 'magic damage'),
    AttributeMatch('Adds Fire Damage', r'adds [\(]*(?P<r11>\d+)([\-]*(?P<r12>\d+)*[\)]*-[\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]*)* fire damage', 'fire damage'),
    AttributeMatch('Adds Cold Damage', r'adds [\(]*(?P<r11>\d+)([\-]*(?P<r12>\d+)*[\)]*-[\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]*)* cold damage((,)*(--)* (?P<d1>[\d\.]+)[\-]*(?P<d2>\d+)* sec. duration)*', 'cold damage'),
    AttributeMatch('Adds Light Damage', r'adds (?P<r1>\d+)[\-]*[\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* lightning damage', 'lightning damage'),
    AttributeMatch('Adds Poison Damage', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* poison damage over (?P<d>\d+) seconds', 'poison damage'),
    
    AttributeMatch('+ to Skills', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to all skills', 'all skills'),
    AttributeMatch('+ to Fire Skills', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to fire skills', 'fire skills')
]

for classname in classes:
    attribute_matches.append(AttributeMatch('+ to '+classname+' Skills', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to '+classname+' skill levels', classname+' skill levels'))

attribute_matches += [    
    AttributeMatch('% Bonus to Attack Rating', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% bonus to attack rating', 'bonus to attack rating'),
    AttributeMatch('+ to Attack Rating Against Demons', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to attack rating against demons', 'attack rating against demons'),
    AttributeMatch('+ to Attack Rating Against Undead', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to attack rating against undead', 'attack rating against undead'),
    AttributeMatch('+ to attack rating', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* to attack rating( \(based on character level\))*', 'attack rating'),
    AttributeMatch('% Increased Attack Speed', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% increased attack speed', 'increased attack speed'),
    AttributeMatch('% Deadly Strike', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>[\d\.]+)[\-]*(?P<r2>[\d\.]+)*% deadly strike( \(based on character level\))*', 'deadly strike'),
    AttributeMatch('% Chance of Crushing Blow', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% chance of crushing blow', 'chance of crushing blow'),
    AttributeMatch('% Chance of Open Wounds', r'(?P<v>\d+)% chance of open wounds', 'chance of open wounds'),

    AttributeMatch('Knockback', r'knockback', 'knockback'),
    AttributeMatch('% Hit Causes Monster to Flee', r'hit causes monster to flee (?P<v>\d+)%', 'hit causes monster to flee'),
    AttributeMatch('Slows Target', r'slows target by (?P<v>\d+)%', 'slows target by'),
    
    AttributeMatch('% Life Stolen Per Hit', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% life stolen per hit', 'life stolen per hit'),
    AttributeMatch('% Mana Stolen Per Hit', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% mana stolen per hit', 'mana stolen per hit'),
    AttributeMatch('Slain Monsters Rest in Peace', r'slain monsters rest in peace', r'slain monsters rest in peace'),
    AttributeMatch('Prevent Monster Heal', r'prevent monster heal', r'prevent monster heal'),

    AttributeMatch('Piercing Attack', r'piercing attack \((?P<v>\d+)\)', 'piercing attack'),
    AttributeMatch('Fires Explosive Bolts', r'fires explosive bolts \[level (?P<v>\d+)\]', 'fires explosive bolts'),
    AttributeMatch('Fires Explosive Arrows', r'fires explosive arrows \[level (?P<v>\d+)\]', 'fires explosive arrows'),
    AttributeMatch('Fires Magic Arrows', r'fires magic arrows \[level (?P<v>\d+)\]', 'fires magic arrows'),
    AttributeMatch('Fires Explosive Arrows or Bolts', r'fires explosive arrows or bolts \[level (?P<v>\d+)\]', 'fires explosive arrows or bolts'),
    
    AttributeMatch('% Faster Cast Rate', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% faster cast rate', 'faster cast rate'),
    AttributeMatch('% Faster Run/Walk', r'(?P<v>\d+)% faster run/walk', 'faster run/walk'),
    AttributeMatch('% Faster Hit Recovery', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% faster hit recovery', 'faster hit recovery'),
    AttributeMatch('Requirements', r'requirements (?P<v>[\d\-]+)%', 'requirements'),
    
    AttributeMatch('% Enhanced Defense', r'\+[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% enhanced defense', 'enhanced defense'),
    AttributeMatch('+ to Defense vs. Melee', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* defense vs. melee', 'defense vs. melee'),
    AttributeMatch('+ to Defense vs. Missile', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* defense vs. missile', 'defense vs. missile'),
    AttributeMatch('+ to Defense', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* defense( \(based on character level\))*', 'defense'),
    
    AttributeMatch('+ to All Attributes', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to all attributes', 'all attributes'),
    AttributeMatch('+ to Strength', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>[\d\.]+)[\-]*(?P<r2>[\d\.]+)* to strength( \(based on character level\))*', 'strength'),
    AttributeMatch('+ to Dexterity', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* to dexterity( \(based on character level\))*', 'dexterity'),
    AttributeMatch('+ to Vitality', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>[\d\.]+)[\-]*(?P<r2>[\d\.]+)* to vitality( \(based on character level\))*', 'vitality'),
    AttributeMatch('+ to Energy', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* to energy( \(based on character level\))*', 'energy'),
]

for classname, trees in class_skills:
    for treename, tree in trees:
        for skill in tree:
            attribute_matches.append(AttributeMatch(skill.replace(" ", "_") + ' Aura When Equipped', r'level (?P<r1>\d+)[\-]*(?P<r2>\d+)* ' + skill + r' aura when equipped', skill+' aura when equipped'))

attribute_matches += [
    AttributeMatch('- to Target Defense', r'\-(?P<v>\d+)% target defense', 'target defense'),
    AttributeMatch('Hit Blinds Target', r'hit blinds target \+(?P<v>\d+)', 'hit blinds target'),
    AttributeMatch('- to Monster Defense Per Hit', r'\-(?P<v>\d+) to monster defense per hit', 'monster defense per hit'),
    AttributeMatch('Freezes Target', r'freezes target \+(?P<v>\d+)', 'freezes target'),
    
    AttributeMatch('+% to Fire Skill Damage', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to fire skill damage', 'fire skill damage'),
    AttributeMatch('+% to Cold Skill Damage', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to cold skill damage', 'cold skill damage'),
    AttributeMatch('+% to Lightning Skill Damage', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to lightning skill damage', 'lightning skill damage'),
    AttributeMatch('+% to Poison Skill Damage', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to poison skill damage', 'poison skill damage'),
    
    AttributeMatch('+ to Magic Absorb', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* magic absorb( \(based on character level\))*', 'magic absorb'),
    AttributeMatch('+ to Fire Absorb', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* fire absorb( \(based on character level\))*', 'fire absorb'),
    AttributeMatch('+ to Cold Absorb', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* cold absorb( \(based on character level\))*', 'cold absorb'),
    AttributeMatch('+ to Lightning Absorb', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* lightning absorb( \(based on character level\))*', 'lightning absorb'),
    AttributeMatch('+ to Poison Absorb', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* poison absorb( \(based on character level\))*', 'poison absorb'),
    AttributeMatch('+% to Fire Absorb', r'fire absorb (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'fire absorb'),
    AttributeMatch('+% to Cold Absorb', r'cold absorb (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'cold absorb'),
    AttributeMatch('+% to Lightning Absorb', r'lightning absorb (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'lightning absorb'),
    AttributeMatch('+% to Poison Absorb', r'poison absorb (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'poison absorb'),
    
    AttributeMatch('All Resistances', r'all resistances \+(?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'all resistances'),
    AttributeMatch('Fire Resist', r'fire resist (\+)*(?P<r1>(-)*\d+)[\-]*(?P<r2>\d+)*%', 'fire resist'),
    AttributeMatch('Cold Resist', r'cold resist \+(?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'cold resist'),
    AttributeMatch('Lightning Resist', r'lightning resist \+( \((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)*%( \(based on character level\))*', 'lightning resist'),
    AttributeMatch('Poison Resist', r'poison resist \+(?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'poison resist'),
    AttributeMatch('Maximum Fire Resist', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to maximum fire resist', 'maximum fire resist'),
    AttributeMatch('Maximum Cold Resist', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to maximum cold resist', 'maximum cold resist'),
    AttributeMatch('Maximum Lightning Resist', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to maximum lightning resist', 'maximum lightning resist'),
    AttributeMatch('Maximum Poison Resist', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to maximum poison resist', 'maximum poison resist'),

    AttributeMatch('-% to Enemy Fire Resistance', r'\-[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% to enemy fire resistance', 'enemy fire resistance'),
    AttributeMatch('-% to Enemy Cold Resistance', r'\-[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% to enemy cold resistance', 'enemy cold resistance'),
    AttributeMatch('-% to Enemy Lightning Resistance', r'\-[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% to enemy lightning resistance', 'enemy lightning resistance'),
    AttributeMatch('-% to Enemy Poison Resistance', r'\-[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% to enemy poison resistance', 'enemy poison resistance'),

    AttributeMatch('Damage Reduced (+)', r'damage reduced by (?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'damage reduced by'),
    AttributeMatch('Damage Reduced (%)', r'damage reduced by (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'damage reduced by'),
    AttributeMatch('Magic Damage Reduced', r'magic damage reduced by (?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'magic damage reduced by'),

    AttributeMatch('Poison Length Reduced', r'poison length reduced by (?P<v>\d+)', 'poison length reduced by'),

    AttributeMatch('Drain Life', r'drain life (?P<r1>-\d+)[\-]*(?P<r2>\d+)*', 'drain life'),
    AttributeMatch('Replenish Life', r'replenish life \+(?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'replenish life'),
    
    AttributeMatch('Reanimate as Returned', r'(?P<v>\d+)% reanimate as: returned', 'reanimate as: returned'),
    AttributeMatch('Replenishes Quantity', r'replenishes quantity \[(?P<v>\d+) in (?P<d>\d+) sec\.\]', 'replenishes quantity'),
    AttributeMatch('Increased Stack Size', r'increased stack size \[(?P<v>\d+)\]', 'increased stack size'),
    
    AttributeMatch('+ to Maximum stamina', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* maximum stamina( \(based on character level\))*', 'maximum stamina'),
    AttributeMatch('% Slower Stamina Drain', r'(?P<r1>(-)*\d+)[\-]*(?P<r2>\d+)*% slower stamina drain', 'slower stamina drain'),
    AttributeMatch('Heal Stamina Plus', r'heal stamina plus (\((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)*%( \(based on character level\))*', 'heal stamina plus'),
    
    AttributeMatch('+ to Life After Each Kill', r'\+(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* life after each kill', 'life after each kill'),
    AttributeMatch('+ to Life After Each Demon Kill', r'\+(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* life after each demon kill', 'life after each demon kill'),
    AttributeMatch('+ to Life', r'(\+ \((?P<perclvl>[\d\.]+[\-]*(?P<perclvl2>[\d\.]+)*) per character level\) )*(\+)*(?P<r1>[\d\.]+)[\-]*(?P<r2>[\d\.]+)* to life( \(based on character level\))*', 'life'),
    
    AttributeMatch('Increase Maximum Life', r'increase maximum life (?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)*%', 'increase maximum life'),
    AttributeMatch('% Damage Taken Goes to Mana', r'(?P<v>\d+)% damage taken goes to mana', 'damage taken goes to mana'),
    AttributeMatch('Regenerate Mana', r'regenerate mana (?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)*%', 'regenerate mana'),
    AttributeMatch('Increase Maximum Mana', r'increase maximum mana (?P<v>\d+)%', 'increase maximum mana'),
    AttributeMatch('+ to Mana After Each Kill', r'\+(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* to mana after each kill', 'mana after each kill'),
    AttributeMatch('+ to Mana', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>[\-]*[\d\.]+)[\-]*(?P<r2>[\d\.]+)* to mana( \(based on character level\))*', 'mana'),
    AttributeMatch('+ to Light Radius', r'(\+)*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* to light radius', 'light radius'),
    AttributeMatch('+ to Durability', r'(\+)*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* durability', 'durability'),
    AttributeMatch('Attacker Takes Damage', r'attacker takes damage of (\((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)*( \(based on character level\))*', 'attacker takes damage of'),
    AttributeMatch('Attacker Takes Lightning Damage', r'attacker takes lightning damage of (?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'attacker takes lightning damage of'),
    
    AttributeMatch('+% to Experience Gained', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to experience gained', 'experience gained'),
    AttributeMatch('% Extra Gold From Monsters', r'(\((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>(-)*[\d\.]+)[\-]*(?P<r2>[\d\.]+)*% extra gold from monsters( \(based on character level\))*', 'extra gold from monsters'),
    AttributeMatch('Reduces All Vendor Prices', r'reduces all vendor prices (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'reduces all vendor prices'),
    AttributeMatch('% Better Chance of Getting Magic Items', r'(\((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>[\d\.]+)[\-]*(?P<r2>[\d\.]+)*% better chance of getting magic items( \(based on character level\))*', 'better chance of getting magic items'),
        
    AttributeMatch('Half Freeze Duration', r'half freeze duration', 'half freeze duration'),
    AttributeMatch('Cannot Be Frozen', r'cannot be frozen', 'cannot be frozen'),
]

for classname, trees in class_skills:
    for treename, tree in trees:
        attribute_matches.append(AttributeMatch('+ to '+treename.replace(" ", "_"), r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to ' + treename + r' \(' + classname + r' only\)', 'to '+treename))
        for skill in tree:
            attribute_matches.append(AttributeMatch('+ to '+skill.replace(" ", "_"), r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to ' + skill + r' \(' + classname + r' only\)', 'to '+skill+ r' \(' + classname + r' only\)'))
            attribute_matches.append(AttributeMatch('+ to '+skill.replace(" ", "_")+' (all classes)', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to ' + skill + '( \(all classes\))*', 'to ' + skill + '( \(all classes\))*'))
            attribute_matches.append(AttributeMatch(skill.replace(" ", "_") + ' charges', r'level (?P<v>\d+) '+skill+r' \((?P<c>\d+) charges\)', skill))

attribute_matches += [
    AttributeMatch('Fade', r'fade', 'fade'),
    AttributeMatch('Display Aura', r'display aura', 'display aura'),
    AttributeMatch('Transforms into Vampire', r'transforms into vampire', 'transforms into vampire'),
    AttributeMatch('Socketed', r'socketed \((?P<r1>\d+)[\-]*(?P<r2>\d+)*\)', 'socketed'),
    AttributeMatch('Repairs Durability', r'repairs (?P<v>\d+) durability in (?P<d>\d+) seconds', r'repairs (?P<v>\d+) durability'),
    AttributeMatch('Indestructible', r'indestructible', 'indestructible'),
    AttributeMatch('Ethereal', r'ethereal \(cannot be repaired\)', 'ethereal'),
    AttributeMatch('Ladder Only', r'\(ladder only\)', 'ladder only'),
    AttributeMatch('Patch', r'\(only spawns in patch (?P<v>[\d\.]+) or later\)', 'only spawns in patch')
]

end_atts = ['Ladder Only', 'Patch']