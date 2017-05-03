import re, shutil
from item import *
from get_items import *
from collections import defaultdict

if not os.path.exists("items.dll"):
    items = get_items_from_summit()
    with open("items.dll", 'wb') as output:
        dill.dump(items, output)
else:
    items = dill.load(open("items.dll", 'rb'))

print("Num items:", len(items))

# produce html pages for each item.

SITENAME = "Weizor's Grimoire"
HTML_DIR = './html'
if not os.path.exists(HTML_DIR):
    os.makedirs(HTML_DIR)
    os.makedirs(HTML_DIR + "/items")
    os.makedirs(HTML_DIR + "/attrs")

shutil.copyfile("style.css", HTML_DIR + "/style.css")

def get_link(dirname, item_name):
    return HTML_DIR + "/" + dirname + "/" + item_name.lower().replace(" ", "_").replace("'", "").replace("/", "_").replace(":", "") + ".html"

for item in items:
    base_attrs = ""
    end_attrs = ""
    attrs = ""
    for attr in item.attr_dict:
        attr_text = item.attr_dict[attr].text.lower()
        match = re.search(attr.highlight_regex, attr_text)
        
        if not match:
            print(attr_text, " couldnt be matched to", attr.highlight_regex)
            raise Exception
        
        text_match = attr_text[match.span()[0]:match.span()[1]]
        text_match_link = '<a href="../../' + get_link('attrs', attr.name) + '">' + text_match + '</a>'
        attr_text = attr_text.replace(text_match, text_match_link)
        
        if attr.name in start_atts:
            base_attrs += attr_text + "<br />"
        elif attr.name in end_atts:
            end_attrs += attr_text + "<br />"
        else:
            attrs += attr_text + "<br />"
    
    base_attrs = base_attrs[:-6].lower()
    end_attrs = end_attrs[:-6].lower()
    attrs = attrs[:-6].lower()

    header = '<html><head>\
                <title>{0} -- {1}</title>\
                <link rel="stylesheet" type="text/css" media="screen" href="../style.css" />\
                </head><body>'.format(item.name, SITENAME)
    
    body = "<div id='container'>\
      <div id='headerContainer'>\
        <p id='headerText'><a href='/d2/'>weizor's grimoire</a></p>\
    	<div id='navContainer'>\
    	  <table class='centerTable' id='navTable'><tr>\
    	    <td><a href='/items/'>items directory</a></td>\
    	  </tr></table><br />\
        </div>\
      </div>\
      <div id='item_container'>\
        <p id='item_name' class='{5}'>{0}</p>\
        <p id='item_image_p'><img src='{1}' alt='{0}' /></p>\
        <p id='item_stype'>{5} {4}</p>\
        <p id='item_type'>({2}{3})</p>\
        <p id='item_attrs_small'>{6}</p>\
        <p id='item_attrs' class='attr'>{7}</p>\
        <p id='item_attrs_small'>{8}</p>\
      </div>\
    </div>".format(item.name, item.imagepath, item.tier + " " if len(item.tier) > 0 else "", item.type, item.stype, item.quality, base_attrs, attrs, end_attrs)
    
    footer = '</body></html>' 
    
    html = header + body + footer
    with open(get_link('items', item.name), 'w') as itemfile:
        itemfile.write(html)

# create the attribute files...

# determine the items associated with each attribute

items_per_attribute = defaultdict(list)
for item in items:
    for attr in item.attr_dict:
        items_per_attribute[attr].append((item, item.attr_dict[attr]))

for attribute in items_per_attribute:
    if len(items_per_attribute[attribute]) == 0:
        continue
        
    items_per_attribute[attribute].sort(key=lambda tup: tup[1].sort_value, reverse=True)
    
    itemrows = ''
    for item, item_attr in items_per_attribute[attribute]:
        itemrows += '<tr class="attr_row"><td><a href="{0}" class="{3}">{1}</a></td><td>{2}</td></tr>'.format('../../' + get_link('items', item.name), item.name, item_attr.value_text, item.quality)
    
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
      <p id='attr_title'><strong>{1}</strong></p>\
      <table class='centerTable' id='attr_table'>\
      {0}\
      </table>\
    </div>".format(itemrows, attribute.name)
    
    footer = '</body></html>' 
    
    html = header + body + footer
    with open(get_link('attrs', attribute.name), 'w') as itemfile:
        itemfile.write(html)