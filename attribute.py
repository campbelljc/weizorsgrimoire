import re
from data import *

class Attribute():
    def __init__(self, name, values, text):
        self.name = name
        self.value_dict = values
        self.text = text
        
        self.sort_value = None
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
            
            if 'perclvl' in self.value_dict and self.value_dict['perclvl'] is not None:
                self.value_text += " (" + self.value_dict['perclvl'] + " per clvl)"
            
            if 'r22' in self.value_dict and self.value_dict['r22'] is not None:
                self.sort_value = float(self.value_dict['r22'])
            elif 'r21' in self.value_dict and self.value_dict['r21'] is not None:
                self.sort_value = float(self.value_dict['r21'])
            elif 'r2' in self.value_dict and self.value_dict['r2'] is not None:
                self.sort_value = float(self.value_dict['r2'])
            elif 'r1' in self.value_dict and self.value_dict['r1'] is not None:
                self.sort_value = float(self.value_dict['r1'])
            elif 'r11' in self.value_dict and self.value_dict['r11'] is not None:
                self.sort_value = float(self.value_dict['r11'])
            else:
                print("value dict:", self.value_dict)
                raise Exception

class AttributeMatch():
    def __init__(self, attr_name, regex, highlight_regex):
        self.name = attr_name
        self.regex = re.compile(regex)
        self.highlight_regex = re.compile(highlight_regex)

start_atts = ['dmg', 'throw_dmg', 'one-hand_dmg', 'two-hand_dmg', 'def', 'rlvl', 'rstr', 'rdex', 'maxstack', 'range', 'durability', 'weap_speed', 'boxes', 'block', 'blockpal', 'blockzonsinbar', 'blockdrunecsor', 'sinkickdmg', 'smitedmg']

