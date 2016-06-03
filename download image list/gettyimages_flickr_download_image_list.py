import urllib
import urllib2
import re
from bs4 import BeautifulSoup
import sys
import os
import errno
import random
import string
from argparse import ArgumentParser
import time


FLAG_python = True
reload(sys)
sys.setdefaultencoding('utf-8')

def _get_random_id():
    characters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a','b','c','d','e','f','g','h','i','j','k','l','m','n']
    id_element = random.sample(characters, 8)
    random_id = ''.join(id_element)
    return random_id

def _mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def _get_page(url):
    headers = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'}
    request = urllib2.Request(url,headers = headers)
    response = urllib2.urlopen(request)
    page = response.read()
    return page

def _get_infos_gettyimages(page):
    total_pages = 0
    content1 = BeautifulSoup(page,"lxml").select('.full.pagination')
    content2 = BeautifulSoup(page,"lxml").select('.details-wrap .asset-link')

    pages_pattern = re.compile(r'page-count="(\d*)"')
    id_pattern = re.compile(r'data-asset-id="(.*?)"')
    pages_find = re.findall(pages_pattern, str(content1))
    id_find = re.findall(id_pattern, str(content2))

    if len(pages_find):
        total_pages = int(pages_find[0])

    return total_pages, id_find

def _get_infos_flickr(page):
    total_pages = 0
    content = BeautifulSoup(page,"lxml").find('p').getText()

    pages_pattern = re.compile(r'"pages":(\d*),')
    url_pattern = re.compile(r',"url_l":"(.*?)\.jpg",')

    pages_find = re.findall(pages_pattern, str(content))
    url_find = re.findall(url_pattern, str(content))

    if len(pages_find):
        total_pages = int(pages_find[0])

    return total_pages, url_find

def _download_img_gettyimages(img_ids, img_dir):
    img_url_prefix = 'http://media.gettyimages.com/photos/id'
    for img_id in img_ids:
        img_url = img_url_prefix + img_id
        print img_url
#         urllib.urlretrieve(img_url, img_dir + '/%s.jpg' % img_id)

def _download_img_flickr(img_urls, img_dir):
    for ele in img_urls:
        img_url = ele.replace("\/", "/") + '.jpg'
        id_pattern = re.compile(r'\/(\d*)_')
        id_find = re.findall(id_pattern, ele)
        if len(id_find):
            img_id = id_find[0]
            print img_url
#             urllib.urlretrieve(img_url, img_dir + '/%s.jpg' % img_id)

def _download_img_list_gettyimages(img_id_list, file_name):
    img_url_prefix = 'http://media.gettyimages.com/photos/id'
    img_list_file = open(file_name, 'w')
    # img_list_file_wget = open((file_name + '_wget'), 'w')

    for img_id in img_id_list:
        img_url = img_url_prefix + img_id
#         print img_url
        # img_list_file_wget.write(img_url + '\n')
        img_list_file.write('gettyimg_' + str(img_id) + '   ' + img_url + '\n')

    img_list_file.close()
    # img_list_file_wget.close()

def _download_img_list_flickr(img_url_list, file_name):
    img_list_file = open(file_name, 'w')
    # img_list_file_wget = open((file_name + '_wget'), 'w')

    for ele in img_url_list:
        img_url = ele.replace("\/", "/") + '.jpg'
        id_pattern = re.compile(r'\/(\d*)_')
        id_find = re.findall(id_pattern, ele)
        if len(id_find):
            img_id = id_find[0]
#             print img_url
            # img_list_file_wget.write(img_url + '\n')
            img_list_file.write('flickr_' + str(img_id) + '   ' + img_url + '\n')

    img_list_file.close()
    # img_list_file_wget.close()


def _get_entry_url_gettyimages(page_index, keywords):
    # entry_url = 'http://www.gettyimages.com/photos/bow-arrows?excludenudity=true&page=2&phrase=bow%20arrows&sort=best'
    keywords_form_1 = '-'.join(keywords.split())
    keywords_form_2 = '%20'.join(keywords.split())

    entry_url = 'http://www.gettyimages.com/photos/' + keywords_form_1 + '?excludenudity=true&page=' + str(page_index) + '&phrase=' + keywords_form_2 + '&sort=best'
    return entry_url

def _get_entry_url_flickr(page_index, keywords):
    search_keywords = '%20'.join(keywords.split())
    # search_keywords = '-'.join(keywords.split())

    valid_api_key = '02e15afd83b1ed0344f80df3ff70a866'

    url_head = 'https://api.flickr.com/services/rest?sort=relevance&parse_tags=1&content_type=7&extras=can_comment%2Ccount_comments%2Ccount_faves%2Cdescription%2Cisfavorite%2Clicense%2Cmedia%2Cneeds_interstitial%2Cowner_name%2Cpath_alias%2Crealname%2Crotation%2Curl_c%2Curl_l%2Curl_m%2Curl_n%2Curl_q%2Curl_s%2Curl_sq%2Curl_t%2Curl_z%2Cis_marketplace_licensable&'
    url_per_page = 'per_page=500'
    url_page_index = '&page=' + str(page_index)
    #url_search_condition = 'dimension_search_mode=min&height=640&width=640&advanced=1&media=photos&text=rubber%20eraser'
    url_search_condition = '&lang=en-US&dimension_search_mode=min&height=640&width=640&media=photos&text=' + search_keywords
    #url_search_condition = '&lang=en-US&media=photos&text=' + search_keywords
    url_api_key = '&viewerNSID=&method=flickr.photos.search&csrf=&api_key=' + valid_api_key
    url_reqId = '&format=json&hermes=1&hermesClient=1&reqId=' + _get_random_id()
    url_end = '&nojsoncallback=1'

    entry_url = url_head + url_per_page + url_page_index + url_search_condition + url_api_key + url_reqId + url_end
    return entry_url

