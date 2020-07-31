import re, glob, shutil
from utils import load_data, load_guides, load_monsters
from item import *
from guide import *
from get_items import *
from collections import defaultdict
import MySQLdb
from config import *

SITENAME = "Weizor's Grimoire"

PRODUCTION_BUILD = True # set to False if testing on local mac webserver, to put cgi files in right place for default apache installation
#HTML_DIR = 'html/' # the directory in which the html files will be created (make sure you have write privileges)
HTML_DIR = '/Users/jcampbell/Sites/root/d2/'
CGI_DIR = '/Library/WebServer/CGI-Executables' if not PRODUCTION_BUILD else HTML_DIR+'cgi-bin/'
ROOT_DIR = '/d2/' # the site path that all links will start with. e.g. "/d2" for http://www.campbelljc.com/d2

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
        os.makedirs(HTML_DIR + "/guide")
        os.makedirs(CGI_DIR)
    with open(CGI_DIR+"/.htaccess", 'w') as f:
        f.write('AddHandler cgi-script .cgi .py\nOptions +ExecCGI\n')
    for file in glob.glob(r'*.py'):
        shutil.copy(file, CGI_DIR)
    for file in glob.glob(r'*.dll'):
        shutil.copy(file, CGI_DIR)
    for file in glob.glob(r'*.pkl'):
        shutil.copy(file, CGI_DIR)
    #os.system("chmod -R 755 "+CGI_DIR)
    #os.system("chmod a+rx "+CGI_DIR+"/create_guide.py")
    if os.path.exists(HTML_DIR + "/css"):
        shutil.rmtree(HTML_DIR + "/css")
    shutil.copytree("css", HTML_DIR + "/css")
    if os.path.exists(HTML_DIR + "/js"):
        shutil.rmtree(HTML_DIR + "/js")
    shutil.copytree("js", HTML_DIR + "/js")

def output_htaccess():
    contents = """RewriteEngine On

RewriteCond %{REQUEST_URI} !(css|js) [NC]
RewriteCond %{REQUEST_URI} "!=/d2/index.html"
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_METHOD} !POST
RewriteCond %{HTTP:X-Requested-With} !=XMLHttpRequest
RewriteCond %{HTTP:X-REQUESTED-WITH} !^(XMLHttpRequest)$
RewriteRule ^([^/]+)(/|$) /d2/index.html#%{REQUEST_URI} [L,NE,R=302]"""
    
    with open(HTML_DIR + "/.htaccess", 'w') as f:
        f.write(contents)

def get_link(item, root=True):
    link = "/" + item.quality.lower() + "/" + item.name.lower().replace("%", "pct").replace("+", "plus").replace("-", "neg").replace("(", "").replace(")", "").replace(" ", "_").replace("'", "").replace("/", "_").replace(":", "")
    if type(item) is Item and item.ethereal:
        link += '_eth'
    link += ".html"
    if root:
        return ROOT_DIR + link
    else:
        return HTML_DIR + link

def get_html_for_attributes(item_name, item_attrs, selection_fns):
    attr_htmls = []
    
    if not isinstance(item_attrs, list):
        item_attrs = [item_attrs]
    if not isinstance(selection_fns, list):
        selection_fns = [selection_fns]
    
    num_htmls = max(len(item_attrs), len(selection_fns))
    if len(item_attrs) < num_htmls:
        item_attrs = [item_attrs[0]] * num_htmls
    if len(selection_fns) < num_htmls:
        selection_fns = [selection_fns[0]] * num_htmls
    
    for attr_dict, selection_fn in zip(item_attrs, selection_fns):
        html = ""
        attr_max_vals = []
        
        # create html
        for i, attr in enumerate(attr_dict):
            if not selection_fn(attr.name): continue
        
            attr_text = attr_dict[attr].text.lower()
            match = re.search(attr.highlight_regex, attr_text)
        
            if not match:
                raise Exception(attr_text + " couldn't be matched to " + attr.highlight_regex)
        
            text_match = attr_text[match.span()[0]:match.span()[1]]
            text_match_link = '<a href="' + get_link(attr) + '">' + text_match + '</a>'
            attr_text = attr_text.replace(text_match, text_match_link)
            html += attr_text
            if attr_dict[attr].varies:
                html += """ <input spellcheck='false' type='text' id='attr_{0}' class='attr_db' size="3" />""".format(len(attr_max_vals))
                attr_max_vals.append('') #attr_dict[attr].max_value)
            html += "<br />"
        
        html = html[:-6].lower()
        
        # script for db/inputs
        item_name = item_name.replace("'", "")
        script = """
                    <script type="text/javascript">\n
                    db.items.add({{\n
                        name: '{0}',\n
                        attributes: {1}\n
                    }});\n
                    \n
                    db.items.where('name').equals('{0}').toArray().then( function(item_arr) {{\n
                        item = item_arr[0];\n
                      """.format(item_name, str(attr_max_vals) if len(attr_max_vals) > 0 else "['']")
    
        for tag_id in range(len(attr_max_vals)):
            script += """
                        $('#attr_{0}').val(item.attributes[{0}]);\n
                        $('#attr_{0}').change(function() {{\n
                            attrs = item.attributes;\n
                            attrs[{0}] = $('#attr_{0}').val();\n
                            db.items.put({{\n
                                name: '{1}',\n
                                attributes: attrs,\n
                                characters: item.characters\n
                            }});\n
                        }});\n
            """.format(tag_id, item_name);
    
        script += """
                    });\n
                    </script>\n"""
        
        html += script
        attr_htmls.append(html)
    
    return attr_htmls

def get_footer(dexie=False):
    footer = """
        </div>\n\
            <div id='lowerContainer'>\n
	          <div id='blurContainer'></div>\n
                 <div id='footer'>\n
                   <p class='centerText'>all content on this site is &copy; 2001-2020 blizzard entertainment.</p>\n
                 </div>\n
              </div>\n
        </div>\n"""
    if dexie:
        footer += """
        <script>\n
            db.config.toArray().then( function(arr) {{\n
                show_fields = arr[0];
                //if (show_fields.status == 0) {
                //    $(".attr_db").hide();
                //}
            }});
        </script>\n"""
    return footer + """</body></html>"""

