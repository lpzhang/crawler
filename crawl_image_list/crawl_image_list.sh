#!/bin/bash
nohup python -u crawler.py -webtype='gettyimages' -keywords_file='keyword/gettyimages.keyword' -image_number=2 -outdir='../output' >& log/gettyimages.log 2>&1 & 
nohup python -u crawler.py -webtype='flickr' -keywords_file='keyword/flickr.keyword' -image_number=2 -outdir='../output' >& log/flickr.log 2>&1 & 
nohup python -u crawler.py -webtype='istockphoto' -keywords_file='keyword/istockphoto.keyword' -image_number=2 -outdir='../output' >& log/istockphoto.log 2>&1 & 
nohup python -u crawler.py -webtype='dreamstime' -keywords_file='keyword/dreamstime.keyword' -image_number=2 -outdir='../output' >& log/dreamstime.log 2>&1 & 
nohup python -u crawler.py -webtype='pond5' -keywords_file='keyword/pond5.keyword' -image_number=2 -outdir='../output' >& log/pond5.log 2>&1 &
