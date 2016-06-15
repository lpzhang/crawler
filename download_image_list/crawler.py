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

def _mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def _get_random_id():
    characters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a','b','c','d','e','f','g','h','i','j','k','l','m','n']
    id_element = random.sample(characters, 8)
    random_id = ''.join(id_element)
    return random_id

def _get_infos_from_textfile(fname):
    info_list = list()

    fid = open(fname, 'r')
    lines = fid.readlines()
    for eachline in lines:
        eachline = eachline.strip()
        if not eachline.startswith('#') and len(eachline):
            info_list.append(eachline)
    fid.close()

    return info_list

def entryurl_gettyimages(page_index, keyword):
    # entry_url = 'http://www.gettyimages.com/photos/bow-arrows?excludenudity=true&page=2&phrase=bow%20arrows&sort=best'
    keyword_form_1 = '-'.join(keyword.split())
    keyword_form_2 = '%20'.join(keyword.split())

    entryurl = 'http://www.gettyimages.com/photos/' + keyword_form_1 + '?excludenudity=true&page=' + str(page_index) + '&phrase=' + keyword_form_2 + '&sort=best'

    return entryurl

def entryurl_flickr(page_index, keyword):
    keyword_form = '%20'.join(keyword.split())
#     keyword_form = '-'.join(keyword.split())
    valid_api_key = 'ac22c904b967ae887c969c9ba5a4d7f5'
    url_head = 'https://api.flickr.com/services/rest?sort=relevance&parse_tags=1&content_type=7&extras=can_comment%2Ccount_comments%2Ccount_faves%2Cdescription%2Cisfavorite%2Clicense%2Cmedia%2Cneeds_interstitial%2Cowner_name%2Cpath_alias%2Crealname%2Crotation%2Curl_c%2Curl_l%2Curl_m%2Curl_n%2Curl_q%2Curl_s%2Curl_sq%2Curl_t%2Curl_z%2Cis_marketplace_licensable&'
    url_per_page = 'per_page=1000'
    url_page_index = '&page=' + str(page_index)
    #url_search_condition = 'dimension_search_mode=min&height=640&width=640&advanced=1&media=photos&text=rubber%20eraser'
    url_search_condition = '&lang=en-US&dimension_search_mode=min&height=640&width=640&media=photos&text=' + keyword_form
    url_api_key = '&viewerNSID=&method=flickr.photos.search&csrf=&api_key=' + valid_api_key
    url_reqId = '&format=json&hermes=1&hermesClient=1&reqId=' + _get_random_id()
    url_end = '&nojsoncallback=1'

    entryurl = url_head + url_per_page + url_page_index + url_search_condition + url_api_key + url_reqId + url_end

    return entryurl

def entryurl_istockphoto(page_index, keyword):
    keyword_form_1 = '+'.join(keyword.split())
    keyword_form_2 = '%20'.join(keyword.split())

    url_head = 'http://www.istockphoto.com/hk/photos/'
    url_search_condition = keyword_form_1 + '?facets=%7B%22text%22:%5B%22' + keyword_form_2
    url_page_index = '%22%5D,%22pageNumber%22:' + str(page_index)
    url_end = ',%22perPage%22:1000,%22abstractType%22:%5B%22photos%22%5D,%22order%22:%22bestMatch%22,%22f%22:true%7D'

    entryurl = url_head + url_search_condition + url_page_index + url_end

    return entryurl

def entryurl_dreamstime(page_index, keyword):
    search_keyword = '%20'.join(keyword.split())
    url_head = 'http://www.dreamstime.com/search.php?srh_field='
    url_end = '&s_ph=y&s_il=y&s_rf=y&s_ed=y&s_clc=y&s_clm=y&s_orp=y&s_ors=y&s_orl=y&s_orw=y&s_st=new&s_sm=all&s_rsf=0&s_rst=7&s_mrg=1&s_sl0=y&s_sl1=y&s_sl2=y&s_sl3=y&s_sl4=y&s_sl5=y&s_mrc1=y&s_mrc2=y&s_mrc3=y&s_mrc4=y&s_mrc5=y&s_exc=&items=1000&pg='

    entryurl = url_head + search_keyword + url_end + str(page_index)

    return entryurl

def response_contents(url):
    headers = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'}
    request = urllib2.Request(url, headers = headers)
    response = urllib2.urlopen(request)
    content = response.read()

    return content

def extract_infos_gettyimages(content):
    urlprefix = 'http://media.gettyimages.com/photos/id'
    img_id_url_dict = dict()

    content1 = BeautifulSoup(content,"lxml").select('.full.pagination')
    content2 = BeautifulSoup(content,"lxml").select('.details-wrap .asset-link')

    pages_pattern = re.compile(r'page-count="(\d*)"')
    id_pattern = re.compile(r'data-asset-id="(.*?)"')
    pages_find = re.findall(pages_pattern, str(content1))
    id_find = re.findall(id_pattern, str(content2))

    total_pages = int(pages_find[0]) if len(pages_find) else 0

    for imgid in id_find:
        if imgid not in img_id_url_dict:
            imgurl = urlprefix + imgid
            img_id_url_dict[imgid] = imgurl

    return total_pages, img_id_url_dict

