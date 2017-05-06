import re, shutil
from item import *
from get_items import *
from collections import defaultdict

SITENAME = "Weizor's Grimoire"
HTML_DIR = './html'

def setup_dirs():
    if not os.path.exists(HTML_DIR):
        os.makedirs(HTML_DIR)
        os.makedirs(HTML_DIR + "/unique")
        os.makedirs(HTML_DIR + "/set")
        os.makedirs(HTML_DIR + "/attribute")
        os.makedirs(HTML_DIR + "/runeword")
        os.makedirs(HTML_DIR + "/rune")
    shutil.copyfile("style.css", HTML_DIR + "/style.css")
    if not os.path.exists(HTML_DIR + "/js"):
        shutil.copytree("js", HTML_DIR + "/js")

def get_link(item):
    return HTML_DIR + "/" + item.quality.lower() + "/" + item.name.lower().replace("%", "pct").replace("+", "plus").replace("-", "neg").replace("(", "").replace(")", "").replace(" ", "_").replace("'", "").replace("/", "_").replace(":", "") + ".html"

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
        text_match_link = '<a href="../../' + get_link(attr) + '">' + text_match + '</a>'
        attr_text = attr_text.replace(text_match, text_match_link)
        html += attr_text + "<br />"
    return html[:-6].lower()

def output_item_files(items):
    for item in items:
        if isinstance(item, Runeword) or item.type == 'socketable': continue
        base_attrs = get_html_for_attrs(item.attr_dict, lambda name: name in start_atts)
        end_attrs = get_html_for_attrs(item.attr_dict, lambda name: name in end_atts)
        attrs = get_html_for_attrs(item.attr_dict, lambda name: name not in start_atts and name not in end_atts)
    
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="../style.css" />\
                    </head><body>'.format(item.name, SITENAME)
    
        if isinstance(item, UniqueItem):
            typeinfo = item.tier + (" " if len(item.tier) > 0 else "")
            typeinfo += item.type
        elif isinstance(item, SetItem):
            typeinfo = "<a href='../../"+get_link(item.set)+"'>"+item.set_name+"</a>"
    
        body = "<div id='container'>\
          <div id='headerContainer'>\
            <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\
        	<div id='navContainer'>\
        	  <table class='centerTable' id='navTable'><tr>\
        	    <td><a href='../index.html'>items directory</a></td>\
        	  </tr></table><br />\
            </div>\
          </div>\
          <div class='item_container'>\
            <p class='item_name {4}'>{0}</p>\
            <p class='item_image_p'><img src='{1}' alt='{0}' /></p>\
            <p class='item_stype'>{4} {3}</p>\
            <p class='item_type'>({2})</p>\
            <p class='item_attrs_small'>{5}</p>\
            <p class='item_attrs attr'>{6}</p>\
            <p class='item_attrs_small'>{7}</p>\
          </div>\
        </div>".format(item.name, item.imagepath, typeinfo, item.stype, item.quality, base_attrs, attrs, end_attrs)
    
        footer = '</body></html>' 
    
        html = header + body + footer
        with open(get_link(item), 'w') as itemfile:
            itemfile.write(html)