def get_header(page_title=None, script=None, jquery=False, jquery_ui=False, stupidtable=False, dexie=False, table=False):
    if page_title is None:
        page_title = SITENAME
    else:
        page_title = page_title + " -- " + SITENAME
    header = """
            <html><head>\n
                <title>{0}</title>\n
                <link rel="stylesheet" type="text/css" media="screen" href="/d2/css/style.css" />\n
                <meta charset="utf-8"/>\n
            """.format(page_title)
    if jquery:
        header += '<script src="https://code.jquery.com/jquery-1.12.4.js"></script>'
    if jquery_ui:
        assert jquery
        header += '<link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">\
                   <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>'
    if stupidtable:
        header += '<script src="js/stupidtable.min.js"></script>'
    if dexie:
        assert jquery
        header += """<script src="https://unpkg.com/dexie@latest/dist/dexie.js"></script>
                   <script src="https://unpkg.com/dexie-export-import/dist/dexie-export-import.js"></script>
                   <script src="https://cdnjs.cloudflare.com/ajax/libs/downloadjs/1.4.8/download.min.js"></script>
                   <script type="text/javascript">
                       var db = new Dexie("grimoire");
                       db.version(1).stores({
                           items: 'name, *attributes, *characters',
                           config: 'show_fields, status',
                           characters: '++id, account, &name'
                       });
                       db.config.add({
                           show_fields: 0,
                           status: 0
                       });
                   </script>"""
    if table:
        header += """
                    <script type="text/javascript" src="js/table.js"></script>
                    <link rel="stylesheet" type="text/css" href="/d2/css/table.css" />
                  """
    if script:
        header += '<script type="text/javascript">' + script + '</script>'
    header += """
            </head><body>"""
    return header

def get_item_collection_db_html(item):
    body = """
        <hr class='item_separator' />
        <p class="attr_db">
            add new character
            <div class='ui-widget'>
              <input spellcheck='false' id='character_input' class='attr_db' />
            </div>
            
            <table id="character_table"><thead><tr>
                <th>Account</th>
                <th>Character</th>
                <th>Notes</th>
                <th>Qty</th>
            </tr></thead></table>
        </p>
        <script>
            db.items.where('name').equals('"""+item.name.replace("'", "")+"""').toArray().then( function(item_arr) {\n
                item = item_arr[0];
                char_data = item.characters;
                
                var table = new Table({
                    id: "character_table",
                    fields: {
                        "Account": {
                            "class": "edit",
                            "type:": "string"
                        },
                        "Character": {
                            "class": "edit",
                            "type:": "string"
                        },
                        "Notes": {
                            "class": "edit",
                            "type:": "string"
                        },
                        "Qty": {
                            "class": "edit",
                            "type:": "number"
                        }
                    },
                    data: char_data,
                    direction: "desc",
                    debug: true
                });
                table.render();
            
                // populate char input autocomplete
                db.characters.toArray().then( function(chars) {
                    var char_names = [];
                    var char_accs = []
                    chars.forEach(function(char) {
                        char_names.push(char.name);
                        char_accs.push(char.account);
                    });
                    $("#character_input").bind( "keydown", function( event ) {
                        if ( event.keyCode === $.ui.keyCode.ENTER && !$(this).data("selectVisible") ) {
                            // add current char input value to the DB and autocomplete list.
                            table.addRow({ data: ["", $(this).val(), "", ""] });
                        }
                    });
                    $("#character_input").autocomplete({
                        source: char_names,
                        select: function(event, ui) {
                            ind = char_names.findIndex(k => k==ui.item.value);
                            table.addRow({ data: [char_accs[ind], char_names[ind], ""] });
                            return false;
                        },
                        open: function() {
                            $(this).data("selectVisible", true);
                        },
                        close: function() {
                            $(this).data("selectVisible", false);
                        }
                    });
                    $("#character_table").on("table_updated", function(event) {
                        var table_data = table.serialize();
                    
                        // store char/acc/notes data in items db
                        db.items.where('name').equals('"""+item.name.replace("'", "")+"""').toArray().then( function(item_arr) {\n
                            item = item_arr[0];
                            db.items.put({
                                name: item.name,
                                attributes: item.attributes,
                                characters: table_data,
                                link: '""" + get_link(item) +  """',
                                quality: '""" + item.quality +  """'
                            });
                        });
                    
                        // store char/acc data in chars db
                        $.each(table_data, function(index, row) {
                            db.characters.put({
                                account: row.Account,
                                name: row.Character
                            });
                        });
                    });
                });
            });
        </script>
    """
    return body

