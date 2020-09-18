#!/usr/bin/python
# Arseniy Tsipenyuk, 2020
#
# Accepts arguments: query in the arxiv.py format.
# Example usage:
# $ python arxiv-custom-search.py ti:phase AND ti:retrieval
import arxiv
import sys

# convert date to readable format
from datetime import datetime
from time import mktime

paper_list = []

# Configuration ################################################################
# Your storage file; feel free to change .org to *.txt if you prefer
out_file = "arxiv-custom-search.org" 
max_res = 20 # Maximal amount of results

### Configure your queries
query_string = ' '.join(sys.argv[1:])

# adjust arxiv.py query to your needs
paper_list = arxiv.query(query=query_string,
                          #sort_by="submittedDate", # "lastUpdatedDate", "relevance"
                          sort_by="relevance",
                          sort_order="descending",
                          prune=True,
                          iterative=False,
                          max_results=max_res);
# END of Configuration #########################################################

### Remove duplicates if multiple queries
paper_list = list(dict.fromkeys(paper_list))

### Prepare output
### Output table contains 4 columns:
# | Date | Authors | Link | Title |
  
# Get paper info as a string that can be written to out_file
def getDate(paper):
  return str(datetime.fromtimestamp(mktime(paper['updated_parsed'])))[0:10]

def getAuthors(paper):
  if len(paper['authors']) > 3:
    author_list = paper['authors'][0:3] + ['et al.']
  else:
    author_list = paper['authors']
  return u', '.join(author_list).encode('utf-8').strip().replace('. ','.').decode('utf-8')

def getLink(paper):
  url = paper['links'][-1]['href']
  url_name = url[url.rfind('/')+1:] # reference code, e.g. 0000.0000v1
  return ''.join(['[[', url, '][', url_name, ']]'])

def getLinkName(paper):
  url = paper['links'][-1]['href']
  url_name = url[url.rfind('/')+1:] # reference code, e.g. 0000.0000v1
  return url_name

def getTitle(paper):
    return paper['title'].encode('utf-8').strip().replace('\n',' ')

# Filler function: get string consisting of N copies of character c
def getChar(c, N):
  return ''.join([c for i in range(N)])

def getLine(paper):
  return u''.join([
    u'| ',
    getDate(paper),    
    u' | ',
    getAuthors(paper) + getChar(' ', authors_col_width - len(getAuthors(paper))),
    u' | ',
    getLink(paper) + getChar(' ', link_col_width - len(getLinkName(paper))),
    u' | ',
    getTitle(paper)  + getChar(' ', title_col_width - len(getTitle(paper))),
    u' |\n'
  ]).encode('utf-8')

def getEmptyLine():
  return ''.join([
    '|-',
    getChar('-', date_col_width),
    '-+-',
    getChar('-', authors_col_width),
    '-+-',
    getChar('-', link_col_width),
    '-+-',
    getChar('-', title_col_width),
    '-|\n'
  ]).encode('utf-8')

def getHeader():
  return ''.join([
    '| ',
    'Date' + getChar(' ', date_col_width - len('Date')),
    ' | ',
    'Authors' + getChar(' ', authors_col_width - len('Authors')),
    ' | ',
    'Link' + getChar(' ', link_col_width - len('Link')),
    ' | ',
    'Title' + getChar(' ', title_col_width - len('Title')),
    ' |\n'
  ]).encode('utf-8')

if len(paper_list) == 0:
  print("No papers found. Refine your query.\n")
else:
  # Determine column widths
  date_col_width = 10 # e.g. "2020-01-01"; 
  authors_col_width = max([len(getAuthors(paper)) for paper in paper_list])
  link_col_width = max([len(getLinkName(paper)) for paper in paper_list]) # Likely superfluous since always = 11
  title_col_width = max([len(getTitle(paper)) for paper in paper_list])

  # Write out results
  outF = open(out_file, "w")
  outF.truncate(0)
  outF.write(getEmptyLine())
  outF.write(getHeader())
  outF.write(getEmptyLine())
  for paper in paper_list:
    outF.write(getLine(paper))
  
  outF.write(getEmptyLine())
  outF.close()
  print("Done.\n")
