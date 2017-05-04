import re, shutil
from item import *
from get_items import *
from collections import defaultdict

SITENAME = "Weizor's Grimoire"
HTML_DIR = './html'

def setup_dirs():
    if not os.path.exists(HTML_DIR):
        os.makedirs(HTML_DIR)
        os.makedirs(HTML_DIR + "/items")
        os.makedirs(HTML_DIR + "/sets")
        os.makedirs(HTML_DIR + "/attrs")
    shutil.copyfile("style.css", HTML_DIR + "/style.css")

def get_link(dirname, item_name):
    return HTML_DIR + "/" + dirname + "/" + item_name.lower().replace(" ", "_").replace("'", "").replace("/", "_").replace(":", "") + ".html"

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
        text_match_link = '<a href="../../' + get_link('attrs', attr.name) + '">' + text_match + '</a>'
        attr_text = attr_text.replace(text_match, text_match_link)
        html += attr_text + "<br />"
    return html[:-6].lower()

def output_item_files(items):
    for item in items:
        base_attrs = get_html_for_attrs(item.attr_dict, lambda name: name in start_atts)
        end_attrs = get_html_for_attrs(item.attr_dict, lambda name: name in end_atts)
        attrs = get_html_for_attrs(item.attr_dict, lambda name: name not in start_atts and name not in end_atts)
    
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="../style.css" />\
                    </head><body>'.format(item.name, SITENAME)
    
        if isinstance(item, UniqueItem):
            typeinfo = item.tier + " " if len(item.tier) > 0 else "", item.type
        elif isinstance(item, SetItem):
            typeinfo = "<a href='../../"+get_link('sets', item.set_name)+"'>"+item.set_name+"</a>"
    
        body = "<div id='container'>\
          <div id='headerContainer'>\
            <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\
        	<div id='navContainer'>\
        	  <table class='centerTable' id='navTable'><tr>\
        	    <td><a href='/items/'>items directory</a></td>\
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
        with open(get_link('items', item.name), 'w') as itemfile:
            itemfile.write(html)

def output_set_files(sets):
    for itemset in sets:
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="../style.css" />\
                    </head><body>'.format(itemset.set_name, SITENAME)
    
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
                </div><hr class='item_seperator' />".format(item.name, item.imagepath, item.quality, base_attrs, attrs, end_attrs, "<a href='../../"+get_link('items', item.name)+"'>"+item.name+"</a>")
    
        set_bonuses = get_html_for_attrs(itemset.set_bonuses, lambda name: True)
    
        body = "<div id='container'>\
          <div id='headerContainer'>\
            <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\
        	<div id='navContainer'>\
        	  <table class='centerTable' id='navTable'><tr>\
        	    <td><a href='/items/'>items directory</a></td>\
        	  </tr></table><br />\
            </div>\
          </div>\
          <p class='item_name set'>{0}</p>\
          {2}\
          <p class='set_bonuses_title'>Set Bonuses</p>\
          <p class='set_bonuses'>{1}</p>\
        </div>".format(itemset.set_name, set_bonuses, setitemrows)
    
        footer = '</body></html>' 
    
        html = header + body + footer
        with open(get_link('sets', itemset.set_name), 'w') as itemfile:
            itemfile.write(html)

def output_attribute_files(items, sets):
    items_per_attribute = defaultdict(list)
    for item in items:
        for attr in item.attr_dict:
            items_per_attribute[attr].append((item, item.attr_dict[attr]))
    
    for itemset in sets:
        for attr in itemset.set_bonuses:
            items_per_attribute[attr].append((itemset, itemset.set_bonuses[attr]))
    
    for attribute in items_per_attribute:
        if len(items_per_attribute[attribute]) == 0:
            continue
        
        items_per_attribute[attribute].sort(key=lambda tup: tup[1].sort_value, reverse=True)
    
        itemrows = ''
        for item, item_attr in items_per_attribute[attribute]:
            if isinstance(item, ItemSet):
                name = item.set_name
                quality = 'set'
                link = get_link('sets', item.set_name)
            elif isinstance(item, SetItem) or isinstance(item, UniqueItem):
                name = item.name
                quality = item.quality
                link = get_link('items', item.name)
            
            itemrows += '<tr class="attr_row"><td><a href="{0}" class="{3}">{1}</a></td><td>{2}</td></tr>'.format('../../' + link, name, item_attr.value_text, quality)
    
        # save file...
        header = '<html><head>\
                    <title>{0} -- {1}</title>\
                    <link rel="stylesheet" type="text/css" media="screen" href="../style.css" />\
                    </head><body>'.format(attribute.name, SITENAME)
    
        body = "<div id='container'>\
          <div id='headerContainer'>\
            <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\
        	<div id='navContainer'>\
        	  <table class='centerTable' id='navTable'><tr>\
        	    <td><a href='/items/'>items directory</a></td>\
        	  </tr></table><br />\
            </div>\
          </div>\
          <p class='attr_title'><strong>{1}</strong></p>\
          <table class='centerTable' id='attr_table'>\
          {0}\
          </table>\
        </div>".format(itemrows, attribute.name)
    
        footer = '</body></html>' 
    
        html = header + body + footer
        with open(get_link('attrs', attribute.name), 'w') as itemfile:
            itemfile.write(html)

def make_website():
    if not os.path.exists("items.dll"):
        items = get_items_from_summit()
        with open("items.dll", 'wb') as output:
            dill.dump(items, output)
    else:
        items = dill.load(open("items.dll", 'rb'))
    
    print("Num items:", len(items))
    
    sets = get_sets_from_items(items)
    
    setup_dirs()
    output_item_files(items)
    output_set_files(sets)
    output_attribute_files(items, sets)

if __name__ == '__main__':
    make_website()