def extract_infos_flickr(content):
    img_id_url_dict = dict()

    content = BeautifulSoup(content,"lxml").find('p').getText()

    pages_pattern = re.compile(r'"pages":(\d*),')
    url_pattern = re.compile(r',"url_l":"(.*?)\.jpg",')
    pages_find = re.findall(pages_pattern, str(content))
    url_find = re.findall(url_pattern, str(content))
    id_pattern = re.compile(r'\/(\d*)_')

    total_pages = int(pages_find[0]) if len(pages_find) else 0

    for eachurl in url_find:
        id_find = re.findall(id_pattern, eachurl)
        if len(id_find):
            imgid = id_find[0]
            if imgid not in img_id_url_dict:
                imgurl = eachurl.replace("\/", "/") + '.jpg'
                img_id_url_dict[imgid] = imgurl

    return total_pages, img_id_url_dict

def extract_infos_istockphoto(content):
    urlprefix = 'http://media.istockphoto.com/photos/id'
    img_id_url_dict = dict()

    content1 = BeautifulSoup(content,"lxml").select('.file-count-label')
    content2 = BeautifulSoup(content,"lxml").select('.figure-holder')

    imgnum_pattern = re.compile(r'>(\d*)</span>')
    id_pattern = re.compile(r'-gm(\d*)-')
    imgnum_find = re.findall(imgnum_pattern, str(content1))
    id_find = re.findall(id_pattern, str(content2))

    imgnum = imgnum_find[0].split(',')
    imgnum = ''.join(imgnum)
    imgnum = int(imgnum) if len(imgnum) else 0
    total_pages = (imgnum//1000 + 1) if (imgnum%1000) else (imgnum//1000)

    for imgid in id_find:
        if imgid not in img_id_url_dict:
            imgurl = urlprefix + imgid
            img_id_url_dict[imgid] = imgurl

    return total_pages, img_id_url_dict

def extract_infos_dreamstime(content):
    urlprefix = 'http://thumbs.dreamstime.com/z/image-'
    img_id_url_dict = dict()

    content1 = BeautifulSoup(content,"lxml").select('.dt-pull-center')
    content2 = BeautifulSoup(content,"lxml").select('.thb-large-gi-box.thb-large-box')

    imgnum_pattern = re.compile(r'<strong>(.*?)</strong>')
    id_pattern = re.compile(r'id="bigthumb(.*?)" src=') #or re.compile(r'<div id="thb_cell(.*?)"><a')
    imgnum_find = re.findall(imgnum_pattern, str(content1))
    id_find = re.findall(id_pattern, str(content2))

    imgnum = imgnum_find[0].split(',')
    imgnum = ''.join(imgnum)
    imgnum = int(imgnum) if len(imgnum) else 0
    total_pages = (imgnum//1000 + 1) if (imgnum%1000) else (imgnum//1000)

    for imgid in id_find:
        if imgid not in img_id_url_dict:
            imgurl = urlprefix + imgid + '.jpg'
            img_id_url_dict[imgid] = imgurl

    return total_pages, img_id_url_dict

def save_infos(img_id_url_dict, idprefix, fname):
    fid = open(fname, 'w')

    for imgid in img_id_url_dict:
        imgurl = img_id_url_dict[imgid]
        fid.write(idprefix + str(imgid) + '   ' + imgurl + '\n')

    fid.close()

def crawler_gettyimages(keyword, image_number):
    image_id_url_dict = dict()
    page_index = 1

    while(1):
        entryurl = entryurl_gettyimages(page_index, keyword)
        contents = response_contents(entryurl)
        total_pages, img_id_url_dict = extract_infos_gettyimages(contents)

        if (total_pages == 0):
            break
        print('****** current page %d (%d) ******' % (page_index, total_pages))

        image_id_url_dict.update(img_id_url_dict)
        if (image_number < len(image_id_url_dict)):
            break

        page_index += 1
        if (page_index > total_pages):
            print('current page %d is last pages' % (page_index))
            break

        print('%d more images need to crawl' % (image_number - len(image_id_url_dict)))

    return image_id_url_dict

def crawler_flickr(keyword, image_number):
    image_id_url_dict = dict()
    page_index = 1

    while(1):
        entryurl = entryurl_flickr(page_index, keyword)
        contents = response_contents(entryurl)
        total_pages, img_id_url_dict = extract_infos_flickr(contents)

        if (total_pages == 0):
            break
        print('****** current page %d (%d) ******' % (page_index, total_pages))

        image_id_url_dict.update(img_id_url_dict)
        if (image_number < len(image_id_url_dict)):
            break

        page_index += 1
        if (page_index > total_pages):
            print('current page %d is last pages' % (page_index))
            break

        print('%d more images need to crawl' % (image_number - len(image_id_url_dict)))

    return image_id_url_dict

def crawler_istockphoto(keyword, image_number):
    image_id_url_dict = dict()
    page_index = 1

    while(1):
        entryurl = entryurl_istockphoto(page_index, keyword)
        contents = response_contents(entryurl)
        total_pages, img_id_url_dict = extract_infos_istockphoto(contents)

        if (total_pages == 0):
            break
        print('****** current page %d (%d) ******' % (page_index, total_pages))

        image_id_url_dict.update(img_id_url_dict)
        if (image_number < len(image_id_url_dict)):
            break

        page_index += 1
        if (page_index > total_pages):
            print('current page %d is last pages' % (page_index))
            break

        print('%d more images need to crawl' % (image_number - len(image_id_url_dict)))

    return image_id_url_dict

def crawler_dreamstime(keyword, image_number):
    image_id_url_dict = dict()
    page_index = 1

    while(page_index <= 10):
        entryurl = entryurl_dreamstime(page_index, keyword)
        contents = response_contents(entryurl)
        total_pages, img_id_url_dict = extract_infos_dreamstime(contents)

        if (total_pages == 0):
            break
        print('****** current page %d (%d) ******' % (page_index, total_pages))

        image_id_url_dict.update(img_id_url_dict)
        if (image_number < len(image_id_url_dict)):
            break

        page_index += 1
        if (page_index > total_pages):
            print('current page %d is last pages' % (page_index))
            break

        print('%d more images need to crawl' % (image_number - len(image_id_url_dict)))

    return image_id_url_dict

def crawler_wrapper(keyword, image_number, webtype, outdir):
    assert webtype in ['gettyimages', 'flickr', 'istockphoto', 'dreamstime'], 'webtype undefined'
    outdir = os.path.normpath(outdir + '/' + '_'.join(keyword.split()))
    _mkdir_p(outdir)
    outfile = outdir + '/' + webtype + '_' + '_'.join(keyword.split()) + '.txt'
    idprefix = webtype + '_'

    assert os.path.exists(outdir), 'outdir not exist'
    assert os.path.isdir(outdir), 'outdir is not a dir'

    print 'keyword:', keyword
    print 'Need total images:', image_number
    print 'output file', outfile
    print 'idprefix', idprefix

    image_infos = dict()
    if webtype == 'gettyimages':
        print 'crawl images infos from gettyimages'
        image_infos = crawler_gettyimages(keyword, image_number)
    elif webtype == 'flickr':
        print 'crawl images infos from flickr'
        image_infos = crawler_flickr(keyword, image_number)
    elif webtype == 'istockphoto':
        print 'crawl images infos from istockphoto'
        image_infos = crawler_istockphoto(keyword, image_number)
    elif webtype == 'dreamstime':
        print 'crawl images infos from dreamstime'
        image_infos = crawler_dreamstime(keyword, image_number)

    print 'save infos'
    save_infos(image_infos, idprefix, outfile)

def main(args):
    start_time = time.time()
    if FLAG_python is True:
        # for python run in command-line
        webtype = args.webtype
        keywords_file = args.keywords_file
        image_number = args.image_number
        outdir = args.outdir
        print 'Python'
    else:
        # for jupyter
        webtype = args['webtype']
        keywords_file = args['keywords_file']
        image_number = args['image_number']
        outdir = args['outdir']
        print 'Jupyter'

    print '++++++++++++++++++++++++++ START +++++++++++++++++++++++++++++++++'
    keywords = _get_infos_from_textfile(keywords_file)
    for keyword in keywords:
        stime = time.time()
        print('------ crawl %s ------' % (keyword))
        crawler_wrapper(keyword, image_number, webtype, outdir)
        print("------ crawl %s cost %s seconds ------" % (keyword, time.time() - stime))
        print ''

    print("------------- total cost %s seconds ----------" % (time.time() - start_time))
    print '++++++++++++++++++++++++++ DONE ++++++++++++++++++++++++++++++++++'

if FLAG_python is True:
    if __name__ == "__main__":
        parser = ArgumentParser(description="crawl images")
        parser.add_argument('-webtype', required=True)
        parser.add_argument('-keywords_file', required=True)
        parser.add_argument('-image_number',type=int,required=True)
        parser.add_argument('-outdir', required = True)
        args = parser.parse_args()
        main(args)
else:
    args = {}
    args['webtype'] = 'istockphoto'
    args['keywords_file'] = '/Users/zlp/Desktop/screwdriver.txt'
    args['image_number'] = 1000
    args['outdir'] = "/Users/zlp/Desktop/"
    # print args
    main(args)
