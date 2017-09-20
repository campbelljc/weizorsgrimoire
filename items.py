import re, glob, shutil
from utils import load_data, load_guides
from item import *
from guide import *
from get_items import *
from collections import defaultdict

SITENAME = "Weizor's Grimoire"
HTML_DIR = '/Users/jcampbell/Sites/root/d2'
ROOT_DIR = '/d2/'

def setup_dirs():
    if not os.path.exists(HTML_DIR):
        os.makedirs(HTML_DIR)
        os.makedirs(HTML_DIR + "/unique")
        os.makedirs(HTML_DIR + "/white")
        os.makedirs(HTML_DIR + "/set")
        os.makedirs(HTML_DIR + "/attribute")
        os.makedirs(HTML_DIR + "/runeword")
        os.makedirs(HTML_DIR + "/rune")
        os.makedirs(HTML_DIR + "/gem")
        os.makedirs(HTML_DIR + "/tier")
        os.makedirs(HTML_DIR + "/type")
        os.makedirs(HTML_DIR + "/subtype")
    shutil.copyfile("style.css", HTML_DIR + "/style.css")
    for file in glob.glob(r'*.py'):
        shutil.copy(file, "/Library/WebServer/CGI-Executables")
    shutil.copy("items.dll", "/Library/WebServer/CGI-Executables")
    os.system("chmod 755 /Library/WebServer/CGI-Executables/create_guide.py")
    if not os.path.exists(HTML_DIR + "/js"):
        shutil.copytree("js", HTML_DIR + "/js")

def get_link(item, root=True):
    link = "/" + item.quality.lower() + "/" + item.name.lower().replace("%", "pct").replace("+", "plus").replace("-", "neg").replace("(", "").replace(")", "").replace(" ", "_").replace("'", "").replace("/", "_").replace(":", "") + ".html"
    if root:
        return ROOT_DIR + link
    else:
        return HTML_DIR + link

def get_html_for_attrs(attr_dict, selection_fn):
    html = ""
    for attr in attr_dict:
        if not selection_fn(attr.name): continue
        
        attr_text = attr_dict[attr].text.lower()
        match = re.search(attr.highlight_regex, attr_text)
        
        if not match:
            print(attr_text, " couldnt be matched to", attr.highlight_regex)
            raise Exception
        
        text_match = attr_text[match.span()[0]:match.span()[1]]
        text_match_link = '<a href="' + get_link(attr) + '">' + text_match + '</a>'
        attr_text = attr_text.replace(text_match, text_match_link)
        html += attr_text + "<br />"
    return html[:-6].lower()

def get_footer():
    return "</div>\n\
            <div id='lowerContainer'>\n\
	          <div id='blurContainer'></div>\n\
                 <div id='footer'>\n\
                   <p class='centerText'>all content on this site is &copy; 2001-2017 blizzard entertainment.</p>\n\
                 </div>\n\
              </div>\n\
            </div>\n\
            </body></html>"

def get_body_header():
    return "<div id='container'>\n\
          <div id='headerContainer'>\n\
            <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\n\
          </div>\n\
          <div id='contentContainer'>"

def output_item_files(items, indexes):
    for item in items:
        if isinstance(item, Runeword) or isinstance(item, Socketable): continue
        base_attrs = get_html_for_attrs(item.attr_dict, lambda name: name in start_atts)
        end_attrs = get_html_for_attrs(item.attr_dict, lambda name: name in end_atts)
        attrs = get_html_for_attrs(item.attr_dict, lambda name: name not in start_atts and name not in end_atts)
    
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="/d2/style.css" />\
                    </head><body>'.format(item.name, SITENAME)
    
        matched_link = None
        for item_type, index_link in indexes:
            if item_type.lower().split()[0] == item.quality.lower():
                matched_link = index_link
        
        quality = item.quality
        if matched_link is not None:
            quality = '<a href="../../'+matched_link+'">'+quality+'</a>'
        
        typeinfo = ""
        if item.tier is not None:
            typeinfo = '<a href="'+get_link(item.tier)+'">'+item.tier.name+'</a> ' + typeinfo
        typeinfo += '<a href="'+get_link(item.type)+'">'+item.type.name+'</a>'
        
        stypeinfo = ""
        if item.stype is not None:
            stypeinfo += '<a href="'+get_link(item.stype)+'">'+item.stype.name+'</a>'            
        
        set_info = ""
        if isinstance(item, SetItem):
            set_info = "<p class='item_type'>(<a href='"+get_link(item.set)+"'>"+item.set_name+"</a>)</p>"
    
        body = get_body_header() + \
        "<div class='item_container'>\
            <p class='item_name {9}'>{0}</p>\
            {8}\
            <p class='item_image_p'><img src='{1}' alt='{0}' /></p>\
            <p class='item_stype'>{4} {3}</p>\
            <p class='item_type'>({2})</p>\
            <p class='item_attrs_small'>{5}</p>\
            <p class='item_attrs attr'>{6}</p>\
            <p class='item_attrs_small'>{7}</p>\
          </div>\
        </div>".format(item.name, item.imagepath, typeinfo, stypeinfo, quality, base_attrs, attrs, end_attrs, set_info, item.quality)
        
        html = header + body + get_footer()
        with open(get_link(item, False), 'w') as itemfile:
            itemfile.write(html)

