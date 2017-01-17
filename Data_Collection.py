import numpy
import requests
import re
import time
import sys
import csv
import pandas as pd
from collections import Counter
from lxml import html
from tqdm import *


page_cstart = 0
href = []
authors = []
year = []
citation = []
journal = []
ref_web = []
while 1:
  page_url = 'https://scholar.google.com/citations?user=__XZ88LXYAAAAJ=en&cstart=' + str(page_cstart) + '&pagesize=100' 
  page = requests.get(page_url)
  tree = html.fromstring(page.content)
  m = tree.xpath('//td[@class="gsc_a_e"]/text()')
  if len(m)>0 and m[0] == 'There are no articles in this profile.':
    break
  page_cstart = page_cstart + 100
  href = href + tree.xpath('//a[@class="gsc_a_at"]/text()')
  authors_temp = tree.xpath('//div[@class="gs_gray"]')
  for i in range(len(authors_temp)):
    if i%2 == 0:
      if authors_temp[i].text:
        authors.append(authors_temp[i].text)
      else:
        authors.append('')
    else:
      if authors_temp[i].text:
        journal.append(authors_temp[i].text)
      else:
        journal.append('')
  year_temp = tree.xpath('//span[@class="gsc_a_h"]')
  year_temp = year_temp[1:]
  for x in year_temp:
    if x.text:
      year.append(x.text)
    else:
      year.append('')
  citation_temp = tree.xpath('//a[contains(@class,"gsc_a_ac")]')
  for x in citation_temp:
    if x.text:
      citation.append(x.text)
    else:
      citation.append('')
  websites = tree.findall('.//a')
  for x in websites:
    try:
      if x.attrib['class'] == 'gsc_a_at':
        ref_web.append(x.attrib['href'])
    except KeyError:
      pass

ref_authors = []
ref_description = []
for ref_page in tqdm(ref_web):
  ref_url = 'https://scholar.google.com/' + ref_page
  page = requests.get(ref_url)
  tree = html.fromstring(str(page.content).replace('<br>',' '))
  ref_div = tree.findall('.//div')
  for i in range(len(ref_div)):
    if ref_div[i].text == 'Authors':
      ref_authors.append(ref_div[i+1].text)
    if ref_div[i].text == 'Description':
      ref_description.append(ref_div[i+1].text)




#### set With missing values in citation to 0
citation_index = [i for i in range(len(citation)) if citation[i]=='\xa0']
my_citation = numpy.array(citation)
my_citation[citation_index] = 0

#### extract name of journals
my_journal = []
for j_temp in journal:
  my_journal.append(re.split(' [0-9]', j_temp)[0])
my_journal = [element.upper() for element in my_journal]

#### Get 
outf = [href, authors, year, my_citation.tolist(), my_journal]
my_df = pd.DataFrame(outf)
my_df.to_csv("output.csv")

with open("output.csv", 'wb') as f:
  writer = csv.writer(f)
  writer.writerows(outf)