def output_item_file(item, indexes, guides, monsters):
    base_attrs, attrs, end_attrs = get_html_for_attributes(item.name, item.attr_dict, [lambda name: name in start_atts, lambda name: name in end_atts, lambda name: name not in start_atts and name not in end_atts])

    matched_link = None
    for item_type, index_link in indexes:
        if item_type.lower().split()[0] == item.quality.lower():
            matched_link = index_link
    
    quality = item.quality
    if matched_link is not None:
        quality = '<a href="../../../'+matched_link+'">'+quality+'</a>'
    
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

    body = "<div class='item_container'>\
        <p class='item_name {9}'>{0}</p>\
        {8}\
        <p class='item_image_p'><img src='{1}' alt='{0}' /></p>\
        <p class='item_stype'>{4} {3}</p>\
        <p class='item_type'>({2})</p>\
        <p class='item_attrs_small'>{5}</p>\
        <p class='item_attrs attr'>{6}</p>\
        <p class='item_attrs_small'>{7}</p>\
      </div>".format(item.name, item.imagepath, typeinfo, stypeinfo, quality, base_attrs, attrs, end_attrs, set_info, item.quality)
    
    # collector info
    body += get_item_collection_db_html(item)
    
    # guide listing
    rows = ''
    for guide in guides:
        for gear_piece in guide.gear_pieces:
            if gear_piece.matched_item is not None and gear_piece.matched_item == item:
                rows += "<tr><td><a href='{1}'>{0}</a></td></tr>".format(guide.name, get_link(guide))
                break
    if len(rows) > 0:
        body += """<hr class='item_separator' />
            <p class="attr_db">
                guides that list this item
                <table>
                {0}
                </table>
            </p>
        """.format(rows)
    
    rows = ''
    for monster in monsters:
        difficulties = ''
        for difficulty in monster.mlvls:
            if item.qlvl <= monster.mlvls[difficulty]:
                difficulties += '{0}, '.format(difficulty)
        if len(difficulties) > 0:
            rows += "<tr><td>{0} ({1})</td></tr>".format(monster.name, difficulties[:-2])

    body += """<hr class='item_separator' />
            <p class="attr_db">
                superuniques that can drop this item
                <table>
                {0}
                </table>
            </p>""".format(rows)
    
    #html = get_header(item.name, jquery=True, jquery_ui=True, dexie=True, table=True) + body + get_footer(dexie=True)
    with open(get_link(item, False), 'w') as itemfile:
        itemfile.write(body)

def output_rune_file(item):
    weap_attrs, armor_attrs, helm_attrs, shield_attrs = get_html_for_attributes(item.name, [item.attr_dict_weap, item.attr_dict_armor, item.attr_dict_helm, item.attr_dict_shield], lambda name: True)
    
    runewords = ""
    for rw_item in items:
        if isinstance(rw_item, Runeword) and item.name.split(" ")[0] in rw_item.runes:
            runewords += "<a href='"+get_link(rw_item)+"'>"+rw_item.name+"</a><br />"
    runewords = runewords[:-6]
    
    body = "<div class='item_container'>\
        <p class='item_name rune'>{0}</p>\
        <p class='item_image_p'><img src='{1}' alt='{0}' /></p>\
        <p class='item_type'>(<a href='runes.html'>Rune</a>)</p>\
        <p class='item_attrs_small'><a href='attribute/required_level.html'>Required Level</a>: {2}</p>\
        <table class='centerTable' id='rune_table'>\
        <tr><td class='attr_restriction'>Weapons</td><td>{3}</td></tr>\
        <tr><td class='attr_restriction'>Armor</td><td>{4}</td></tr>\
        <tr><td class='attr_restriction'>Helms</td><td>{5}</td></tr>\
        <tr><td class='attr_restriction'>Shields</td><td>{6}</td></tr>\
        </table>\
        <p>Runewords that use this rune:</p>\
        <p>{7}</p>\
        {8}\
      </div>".format(item.name, item.imagepath, item.rlvl, weap_attrs, armor_attrs, helm_attrs, shield_attrs, runewords, get_item_collection_db_html(item))

    #html = get_header(item.name) + body + get_footer()
    with open(get_link(item, False), 'w') as itemfile:
        itemfile.write(body)

def output_gem_file(item):
    weap_attrs, armor_attrs, helm_attrs, shield_attrs = get_html_for_attributes(item.name, [item.attr_dict_weap, item.attr_dict_armor, item.attr_dict_helm, item.attr_dict_shield], lambda name: True)
            
    body = "<div class='item_container'>\
        <p class='item_name gem'>{0}</p>\
        <p class='item_image_p'><img src='{1}' alt='{0}' /></p>\
        <p class='item_type'>(<a href='/d2/gems.html'>Gem</a>)</p>\
        <p class='item_attrs_small'><a href='attribute/required_level.html'>Required Level</a>: {2}</p>\
        <table class='centerTable' id='rune_table'>\
        <tr><td class='attr_restriction'>Weapons</td><td>{3}</td></tr>\
        <tr><td class='attr_restriction'>Armor</td><td>{4}</td></tr>\
        <tr><td class='attr_restriction'>Helms</td><td>{5}</td></tr>\
        <tr><td class='attr_restriction'>Shields</td><td>{6}</td></tr>\
        </table>\
      </div>".format(item.name, item.imagepath, item.rlvl, weap_attrs, armor_attrs, helm_attrs, shield_attrs)
    
    #html = get_header(item.name) + body + get_footer()
    with open(get_link(item, False), 'w') as itemfile:
        itemfile.write(body)

def output_runeword_file(item):
    base_attrs, attrs, end_attrs = get_html_for_attributes(item.name, item.attr_dict, [lambda name: name in start_atts, lambda name: name in end_atts, lambda name: name not in start_atts and name not in end_atts])
    
    rune_links = ""
    rune_images = ""
    for rune in item.runes:
        rune_links += "<a href='"+get_link([i for i in items if rune+" Rune"==i.name][0])+"'>"+rune+"</a> + "
        rune_images += "<a href='"+get_link([i for i in items if rune+" Rune"==i.name][0])+"'><img src='http://classic.battle.net/images/battle/diablo2exp/images/runes/rune"+rune.replace("Jah", "Jo").replace("Shael", "Shae")+".gif' alt='"+rune+"'/></a>"
    rune_links = rune_links[:-3]
    
    typeinfo = ""
    types = item.type if isinstance(item.type, list) else [item.type]
    for typ in types:
        typeinfo += '<a href="'+get_link(typ)+'">'+typ.name+'</a> / '
    typeinfo = typeinfo[:-3]
    
    body = "<div class='item_container'>\
        <p class='item_name runeword'>{0}</p>\
        <p class='item_stype'>{1}</p>\
        <p class='item_runes'>{6}</p>\
        <p class='item_type'>{2}</p>\
        <p class='item_attrs_small'>{3}</p>\
        <p class='item_attrs attr'>{4}</p>\
        <p class='item_attrs_small'>{5}</p>\
      </div>".format(item.name, rune_links, typeinfo, base_attrs, attrs, end_attrs, rune_images)
    
    #html = get_header(item.name, jquery=True, dexie=True) + body + get_footer(dexie=True)
    with open(get_link(item, False), 'w') as itemfile:
        itemfile.write(body)

