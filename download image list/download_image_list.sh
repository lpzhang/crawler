#!/bin/bash

nohup python -u gettyimages_flickr_download_image_list.py -keywords_file='/home/lpzhang/Desktop/crawler/keywords_01.txt' -img_num=10000 -outdir='/home/lpzhang/Desktop/crawler/ImageNet/' >& log_download_image_list_keywords_01.txt 2>&1 & 

