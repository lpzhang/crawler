#!/bin/bash
nohup python -u refiner.py -dtype="ITSELF" -fpath="/home/lpzhang/Desktop/crawler/refine_images/refiner/refine_itself_part2.txt" -threshold=0.6 >& log_refine_itself_part2.txt 2>&1 &
