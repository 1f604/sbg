# sbg

Static blog generator

Put your blog posts as markdown files in the pages/category directories. 
Put your assets in the assets directory. 
And then just run build.py when you're done. 

If you want to preview changes without pushing, simply commit, view the generated pages, then do a manual git push afterwards. 

Example structure:

- pages
  - cat1
    - page1.md
    - page2.md
  - cat2
    - page3.md
    - page4.md
- assets
  - asset1.pdf
  - asset2.jpg

You have to structure your blog in this way. Any other structure is not supported. 

Also, each page has 4 attributes that you must write into the file at the top of the file (in any order): title, desc, tags, and prereqs. See example file to see how it's done. 

This program has only been tested for adding new files, not deleting old files. Actually it will bug out when you delete old assets and pages, so just don't do that. 

You need to have gitpython installed: `pip install gitpython`
