#!/usr/bin/env python2

"""
Builds static blog from markdown files. 

This handles all the git commit and push so you only need to run this file to save your changes, generate the static html pages and push them to github. No need to run any git commands yourself. 
"""

import markdown2
import os, git, datetime
from collections import defaultdict
from git import Actor
timestamp_filename = ".timestamps"
author = Actor("1f604", "1f604@users.noreply.github.com")
repo = git.Repo(".")

"""check if required directories exist, if not make them"""
dirs = ['.gen', 'assets', 'pages']
for d in dirs:
    if not os.path.exists(d):
        os.makedirs(d)


attributes = ['posted', 'title', 'desc', 'length', 'updated', 'category', 'tags', 'prereqs', 'filename']

""" text colors """
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

""" utility functions """
def getdatemtime(s): # parses date strings produced by os.path.getmtime()
    if type(s) is not float:
        s = float(s)
    return datetime.datetime.fromtimestamp(s).date()

def getdatetime(s): # parses date strings produced by isoformat()
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()

def toascii(s):
    return s.encode('ascii','replace')

def getupdated():
    changed = [item.a_path for item in repo.index.diff(None)]
    untracked = repo.untracked_files
    updated = changed + untracked
    return updated

def parsetimestamps():
    filename = timestamp_filename
    if not os.path.exists(filename):
        file(filename, 'w').close()
        return {}
    else:
        with open(filename, "r") as f:
            lines = f.read().splitlines()
    timestamps = {}
    for line in lines:
        published, updated, filename = line.split("$", 2)
        timestamps[filename] = [getdatetime(published), getdatetime(updated)]
    return timestamps

def writetimestamps(timestamps):
   filename = timestamp_filename
   with open(filename, "w+") as f:
        lines = []
        for key, value in timestamps.items():
            w = [str(value[0]), str(value[1]), key]
            lines.append("$".join(w))
        f.write("\n".join(lines))

def processpage(text):
    lines = text.splitlines()
    finished = False
    result = []
    linenumber = 0
    prefixes = set(['title', 'tags', 'desc', 'prereqs'])
    tags = ['None.']
    desc = "None."
    prereqs = ['None.']
    title = "Untitled"
    for line in lines:
        if finished:
            result.extend(lines[linenumber:])
            break
        else:
            parts = line.split(':', 1)
            prefix = parts[0].lower()
            if prefix in prefixes and len(parts) > 1:
                suffix = parts[1]
                if prefix == 'title':
                    title = suffix.strip()
                elif prefix == 'desc':
                    desc = suffix.strip()
                elif prefix == 'prereqs':
                    prereqs = [x.strip() for x in suffix.strip().split(',')]
                elif prefix == 'tags':
                    tags = [x.strip() for x in suffix.strip().split(',')]
                linenumber += 1
            else:
                finished = True
    return title, tags, desc, prereqs, '\n'.join(result)

def createindexpage(pagedict):
    html = ["""
<style>


 html * {
  font-family:'Courier New',Courier,monospace !important;
}
td {
  padding:2px; 
  border:solid 1px #eee;
}
th {
  width:140px;
}
</style>

<div id="myTable">
  <h1>Welcome to My Personal Blog!</h1>
  <div width = "100%">
  """]
  
    
    html.append("""</div>
  <table id = "entries">
    <thead>
      <tr>""")
    
    for ind, attribute in enumerate(attributes):
        html.extend(['<th id="cols" class="sortable" >', attribute])
        searchfieldname = attribute+"-search"
        html.extend(['<br><input data-search-type="',attribute,'"  onkeyup="searchTable(',str(ind),', \''+searchfieldname+'\')" placeholder="Search ', attribute, '" id = "', searchfieldname ,'"style="display:table-cell; width:100%" />'])
        html.append('</th>')        
    
    html.append("""</tr>
    </thead>
    <tbody class="list">""")
        
    for filename in pagedict:
        html.append("""<tr class="even">""")
        for attribute in attributes:
            html.append('<td id="cols" class="'+attribute+'">')
            if type(pagedict[filename][attribute]) is list:
                html.append(', '.join((pagedict[filename][attribute])))
            else:
                html.append(str(pagedict[filename][attribute]))
            html.append('</td>')
        html.append("</tr>")
    html.append("""</tbody>
  </table>
</div>
<script type='text/javascript' src='scripts.js'></script>
""")
    return ''.join(html)


"""
First of all, check for duplicate pages
"""
all_filenames = []
for dirpath, dirnames, filenames in os.walk('pages'):
    all_filenames.extend(filenames)
seen = set()
dupes = set()
for fname in all_filenames:
    if fname not in seen:
        seen.add(fname)
    else:
        dupes.add(fname)
if len(dupes) != 0:
    print bcolors.BOLD + bcolors.FAIL + "Duplicates found:" + bcolors.ENDC
    for dupe in dupes:
        print bcolors.FAIL + "  " + dupe + bcolors.ENDC
    print "Use the find command to find the dupes. Example:"
    print '  find . -name "'+ dupes.pop()+'"'
    print "Exiting."
    exit(1)

