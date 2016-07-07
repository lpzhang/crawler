#!/bin/bash
nohup ./wget_tools.sh "../crawl_image_list/keyword/gettyimages.download" >& log/gettyimages.log 2>&1 &
nohup ./wget_tools.sh "../crawl_image_list/keyword/flickr.download" >& log/flickr.log 2>&1 &
nohup ./wget_tools.sh "../crawl_image_list/keyword/istockphoto.download" >& log/istockphoto.log 2>&1 &
nohup ./wget_tools.sh "../crawl_image_list/keyword/dreamstime.download" >& log/dreamstime.log 2>&1 &
nohup ./wget_tools.sh "../crawl_image_list/keyword/pond5.download" >& log/pond5.log 2>&1 &
