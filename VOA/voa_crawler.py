from urllib import request
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd


#get all available links from the voa website
def getAllLinks(category, sizes, link):
  links = []
  for cat in range(len(category)):
    print("Getting all links from ", category[cat] , " new category")
    siz = sizes[cat]
    ls = []
    for ln in range(siz):
      href = link[cat]+str(ln)
      #print(href)
      page_request = request.Request(href, headers=headers)
      page = request.urlopen(page_request)
      soup = BeautifulSoup(page, 'html.parser')
      result_set = soup.findAll("div", {"class":"media-block__content media-block__content--h media-block__content--h-xs"})
      ls.extend([x.a['href'] for x in result_set ])
    links.extend(ls)
    print(category[cat], "returned ", len(ls), " links ...")

  print("Got ", len(links), " links in all .. and  ", len(set(links)), "unique links ....")

  return list(set(links))


# scaps each new article for the title, date, introduction and content
def page_content(soups):
    if soups.find("h1", {"class": "title pg-title"}) != None:
        title = soups.find("h1", {"class": "title pg-title"}).text.replace("\t", "").replace("\n", "")
    elif soups.find("h1", {"class": "title pg-title pg-title--featured"}) != None:
        title = soups.find("h1", {"class": "title pg-title pg-title--featured"}).text.replace("\t", "").replace("\n",
                                                                                                                "")
    else:
        title = ""
    if soups.find("span", {"class": "date"}) != None:
        time = ""  # soups.find("span", {"class":"date"}).text
    else:
        time = ""

    introstring = ""
    if soups.find("div", {"class": "intro intro--bold"}) != None:
        intro_res = soups.find("div", {"class": "intro intro--bold"}).findAll('p')
        # for x in intro_res:
        #  introstring+=x.text.replace(u'\xa0', u' ').replace('\n'," ")+" \n"
        introstring = " ".join([x.text.replace(u'\xa0', u' ').replace('\n', " ") + " \n" for x in intro_res])

    if soups.find("div", {"class": "wsw"}) != None:
        result = soups.find("div", {"class": "wsw"}).findAll('p')
        # txtstring=""
        # for x in result:
        # print (x.text)
        # txtstring+=x.text.replace(u'\xa0', u' ').replace('\n'," ")+" \n"
        texts = " ".join([x.text.replace(u'\xa0', u' ').replace('\n', " ") + " \n" for x in result])
        texts = texts.strip()
    else:
        texts = ""
    finaltext = introstring + "\n" + texts
    return title, time, finaltext.strip()


def scrap_pages(alllinks):
    titles, times, texts = [], [], []
    count = 0
    for urls in alllinks:
        page_request = request.Request(home + urls)
        page = request.urlopen(page_request)
        soup = BeautifulSoup(page, 'html.parser')
        title, time, text = page_content(soup)
        titles.append(title)
        times.append(time)
        texts.append(text)
        count = count + 1
        progresse = (count / len(alllinks) * 100)
        if progresse % 10 == 0:
            print("Scrapped ", progresse, "% of the articles")
    return titles, times, texts


if __name__ == '__main__':

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    soupx = []

    categories = ["Habari"] #get all the news categories
    size = [101]  #get the number of pages each link has
    home = "https://www.voaswahili.com" #the link to the home page
    #get the link to each category append /z/2866?p= at the end
    links = ['https://www.voaswahili.com/z/2772?p=']

    allinks = getAllLinks(categories, size, links)
    #print(allinks)

    titles, times, texts = scrap_pages(allinks)

    # create a dictionary of the top
    d = {'Title':titles,'Date':times,"Text":texts}

    df = pd.DataFrame(d)
    df.to_csv (r'voa_swahili.csv', index = False, header=True)