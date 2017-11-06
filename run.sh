#!/bin/bash
# Thanks to Naoki Shibuya for basic ideas of this script

export EXPLORER=$1
export SEARCH=$2

maze_id=$3

python tester.py test_maze_$maze_id.txt