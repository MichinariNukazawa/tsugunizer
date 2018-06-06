#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# michinari.nukazawa@gmail.com

import pprint
pp = pprint.PrettyPrinter(indent=4)
import argparse
import sys
from glob import glob
import time
import PIL.Image
import os
import logging
import random
import shutil


def shuffle_copy_dir(test_dir, train_dir, directory, test_ratio):
	files = glob('{}/*.jpg'.format(directory))
	random.shuffle(files)
	for i, file_ in enumerate(files):
		if i < (len(files) * test_ratio):
			shutil.copy2(file_, test_dir)
		else:
			shutil.copy2(file_, train_dir)



def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("output_dir")
	parser.add_argument("--input_dirsA", nargs='+')
	parser.add_argument("--input_dirsB", nargs='+')
	parser.add_argument("--test_ratio", type=float, default=0.15)
	parsed = parser.parse_args()

	if not parsed.input_dirsA:
		sys.stderr.write('Error: invalid argument A.')
		sys.exit()

	if not parsed.input_dirsB:
		sys.stderr.write('Error: invalid argument B.')
		sys.exit()

	if parsed.test_ratio < 0 or 0.5 < parsed.test_ratio:
		sys.stderr.write('Error: invalid argument test_ratio.')
		sys.exit()


	trainA_dir = os.path.join(parsed.output_dir, "trainA")
	trainB_dir = os.path.join(parsed.output_dir, "trainB")
	testA_dir = os.path.join(parsed.output_dir, "testA")
	testB_dir = os.path.join(parsed.output_dir, "testB")

	os.makedirs(parsed.output_dir, exist_ok=False)
	os.makedirs(trainA_dir, exist_ok=False)
	os.makedirs(trainB_dir, exist_ok=False)
	os.makedirs(testA_dir, exist_ok=False)
	os.makedirs(testB_dir, exist_ok=False)

	for directory in parsed.input_dirsA:
		shuffle_copy_dir(testA_dir, trainA_dir, directory, parsed.test_ratio)

	for directory in parsed.input_dirsB:
		shuffle_copy_dir(testB_dir, trainB_dir, directory, parsed.test_ratio)


if __name__ == '__main__':
	main()