def output_rune_files(items):
    for item in items:
        if item.quality != 'Rune': continue
        
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="../style.css" />\
                    </head><body>'.format(item.name, SITENAME)
        
        weap_attrs = get_html_for_attrs(item.attr_dict_weap, lambda name: True)
        armor_attrs = get_html_for_attrs(item.attr_dict_armor, lambda name: True)
        helm_attrs = get_html_for_attrs(item.attr_dict_helm, lambda name: True)
        shield_attrs = get_html_for_attrs(item.attr_dict_shield, lambda name: True)
        
        runewords = ""
        for rw_item in items:
            if isinstance(rw_item, Runeword) and item.name.split(" ")[0] in rw_item.runes:
                runewords += "<a href='../../"+get_link(rw_item)+"'>"+rw_item.name+"</a><br />"
        runewords = runewords[:-6]
        
        body = "<div id='container'>\
          <div id='headerContainer'>\
            <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\
        	<div id='navContainer'>\
        	  <table class='centerTable' id='navTable'><tr>\
        	    <td><a href='../index.html'>items directory</a></td>\
        	  </tr></table><br />\
            </div>\
          </div>\
          <div class='item_container'>\
            <p class='item_name rune'>{0}</p>\
            <p class='item_image_p'><img src='{1}' alt='{0}' /></p>\
            <p class='item_type'>(Rune)</p>\
            <p class='item_attrs_small'>Required Level: {2}</p>\
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
    
        footer = '</body></html>' 
    
        html = header + body + footer
        with open(get_link(item), 'w') as itemfile:
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
            rune_links += "<a href='../../"+get_link([i for i in items if rune+" Rune"==i.name][0])+"'>"+rune+"</a> + "
            rune_images += "<a href='../../"+get_link([i for i in items if rune+" Rune"==i.name][0])+"'><img src='http://classic.battle.net/images/battle/diablo2exp/images/runes/rune"+rune.replace("Jah", "Jo").replace("Shael", "Shae")+".gif' alt='"+rune+"'/></a>"
        rune_links = rune_links[:-3]
            
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="../style.css" />\
                    </head><body>'.format(item.name, SITENAME)
            
        body = "<div id='container'>\
          <div id='headerContainer'>\
            <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\
        	<div id='navContainer'>\
        	  <table class='centerTable' id='navTable'><tr>\
        	    <td><a href='../index.html'>items directory</a></td>\
        	  </tr></table><br />\
            </div>\
          </div>\
          <div class='item_container'>\
            <p class='item_name runeword'>{0}</p>\
            <p class='item_stype'>{1}</p>\
            <p class='item_runes'>{6}</p>\
            <p class='item_type'>{2}</p>\
            <p class='item_attrs_small'>{3}</p>\
            <p class='item_attrs attr'>{4}</p>\
            <p class='item_attrs_small'>{5}</p>\
          </div>\
        </div>".format(item.name, rune_links, item.allowed_items, base_attrs, attrs, end_attrs, rune_images)
    
        footer = '</body></html>' 
    
        html = header + body + footer
        with open(get_link(item), 'w') as itemfile:
            itemfile.write(html)

def output_set_files(sets):
    for itemset in sets:
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="../style.css" />\
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
                </div><hr class='item_seperator' />".format(item.name, item.imagepath, item.quality, base_attrs, attrs, end_attrs, "<a href='../../"+get_link(item)+"'>"+item.name+"</a>")
    
        set_bonuses = get_html_for_attrs(itemset.set_bonuses, lambda name: True)
    
        body = "<div id='container'>\
          <div id='headerContainer'>\
            <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\
        	<div id='navContainer'>\
        	  <table class='centerTable' id='navTable'><tr>\
        	    <td><a href='../index.html'>items directory</a></td>\
        	  </tr></table><br />\
            </div>\
          </div>\
          <p class='item_name set'>{0}</p>\
          {2}\
          <p class='set_bonuses_title'>Set Bonuses</p>\
          <p class='set_bonuses'>{1}</p>\
        </div>".format(itemset.name, set_bonuses, setitemrows)
    
        footer = '</body></html>' 
    
        html = header + body + footer
        with open(get_link(itemset), 'w') as itemfile:
            itemfile.write(html)

def output_attribute_files(items_per_attribute):
    for attribute in items_per_attribute:
        if len(items_per_attribute[attribute]) == 0:
            continue
        
        items_per_attribute[attribute].sort(key=lambda tup: tup[1].sort_value, reverse=True)
        
        has_val_text = []
        for item, item_attr in items_per_attribute[attribute]:
            has_val_text.append(len(item_attr.value_text) > 0)
        display_value_column = sum(has_val_text) > 0
        
        if not display_value_column:
            items_per_attribute[attribute].sort(key=lambda tup: tup[0].name)
    
        itemrows = ''
        for item, item_attr in items_per_attribute[attribute]:
            itemrows += '<tr class="attr_row"><td><a href="{0}" class="{2}">{1}</a></td>'.format('../../' + get_link(item), item.name, item.quality)
            if display_value_column:
                itemrows += "<td>{0}</td>".format(item_attr.value_text)
            itemrows += "</tr>"
        
        table_headers = "<th class='attr_table_header' data-sort='string'>item</th>"
        if display_value_column:
            table_headers += "<th class='attr_table_header' data-sort='range_string'>value</th>"
        
        # save file...
        # ref sorting: https://github.com/joequery/Stupid-Table-Plugin#readme
        # ref sort(a,b): https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="../style.css" />\
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
                    </head><body>'.format(attribute.name, SITENAME)
    
        body = "<div id='container'>\
          <div id='headerContainer'>\
            <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\
        	<div id='navContainer'>\
        	  <table class='centerTable' id='navTable'><tr>\
        	    <td><a href='../index.html'>items directory</a></td>\
        	  </tr></table><br />\
            </div>\
          </div>\
          <p class='attr_title'><strong>{1}</strong></p>\
          <table class='centerTable' id='attr_table'>\
          <thead><tr>{2}</tr></thead><tbody>\
          {0}\
          </tbody></table>\
        </div>".format(itemrows, attribute.name, table_headers)
    
        footer = '</body></html>' 
    
        html = header + body + footer
        with open(get_link(attribute), 'w') as itemfile:
            itemfile.write(html)

