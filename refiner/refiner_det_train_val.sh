#!/bin/bash
#nq python -u refiner.py -dtype="TRAIN" -fpath="/home/lpzhang/Desktop/crawler/refine_images/refiner/refine_det_train_val.txt_0.5" -threshold=0.5 >& log_refine_det_train_val.txt_0.5 2>&1 &
#nq python -u refiner.py -dtype="TRAIN" -fpath="/home/lpzhang/Desktop/crawler/refine_images/refiner/refine_det_train_val.txt_0.6" -threshold=0.5 >& log_refine_det_train_val.txt_0.6 2>&1 &
#nq python -u refiner.py -dtype="TRAIN" -fpath="/home/lpzhang/Desktop/crawler/refine_images/refiner/refine_det_train_val.txt_0.7" -threshold=0.5 >& log_refine_det_train_val.txt_0.7 2>&1 &
#nq python -u refiner.py -dtype="TRAIN" -fpath="/home/lpzhang/Desktop/crawler/refine_images/refiner/refine_det_train_val.txt_0.8" -threshold=0.5 >& log_refine_det_train_val.txt_0.8 2>&1 &
#nohup python -u refiner.py -dtype="TRAIN" -fpath="/home/lpzhang/Desktop/crawler/refine_images/refiner/refine_det_train_val_part2.txt" -threshold=0.5 >& log_refine_det_train_val_part2.txt 2>&1 &
nohup python -u refiner.py -dtype="TRAIN" -fpath="/home/lpzhang/Desktop/crawler/refine_images/refiner/refine_det_train_val_part2.txt" -threshold=0.5 >& log_refine_det_train_val_part2_extra.txt 2>&1 &