#    return tags, desc, prereqs, '\n'.join(result)
"""Get list of pages with their respective categories""" 
pagedirectory = "pages"

filecat = {}
cats = [o for o in os.listdir(pagedirectory) if os.path.isdir(pagedirectory+"/"+o)]
pages = []
result = []
for cat in cats:
    files = [(x,cat) for x in os.listdir(pagedirectory+"/"+cat) if x.endswith(".md")]
    pages.extend(files)

"""parse timestamp file and add newly created pages to timestamps dict"""
timestamps = parsetimestamps()
for page in pages:
    filecat[page[0]] = page[1]
    if page[0] not in timestamps:
        today = datetime.date.today()
        timestamps[page[0]] = (today, today)

"""update last modified times in timestamps dict"""
"""please note that this method is not safe to use if you are moving repositories"""
updated = getupdated()
for fname in updated:
    if fname.endswith(".md") or fname.startswith("assets/"):
        filepath = fname.encode('ascii','replace')
        filename = os.path.basename(filepath)
        last_modified = getdatemtime(os.path.getmtime(filepath))
        if filename in timestamps:
            if timestamps[filename][1] < last_modified:
                timestamps[filename][1] = last_modified


writetimestamps(timestamps)

"""Now parse the pages themselves to get tags, abstract, and prereqs"""

""" Get all untracked and modified files and ask the user if he wants to commit these """

updated = getupdated()
allpages = pages
pages = []
assets = []
other = []
for item in updated:
    if item.startswith("pages/") and item.endswith(".md"):
        pages.append(item)
    elif item.startswith("assets/"):
        assets.append(item)
    else:
        other.append(item)
unexpected = set(other) - set(["colors.css", "markdown2.py", "README.md", ".gitignore", "LICENSE", ".timestamps", "build.py", "index.html", "scripts.js"])

print bcolors.BOLD + "Items to be added/updated: " + bcolors.ENDC 
if updated == []:
    print bcolors.BOLD + bcolors.HEADER + "  None. Exiting now." + bcolors.ENDC
    exit(0)

def printlist(title, lines, color):
    if lines:
        print "   " + bcolors.BOLD + title + bcolors.ENDC
    for line in lines:
        print color + "      " + line + bcolors.ENDC

printlist("Pages: ", pages, bcolors.OKGREEN)
printlist("Assets: ", assets, bcolors.WARNING)
printlist("Unexpected: ", unexpected, bcolors.FAIL)
if unexpected:
    print "Unexpected files found. Exiting"
    exit(1)
if pages == [] and assets == []:
    print "   None."

"""Now we have filename, category, dates, tags, abstract, and prereqs. Now we generate the index page."""

"""Now we generate the pages. Each .md file gets mapped to a .html file."""

# First generate the pages individually in the .gen directory

raw_input("press enter to start generating pages")
#import subprocess
pagedict = {}
pages = allpages
for page in pages:
    filename = page[0]
    outfilename = ".gen/"+filename[:-2]+"html"
    with open(pagedirectory+"/"+page[1]+"/"+page[0], 'r') as f:
        text = f.read()
        title, tags, desc, prereqs, text = processpage(text)
        pagedict[filename] = {}
        pagedict[filename]['title'] = '<a href = "' + outfilename +'">' + title + '</a>'
        pagedict[filename]['desc'] = desc
        pagedict[filename]['length'] = len(text.split()) # word count
        pagedict[filename]['category'] = filecat[filename]
        pagedict[filename]['tags'] = tags
        pagedict[filename]['prereqs'] = prereqs
        pagedict[filename]['posted'] = timestamps[filename][0]
        pagedict[filename]['updated'] = timestamps[filename][1]
        pagedict[filename]['filename'] = filename
        html = markdown2.markdown(text, extras=['header-ids','fenced-code-blocks','break-on-newline'])
    with open(outfilename, 'w+') as f:
        f.write("""<head>
<link rel="stylesheet" type="text/css" href="../colors.css">
</head>""" + html)
        
# Now we generate index.html


content = createindexpage(pagedict)


with open("index.html", 'w+') as f: 


    f.write(content)

print "Pages generated."

"""Finally, we commit and push the changes"""

print "============All files to be committed============"
changed = [item.a_path for item in repo.index.diff(None)]
untracked = repo.untracked_files
updated = changed + untracked
updated = sorted(updated)
if not updated:
    print "None."
for update in updated:
    print update
print "================================================="
index = repo.index
index.add(updated)

commit_msg = raw_input("Please enter a commit message: ")
index.commit(commit_msg, author=author, committer=author)

print "All changes committed."
ans = raw_input("Are you sure you want to push? (y/n): ")
if ans == "y":
    origin = repo.remotes.origin
    origin.push()
    print "All changes pushed."
else:
    print "Changes not pushed"