def output_set_files(sets):
    for itemset in sets:
        setitemrows = ''
        for item in itemset.set_items:
            base_attrs, attrs, end_attrs = get_html_for_attributes(item.name, item.attr_dict, [lambda name: name in start_atts, lambda name: name in end_atts, lambda name: name not in start_atts and name not in end_atts])
            
            setitemrows += "\
                <div class='item_container'>\
                    <p class='item_name_small {2}'>{6}</p>\
                    <p class='item_image_p'><img src='{1}' alt='{0}' /></p>\
                    <p class='item_attrs_small'>{3}</p>\
                    <p class='item_attrs attr'>{4}</p>\
                    <p class='item_attrs_small'>{5}</p>\
                </div><hr class='item_separator' />".format(item.name, item.imagepath, item.quality, base_attrs, attrs, end_attrs, "<a href='"+get_link(item)+"'>"+item.name+"</a>")
    
        set_bonuses = get_html_for_attributes(itemset.name, itemset.set_bonuses, lambda name: True)
    
        body = "<p class='item_name set'>{0}</p>\
          {2}\
          <p class='set_bonuses_title'>Set Bonuses</p>\
          <p class='set_bonuses'>{1}</p>".format(itemset.name, set_bonuses, setitemrows)
        
       # html = get_header(itemset.name, jquery=True, dexie=True) + body + get_footer(dexie=True)
        with open(get_link(itemset, False), 'w') as itemfile:
            itemfile.write(body)

TableCol = namedtuple('tablecol', 'link classval value subvalue')
TableRow = namedtuple('tablerow', 'cols')

def get_html_for_table(cat, table_headers, itemrows, sort_val=False):
    # ref sorting: https://github.com/joequery/Stupid-Table-Plugin#readme
    # ref sort(a,b): https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort

    headers = ""
    for i, (title, sort_type) in enumerate(table_headers):
        headers += "<th class='attr_table_header' data-sort='{1}'>{0}</th>\n".format(title, sort_type)
    
    rows = ""
    for row in itemrows:
        rows += "<tr class='attr_row'>"
        for tcol in row.cols:
            col = "<td>"
            if tcol.link != "":
                col += "<a href='{0}' class='{1}'>".format(tcol.link, tcol.classval)
            col += str(tcol.value)
            if tcol.subvalue != "":
                col += "<br /><span class='item_type'>{0}</span>".format(tcol.subvalue)
            if tcol.link != "":
                col += "</a>"
            col += "</td>"
            rows += col
            #if len(col) == 1:
            #    rows += "<td>{0}</td>\n".format(col)
            #elif len(col) == 3:
            #    rows += "<td><a href='{0}' class='{2}'>{1}</a></td>\n".format(col[0], col[1], col[2])
            #elif len(col) == 4:
            #    rows += "<td><a href='{0}' class='{2}'>{1}<br /><span class='item_type'>{3}</span></a></td>\n".format(col[0], col[1], col[2], col[3])
        rows += "</tr>\n"
    
    body = "<p class='attr_title'><strong>{1}</strong></p>\
      <table class='centerTable' id='attr_table'>\
      <thead><tr>{2}</tr></thead><tbody>\
      {0}\
      </tbody></table>".format(rows, cat, headers)
    
    script = """<script type="text/javascript">$(function(){\n
                  $("#attr_table").stupidtable({\n
                    "range_string":function(a,b){\n
                      var valA = a;\n
                      if (a.indexOf("-") > -1)\n
                      {\n
                        valA = a.split("-")[1];\n
                      }\n
                      var valB = b;\n
                      if (b.indexOf("-") > -1)\n
                      {\n
                        valB = b.split("-")[1];\n
                      }\n
                      return parseInt(valA,10) - parseInt(valB,10);\n
                    }\n
                  });"""
    
    if sort_val:
        script += """var $th_to_sort = $("#attr_table").find("thead th").eq(1);
                     $th_to_sort.stupidsort('desc');"""
    
    script += "});</script>"""
    
    return body + script

def output_attribute_files(items_per_attribute):
    for attribute in items_per_attribute:
        has_val_text = []
        for item, item_attr in items_per_attribute[attribute]:
            has_val_text.append(len(item_attr.value_text) > 0)
        display_value_column = sum(has_val_text) > 0
        
        rows = []
        
        for item, item_attr in items_per_attribute[attribute]:
            cols = [TableCol(link=get_link(item), value=item.name, classval=item.quality, subvalue=str(item.type))]
            if display_value_column:
                cols.append(TableCol(value=item_attr.value_text, link='', classval='', subvalue=''))
            rows.append(TableRow(cols=cols))
            #row = []
            #row.append([get_link(item), item.name, item.quality, str(item.type)])
            #itemrows += '<tr class="attr_row"><td><a href="{0}" class="{2}">{1}<br /><span class="item_type">{3}</span></a></td>'.format(get_link(item), item.name, item.quality, str(item.type))
            #if display_value_column:
            #    itemrows += "<td>{0}</td>".format(item_attr.value_text)
            #rows.append(row)
        
        table_headers = [('item', 'string')]
        if display_value_column:
            table_headers += [('value', 'range_string')]
        
        body = get_html_for_table(attribute.name, table_headers, rows)
        with open(get_link(attribute, False), 'w') as itemfile:
            itemfile.write(body)

