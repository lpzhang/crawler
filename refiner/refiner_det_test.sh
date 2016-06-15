#!/bin/bash
#nohup python -u refiner.py -dtype="TEST" -fpath="/home/lpzhang/Desktop/crawler/refine_images/refiner/refine_det_test.txt_part1" -threshold=0.5 >& log_refine_det_test.txt_part1 2>&1 &
nohup python -u refiner.py -dtype="TEST" -fpath="/home/lpzhang/Desktop/crawler/refine_images/refiner/refine_det_test_part2.txt" -threshold=0.5 >& log_refine_det_test_part2_extra.txt 2>&1 &
