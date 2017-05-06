classes = ['amazon', 'assassin', 'barbarian', 'druid', 'necromancer', 'paladin', 'sorceress']
class_skills = [
    ('amazon', [
        ('javelin and spear skills', ['jab', 'power strike', 'poison javelin', 'impale', 'lightning bolt', 'charged strike', 'plague javelin', 'fend', 'lightning strike', 'lightning fury']),
        ('passive and magic skills', ['inner sight', 'dodge', 'critical strike', 'slow missiles', 'avoid', 'penetrate', 'decoy', 'evade', 'valkyrie', 'pierce']),
        ('bow and crossbow skills', ['magic arrow', 'fire arrow', 'cold arrow', 'multiple shot', 'exploding arrow', 'ice arrow', 'guided arrow', 'immolation arrow', 'strafe', 'freezing arrow'])
    ]),
    ('assassin', [
        ('martial arts', ['tiger strike', 'dragon talon', 'fists of fire', 'dragon claw', 'cobra strike', 'claws of thunder', 'blades of ice', 'dragon tail', 'dragon flight', 'phoenix strike']),
        ('shadow disciplines', ['claw mastery', 'psychic hammer', 'burst of speed', 'cloak of shadows', 'weapon block', 'fade', 'shadow warrior', 'mind blast', 'venom', 'shadow master']),
        ('traps', ['fire blast', 'shock web', 'blade sentinel', 'charged bolt sentry', 'wake of fire', 'blade fury', 'lightning sentry', 'wake of inferno', 'death sentry', 'blade shield'])
    ]),
    ('barbarian', [
        ('warcries', ['howl', 'find potion', 'shout', 'taunt', 'battle cry', 'find item', 'battle orders', 'grim ward', 'war cry', 'battle command']),
        ('masteries', ['sword mastery', 'axe mastery', 'mace mastery', 'polearm mastery', 'throwing mastery', 'spear mastery', 'increased stamina', 'iron skin', 'increased speed', 'natural resistance']),
        ('combat skills', ['bash', 'double swing', 'leap', 'double throw', 'stun', 'leap attack', 'concentrate', 'frenzy', 'whirlwind', 'berserk'])
    ]),
    ('druid', [
        ('elemental skills', ['firestorm', 'molten boulder', 'arctic blast', 'cyclone armor', 'fissure', 'twister', 'volcano', 'tornado', 'hurricane', 'armageddon']),
        ('shape shifting skills', ['werewolf', 'lycanthropy', 'werebear', 'maul', 'feral rage', 'fire claws', 'rabies', 'shock wave', 'hunger', 'fury']),
        ('summoning skills', ['raven', 'poison creeper', 'oak sage', 'summon spirit wolf', 'carrion vine', 'heart of wolverine', 'summon dire wolf', 'solar creeper', 'spirit of barbs', 'summon grizzly'])
    ]),
    ('necromancer', [
        ('summoning skills', ['raise skeleton', 'skeleton mastery', 'clay golem', 'golem mastery', 'raise skeletal mage', 'blood golem', 'summon resist', 'iron golem', 'fire golem', 'revive']),
        ('poison and bone skills', ['teeth', 'bone armor', 'poison dagger', 'corpse explosion', 'bone wall', 'poison explosion', 'bone spear', 'bone prison', 'poison nova', 'bone spirit']),
        ('curses', ['amplify damage', 'dim vision', 'weaken', 'iron maiden', 'terror', 'confuse', 'life tap', 'attract', 'decrepify', 'lower resist'])
    ]),
    ('paladin', [
        ('defensive auras', ['prayer', 'resist fire', 'resist cold', 'resist lightning', 'defiance', 'cleansing', 'vigor', 'meditation', 'redemption', 'salvation']),
        ('offensive auras', ['might', 'holy fire', 'thorns', 'blessed aim', 'concentration', 'holy freeze', 'holy shock', 'sanctuary', 'fanaticism', 'conviction']),
        ('combat skills', ['sacrifice', 'holy bolt', 'smite', 'zeal', 'charge', 'vengeance', 'blessed hammer', 'conversion', 'holy shield', 'fist of the heavens'])
    ]),
    ('sorceress', [
        ('cold spells', ['ice bolt', 'frozen armor', 'frost nova', 'ice blast', 'shiver armor', 'glacial spike', 'blizzard', 'chilling armor', 'frozen orb', 'cold mastery']),
        ('lightning spells', ['charged bolt', 'telekinesis', 'static field', 'nova', 'chain lightning', 'teleport', 'thunder storm', 'energy shield', 'lightning mastery', 'lightning']),
        ('fire spells', ['fire bolt', 'warmth', 'inferno', 'blaze', 'fireball', 'fire wall', 'enchant', 'meteor', 'fire mastery', 'hydra'])
    ]),
]

proc_types = ['on striking', 'when struck', 'when you level-up', 'when you die', 'on attack', 'when you kill an enemy']

attribute_infos = [
    ('ow', 'This is a chance of making a monster bleed uncontrollably. They lose health while bleeding.'),
    ('hitblinds', 'Decreases radius of awareness similar to the Necromancer Curse: Dim Vision.'),
    ('freezes', 'Not the same as Cold Damage.'),
    ('defmissile', 'Reduces the % chance of getting hit by missiles (by raising the effective armor rating)'),
    ('colddmg', 'This cold duration will combine with other cold attack spells, so you can, for example, get a Freezing Arrow that lasts 3 seconds on Hell difficulty with a 10 second Eye of Etlich. Remember that Cold durations are 1/2 in Nightmare, and 1/4 in Hell.'),
    ('incrblockchance', 'Will only work if you have a shield equipped.'),
    ('atkdmg', 'Will not work with ranged weapons.'),
    ('atklightdmg', 'Will not work with ranged weapons.'),
    ('plusfireskills', 'Fire skills include all of the Sorceress Fire tree, Amazon Fire Arrow/Explosive Arrow/Immolation Arrow, Paladin Holy Fire, Assassin Fire Skills and Druid Fire Skills. These will raise Necromancer\'s Corpse Explosion and Fire Golem, if at least 1 skill point is spent on it.'),
    ('firestorm', 'Firestorm is Diablo\'s special attack.'),
    ('rip', "Means that the bodies can't be resurrected or they can't be used to raise skeletons (Necromancer). They can't be used for Corpse Explosion either. It will work only if you kill the enemy with a physical damage or elemental (Blizzard or Fireball) and not magical damage. The ring will work for the Paladin's Blessed Hammer skill."),
    ('maek', 'Will not work when the killing blow is made by a minion.')
]