def output_main_page(items, sets, attributes, index_links):
    names = ""
    for item in items + sets:
        names += '{ value: "' + item.name + '", link: "../' + get_link(item) + '", category: "' + item.quality +'" },'
    for attr in attributes:
        names += '{ value: "' + attr.name + '", link: "../' + get_link(attr) + '", category: "' + attr.quality +'" },'
    
    header = '<html><head>\
                <title>{0}</title>\
                <link rel="stylesheet" type="text/css" media="screen" href="../style.css" />\
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
    
    body = "<div id='container'>\
      <div id='headerContainer'>\
        <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\
    	<div id='navContainer'>\
    	  <table class='centerTable' id='navTable'><tr>\
    	    <td><a href='#'>items directory</a></td>\
    	  </tr></table><br />\
        </div>\
      </div>\
      <div id='contentContainer'>\
        <p>type an item/set/attribute name</p>\
        <div class='ui-widget'>\
          <input spellcheck='false' id='tags' />\
        </div>\
        <hr class='item_seperator' />\
        <p class='header'>indexes</p>\
        {0}\
      </div>\
    </div>".format(index_pages)

    footer = '</body></html>' 

    html = header + body + footer
    with open(HTML_DIR + "/index.html", 'w') as itemfile:
        itemfile.write(html)

def output_index_pages(items, sets, attributes):
    unique_items = [item for item in items if isinstance(item, UniqueItem)]
    set_items = [item for item in items if isinstance(item, SetItem)]
    rw_items = [item for item in items if isinstance(item, Runeword)]
    runes = [item for item in items if isinstance(item, Rune)]
    item_sets = sets
    
    items_types = [(unique_items, 'Unique Items'), (set_items, 'Set Items'), (item_sets, 'Item Sets'), (rw_items, 'Runewords'), (runes, 'Runes'), (list(attributes), 'Attributes')]
    
    links = []
    for items, item_type in items_types:
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="../style.css" />\
                    </head><body>'.format(item_type, SITENAME)
        
        itemrows = ''
        items.sort(key=lambda item: item.name)
        for item in items:
            itemrows += '<tr class="attr_row"><td><a href="{0}" class="{2}">{1}</a></td></tr>'.format('../' + get_link(item), item.name, item.quality)
        
        body = "<div id='container'>\
          <div id='headerContainer'>\
            <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\
        	<div id='navContainer'>\
        	  <table class='centerTable' id='navTable'><tr>\
        	    <td><a href='../index.html'>items directory</a></td>\
        	  </tr></table><br />\
            </div>\
          </div>\
          <p class='attr_title'><strong>{0}</strong></p>\
          <table class='centerTable' id='attr_table'>\
          {1}\
          </table>\
        </div>".format(item_type, itemrows)
    
        footer = '</body></html>' 
    
        html = header + body + footer
        links.append((item_type, HTML_DIR + "/" + item_type.lower().replace(" ", "_")+'.html'))
        with open(links[-1][1], 'w') as itemfile:
            itemfile.write(html)
    
    return links

def make_website():
    if not os.path.exists("items.dll"):
        items = get_items_from_summit()
        with open("items.dll", 'wb') as output:
            dill.dump(items, output)
    else:
        items = dill.load(open("items.dll", 'rb'))
    
    print("Num items:", len(items))
    
    sets, items = get_sets_from_items(items)
    attributes = get_global_attr_dict(items, sets)
    
    setup_dirs()
    output_item_files(items)
    output_runeword_files(items)
    output_set_files(sets)
    output_rune_files(items)
    output_attribute_files(attributes)
    index_links = output_index_pages(items, sets, attributes)
    output_main_page(items, sets, attributes, index_links)

if __name__ == '__main__':
    make_website()