def output_cat_files(items_per_cat):
    for cat in items_per_cat:
        #itemrows = ''
        #for item in items_per_cat[cat]:
        #    itemrows += '<tr class="attr_row"><td><a href="{0}" class="{2}">{1}</a></td></tr>'.format(get_link(item), item.name, item.quality)
        
        rows = [TableRow(cols=[TableCol(link=get_link(item), value=item.name, classval=item.quality, subvalue='')]) for item in items_per_cat[cat]]
        
        #rows = [[(get_link(item), item.name, item.quality)] for item in items_per_cat[cat]]
        
        body = get_html_for_table(cat.name, [('item', 'string')], rows)
        with open(get_link(cat, False), 'w') as itemfile:
            itemfile.write(body)

def output_main_page(items, sets, attributes, cat_dicts, index_links):
    names = ""
    for item in items + sets:
        names += '{ value: "' + item.name + '", link: "' + get_link(item) + '", category: "' + item.quality +'" },'
    for attr in attributes:
        names += '{ value: "' + attr.name + '", link: "' + get_link(attr) + '", category: "' + attr.quality +'" },'
    for cat_dict, _ in cat_dicts:
        for cat in cat_dict:
            names += '{ value: "' + cat.name + '", link: "' + get_link(cat) + '", category: "' + cat.quality +'" },'
    
    script = """$(function(){
                  var availableTags = ["""+names+"""];\n
                  $("#tags").autocomplete({\n
                    source: availableTags,\n
                    select: function(event, ui) {\n
                      var page = ui.item.link;\n
                      $('#contentContainer').load(page, function(responseTxt, statusTxt, xhr) {\n
                          if (statusTxt == "success")\n
                          {\n
                              window.history.pushState(page, null, page);\n
                              ajaxify_links();\n                              
                          }\n
                      });\n
                      return false;\n
                    }\n
                  });\n
                  $("#tags").focus();\n
                });\n"""
        
    body = """<div id='container'>\n
    <div id='headerContainer'>\n
        <p id='headerText'><a href="/d2/site_map.html">weizor's grimoire</a></p>\n
        <div class='ui-widget'>\n
            <input spellcheck='false' id='tags' placeholder='enter search term' />\n
        </div>\n
    </div>\n
    <div id='contentContainer'>
    
    </div>
    
    <script type="text/javascript">
        var first = true;
        var loading_hash = false;
        function ajaxify_links()
        {
            $('a').click(function(event) { 
                var page = $(this).attr('href');
                if (page.includes("d2/") && (!window.location.hash || window.location.hash != '#'))
                {
                    //alert("click");
                    event.preventDefault();
                    $('#contentContainer').load(page, function(responseTxt, statusTxt, xhr){
                        if (statusTxt == "success")
                        {
                            if (first)
                            {
                                first = false;
                                window.history.pushState('site_map.html', null, 'site_map.html');
                            }
                            window.history.pushState(page, null, page);
                            ajaxify_links();
                        }
                    });
                    return false;
                }
            });
        }
        
        $( window ).on( "load", function() {
            var page = 'site_map.html';
            if(window.location.hash) {
                // check if hash present (due to htaccess url rewriting)
                page = window.location.hash.slice(1);
                loading_hash = true;
            }
            $('#contentContainer').load(page, function(responseTxt, statusTxt, xhr){
                if (statusTxt == "success")
                {
                    ajaxify_links();
                    loading_hash = false;                    
                }
            });
        });
        
        window.onpopstate = function() {  
            if (loading_hash)
                return false;
            $('#contentContainer').load(location.href, function(responseTxt, statusTxt, xhr){
                if (statusTxt == "success")
                {
                    ajaxify_links();
                }
            });
        };
        
        $( document ).ajaxSuccess(function() {
            setTimeout(function() {
                $('html, body').animate({ scrollTop: 0 }, 1);
            }, 5);
            
        });
    </script>"""

    html = get_header(script=script, jquery=True, jquery_ui=True, dexie=True, table=True, stupidtable=True) + body + get_footer(dexie=True)
    with open(HTML_DIR + "/index.html", 'w') as itemfile:
        itemfile.write(html)

def output_site_map(items, sets, attributes, cat_dicts, index_links):
    names = ""
    for item in items + sets:
        names += '{ value: "' + item.name + '", link: "' + get_link(item) + '", category: "' + item.quality +'" },'
    for attr in attributes:
        names += '{ value: "' + attr.name + '", link: "' + get_link(attr) + '", category: "' + attr.quality +'" },'
    for cat_dict, _ in cat_dicts:
        for cat in cat_dict:
            names += '{ value: "' + cat.name + '", link: "' + get_link(cat) + '", category: "' + cat.quality +'" },'
    
    script = '$(function(){{\
                  var availableTags = [{0}];\
                  $("#tags").autocomplete({{\
                    source: availableTags,\
                    select: function(event, ui) {{\
                      window.location.href = ui.item.link;\
                      return false;\
                    }}\
                  }});\
                  $("#tags").focus();\
                }});'.format(names)
    
    classes = {"Unique Items": "Unique", "Set Items": "Set", "Runewords": "runeword", "Runes": "rune", "Gems": "gem", "Attributes": "attr", "White Items": "white"}
    
    index_pages = "<p>"
    for i, (item_type, index_link) in enumerate(index_links):
        style = ''
        if i not in [2, 6, 10, 11]:
            style = 'margin-right: 10px;'
        index_pages += '<a href="../{0}" class="{2}" style="{3}">{1}</a>'.format(index_link, item_type, classes[item_type] if item_type in classes else '', style)
        if i in [2, 6, 10]:
            index_pages += "</p><p>"
    index_pages += "</p>"
    
    body = """
        <p class='header'>indexes</p>\n
        {0}\n
        <p class='header'>tools</p>\n
        <p><a href='/d2/create_guide.html'>create gear guide</a></p>\n
        <p><a href='/d2/available_rws.html'>available runewords</a></p>\n
        <p><a href='/d2/inventory.html'>your items</a></p>
        <p><a href='/d2/db.html'>import/export db</a></p>
    """.format(index_pages)
    
    # collection fields checkbox
    x = """
        <hr class='item_separator' />\n
        <p><input type="checkbox" id="show_col_info" style="margin-left: 5px" /> show collector fields</p>\n
        <script>\n
            db.config.toArray().then( function(arr) {{\n
                show_fields = arr[0];
                $('#show_col_info').prop('checked', show_fields.status);\n
                $('#show_col_info').change(function() {{\n
                    show_fields_ = this.checked;
                    db.config.put({{\n
                        show_fields: 0,\n
                        status: show_fields_ ? 1 : 0\n
                    }});\n
                }});\n
            }});
        </script>\n
      </div>""" #.format(index_pages)

    with open(HTML_DIR + "/site_map.html", 'w') as itemfile:
        itemfile.write(body)

