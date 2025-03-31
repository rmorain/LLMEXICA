#!/bin/sh
# salloc --ntasks=1 --qos=cs --nodes=1 --gpus=6 --mem-per-cpu=64G --time=02:00:00
salloc --ntasks=1 --qos=test --nodes=1 --gpus=1 --mem-per-cpu=64G --time=00:30:00