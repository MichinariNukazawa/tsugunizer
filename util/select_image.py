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
import json
import re
import PIL.Image
import shutil



def read_pixiv_datas_file(pixiv_data_filepath):
	f = open(pixiv_data_filepath, 'r')
	s = f.read()
	#pp.pprint(s)
	s = s[:-2]
	s = "[\n" + s + "\n]"
	#pp.pprint(s)
	pixiv_data_list = json.loads(s)
	#pp.pprint(pixiv_data_list)
	#pp.pprint(len(pixiv_data_list))
	f.close()
	return pixiv_data_list


def read_pixiv_datas_file_from_dirpath(dirpath):
	pixiv_data_filepath = os.path.join(dirpath, "data.json")
	if not os.path.exists(pixiv_data_filepath):
		sys.stderr.write("Error: `{}`\n".format(pixiv_data_filepath))
		sys.exit()

	return read_pixiv_datas_file(pixiv_data_filepath)


def get_pixiv_data_from_pixiv_image_id(pixiv_data_list, pixiv_image_id):
	for pdata in pixiv_data_list:
		if pdata["id"] == pixiv_image_id:
			return pdata
	return None


def read_ignore_list_file(ignore_list_filepath):
	f = open(ignore_list_filepath, 'r')
	lines = f.readlines()
	f.close()

	datas = {}
	for line_num, line in enumerate(lines):
		if '#' == line[0]:
			# comment
			continue
		match = re.search('^([0-9]+)', line)
		if not match:
			continue
		pixiv_image_id = int(match.group(1), 10)

		#print("line: {}:{} {}".format(line_num, pixiv_image_id, line))

		match = re.search('^[^\s]+[\s]+(.+)$', line)
		data = {
			'is_ignore': False,
			'line_num': line_num,
			'data': None
		}
		if match:
			data['is_ignore'] = True
			data['data'] = match.group(1) # not implement read ignore string

		if pixiv_image_id in datas:
			print("already. line_num:{} id:{} line_num{}".format(
				line_num, pixiv_image_id, datas[pixiv_image_id]["line_num"]))
			continue

		datas[pixiv_image_id] = data
	return datas

def is_image(filepath):
	match = re.match(".*\.(jpg|png)$", filepath)
	if match:
		return True
	else:
		return False

def get_pixiv_image_id_from_image_filename(filename):
	match = re.search('^([0-9]+)', filename)
	if not match:
		return None
	pixiv_image_id = int(match.group(1), 10)

	return pixiv_image_id


def is_ignore_from_pixiv_image_id(ignore_list, pixiv_image_id):
	if not pixiv_image_id in ignore_list:
		sys.stderr.write("Notice: {}\n".format(pixiv_image_id))
		return True

	return ignore_list[pixiv_image_id]["is_ignore"]


def main():

	# ** arg
	parser = argparse.ArgumentParser()
	parser.add_argument("input_dir")
	parser.add_argument("--output_dir", type=str, default="./select")
	parser.add_argument('--max_num', type=int, default=-1)
	parser.add_argument('--score_min', type=int, default=0)
	parser.add_argument('--ignore_list', help="ignore list filepath")
	parsed = parser.parse_args()

	#print(parsed.input_dir)
	#print(parsed.score_min)
	#print(parsed.ignore_list)

	# *** input_dir
	files = glob('{}/*.*'.format(parsed.input_dir))

	image_files = []
	for ifile in files:
		if is_image(ifile):
			image_files.append(ifile)
		else:
			sys.stderr.write("Notice: not image. `{}`\n".format(ifile))

	if 0 == len(image_files):
		sys.stderr.write("Error: `{}`\n".format(parsed.input_dir))
		sys.exit()

	#print(files)
	print("files: {}/{}".format(len(image_files), len(files)))

	## *** score_min
	if 0 != parsed.score_min:
		pixiv_data_list = read_pixiv_datas_file_from_dirpath(parsed.input_dir)
		if not pixiv_data_list:
			sys.stderr.write("Error: cant get score. `{}`\n".format(parsed.input_dir))
			sys.exit()

		print("pixiv_data_list:{}".format(len(pixiv_data_list)))
		#pprint.pprint(pixiv_data_list)

	## *** ignore_list
	ignore_list = []
	if parsed.ignore_list:
		ignore_list = read_ignore_list_file(parsed.ignore_list)
		if not ignore_list:
			sys.stderr.write("Error: cant get ignore_list. `{}`\n".format(parsed.ignore_list))
			sys.exit()

	# pprint.pprint(ignore_list)

	y_ignore_count = 0
	n_ignore_count = 0
	for key in ignore_list:
		ignore = ignore_list[key]
		if ignore["is_ignore"]:
			y_ignore_count += 1
		else:
			n_ignore_count += 1

	print("ignore_list:{}".format(len(ignore_list)))
	print("ignore_list:{} {}".format(y_ignore_count, n_ignore_count))
	#pprint.pprint(ignore_list)

	# * output dir
	# output_dir = os.path.join(os.path.dirname(os.path.normpath(parsed.input_dir)), parsed.outout_dirname)
	output_dir = parsed.output_dir
	os.makedirs(output_dir, exist_ok=False)

	imagefile_count = 0
	under_score_image_count = 0
	for i, image_file in enumerate(image_files):

		pixiv_image_id = get_pixiv_image_id_from_image_filename(os.path.basename(image_file))
		if not pixiv_image_id:
			sys.stderr.write("Notice: {}`{}`\n".format(i, image_file))
			continue

		pixiv_data = get_pixiv_data_from_pixiv_image_id(pixiv_data_list, pixiv_image_id)
		if not pixiv_data:
			sys.stderr.write("Notice: {} `{}``{}`\n".format(i, image_file, pixiv_image_id))
			continue

		if pixiv_data["type"] != "illustration":
			continue

		# TODO image num = 1

		if 0 < parsed.score_min:
			if pixiv_data["stats"]["score"] < parsed.score_min:
				under_score_image_count += 1
				#sys.stderr.write("Info: {} `{}``{}`\n".format(i, image_file, pixiv_image_id))
				continue

		if parsed.ignore_list:
			if is_ignore_from_pixiv_image_id(ignore_list, pixiv_image_id):
				#sys.stderr.write("Info: {} `{}``{}`\n".format(i, image_file, pixiv_image_id))
				continue

		shutil.copy2(image_file, output_dir)

		if 0 == (imagefile_count % 100):
			print("progress: {} {} {}/{}".format(i, under_score_image_count, imagefile_count, len(image_files)))
		imagefile_count += 1

		if -1 != parsed.max_num and parsed.max_num <= imagefile_count:
			break

	print("end: {} {} {}/{}".format(i, under_score_image_count, imagefile_count, len(image_files)))

if __name__ == '__main__':
	main()

