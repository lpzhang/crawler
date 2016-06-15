# crawler
crawler images from website for ImageNet Extra Dataset

step 1: crawl image url
download_image_list.sh call gettyimages_flickr_download_image_list.py to:
crawl images id and url from keywords
output image list file which eachline contains image id and url

step 2: download image from url
wget_download_images.sh call wget_download.sh to:
download images from crawled file from step 1 which contain image id and url.

step 3: Refiner for ITSELF
delete duplicate images based on histogram features

step 4: Refiner for Train
delete images which are similar with Imagenet train dataset

step 5: Refiner for Test
delete images which are similar with Imagenet Test dataset