def get_index_links(items, sets, attributes, cat_dicts, guides):
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
    
    items_types = [(unique_items, 'Unique Items'), (set_items, 'Set Items'), (rw_items, 'Runewords'), (white_items, 'White Items'), (item_sets, 'Item Sets'), (runes, 'Runes'), (gems, 'Gems'), (list(attributes), 'Attributes'), *[(list(d), n) for d, n in cat_dicts], (guides, 'Guides')]
    #, (unique_attributes, 'Rarely-occurring attributes')]
    
    links = []
    for items, item_type in items_types:
        itemrows = ''
        items.sort(key=lambda item: item.name)
        for item in items:
            itemrows += '<tr class="attr_row"><td><a href="{0}" class="{2}">{1}</a></td></tr>'.format(get_link(item, True), item.name, item.quality)
        
        body = "<p class='attr_title'><strong>{0}</strong></p>\
          <table class='centerTable' id='attr_table'>\
          {1}\
          </table>\
        </div>".format(item_type, itemrows)
        
        #html = get_header(item_type) + body + get_footer()
        links.append((item_type, ROOT_DIR + "/" + item_type.lower().replace(" ", "_")+'.html'))
        with open(HTML_DIR + "/" + item_type.lower().replace(" ", "_")+'.html', 'w') as itemfile:
            itemfile.write(body)
    
    return links

def output_available_rws_page(runes, runewords):
    print(len(runes), len(runewords))
    runewords.sort(key=lambda item: item.name)
    itemrows = ''
    for i, item in enumerate(runewords):
        itemrows += '<tr class="attr_row" id="rw_{3}" style="display: none;"><td><a href="{0}" class="{2}">{1}</a></td></tr>'.format(get_link(item, True), item.name, item.quality, i)
    
    body = "<p class='attr_title'><strong>Runewords you can currently make</strong></p>\
      <table class='centerTable' id='attr_table'>\
      {0}\
      </table>\
    </div>".format(itemrows)
    
    # script to load qty of all runes
    body += """<script>
    var runeQtys = {};
    //var numRunesLoaded = 0;
    """
    
    for rune in runes:
        body += """
        db.items.where('name').equals('"""+rune.name.replace("'", "")+"""').toArray().then( function(item_arr) {\n
            item = item_arr[0];
            char_data = item.characters;
            total_qty = 0;
            $.each(char_data, function(index, row) {
                total_qty += parseInt(row.Qty);
            });
            runeQtys['"""+rune.name.replace("'", "")+"""'] = total_qty;
            //numRunesLoaded += 1;
        });
        """

    body += """
    $(function(){
        setTimeout(function() {
    """
    
    for i, rw in enumerate(runewords):
        # get qty of needed runes
        neededRuneQtys = defaultdict(int)
        for rune in rw.runes:
            neededRuneQtys[rune+" Rune"] += 1
        
        cond = ''
        for j, rune in enumerate(neededRuneQtys):
            cond += "runeQtys['{0}'] >= {1}".format(rune, neededRuneQtys[rune])
            if j < len(neededRuneQtys)-1:
                cond += " && "
                
        body += """
        if ({0})
        {{
            $("#rw_{1}").show();
        }}""".format(cond, i)
    
    body += """
        }, 500);
    });
    </script>
    """
        
    with open(HTML_DIR + "/available_rws.html", 'w') as itemfile:
        itemfile.write(body)