def output_rune_files(items):
    for item in items:
        if item.quality != 'Rune': continue
        
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="/d2/style.css" />\
                    </head><body>'.format(item.name, SITENAME)
        
        weap_attrs = get_html_for_attrs(item.attr_dict_weap, lambda name: True)
        armor_attrs = get_html_for_attrs(item.attr_dict_armor, lambda name: True)
        helm_attrs = get_html_for_attrs(item.attr_dict_helm, lambda name: True)
        shield_attrs = get_html_for_attrs(item.attr_dict_shield, lambda name: True)
        
        runewords = ""
        for rw_item in items:
            if isinstance(rw_item, Runeword) and item.name.split(" ")[0] in rw_item.runes:
                runewords += "<a href='"+get_link(rw_item)+"'>"+rw_item.name+"</a><br />"
        runewords = runewords[:-6]
        
        body = get_body_header() + \
        "<div class='item_container'>\
            <p class='item_name rune'>{0}</p>\
            <p class='item_image_p'><img src='{1}' alt='{0}' /></p>\
            <p class='item_type'>(<a href='../runes.html'>Rune</a>)</p>\
            <p class='item_attrs_small'><a href='../attribute/required_level.html'>Required Level</a>: {2}</p>\
            <table class='centerTable' id='rune_table'>\
            <tr><td class='attr_restriction'>Weapons</td><td>{3}</td></tr>\
            <tr><td class='attr_restriction'>Armor</td><td>{4}</td></tr>\
            <tr><td class='attr_restriction'>Helms</td><td>{5}</td></tr>\
            <tr><td class='attr_restriction'>Shields</td><td>{6}</td></tr>\
            </table>\
            <p>Runewords that use this rune:</p>\
            <p>{7}</p>\
          </div>\
        </div>".format(item.name, item.imagepath, item.rlvl, weap_attrs, armor_attrs, helm_attrs, shield_attrs, runewords)
    
        html = header + body + get_footer()
        with open(get_link(item, False), 'w') as itemfile:
            itemfile.write(html)

def output_gem_files(items):
    for item in items:
        if item.quality != 'Gem': continue
        
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="/d2/style.css" />\
                    </head><body>'.format(item.name, SITENAME)
        
        weap_attrs = get_html_for_attrs(item.attr_dict_weap, lambda name: True)
        armor_attrs = get_html_for_attrs(item.attr_dict_armor, lambda name: True)
        helm_attrs = get_html_for_attrs(item.attr_dict_helm, lambda name: True)
        shield_attrs = get_html_for_attrs(item.attr_dict_shield, lambda name: True)
                
        body = get_body_header() + \
        "<div class='item_container'>\
            <p class='item_name gem'>{0}</p>\
            <p class='item_image_p'><img src='{1}' alt='{0}' /></p>\
            <p class='item_type'>(<a href='../gems.html'>Gem</a>)</p>\
            <p class='item_attrs_small'><a href='../attribute/required_level.html'>Required Level</a>: {2}</p>\
            <table class='centerTable' id='rune_table'>\
            <tr><td class='attr_restriction'>Weapons</td><td>{3}</td></tr>\
            <tr><td class='attr_restriction'>Armor</td><td>{4}</td></tr>\
            <tr><td class='attr_restriction'>Helms</td><td>{5}</td></tr>\
            <tr><td class='attr_restriction'>Shields</td><td>{6}</td></tr>\
            </table>\
          </div>\
        </div>".format(item.name, item.imagepath, item.rlvl, weap_attrs, armor_attrs, helm_attrs, shield_attrs)
        
        html = header + body + get_footer()
        with open(get_link(item, False), 'w') as itemfile:
            itemfile.write(html)

