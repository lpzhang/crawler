#!/bin/bash
nohup python -u crawler.py -webtype='gettyimages' -keywords_file='/home/lpzhang/Desktop/crawler/crawl_image_list/gettyimages_keywords' -image_number=3000 -outdir='/home/lpzhang/Desktop/crawler/ImageNet/' >& log_crawler_gettyimages_keywords_02.txt 2>&1 & 
#nohup python -u crawler.py -webtype='flickr' -keywords_file='/home/lpzhang/Desktop/crawler/crawl_image_list/flickr_keywords' -image_number=9000 -outdir='/home/lpzhang/Desktop/crawler/ImageNet/' >& log_crawler_flickr_keywords.txt 2>&1 & 
#nohup python -u crawler.py -webtype='istockphoto' -keywords_file='/home/lpzhang/Desktop/crawler/crawl_image_list/istockphoto_keywords' -image_number=9000 -outdir='/home/lpzhang/Desktop/crawler/ImageNet/' >& log_crawler_istockphoto_keywords.txt 2>&1 & 
# nohup python -u crawler.py -webtype='dreamstime' -keywords_file='/home/lpzhang/Desktop/crawler/crawl_image_list/dreamstime_keywords' -image_number=9000 -outdir='/home/lpzhang/Desktop/crawler/ImageNet/' >& log_crawler_dreamstime_keywords.txt 2>&1 & 

