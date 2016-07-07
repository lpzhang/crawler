#crawler images from website
step 1: crawl image url
./crawl_image_list/crawl_image_list.sh
crawl images id and url from keyword file
results which each file contains image id and url are store in ./output

step 2: download image from url
./download_images/download_images.sh
download images from above crawled file
outputs are store in ./output

#delete similar images compare to other dataset
step 1: Refiner for ITSELF
delete duplicate images based on histogram features

step 2: Refiner for TRAIN
delete images which are similar with trainval set

step 3: Refiner for TEST
delete images which are similar with testset