def output_guide_creation_page(items, sets, attributes):
    classnames = ""
    for classname in classes:
        classnames += '{ value: "' + classname + '" },'
    
    item_types = [('Primary Weapon', 'weapon1', weapon_and_offhand_types), ('Shield/Other Weapon', 'weapon2', weapon_and_offhand_types), ('Off-hand Weapon', 'weapon3', weapon_and_offhand_types), ('Off-hand shield/Other Weapon', 'weapon4', weapon_and_offhand_types), ('Helm', 'helm', helm_types), ('Body armor', 'bodyarmor', body_armor_types), ('Belt', 'belt', belt_types), ('Gloves', 'gloves', glove_types), ('Boots', 'boots', boot_types), ('Amulet', 'amulet', amulet_types), ('Ring 1', 'ring1', ring_types), ('Ring 2', 'ring2', ring_types), ('Mercenary Weapon', 'mercweap', weapon_and_offhand_types), ('Mercenary Helm', 'merchelm', helm_types), ('Charms', 'charms', charm_types), ('Sockets', 'sockets', ['Socketable', 'Jewel']), ('White Items', 'white_items', weapon_and_offhand_types + body_armor_types + helm_types)]
    
    Field = namedtuple('Field', 'name id type_vals')
    
    fields = []
    for title, idname, item_type_list in item_types:
        type_vals = ""
        for item in items:
            if (isinstance(item, WhiteItem) and idname != 'white_items') or (not isinstance(item, WhiteItem) and idname == 'white_items'): continue
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
                 var div = 2;\n\
                 if (qty_field) div = 3;\n\
                 var new_field_name = attr_name + '_'+field_id+'_' + Math.ceil($(field_container_id + ' > input').length/div);\n\
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
               function new_item_div(field_id, name, type_vals, spawn_new_field, qty_field, desc_field)\n\
               {\n\
                 var plural = name; // + 's'; \n\
                 var field_container_id = '#'+plural+'_'+field_id;\n\
                 var field_num = $(field_container_id + ' > input').length;\n\
                 var new_field_name = name+'_'+field_id+'_' + field_num;\n\
                 var new_field_html = \"<input spellcheck='false' placeholder='\"+new_field_name+\"' class='item_input \"+name+\"' id='\" + new_field_name + \"' name='\" + new_field_name + \"' />\";\n\
                 var checkboxId = 'custom_'+name+field_num+'_'+field_id;\n\
                 new_field_html += \"<span class='field_name'><input type='checkbox' id='\"+checkboxId+\"' /> Custom \"+name+\"</span><br />\";\n\
                 var desc_field_name = 'desc_' + new_field_name; \n\
                 if (desc_field)\n\
                    new_field_html += \"<textarea name='\"+desc_field_name+\"' id='\"+desc_field_name+\"' class='item_desc' rows='1' placeholder='Description' /></textarea>\"\n\
                 $(field_container_id).append(new_field_html);\n\
                 if (spawn_new_field)\n\
                    $('#'+new_field_name).autocomplete({ source: type_vals,\n\
                                                         select: function(event, ui) {\n\
                                                           new_item_div(field_id, name, type_vals, spawn_new_field, qty_field, desc_field);\n\
                                                         }});\n\
                 else\n\
                    $('#'+new_field_name).autocomplete({ source: type_vals });\n\
                 $('#'+checkboxId).change(function() {{\n\
                    if($(this).is(':checked')) {{\n\
                       $('#'+new_field_name).hide();\n\
                       $('#'+new_field_name).val('');\n\
                       new_field(attr_type_vals, 'attribute', plural+'_'+field_id, true, qty_field);\n\
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
                           new_item_div('{0}', 'sockets', sockets, false, false, false);\n\
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
                           // if custom item is selected, hide the other fields (ethereal, runeword base, sockets)\n\
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
                 new_item_div("charm", "charm", charms, true, true, true);'.format(charms.id, charms.type_vals)
    
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
                          <textarea name='desc_{0}' id='{0}_desc' class='item_desc' rows='1' placeholder='Description' /></textarea>\n\
                        </fieldset></div>\n".format(field.id, field.name)
    
    field_inputs += "<div class='ui-widget'><fieldset>\n\
                       <legend class='item_header'>Charms</legend>\n\
                       <div id='charm_charm'></div>\n\
                       <div id='custom_fields_charm_charm'></div>\n\
                       <p></p><p></p>\n\
                     </fieldset></div>\n"
    
    # auto resizing textarea
    # ref: https://stackoverflow.com/questions/454202/creating-a-textarea-with-auto-resize
    script = '{2}\n\
                $(function(){{\n\
                  var classnames = [{0}];\n\
                  $("#classname").autocomplete({{ source: classnames }});\n\
                  {1}\n\
                  $("#name").focus();\n\
                  $(".socket").hide();\n\
                  $("textarea").each(function(){{\n\
                    this.setAttribute("style", "height:" + (this.scrollHeight) + "px;overflow-y:hidden;");\n\
                  }}).on("input", function(){{\n\
                    this.style.height = "auto";\n\
                    this.style.height = (this.scrollHeight) + "px";\n\
                  }});\n\
                }});'.format(classnames, field_js, fn_defs)
    
    body =  '<script type="text/javascript">' + script + '</script>' + "<form action='/d2/cgi-bin/create_guide.py' method='post'>\n\
          <div id='guide_form'>\n\
            <p><input type='text' placeholder='Gear Guide Name' name='name' id='name' required /></p>\n\
            <p><input type='text' placeholder='Author' name='author' id='author' required /></p>\n\
            <div class='ui-widget'>\n\
              <p><input spellcheck='false' placeholder='classname' id='classname' name='classname' required /></p>\n\
            </div>\n\
            <p><input type='text' placeholder='Link to guide (optional)' name='link' id='link' /></p>\n\
            {0}\n\
            <p></p>\n\
            <button type='submit'>Submit</button>\n\
          </div>\n\
        </form>".format(field_inputs)
        
    with open(HTML_DIR + "/create_guide.html", 'w') as itemfile:
        itemfile.write(body)

def output_inventory_page(items):
    body = """
    <div>
        <table class='centerTable' id='attr_table'>
        
        </table>
    </div>
    
    <script>
    
    db.items.toArray().then( function(item_arr) {\n
        $.each(item_arr, function(index, item) {
            if (item.quality)
                $('#attr_table').append('<tr class="attr_row"><td><a href="' + item.link + '" class="' + item.quality + '">' + item.name + '</a></td></tr>');
        });
    });
    
    </script>"""
    
    with open(HTML_DIR + "/inventory.html", 'w') as itemfile:
        itemfile.write(body)

def output_db_page():
    body = """
    
    <div class="column">
        <p><a id="exportLink" href="#">Export database</a></p>
        <div id="dropzone">
            Drop database file here to import
        </div>
    </div>
    <div id="status"></div>
    
    <script>
    $(function(){
        $('#exportLink').click(function() {
            db.export({prettyJson: true}).then(function(blob) {
                download(blob, "my-grimoire-db.json", "application/json");
            });
        });
        
        $('#dropzone').on("dragover", function(event) {
            event.stopPropagation();
            event.preventDefault();
            event.originalEvent.dataTransfer.dropEffect = 'copy';
        });
        $('#dropzone').on("drop", function(event) {
            event.stopPropagation();
            event.preventDefault();

            // Pick the File from the drop event (a File is also a Blob):
            const file = event.originalEvent.dataTransfer.files[0];
            if (!file) throw new Error(`Only files can be dropped here`);
            console.log("Importing " + file.name);
            db.import(file, {clearTablesBeforeImport: true}).then(function() {
                $("#status").html("Import complete.");         
                console.log("Import complete.");             
            });
        });
    });
    
    </script>
    """
    
    with open(HTML_DIR + "/db.html", 'w') as itemfile:
        itemfile.write(body)

def create_databases():
    print("Running sql.")
    db = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD)
    
    file = open('create_db.sql', 'r')
    cursor = db.cursor()
    for line in file.readlines():
        if len(line) > 0 and not all(l == ' ' for l in line):
            try:
                cursor.execute(line)
            except:
                break
    db.commit()
    
    db.close()