def _get_entry_url(page_index, keywords, website):
    if (website == 'gettyimages'):
        return _get_entry_url_gettyimages(page_index, keywords)
    elif (website == 'flickr'):
        return _get_entry_url_flickr(page_index, keywords)

def _get_infos(pages, website):
    if (website == 'gettyimages'):
        return _get_infos_gettyimages(pages)
    elif (website == 'flickr'):
        return _get_infos_flickr(pages)

def _download_img_list(img_infos_list, file_name, website):
    if (website == 'gettyimages'):
        return _download_img_list_gettyimages(img_infos_list, file_name)
    elif (website == 'flickr'):
        return _download_img_list_flickr(img_infos_list, file_name)


def _crawl_images(keywords, img_num, file_name, website):
    print 'keywords:', keywords
    print 'Need total images:', img_num
    print 'output file:', file_name

    page_index = 1
    img_infos = []

    while(1):
        entry_url = _get_entry_url(page_index, keywords, website)
        page = _get_page(entry_url)
#         print entry_url

        total_pages, infos = _get_infos(page, website)
        print '******current page:', page_index, '******total_page:', total_pages, '*******'

        if (total_pages==0):
            break

        if len(infos):
            img_infos.extend(infos)

        # remove redundant id
        # if ((len(img_infos)%500 == 0)):
        img_infos = list(set(img_infos))

        if (img_num < len(img_infos)):
            break

        print (img_num - len(img_infos)), 'more images need to crawl'

        page_index += 1

        if (page_index > total_pages):
            print 'current page:', page_index, 'is last pages'
            break


    print 'Downloading...............'
    #remove redundant id
    img_infos = list(set(img_infos))
    print 'img_infos len:', len(img_infos)
    _download_img_list(img_infos, file_name, website)


def _crawler(keywords, img_num, outdir):
    print '############################ Keywords ###############################'
    file_dir = os.path.normpath(outdir + '/' + '_'.join(keywords.split()))
    _mkdir_p(file_dir)

    file_name_gettyimages = file_dir + '/' + 'gettyimages_' + '_'.join(keywords.split()) + '.txt'
    file_name_flickr = file_dir + '/' + 'flickr_' + '_'.join(keywords.split()) + '.txt'

    start_time = time.time()

    print '*************** Download images from gettyiimages ****************'
    _crawl_images(keywords, img_num, file_name_gettyimages, 'gettyimages')
    print("----------- %s seconds ----------" % (time.time() - start_time))

    print '*************** Download images from flickr **********************'
    # _crawl_images(keywords, img_num, file_name_flickr, 'flickr')
    print("----------- %s seconds ----------" % (time.time() - start_time))



def main(args):
    if FLAG_python is True:
        # for python run in command-line
#         keywords = args.keywords
        keywords_file = args.keywords_file
        outdir = args.outdir
        img_num = args.img_num
        print 'Python'
    else:
        # for jupyter
#         keywords = args['keywords']
        keywords_file = args['keywords_file']
        outdir = args['outdir']
        img_num = args['img_num']
        print 'Jupyter'

    print '######################## Keywords List ###############################'

    keywords_list = list()

    fkeywords = open(keywords_file, 'r')
    lines = fkeywords.readlines()
    for eachline in lines:
        eachline = eachline.strip()
        if not len(eachline) or eachline.startswith('#'):
            continue
        keywords_list.append(eachline)
        print eachline
    fkeywords.close()

    print '################################################################'
    print ''
    print '++++++++++++++++++++++++++ START +++++++++++++++++++++++++++++++++'
    for keywords in keywords_list:
        _crawler(keywords, img_num, outdir)
        print '-----------------------------------------'
        print ''
        print ''
    print '++++++++++++++++++++++++++ DONE ++++++++++++++++++++++++++++++++++'



if FLAG_python is True:
    if __name__ == "__main__":
        parser = ArgumentParser(
            description="crawl images")
#         parser.add_argument('-keywords', required=True)
        parser.add_argument('-keywords_file', required=True)
        parser.add_argument('-img_num',type=int,required=True)
        parser.add_argument('-outdir', required = True)
        args = parser.parse_args()
        main(args)
else:
    args = {}
#     args['keywords'] = 'dog'
    args['keywords_file'] = '/home/lpzhang/Desktop/crawler/keywords_01.txt'
    args['img_num'] = 10
    args['outdir'] = "/home/lpzhang/Desktop/crawler/ImageNet"
    # print args
    main(args)