def output_runeword_files(items):
    for item in items:
        if not isinstance(item, Runeword): continue
        base_attrs = get_html_for_attrs(item.attr_dict, lambda name: name in start_atts)
        end_attrs = get_html_for_attrs(item.attr_dict, lambda name: name in end_atts)
        attrs = get_html_for_attrs(item.attr_dict, lambda name: name not in start_atts and name not in end_atts)
        
        rune_links = ""
        rune_images = ""
        for rune in item.runes:
            rune_links += "<a href='"+get_link([i for i in items if rune+" Rune"==i.name][0])+"'>"+rune+"</a> + "
            rune_images += "<a href='"+get_link([i for i in items if rune+" Rune"==i.name][0])+"'><img src='http://classic.battle.net/images/battle/diablo2exp/images/runes/rune"+rune.replace("Jah", "Jo").replace("Shael", "Shae")+".gif' alt='"+rune+"'/></a>"
        rune_links = rune_links[:-3]
            
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="/d2/style.css" />\
                    </head><body>'.format(item.name, SITENAME)
        
        typeinfo = ""
        types = item.type if isinstance(item.type, list) else [item.type]
        for typ in types:
            typeinfo += '<a href="'+get_link(typ)+'">'+typ.name+'</a> / '
        typeinfo = typeinfo[:-3]
        
        body = get_body_header() + \
        "<div class='item_container'>\
            <p class='item_name runeword'>{0}</p>\
            <p class='item_stype'>{1}</p>\
            <p class='item_runes'>{6}</p>\
            <p class='item_type'>{2}</p>\
            <p class='item_attrs_small'>{3}</p>\
            <p class='item_attrs attr'>{4}</p>\
            <p class='item_attrs_small'>{5}</p>\
          </div>\
        </div>".format(item.name, rune_links, typeinfo, base_attrs, attrs, end_attrs, rune_images)
        
        html = header + body + get_footer()
        with open(get_link(item, False), 'w') as itemfile:
            itemfile.write(html)

def output_set_files(sets):
    for itemset in sets:
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="/d2/style.css" />\
                    </head><body>'.format(itemset.name, SITENAME)
    
        setitemrows = ''
        for item in itemset.set_items:
            base_attrs = get_html_for_attrs(item.attr_dict, lambda name: name in start_atts)
            end_attrs = get_html_for_attrs(item.attr_dict, lambda name: name in end_atts)
            attrs = get_html_for_attrs(item.attr_dict, lambda name: name not in start_atts and name not in end_atts)
            setitemrows += "\
                <div class='item_container'>\
                    <p class='item_name_small {2}'>{6}</p>\
                    <p class='item_image_p'><img src='{1}' alt='{0}' /></p>\
                    <p class='item_attrs_small'>{3}</p>\
                    <p class='item_attrs attr'>{4}</p>\
                    <p class='item_attrs_small'>{5}</p>\
                </div><hr class='item_seperator' />".format(item.name, item.imagepath, item.quality, base_attrs, attrs, end_attrs, "<a href='"+get_link(item)+"'>"+item.name+"</a>")
    
        set_bonuses = get_html_for_attrs(itemset.set_bonuses, lambda name: True)
    
        body = get_body_header() + \
        "<p class='item_name set'>{0}</p>\
          {2}\
          <p class='set_bonuses_title'>Set Bonuses</p>\
          <p class='set_bonuses'>{1}</p>\
        </div>".format(itemset.name, set_bonuses, setitemrows)
        
        html = header + body + get_footer()
        with open(get_link(itemset, False), 'w') as itemfile:
            itemfile.write(html)