def output_guides(guides):
    for guide in guides:
        body = "<p class='item_name'>{0} by {2}</p>\n\
                <p class='item_type'>{1}</p>\n".format(guide.name, guide.classname, guide.author)
        
        if len(guide.link) > 0:
            body += "<p class='item_type'><a href='{0}'>more details</a></p>".format(guide.link)
        
        for gear_piece in guide.gear_pieces:
            body += "<div class='item_container'><fieldset><legend class='gear_type'>{0}</legend>\n".format(gear_piece.type)
            if gear_piece.matched_item is not None:
                body += "<p class='item_name {0}'>{1}</p>\n".format(gear_piece.matched_item.quality, "<a href='"+get_link(gear_piece.matched_item)+"'>"+gear_piece.matched_item.name+"</a>")
            elif len(gear_piece.custom_atts) > 0:
                body += "<p class='item_attrs attr'>{0}</p>\n".format(get_html_for_attributes(gear_piece.gear_name, gear_piece.custom_atts, lambda name: True))
            if gear_piece.ethereal:
                body += "<p class='ethereal'>(Ethereal)</p>\n"
            if gear_piece.runeword_base is not None:
                body += "<p class='item_name_small white'><a href='{0}'>{1}</a></p>\n".format(get_link(gear_piece.runeword_base), gear_piece.runeword_base.name)

            if len(gear_piece.sockets) > 0 or len(gear_piece.custom_socket_atts) > 0:
                body += "<p>Sockets</p>\n"
            for socket in gear_piece.matched_sockets:
                body += "<p class='item_name_small {0}'>{1}</p>\n".format(socket.quality, "<a href='"+get_link(socket)+"'>"+socket.name+"</a>")
            if len(gear_piece.custom_socket_atts) > 0:
                body += "<p class='item_attrs attr'>{0}</p>\n".format(get_html_for_attributes(gear_piece.gear_name, gear_piece.custom_socket_atts, lambda name: True))
            if gear_piece.qty > 1:
                body += "<p>Quantity: {0}</p>\n".format(gear_piece.qty)
            if len(gear_piece.desc) > 0:
                body += "<p>{0}</p>\n".format(gear_piece.desc)
            body += "</fieldset></div>"
        
        # combined stats
        stat_totals = defaultdict(int)
        
        attrs = []
        for gear_piece in guide.gear_pieces:
            if gear_piece.matched_item is not None:
                attrs.extend(list(gear_piece.matched_item.attr_dict.values()))
            attrs.extend(gear_piece.custom_atts)
            for soc in gear_piece.matched_sockets:
                attrs.extend(list(soc.attr_dict.values()))
            attrs.extend(gear_piece.custom_socket_atts)
        
        assert all(type(attr) is Attribute for attr in attrs)
        for attr in attrs:
            # add high end of range
            if attr.sort_value == True:
                stat_totals[attr.name] = 0
            elif isinstance(stat_totals[attr.name], (int, float)):
                stat_totals[attr.name] += int(attr.sort_value)
            else:
                raise Exception(stat_totals[attr.name])

        rows = []
        for attr_name in stat_totals:
            cols = [TableCol(value=attr_name, link='', classval='', subvalue='')]
            if stat_totals[attr_name] is not None:
                cols.append(TableCol(value=stat_totals[attr_name], link='', classval='', subvalue=''))
            rows.append(TableRow(cols=cols))
        #rows = [TableRow(cols=[TableCol(value=attr_name, link='', classval='', subvalue=''), TableCol(value=stat_totals[attr_name], link='', classval='', subvalue='')]) for attr_name in stat_totals]
        #[[attr_name, stat_totals[attr_name]] for attr_name in stat_totals]
        #print(rows)
        # output table
        body += get_html_for_table("Attribute totals", [("Attribute", 'string'), ("Total", 'range_string')], rows, sort_val=True)
        
        with open(get_link(guide, False), 'w') as itemfile:
            itemfile.write(body)

def make_website():
    setup_dirs()
    output_htaccess()

    items, sets, attributes = load_data()
    monsters = load_monsters()
    guides = load_guides()
    output_guides(guides)
            
    cat_dicts = []
    for cat_name, disp_name in [('tier', 'Item Tiers'), ('type', 'Item Types'), ('stype', 'Item Subtypes')]:
        cat_dict = get_cat_dict(items, cat_name)
        output_cat_files(cat_dict)
        cat_dicts.append((cat_dict, disp_name))
    
    index_links = get_index_links(items, sets, attributes, cat_dicts, guides)
    
    rws, runes = [], []
    for item in items:
        if isinstance(item, Runeword):
            rws.append(item)
            output_runeword_file(item)        
        elif isinstance(item, Socketable):
            if item.quality == 'Rune':
                runes.append(item)
                output_rune_file(item)
            elif item.quality == 'Gem':
                output_gem_file(item)
        else:
            output_item_file(item, index_links, guides, monsters)
            if item.eth_item is not None:
                output_item_file(item.eth_item, index_links, guides, monsters)
    
    output_set_files(sets)
    output_attribute_files(attributes)
    output_guide_creation_page(items, sets, attributes)
    output_available_rws_page(runes, rws)
    output_site_map(items, sets, attributes, cat_dicts, index_links)
    output_main_page(items, sets, attributes, cat_dicts, index_links)
    
    output_inventory_page(items)
    output_db_page()
    
    #output_login_page()
    #output_register_page()
    
    create_databases()

if __name__ == '__main__':
    make_website()