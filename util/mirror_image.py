#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# michinari.nukazawa@gmail.com

import cv2
import sys
import os.path
import argparse
import sys
import copy
import logging
from glob import glob
import PIL.Image
import PIL.ImageOps

import pprint
pp = pprint.PrettyPrinter(indent=4)



def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("input_dir")
	parser.add_argument("--is_same_dir", action="store_true", help="output image to a input_dir")
	parser.add_argument('--max_num', type=int, default=-1)
	parsed = parser.parse_args()

	# input image files
	if os.path.isfile(parsed.input_dir):
		files = [parsed.input_dir]
	else:
		files = glob('{}/*.*'.format(parsed.input_dir))

	# ** output dir
	if parsed.is_same_dir:
		output_dir = os.path.normpath(parsed.input_dir)
	else:
		output_dir = "{}_{}".format(os.path.normpath(parsed.input_dir), "mirror")
		os.makedirs(output_dir, exist_ok=True)


	imagefile_count = 0
	for i, image_filepath in enumerate(files):
		image_filename, ext = os.path.splitext(os.path.basename(image_filepath))
		output_imagefile = os.path.join(output_dir, "{}_mirror{:02}{}".format(image_filename, 0, ".jpg"))

		try:
			image = PIL.Image.open(image_filepath)

			image_mirror = PIL.ImageOps.mirror(image)
			image_mirror.save(output_imagefile, quality=95)
		except Exception:
			logging.exception('Failed to image: `%s`', image_filepath)
			continue

		imagefile_count += 1
		if -1 != parsed.max_num and parsed.max_num <= imagefile_count:
			break
		if 0 == (imagefile_count % 100):
			print("{} {}/{}".format(i, imagefile_count, len(files)))


	print("end:{:4}/{:4}".format(imagefile_count, len(files)))


if __name__ == '__main__':
	main()

