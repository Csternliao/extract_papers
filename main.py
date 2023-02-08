import re

import requests

import csv
from tqdm import tqdm
from lxml import etree
from lxml.etree import HTMLParser
import argparse
import os

A_CONF_LIST = ['sigcomm', 'usenix', 'nsdi', 'infocom', 'mobicom', 'ijcai']
A_JOURNAL_LIST = [
    'pieee', # Proceedings of the IEEE
    'ton', # IEEE/ACM Transactions on Networking
    'jsac', # IEEE Journal of Selected Areas in Communications
    'tocs', # ACM Transactions on Computer Systems
    'tmc', # IEEE Transactions on Mobile Computing
]


def getHTMLText(url):
    kv = {'user_agent':'Mozilla/5.0'}
    proxies_myself = {'http':'105.27.238.167:80'}
    try:
        r = requests.get(url,headers = kv,proxies = proxies_myself,timeout=120)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print('Failed! Please check the conference name, conference year and the keyword!')
        return ''

def writeToCsv(args, name, dicts):
    if not args.save_dir:
        args.save_dir = '.'
    else:
        if not os.path.exists(args.save_dir):
            os.mkdir(args.save_dir)

    if args.keyword:
        file_path = os.path.join(args.save_dir,"{}_{}_{}.csv".format(name,args.time,args.keyword))
    else:
        file_path = os.path.join(args.save_dir,"{}_{}.csv".format(name,args.time))

    with open(file_path,'w',encoding='utf-8',newline='') as f:
        csv_write = csv.writer(f)
        csv_head = ["Title","Authors", "url"]
        csv_write.writerow(csv_head)
        for ele in dicts:
            csv_write.writerow([ele['title'],"\n".join(ele['authors']), ele['url']])

def extract_papers(url, type, name, keyword):
    htmltext = getHTMLText(url)
    try:
        parse_html = etree.HTML(htmltext, HTMLParser())
    except:
        print('Failed! Please check the conference name ,conference year and the keyword!')
        exit(1)

    if type == 'conf':
        print("Parsing URL: {}".format(url))
        dics = []
        parse_xpaths = parse_html.xpath('//li[@class="entry inproceedings"]')
        print("Number of papers(all fields): {}".format(len(parse_xpaths)))
        for parse_xpath in tqdm(parse_xpaths):
            parse_html_str = etree.tostring(parse_xpath)
            parse_html1 = etree.HTML(parse_html_str, HTMLParser())
            paper_url = parse_html1.xpath('//div[@class="head"]/a/@href')[0]
            parse_content = parse_html1.xpath('//cite//span[@itemprop="name"]')
            parse_content = [parse_content[idx].text for idx in range(len(parse_content))]
            try:
                if args.keyword:
                    paper_title = parse_content[-1].upper()
                    if paper_title.find(keyword) == -1:
                        # print(parse_content[-1])
                        continue
                    else:
                        dic = {"title": parse_content[-1], "authors": parse_content[:-1], "url": paper_url}
                        dics.append(dic)
                else:
                    dic = {"title": parse_content[-1], "authors": parse_content[:-1], "url": paper_url}
                    dics.append(dic)
            except:
                continue

        writeToCsv(args, name, dics)
        print("The number of Papers extracted: {}".format(len(dics)))

    elif type == 'journal':
        # 网页后面跟的是volumn卷数而不是年份，正则表达式提取年份
        # 例：<li><a href="https://dblp.uni-trier.de/db/journals/pieee/pieee110.html">Volume 110: 2022</a></li>
        # 爬取规则跟会议不同
        # print(htmltext)
        matchObj = re.match(r'.*<li><a href="(.*)">Volume .*[,:] %s</a></li>.*' % args.time, htmltext, re.DOTALL)
        url = matchObj.group(1)
        print("Parsing URL: {}".format(url))
        htmltext = getHTMLText(url)
        try:
            parse_html = etree.HTML(htmltext, HTMLParser())
            parse_xpaths = parse_html.xpath('//li[@class="entry article"]')
        except:
            print('Failed! Please check the journal name ,conference year and the keyword!')
            exit(1)
        dics = []
        print("Number of papers(all fields): {}".format(len(parse_xpaths)))
        for parse_xpath in tqdm(parse_xpaths):
            parse_html_str = etree.tostring(parse_xpath)
            parse_html1 = etree.HTML(parse_html_str, HTMLParser())
            paper_url = parse_html1.xpath('//div[@class="head"]/a/@href')[0]
            parse_content = parse_html1.xpath('//cite//span[@itemprop="name"]')
            parse_content = [parse_content[idx].text for idx in range(len(parse_content))]
            try:
                if args.keyword:
                    paper_title = parse_content[-1].upper()
                    if paper_title.find(keyword) == -1:
                        # print(parse_content[-1])
                        continue
                    else:
                        dic = {"title": parse_content[-1], "authors": parse_content[:-1], "url": paper_url}
                        dics.append(dic)
                else:
                    dic = {"title": parse_content[-1], "authors": parse_content[:-1], "url": paper_url}
                    dics.append(dic)
            except:
                continue

        writeToCsv(args, name, dics)
        print("The number of Papers extracted: {}".format(len(dics)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Conference Information")
    # parser.add_argument('-n',"--name", type=str, required=True,help="Name of Conference you want to search.")
    parser.add_argument('-t',"--time", type=int, default=2022, help="Year of Conference you want to search.")
    parser.add_argument("--save_dir", type=str, default=None, help="the file directory which you want to save to.")
    parser.add_argument('-k',"--keyword", type=str, default=None, help="the keyword filter, if None, save all the paper found.")
    args = parser.parse_args()
    keyword = args.keyword.upper().replace('_', ' ')

    # args.name = args.name.lower()

    # if args.name == "neurips" or args.name == "nips":
    #     url = "https://dblp.org/db/conf/nips/neurips{}.html".format(args.time)
    # else:
    #     url = "https://dblp.org/db/conf/{}/{}{}.html".format(args.name,args.name,args.time)

    # Conf
    for conf in A_CONF_LIST:
        print("Looking for papers from conferences {} {}, keyword: {}".format(conf, args.time, keyword))
        url = "https://dblp.org/db/conf/%s/%s%s.html" % (conf, conf, args.time)
        extract_papers(url, 'conf', conf, keyword)

    # Journal
    for journal in A_JOURNAL_LIST:
        print("Looking for papers from journals {} {}, keyword: {}".format(journal, args.time, keyword))
        url = 'https://dblp.uni-trier.de/db/journals/%s/index.html' % journal

        extract_papers(url, 'journal', journal, keyword)