def write_html_for_table(cat, table_headers, itemrows):
    # save file...
    # ref sorting: https://github.com/joequery/Stupid-Table-Plugin#readme
    # ref sort(a,b): https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort
    header = '<html><head>\
                <title>{0} -- {1}</title>\
                <link rel="stylesheet" type="text/css" media="screen" href="/d2/style.css" />\
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>\
                <script type="text/javascript" src="../js/stupidtable.min.js"></script>\
                <script type="text/javascript">\
                $(function(){{\
                  $("#attr_table").stupidtable({{\
                    "range_string":function(a,b){{\
                      var valA = a;\
                      if (a.indexOf("-") > -1)\
                      {{\
                        valA = a.split("-")[1];\
                      }}\
                      var valB = b;\
                      if (b.indexOf("-") > -1)\
                      {{\
                        valB = b.split("-")[1];\
                      }}\
                      return parseInt(valA,10) - parseInt(valB,10);\
                    }}\
                  }});\
                }});\
                </script>\
                </head><body>'.format(cat.name, SITENAME)

    body = get_body_header() + \
    "<p class='attr_title'><strong>{1}</strong></p>\
      <table class='centerTable' id='attr_table'>\
      <thead><tr>{2}</tr></thead><tbody>\
      {0}\
      </tbody></table>\
    </div>".format(itemrows, cat.name, table_headers)

    html = header + body + get_footer()
    with open(get_link(cat, False), 'w') as itemfile:
        itemfile.write(html)

def output_attribute_files(items_per_attribute):
    for attribute in items_per_attribute:
        has_val_text = []
        for item, item_attr in items_per_attribute[attribute]:
            has_val_text.append(len(item_attr.value_text) > 0)
        display_value_column = sum(has_val_text) > 0
    
        itemrows = ''
        for item, item_attr in items_per_attribute[attribute]:
            itemrows += '<tr class="attr_row"><td><a href="{0}" class="{2}">{1}<br /><span class="item_type">{3}</span></a></td>'.format(get_link(item), item.name, item.quality, str(item.type))
            if display_value_column:
                itemrows += "<td>{0}</td>".format(item_attr.value_text)
            itemrows += "</tr>"
        
        table_headers = "<th class='attr_table_header' data-sort='string'>item</th>"
        if display_value_column:
            table_headers += "<th class='attr_table_header' data-sort='range_string'>value</th>"
        
        write_html_for_table(attribute, table_headers, itemrows)

def output_cat_files(items_per_cat):
    for cat in items_per_cat:
        itemrows = ''
        for item in items_per_cat[cat]:
            itemrows += '<tr class="attr_row"><td><a href="{0}" class="{2}">{1}</a></td></tr>'.format(get_link(item), item.name, item.quality)
        
        table_headers = "<th class='attr_table_header' data-sort='string'>item</th>"
        
        write_html_for_table(cat, table_headers, itemrows)

def output_main_page(items, sets, attributes, cat_dicts, index_links):
    names = ""
    for item in items + sets:
        names += '{ value: "' + item.name + '", link: "' + get_link(item) + '", category: "' + item.quality +'" },'
    for attr in attributes:
        names += '{ value: "' + attr.name + '", link: "' + get_link(attr) + '", category: "' + attr.quality +'" },'
    for cat_dict, _ in cat_dicts:
        for cat in cat_dict:
            names += '{ value: "' + cat.name + '", link: "' + get_link(cat) + '", category: "' + cat.quality +'" },'
    
    header = '<html><head>\
                <title>{0}</title>\
                <link rel="stylesheet" type="text/css" media="screen" href="/d2/style.css" />\
                <link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">\
                <script src="https://code.jquery.com/jquery-1.12.4.js"></script>\
                <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>\
                <script>\
                $(function(){{\
                  var availableTags = [{1}];\
                  $("#tags").autocomplete({{\
                    source: availableTags,\
                    select: function(event, ui) {{\
                      window.location.href = ui.item.link;\
                      return false;\
                    }}\
                  }});\
                  $("#tags").focus();\
                }});\
                </script>\
                </head><body>'.format(SITENAME, names)
    
    index_pages = ""
    for item_type, index_link in index_links:
        index_pages += '<p><a href="../{0}">{1}</a></p>'.format(index_link, item_type)
    
    body = get_body_header() + \
    "<div id='contentContainer'>\
        <p>type an item/set/attribute name</p>\
        <div class='ui-widget'>\
          <input spellcheck='false' id='tags' />\
        </div>\
        <hr class='item_seperator' />\
        <p class='header'>indexes</p>\
        {0}\
        <p class='header'>tools</p>\
        <p><a href='./create_guide.html'>create gear guide</a></p>\
      </div>\
    </div>".format(index_pages)

    html = header + body + get_footer()
    with open(HTML_DIR + "/index.html", 'w') as itemfile:
        itemfile.write(html)

