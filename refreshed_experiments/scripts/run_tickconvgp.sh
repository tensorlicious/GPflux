#!/usr/bin/env bash

CUDA_VISIBLE_DEVICES=0 python ../main.py -mc convgp_creator -d mnist -c TickConvGPConfig -t ClassificationGPTrainer -p "$1" &
CUDA_VISIBLE_DEVICES=1 python ../main.py -mc convgp_creator -d fashion_mnist -c TickConvGPConfig -t ClassificationGPTrainer -p "$1" &
CUDA_VISIBLE_DEVICES=2 python ../main.py -mc convgp_creator -d grey_cifar10 -c TickConvGPConfig -t ClassificationGPTrainer -p "$1" &
CUDA_VISIBLE_DEVICES=3 python ../main.py -mc convgp_creator -d svhn -c TickConvGPConfig -t ClassificationGPTrainer -p "$1" &