attribute_matches = [
    AttributeMatch('dmg', r'damage: [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]* to [\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* \([\(]*(?P<ravg1>[\d\.]+)[\-]*(?P<ravg2>[\d\.]+)*[\)]* avg\)', 'damage'),
    AttributeMatch('throw_dmg', r'throw damage: [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]* to [\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* \([\(]*(?P<ravg1>[\d\.]+)[\-]*(?P<ravg2>[\d\.]+)*[\)]* avg\)', 'throw damage'),
    AttributeMatch('one-hand_dmg', r'one-hand damage: [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]* to [\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* \([\(]*(?P<ravg1>[\d\.]+)[\-]*(?P<ravg2>[\d\.]+)*[\)]* avg\)', 'one-hand damage'),
    AttributeMatch('two-hand_dmg', r'two-hand damage: [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]* to [\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* \([\(]*(?P<ravg1>[\d\.]+)[\-]*(?P<ravg2>[\d\.]+)*[\)]* avg\)', 'two-hand damage'),
    AttributeMatch('def', r'defense: [\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*( \(base defense: [\(]*(?P<br1>\d+)[\-]*(?P<br2>\d+)*[\)]*\))*', 'defense'),
    AttributeMatch('rlvl', r'required level: (?P<v>\d+)', 'required level'),
    AttributeMatch('rstr', r'required strength: (?P<v>\d+)', 'required strength'),
    AttributeMatch('rdex', r'required dexterity: (?P<v>\d+)', 'required dexterity'),
    AttributeMatch('maxstack', r'max stack \((?P<v>\d+)\)', 'max stack'),
    AttributeMatch('range', r'range: (?P<v>\d+)', 'range'),
    AttributeMatch('durability', r'durability: (?P<v>\d+)', 'durability'),
    AttributeMatch('weap_speed', r'(base )*weapon speed: \[(?P<v>[\d\-]+)\]', r'(base )*weapon speed'),
    AttributeMatch('boxes', r'(?P<v>\d+) boxes', 'boxes'),
    AttributeMatch('block', r'chance to block: (?P<v>\d+)%', 'chance to block'),
    AttributeMatch('blockpal', r'chance to block: pal: (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'chance to block: pal'),
    AttributeMatch('blockzonsinbar', r'chance to block: ama/asn/bar: (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'chance to block: ama/asn/bar'),
    AttributeMatch('blockdrunecsor', r'chance to block: dru/nec/sor: (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'chance to block: dru/nec/sor'),
    AttributeMatch('sinkickdmg', r'assassin kick damage: (?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'assassin kick damage'),
    AttributeMatch('smitedmg', r'(paladin )*smite damage: [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]* to [\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]*', r'(paladin )*smite damage'),
]

for classname in classes:
    attribute_matches.append(AttributeMatch(classname+'_only', r'\('+classname+' only\)', r'\('+classname+' only\)'))

for classname, trees in class_skills:
    for treename, tree in trees:
        for skill in tree:
            for proc_type in proc_types:
                attribute_matches.append(AttributeMatch('ctc_'+proc_type.replace(" ", "_")+'_'+skill.replace(" ", "_"), r'(?P<p>\d+)% chance to cast level (?P<r1>\d+)[\-]*(?P<r2>\d+)* '+skill+' '+proc_type, r'chance to cast level (?P<r1>\d+)[\-]*(?P<r2>\d+)* '+skill+' '+proc_type))

attribute_matches += [
    AttributeMatch('firestorm', r'5% chance to cast level 10 firestorm on striking', r'5% chance to cast level 10 firestorm on striking'),
    AttributeMatch('edmg', r'\+[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% enhanced damage', 'enhanced damage'),
    AttributeMatch('emaxdmg', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)*% enhanced maximum damage( \(based on character level\))*', 'enhanced maximum damage'),
    AttributeMatch('dmgdemons', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)*% damage to demons( \(based on character level\))*', 'damage to demons'),
    AttributeMatch('dmgundead', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)*% damage to undead( \(based on character level\))*', 'damage to undead'),
    AttributeMatch('mindmg', r'\+(?P<v>\d+) to minimum damage', 'minimum damage'),
    AttributeMatch('maxdmg', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* to maximum damage( \(based on character level\))*', 'maximum damage'),
    AttributeMatch('maxfiredmg', r'\+(?P<v>\d+) to maximum fire damage', 'maximum fire damage'),

    AttributeMatch('ignoretargetdef', r"ignore target's defense", r"ignore target's defense"),    
    AttributeMatch('incrblockchance', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% increased chance of blocking', 'increased chance of blocking'),
    AttributeMatch('fbr', r'(?P<v>\d+)% faster block rate', 'faster block rate'),
    
    AttributeMatch('addsdmg', r'adds [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]*-[\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* damage', 'damage'),
    AttributeMatch('magicdmg', r'adds (?P<r1>\d+)[\-]*[\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* magic damage', 'magic damage'),
    AttributeMatch('firedmg', r'adds [\(]*(?P<r11>\d+)[\-]*(?P<r12>\d+)*[\)]*-[\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* fire damage', 'fire damage'),
    AttributeMatch('colddmg', r'adds [\(]*(?P<r11>\d+)([\-]*(?P<r12>\d+)*[\)]*-[\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]*)* cold damage(, (?P<d1>\d+)[\-]*(?P<d2>\d+)* sec. duration)*', 'cold damage'),
    AttributeMatch('lightdmg', r'adds (?P<r1>\d+)[\-]*[\(]*(?P<r21>\d+)[\-]*(?P<r22>\d+)*[\)]* lightning damage', 'lightning damage'),
    AttributeMatch('psndmg', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* poison damage over (?P<d>\d+) seconds', 'poison damage'),
    
    AttributeMatch('plusskills', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to all skills', 'all skills'),
    AttributeMatch('plusfireskills', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to fire skills', 'fire skills')
]

for classname in classes:
    attribute_matches.append(AttributeMatch('plus_'+classname, r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to '+classname+' skill levels', classname+' skill levels'))

attribute_matches += [    
    AttributeMatch('ar', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* to attack rating( \(based on character level\))*', 'attack rating'),
    AttributeMatch('arbonus', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% bonus to attack rating', 'bonus to attack rating'),
    AttributeMatch('ardemons', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to attack rating against demons', 'attack rating against demons'),
    AttributeMatch('arundead', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to attack rating against undead', 'attack rating against undead'),
    AttributeMatch('ias', r'(?P<v>\d+)% increased attack speed', 'increased attack speed'),
    AttributeMatch('ds', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>\d+)[\-]*(?P<r2>\d+)*% deadly strike( \(based on character level\))*', 'deadly strike'),
    AttributeMatch('cb', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% chance of crushing blow', 'chance of crushing blow'),
    AttributeMatch('ow', r'(?P<v>\d+)% chance of open wounds', 'chance of open wounds'),

    AttributeMatch('knockback', r'knockback', 'knockback'),
    AttributeMatch('monflee', r'hit causes monster to flee (?P<v>\d+)%', 'hit causes monster to flee'),
    AttributeMatch('slowstarget', r'slows target by (?P<v>\d+)%', 'slows target by'),
    
    AttributeMatch('lifesteal', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% life stolen per hit', 'life stolen per hit'),
    AttributeMatch('manasteal', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% mana stolen per hit', 'mana stolen per hit'),
    AttributeMatch('rip', r'slain monsters rest in peace', r'slain monsters rest in peace'),
    AttributeMatch('preventheal', r'prevent monster heal', r'prevent monster heal'),

    AttributeMatch('piercing', r'piercing attack \((?P<v>\d+)\)', 'piercing attack'),
    AttributeMatch('explbolt', r'fires explosive bolts \[level (?P<v>\d+)\]', 'fires explosive bolts'),
    AttributeMatch('explarrow', r'fires explosive arrows \[level (?P<v>\d+)\]', 'fires explosive arrows'),
    AttributeMatch('magicarrow', r'fires magic arrows \[level (?P<v>\d+)\]', 'fires magic arrows'),
    AttributeMatch('explboltarrow', r'fires explosive arrows or bolts \[level (?P<v>\d+)\]', 'fires explosive arrows or bolts'),
    
    AttributeMatch('fcr', r'(?P<v>\d+)% faster cast rate', 'faster cast rate'),
    AttributeMatch('frw', r'(?P<v>\d+)% faster run/walk', 'faster run/walk'),
    AttributeMatch('fhr', r'(?P<v>\d+)% faster hit recovery', 'faster hit recovery'),
    AttributeMatch('reqs', r'requirements (?P<v>[\d\-]+)%', 'requirements'),
    
    AttributeMatch('edef', r'\+[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% enhanced defense', 'enhanced defense'),
    AttributeMatch('defmelee', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* defense vs. melee', 'defense vs. melee'),
    AttributeMatch('defmissile', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* defense vs. missile', 'defense vs. missile'),
    AttributeMatch('defplus', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* defense( \(based on character level\))*', 'defense'),
    
    AttributeMatch('atts', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to all attributes', 'all attributes'),
    AttributeMatch('str', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* to strength( \(based on character level\))*', 'strength'),
    AttributeMatch('dex', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* to dexterity( \(based on character level\))*', 'dexterity'),
    AttributeMatch('vit', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* to vitality( \(based on character level\))*', 'vitality'),
    AttributeMatch('enr', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* to energy( \(based on character level\))*', 'energy'),
    AttributeMatch('life', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* to life( \(based on character level\))*', 'life'),
    AttributeMatch('mana', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* to mana( \(based on character level\))*', 'mana')
]

for classname, trees in class_skills:
    for treename, tree in trees:
        for skill in tree:
            attribute_matches.append(AttributeMatch('aura_'+skill.replace(" ", "_"), r'level (?P<r1>\d+)[\-]*(?P<r2>\d+)* ' + skill + r' aura when equipped', skill+' aura when equipped'))

attribute_matches += [
    AttributeMatch('negtargetdef', r'\-(?P<v>\d+)% target defense', 'target defense'),
    AttributeMatch('hitblinds', r'hit blinds target \+(?P<v>\d+)', 'hit blinds target'),
    AttributeMatch('negmondef', r'\-(?P<v>\d+) to monster defense per hit', 'monster defense per hit'),
    AttributeMatch('freezes', r'freezes target \+(?P<v>\d+)', 'freezes target'),
    
    AttributeMatch('fireskilldmg', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to fire skill damage', 'fire skill damage'),
    AttributeMatch('coldskilldmg', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to cold skill damage', 'cold skill damage'),
    AttributeMatch('lightskilldmg', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to lightning skill damage', 'lightning skill damage'),
    AttributeMatch('psnskilldmg', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to poison skill damage', 'poison skill damage'),
    
    AttributeMatch('firesorbplus', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* fire absorb( \(based on character level\))*', 'fire absorb'),
    AttributeMatch('coldsorbplus', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* cold absorb( \(based on character level\))*', 'cold absorb'),
    AttributeMatch('lightsorbplus', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* lightning absorb( \(based on character level\))*', 'lightning absorb'),
    AttributeMatch('psnsorbplus', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* poison absorb( \(based on character level\))*', 'poison absorb'),
    AttributeMatch('firesorb', r'fire absorb (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'fire absorb'),
    AttributeMatch('coldsorb', r'cold absorb (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'cold absorb'),
    AttributeMatch('lightsorb', r'lightning absorb (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'lightning absorb'),
    AttributeMatch('psnsorb', r'poison absorb (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'poison absorb'),
    
    AttributeMatch('allres', r'all resistances \+(?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'all resistances'),
    AttributeMatch('fireres', r'fire resist (\+)*(?P<r1>(-)*\d+)[\-]*(?P<r2>\d+)*%', 'fire resist'),
    AttributeMatch('coldres', r'cold resist \+(?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'cold resist'),
    AttributeMatch('lightres', r'lightning resist \+( \((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)*%( \(based on character level\))*', 'lightning resist'),
    AttributeMatch('psnres', r'poison resist \+(?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'poison resist'),
    AttributeMatch('maxfireres', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to maximum fire resist', 'maximum fire resist'),
    AttributeMatch('maxcoldres', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to maximum cold resist', 'maximum cold resist'),
    AttributeMatch('maxlightres', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to maximum lightning resist', 'maximum lightning resist'),
    AttributeMatch('maxpsnres', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to maximum poison resist', 'maximum poison resist'),

    AttributeMatch('negfireres', r'\-[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% to enemy fire resistance', 'enemy fire resistance'),
    AttributeMatch('negcoldres', r'\-[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% to enemy cold resistance', 'enemy cold resistance'),
    AttributeMatch('neglightres', r'\-[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% to enemy lightning resistance', 'enemy lightning resistance'),
    AttributeMatch('negpsnres', r'\-[\(]*(?P<r1>\d+)[\-]*(?P<r2>\d+)*[\)]*% to enemy poison resistance', 'enemy poison resistance'),

    AttributeMatch('dmgred', r'damage reduced by (?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'damage reduced by'),
    AttributeMatch('dmgredperc', r'damage reduced by (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'damage reduced by'),
    AttributeMatch('magicdmgred', r'magic damage reduced by (?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'magic damage reduced by'),

    AttributeMatch('poisonlenred', r'poison length reduced by (?P<v>\d+)', 'poison length reduced by'),

    AttributeMatch('repllife', r'replenish life \+(?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'replenish life'),
    
    AttributeMatch('reanimatereturned', r'(?P<v>\d+)% reanimate as: returned', 'reanimate as: returned'),
    AttributeMatch('replquan', r'replenishes quantity \[(?P<v>\d+) in (?P<d>\d+) sec\.\]', 'replenishes quantity'),
    AttributeMatch('stacksize', r'increased stack size \[(?P<v>\d+)\]', 'increased stack size'),
    
    AttributeMatch('maxstamina', r'(\+ \((?P<perclvl>[\d\.]+) per character level\) )*(\+)*(?P<r1>\d+)[\-]*(?P<r2>\d+)* maximum stamina( \(based on character level\))*', 'maximum stamina'),
    AttributeMatch('slowerstaminadrain', r'(?P<r1>\d+)[\-]*(?P<r2>\d+)*% slower stamina drain', 'slower stamina drain'),
    AttributeMatch('healstamina', r'heal stamina plus (\((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)*%( \(based on character level\))*', 'heal stamina plus'),
    
    AttributeMatch('laek', r'\+(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* life after each kill', 'life after each kill'),
    AttributeMatch('laekdemon', r'\+(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* life after each demon kill', 'life after each demon kill'),
    AttributeMatch('maxlife', r'increase maximum life (?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)*%', 'increase maximum life'),
    AttributeMatch('dmgtomana', r'(?P<v>\d+)% damage taken goes to mana', 'damage taken goes to mana'),
    AttributeMatch('manaregen', r'regenerate mana (?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)*%', 'regenerate mana'),
    AttributeMatch('maxmana', r'increase maximum mana (?P<v>\d+)%', 'increase maximum mana'),
    AttributeMatch('maek', r'\+(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* to mana after each kill', 'mana after each kill'),
    AttributeMatch('lrad', r'(\+)*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* to light radius', 'light radius'),
    AttributeMatch('duraplus', r'(\+)*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)* durability', 'durability'),
    AttributeMatch('atkdmg', r'attacker takes damage of (\((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>[\-]*\d+)[\-]*(?P<r2>\d+)*( \(based on character level\))*', 'attacker takes damage of'),
    AttributeMatch('atklightdmg', r'attacker takes lightning damage of (?P<r1>\d+)[\-]*(?P<r2>\d+)*', 'attacker takes lightning damage of'),
    
    AttributeMatch('exp', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)*% to experience gained', 'experience gained'),
    AttributeMatch('gf', r'(\((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>\d+)[\-]*(?P<r2>\d+)*% extra gold from monsters( \(based on character level\))*', 'extra gold from monsters'),
    AttributeMatch('prices', r'reduces all vendor prices (?P<r1>\d+)[\-]*(?P<r2>\d+)*%', 'reduces all vendor prices'),
    AttributeMatch('mf', r'(\((?P<perclvl>[\d\.]+) per character level\) )*(?P<r1>\d+)[\-]*(?P<r2>\d+)*% better chance of getting magic items( \(based on character level\))*', 'better chance of getting magic items'),
        
    AttributeMatch('halffreezeduration', r'half freeze duration', 'half freeze duration'),
    AttributeMatch('cannotbefrozen', r'cannot be frozen', 'cannot be frozen'),
]

for classname, trees in class_skills:
    for treename, tree in trees:
        attribute_matches.append(AttributeMatch('plus_'+treename.replace(" ", "_"), r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to ' + treename + r' \(' + classname + r' only\)', 'to '+treename))
        for skill in tree:
            attribute_matches.append(AttributeMatch('plus_'+skill.replace(" ", "_"), r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to ' + skill + r' \(' + classname + r' only\)', 'to '+skill+ r' \(' + classname + r' only\)'))
            attribute_matches.append(AttributeMatch('plus_'+skill.replace(" ", "_")+'_all', r'\+(?P<r1>\d+)[\-]*(?P<r2>\d+)* to ' + skill + '( \(all classes\))*', 'to ' + skill + '( \(all classes\))*'))
            attribute_matches.append(AttributeMatch('charges_'+skill.replace(" ", "_"), r'level (?P<v>\d+) '+skill+r' \((?P<c>\d+) charges\)', skill))

attribute_matches += [
    AttributeMatch('sockets', r'socketed \((?P<r1>\d+)[\-]*(?P<r2>\d+)*\)', 'socketed'),
    AttributeMatch('repdura', r'repairs (?P<v>\d+) durability in (?P<d>\d+) seconds', r'repairs (?P<v>\d+) durability'),
    AttributeMatch('indestructible', r'indestructible', 'indestructible'),
    AttributeMatch('ethereal', r'ethereal \(cannot be repaired\)', 'ethereal'),
    AttributeMatch('ladder_only', r'\(ladder only\)', 'ladder only'),
    AttributeMatch('patch', r'\(only spawns in patch (?P<v>[\d\.]+) or later\)', 'only spawns in patch')
]

end_atts = ['ladder_only', 'patch']