def output_index_pages(items, sets, attributes, cat_dicts, guides):
    unique_items = [item for item in items if isinstance(item, UniqueItem)]
    set_items = [item for item in items if isinstance(item, SetItem)]
    rw_items = [item for item in items if isinstance(item, Runeword)]
    runes = [item for item in items if isinstance(item, Rune)]
    gems = [item for item in items if isinstance(item, Gem)]
    white_items = [item for item in items if isinstance(item, WhiteItem)]
    item_sets = sets
    
    #unique_attributes = []
    #for attribute in attributes:
    #    if len(attributes[attribute]) == 1:
    #        unique_attributes.append(attribute)
    
    items_types = [(unique_items, 'Unique Items'), (set_items, 'Set Items'), (item_sets, 'Item Sets'), (rw_items, 'Runewords'), (runes, 'Runes'), (gems, 'Gems'), (list(attributes), 'Attributes'), (white_items, 'White Items'), *[(list(d), n) for d, n in cat_dicts], (guides, 'Guides')]
    #, (unique_attributes, 'Rarely-occurring attributes')]
    
    links = []
    for items, item_type in items_types:
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="/d2/style.css" />\
                    </head><body>'.format(item_type, SITENAME)
        
        itemrows = ''
        items.sort(key=lambda item: item.name)
        for item in items:
            itemrows += '<tr class="attr_row"><td><a href="{0}" class="{2}">{1}</a></td></tr>'.format(get_link(item, True), item.name, item.quality)
        
        body = get_body_header() + \
        "<p class='attr_title'><strong>{0}</strong></p>\
          <table class='centerTable' id='attr_table'>\
          {1}\
          </table>\
        </div>".format(item_type, itemrows)
        
        html = header + body + get_footer()
        links.append((item_type, ROOT_DIR + "/" + item_type.lower().replace(" ", "_")+'.html'))
        with open(HTML_DIR + "/" + item_type.lower().replace(" ", "_")+'.html', 'w') as itemfile:
            itemfile.write(html)
    
    return links

