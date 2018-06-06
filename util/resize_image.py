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



def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("input_dir")
	parser.add_argument('--size', type=int, default=256, choices=[0, 16, 32, 64, 128, 256])
	parser.add_argument('--max_num', type=int, default=-1)
	parsed = parser.parse_args()

	#print(parsed.input_dir)

	IMAGE_SIZE = (parsed.size, parsed.size)

	files = glob('{}/*.*'.format(parsed.input_dir))

	if 0 == len(files):
		sys.stderr.write('Error: `{}`'.format(parsed.input_dir))
		sys.exit()

	output_dir = "{}_{}x{}".format(os.path.normpath(parsed.input_dir), IMAGE_SIZE[0], IMAGE_SIZE[1])
	#os.makedirs(output_dir, exist_ok=True)
	os.makedirs(output_dir, exist_ok=False)

	imagefile_count = 0
	for i, image_filepath in enumerate(files):
		try:
			image = PIL.Image.open(image_filepath)
		except Exception:
			logging.exception('Failed to open image: `%s`', image_filepath)
			continue

		image_filename, ext = os.path.splitext(os.path.basename(image_filepath))
		dst_image_filepath = os.path.join(output_dir, image_filename + ".jpg")

		try:
			if 0 != parsed.size:
				image.thumbnail(IMAGE_SIZE, resample=PIL.Image.BICUBIC)
			dst_image = image
			if dst_image.mode == 'RGB':
				pass
			elif dst_image.mode == 'RGBA':
				#dst_image.convert("RGB")
				BACKGROUND_COLOR = (255, 255, 255)
				src_image_size = (dst_image.width, dst_image.height)
				tmp_dst_image = PIL.Image.new("RGB", src_image_size, BACKGROUND_COLOR)
				tmp_dst_image.paste(dst_image, mask=dst_image.split()[3]) # 3 is the alpha channel
				dst_image = tmp_dst_image
			else:
				logging.exception('skip: %s %s', image_filepath, dst_image.mode)
				continue

			dst_image.save(dst_image_filepath, quality=95)
			image_filepath = dst_image_filepath
		except Exception:
			logging.exception('Failed to convert: %s', image_filepath)
			continue

		imagefile_count += 1
		if -1 != parsed.max_num and parsed.max_num <= imagefile_count:
			break
		if 0 == (imagefile_count % 100):
			print("{} {}/{}".format(i, imagefile_count, len(files)))


	print("end:{:4}/{:4}".format(imagefile_count, len(files)))

if __name__ == '__main__':
	main()