def output_guide_creation_page(items, sets, attributes):
    classnames = ""
    for classname in classes:
        classnames += '{ value: "' + classname + '" },'
    
    item_types = [('Primary Weapon', 'weapon1', weapon_and_offhand_types), ('Shield/Other Weapon', 'weapon2', weapon_and_offhand_types), ('Off-hand Weapon', 'weapon3', weapon_and_offhand_types), ('Off-hand shield/Other Weapon', 'weapon4', weapon_and_offhand_types), ('Helm', 'helm', helm_types), ('Body armor', 'bodyarmor', body_armor_types), ('Belt', 'belt', belt_types), ('Gloves', 'gloves', glove_types), ('Boots', 'boots', boot_types), ('Amulet', 'amulet', amulet_types), ('Ring 1', 'ring1', ring_types), ('Ring 2', 'ring2', ring_types), ('Mercenary Weapon', 'mercweap', weapon_and_offhand_types), ('Mercenary Helm', 'merchelm', helm_types), ('Charms', 'charms', charm_types), ('Sockets', 'sockets', ['Socketable', 'Jewel']), ('White Items', 'white_items', [weapon_and_offhand_types + body_armor_types + helm_types])]
    
    Field = namedtuple('Field', 'name id type_vals')
    
    fields = []
    for title, idname, item_type_list in item_types:
        type_vals = ""
        for item in items:
            if isinstance(item, WhiteItem) and idname != 'white_items': continue
            types = item.type if isinstance(item.type, list) else [item.type]
            for typ in types:
                if typ.name in item_type_list:
                    type_vals += '{ value: "' + item.name + '", sockets: ' + str(item.num_possible_sockets) + ', ethereal: ' + str(item.can_spawn_ethereal).lower() + ', runeword: ' + str(item.quality == 'Runeword').lower() + ' },'
                    break
        fields.append(Field(title, idname, type_vals))
    
    white_items = fields[-1]
    fields = fields[:-1]
    
    sockets = fields[-1]
    fields = fields[:-1]
    
    charms = fields[-1]
    fields = fields[:-1]
    
    attr_type_vals = ""
    for attr in attributes:
        attr_type_vals += '{ value: "' + attr.name + '", link: "' + get_link(attr) + '", category: "' + attr.quality +'" },'
    
    fn_defs = "var attr_type_vals = [{0}];\n".format(attr_type_vals)
    fn_defs += "var sockets = [{0}];\n".format(sockets.type_vals)
    fn_defs += "var white_items = [{0}];\n".format(white_items.type_vals)
    fn_defs += "function new_field(type_vals, attr_name, field_id, val_field, qty_field)\n\
               {\n\
                 var field_container_id = '#custom_fields_'+field_id;\n\
                 var new_field_name = attr_name + '_'+field_id+'_' + Math.ceil($(field_container_id + ' > input').length/2);\n\
                 var new_field_html = \"<input spellcheck='false' placeholder='\"+new_field_name+\"' class='item_input \"+attr_name+\"' id='\" + new_field_name + \"' name='\" + new_field_name + \"' />\";\n\
                 if (val_field) {{\n\
                   new_field_html += \"<input placeholder='\"+new_field_name+\"_val' class='item_input' name='\"+new_field_name+\"_val' />\"\n\
                 }}\n\
                 if (qty_field) {{\n\
                   new_field_html += \"<input placeholder='\"+new_field_name+\"_qty' class='item_input' name='\"+new_field_name+\"_qty' />\"\n\
                 }}\n\
                 $(field_container_id).append(new_field_html);\n\
                 $('#'+new_field_name).autocomplete({ source: type_vals,\n\
                                                      select: function(event, ui) {\n\
                                                        new_field(type_vals, attr_name, field_id, val_field, qty_field);\n\
                                                      }});\n\
               }\n\
               function new_item_div(field_id, name, type_vals, spawn_new_field, qty_field)\n\
               {\n\
                 var plural = name + 's'; \n\
                 var field_container_id = '#'+plural+'_'+field_id;\n\
                 var field_num = $(field_container_id + ' > input').length;\n\
                 var new_field_name = name+'_'+field_id+'_' + field_num;\n\
                 var new_field_html = \"<input spellcheck='false' placeholder='\"+new_field_name+\"' class='item_input \"+name+\"' id='\" + new_field_name + \"' name='\" + new_field_name + \"' />\";\n\
                 var checkboxId = 'custom_'+name+field_num+'_'+field_id;\n\
                 new_field_html += \"<span class='field_name'><input type='checkbox' id='\"+checkboxId+\"' /> Custom \"+name+\"</span>\";\n\
                 $(field_container_id).append(new_field_html);\n\
                 if (spawn_new_field)\n\
                    $('#'+new_field_name).autocomplete({ source: type_vals,\n\
                                                         select: function(event, ui) {\n\
                                                           new_item_div(field_id, name, type_vals, spawn_new_field, qty_field);\n\
                                                         }});\n\
                 else\n\
                    $('#'+new_field_name).autocomplete({ source: type_vals });\n\
                 $('#'+checkboxId).change(function() {{\n\
                    if($(this).is(':checked')) {{\n\
                       $('#'+new_field_name).hide();\n\
                       $('#'+new_field_name).val('');\n\
                       new_field(attr_type_vals, 'attribute',plural+'_'+field_id, true, qty_field);\n\
                       return;\n\
                    }}\n\
                    $('#'+new_field_name).show();\n\
                    $('#custom_fields_'+plural+'_'+field_id).empty();\n\
                    \n\
                 }});\n\
               }\n"
    
    field_js = ""    
    for field in fields:
        field_js += "var {0} = [{1}];\n\
                     $('#{0}').autocomplete({{ source: {0},\n\
                       select: function(event, ui) {{\n\
                         $('#sockets_{0}').empty();\n\
                         for(i=0; i<ui.item.sockets; i++){{\n\
                           // here we add fields for each socket.\n\
                           new_item_div('{0}', 'socket', sockets, false, false);\n\
                         }}\n\
                         if (ui.item.runeword === true){{\n\
                           $('#runeword_base_{0}').show();\n\
                         }} else {{\n\
                           $('#runeword_base_{0}').hide();\n\
                         }}\n\
                         if (ui.item.ethereal === true){{\n\
                           $('#ethereal_{0}').show();\n\
                         }} else {{\n\
                           $('#ethereal_{0}').hide();\n\
                         }}\n\
                       }}\n\
                     }});\n\
                     $('#runeword_base_{0}_field').autocomplete({{ source: white_items }});\n\
                     $('#custom_item_{0}').change(function() {{\n\
                        if($(this).is(':checked')) {{\n\
                           $('#{0}').hide();\n\
                           $('#{0}').val('');\n\
                           $('.{0}').hide();\n\
                           $('#ethereal_{0}').hide();\n\
                           $('#runeword_base_{0}').hide();\n\
                           $('#sockets_{0}').empty();\n\
                           $('#custom_fields_sockets_{0}').empty();\n\
                           new_field(attr_type_vals, 'attribute', '{0}', true, false);\n\
                           return;\n\
                        }}\n\
                        $('#{0}').show();\n\
                        $('#custom_fields_{0}').empty();\n\
                        \n\
                     }});\n".format(field.id, field.type_vals)
    
    field_js += 'var {0} = [{1}];\n\
                 new_item_div("charm", "charm", charms, true, true);'.format(charms.id, charms.type_vals)
    field_js += "$('.socket').autocomplete({source: sockets});\n\
                 $('.ethereal').hide();\n\
                 $('.runeword_base').hide();\n"
    
    field_inputs = ""
    for field in fields:
        if 'socket' in field.id: continue
        field_inputs += "<div class='ui-widget'><fieldset>\n\
                          <legend class='item_header'>{1}</legend>\n\
                          <p class='item_selection'>\n\
                            <input spellcheck='false' placeholder='{0}' id='{0}' name='{0}' class='item_input {0}' />\n\
                            <span class='field_name runeword_base' id='runeword_base_{0}'><input spellcheck='false' placeholder='runeword_base_{0}' id='runeword_base_{0}_field' name='runeword_base_{0}_field' class='item_input {0}' /></span>\n\
                            <span class='field_name'><input type='checkbox' id='custom_item_{0}' /> Custom item</span>\n\
                            <div id='custom_fields_{0}'></div>\n\
                            <div id='sockets_{0}'></div>\n\
                            <div id='custom_fields_sockets_{0}'></div>\n\
                            <span class='field_name ethereal' id='ethereal_{0}'><input type='checkbox' name='ethereal_{0}' /> Ethereal</span>\n\
                          </p>\n\
                          <textarea name='{0}_desc' id='{0}_desc' class='item_desc' rows='1' />Description</textarea>\n\
                        </fieldset></div>\n".format(field.id, field.name)
    
    field_inputs += "<div class='ui-widget'><fieldset>\n\
                       <legend class='item_header'>Charms</legend>\n\
                       <div id='charms_charm'></div>\n\
                       <div id='custom_fields_charms_charm'></div>\n\
                       <p></p><p></p>\n\
                       <textarea name='charms_desc' id='charms_desc' class='item_desc' rows='1' />Description</textarea>\n\
                     </fieldset></div>\n"
    
    # auto resizing textarea
    # ref: https://stackoverflow.com/questions/454202/creating-a-textarea-with-auto-resize
    header = '<html><head>\n\
                <title>{0} -- {1}</title>\n\
                <link rel="stylesheet" type="text/css" media="screen" href="/d2/style.css" />\n\
                <link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">\n\
                <script src="https://code.jquery.com/jquery-1.12.4.js"></script>\n\
                <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>\n\
                <script>\n\
                {4}\n\
                $(function(){{\n\
                  var classnames = [{2}];\n\
                  $("#classname").autocomplete({{ source: classnames }});\n\
                  {3}\n\
                  $("#name").focus();\n\
                  $(".socket").hide();\n\
                  $("textarea").each(function(){{\n\
                    this.setAttribute("style", "height:" + (this.scrollHeight) + "px;overflow-y:hidden;");\n\
                  }}).on("input", function(){{\n\
                    this.style.height = "auto";\n\
                    this.style.height = (this.scrollHeight) + "px";\n\
                  }});\n\
                }});\n\
                </script>\n\
                </head><body>'.format("Create a Gear Guide", SITENAME, classnames, field_js, fn_defs)
    
    body = get_body_header() + \
    "<div id='contentContainer'>\n\
        <form action='/cgi-bin/create_guide.py' method='post'>\n\
          <div id='guide_form'>\n\
            <p><input type='text' placeholder='Gear Guide Name' name='name' id='name' /></p>\n\
            <div class='ui-widget'>\n\
              <p><input spellcheck='false' placeholder='classname' id='classname' name='classname' /></p>\n\
            </div>\n\
            <p><input type='text' placeholder='Link to guide (optional)' name='link' id='link' /></p>\n\
            {0}\n\
            <p></p>\n\
            <button type='submit'>Submit</button>\n\
          </div>\n\
        </form>\n\
      </div>\n\
    </div>".format(field_inputs)
        
    html = header + body + get_footer()
    with open(HTML_DIR + "/create_guide.html", 'w') as itemfile:
        itemfile.write(html)

def output_guides(guides):
    for guide in guides:
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="/d2/style.css" />\
                    </head><body>'.format(guide.name, SITENAME)
    
        body = "<div class='item_container'>\n\
                  <p class='item_name'>{0}</p>\n\
                  <p class='item_type'>{1}</p>\n".format(guide.name, guide.classname)
        if guide.link is not None:
            body += "<p class='item_type'><a href='{0}'>more details</a></p>".format(guide.link)
        
        for gear_piece in guide.gear_pieces:
            body += "<div class='item_container'>\n"
            if gear_piece.matched_item is not None:
                body += "<p class='item_name {0}'>{1}</p>\n".format(gear_piece.matched_item.quality, "<a href='"+get_link(gear_piece.matched_item)+"'>"+gear_piece.matched_item.name+"</a>")
            else:
                body += "<p class='item_attrs attr'>{0}</p>\n".format(get_html_for_attrs(gear_piece.custom_atts, lambda name: True))
            if gear_piece.ethereal:
                body += "<p class='ethereal'>(Ethereal)</p>\n"
            if gear_piece.runeword_base is not None:
                body += "<p class='item_name_small white>{0}</p>\n".format("<a href='"+get_link(gear_piece.runeword_base)+"'>"+gear_piece.runeword_base.name+"</a>")
            if len(gear_piece.sockets) > 0 or len(gear_piece.custom_socket_atts) > 0:
                body += "<p>Sockets</p>\n"
            for socket in gear_piece.matched_sockets:
                body += "<p class='item_name_small {0}'>{1}</p>\n".format(socket.quality, "<a href='"+get_link(socket)+"'>"+socket.name+"</a>")
            if len(gear_piece.custom_socket_atts) > 0:
                body += "<p class='item_attrs attr'>{0}</p>\n".format(get_html_for_attrs(gear_piece.custom_socket_atts, lambda name: True))
            if len(gear_piece.desc) > 0:
                body += "<p>{0}</p>\n".format(gear_piece.desc)
            body += "</div>"
        
        body += "</div>"
        
        html = header + body + get_footer()
        with open(get_link(guide, False), 'w') as itemfile:
            itemfile.write(html)

def make_website():
    items, sets, attributes = load_data()
    guides = load_guides()
    
    setup_dirs()
    
    cat_dicts = []
    for cat_name, disp_name in [('tier', 'Item Tiers'), ('type', 'Item Types'), ('stype', 'Item Subtypes')]:
        cat_dict = get_cat_dict(items, cat_name)
        output_cat_files(cat_dict)
        cat_dicts.append((cat_dict, disp_name))
    
    index_links = output_index_pages(items, sets, attributes, cat_dicts, guides)
    output_guides(guides)
    output_item_files(items, index_links)
    output_runeword_files(items)
    output_set_files(sets)
    output_rune_files(items)
    output_gem_files(items)
    output_attribute_files(attributes)
    output_guide_creation_page(items, sets, attributes)
    output_main_page(items, sets, attributes, cat_dicts, index_links)

if __name__ == '__main__':
    make_website()