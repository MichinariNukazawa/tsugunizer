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

import pprint
pp = pprint.PrettyPrinter(indent=4)



def detect(filename, cascade_file):
	if not os.path.isfile(cascade_file):
		raise RuntimeError("%s: not found" % cascade_file)

	cascade = cv2.CascadeClassifier(cascade_file)
	image = cv2.imread(filename, cv2.IMREAD_COLOR)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.equalizeHist(gray)
	
	faces_ = cascade.detectMultiScale(gray,
									 # detector options
									 scaleFactor = 1.1,
									 minNeighbors = 5,
									 minSize = (24, 24))
	#for (x, y, w, h) in faces:
	#	cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
	faces = []
	for (x, y, w, h) in faces_:
		faces.append({'x': x, 'y': y, 'w': w, 'h': h})
	return faces

	#cv2.imshow("AnimeFaceDetect", image)
	#cv2.waitKey(0)
	#cv2.imwrite("out.png", image)

def expand_rect(rect, crop_info):
	#pprint.pprint(rect)

	offset_w = rect['w'] * crop_info['crop_width'] * crop_info['crop_scale']
	offset_h = rect['h'] * crop_info['crop_top'] * crop_info['crop_scale']
	rect['x'] -= int(offset_w / 2)
	rect['w'] += int(offset_w)
	rect['y'] -= int(offset_h / 2)
	rect['h'] += int(rect['h'] * crop_info['crop_bottom'] * crop_info['crop_scale'])

def conv_rgb(image):
	if image.mode == 'RGB':
		pass
	elif image.mode == 'RGBA':
		#image.convert("RGB")
		BACKGROUND_COLOR = (255, 255, 255)
		src_image_size = (image.width, image.height)
		tmp_image = PIL.Image.new("RGB", src_image_size, BACKGROUND_COLOR)
		tmp_image.paste(image, mask=image.split()[3]) # 3 is the alpha channel
		image = tmp_image
	else:
		raise RuntimeError("image mode `%s`" % image.mode)
	return image

def crop_image(image, rect, crop_mode):
	rect_ = copy.deepcopy(rect)
	image_ = copy.deepcopy(image)

	if 'ignore' == crop_mode:
		if rect['x'] < 0 or rect['y'] < 0 or image.width < (rect['x'] + rect['w']) or image.height < (rect['y'] + rect['h']):
			return None
	elif 'wrap' == crop_mode:
		print("not implement\n")
		return None
	else: # fill
		# crop default background(black)
		pass

	return crop_image_(image_, rect_)

def crop_image_(image, rect):
	area = (rect['x'], rect['y'], rect['x'] + rect['w'], rect['y'] + rect['h'])
	cr_image = image.crop(area)
	#cr_image.show()
	return cr_image

def inflate_rect(rect, offset):
	offseta_list = [
		[ 1, 0, 0, 0],
		[ 0, 1, 0, 0],
		[ 1, 1, 0, 0],
		[ 0, 0, 1, 0],
		[ 1, 0, 1, 0],
		[ 0, 1, 1, 0],
		[ 1, 1, 1, 0],
		[ 0, 0, 0, 1],
		[ 1, 0, 0, 1],
		[ 0, 1, 0, 1],
		[ 1, 1, 0, 1],
		[ 0, 0, 1, 1],
		[ 1, 0, 1, 1],
		[ 0, 1, 1, 1],
		[ 1, 1, 1, 1],
	]

	offset_w_px = rect["w"] * offset
	offset_h_px = rect["h"] * offset

	inflate_rects = []
	for offseta in offseta_list:
		inflate_area_rect = copy.deepcopy(rect)
		inflate_area_rect["x"] -= offseta[0] * offset_w_px
		inflate_area_rect["y"] -= offseta[1] * offset_h_px
		inflate_area_rect["w"] += offseta[2] * offset_w_px
		inflate_area_rect["h"] += offseta[3] * offset_h_px
		inflate_rects.append(inflate_area_rect)

	return inflate_rects


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("input_dir")
	parser.add_argument('--cascade_file', type=str, default="./lbpcascade_animeface/lbpcascade_animeface.xml")
	parser.add_argument('--show', type=int, default=0, help="number of show detected face rect on image")
	parser.add_argument('--crop_mode', type=str, default="ignore",
			help="action when crop area out of image. ignore crop/fill background/wrap size")
	parser.add_argument('--crop_width', type=float, default=0.5, help="crop offset of ")
	parser.add_argument('--crop_top', type=float, default=1.0, help="crop offset of ")
	parser.add_argument('--crop_bottom', type=float, default=2.0, help="crop offset of ")
	parser.add_argument('--crop_minimize', action="store_true")
	parser.add_argument('--crop_minimize_v', type=float, default=-0.2)
	parser.add_argument('--crop_scale', type=float, default=1.0)
	parser.add_argument('--inflate_area', action="store_true")
	parser.add_argument('--inflate_area_offset', type=int, default=0.1)
	parser.add_argument('--inflate_rotate_num', type=int, default=0)
	parser.add_argument('--inflate_rotate_degree', type=int, default=10)
	parser.add_argument('--max_num', type=int, default=-1)
	parsed = parser.parse_args()

	crop_info = {
			"crop_width": parsed.crop_width,
			"crop_top": parsed.crop_top,
			"crop_bottom": parsed.crop_bottom,
			"crop_scale": parsed.crop_scale
			}

	parsed.output_dir = "{}_{}".format(os.path.normpath(parsed.input_dir), "inflcrop")
	#os.makedirs(parsed.output_dir, exist_ok=False)
	os.makedirs(parsed.output_dir, exist_ok=True)


	if os.path.isfile(parsed.input_dir):
		files = [parsed.input_dir]
	else:
		files = glob('{}/*.*'.format(parsed.input_dir))

	imagefile_count = 0
	all_saved_count = 0
	for i, image_filepath in enumerate(files):
		try:
			face_rects = detect(image_filepath, parsed.cascade_file)
		except Exception:
			logging.exception('Failed to image: `%s`', image_filepath)
			continue

		if 0 == len(face_rects):
			continue

		for face_rect in face_rects:
			expand_rect(face_rect, crop_info)

		if imagefile_count < parsed.show:
			image = cv2.imread(image_filepath, cv2.IMREAD_COLOR)
			for face in face_rects:
				cv2.rectangle(image, (face['x'], face['y']), (face['x'] + face['w'], face['y'] + face['h']), (0, 255, 0), 2)

			print("WARNING: windowをcloseするとハングする")
			cv2.imshow("AnimeFaceDetect", image)
			cv2.waitKey(0)
			#cv2.imwrite("out.png", image)

		inflate_area_face_rects = []
		if parsed.inflate_area:
			for face_rect in face_rects:
				inflate_area_face_rects.extend(inflate_rect(face_rect, parsed.inflate_area_offset))
			face_rects.extend(inflate_area_face_rects)

		image_filename, ext = os.path.splitext(os.path.basename(image_filepath))
		saved_count = 0
		for t, face_rect in enumerate(face_rects):
			info_str = ""
			is_minimize = False

			try:
				#print(image_filepath)
				#pprint.pprint(face_rect)

				image = PIL.Image.open(image_filepath)
				if not image:
					continue

				croped_image = crop_image(image, face_rect, parsed.crop_mode)
				if not croped_image:
					if parsed.crop_minimize:
						minimize_crop_info = {
								"crop_width": parsed.crop_minimize_v,
								"crop_top": parsed.crop_minimize_v,
								"crop_bottom": parsed.crop_minimize_v,
								"crop_scale": 1.0
								}
						minimize_face_rect = face_rect
						expand_rect(face_rect, minimize_crop_info)
						croped_image = crop_image(image, minimize_face_rect, parsed.crop_mode)
						info_str += "_min"
						is_minimize = True
				if not croped_image:
					continue

				output_imagefile = os.path.join(parsed.output_dir, "{}_f{:02}{}{}".format(image_filename, t, info_str, ".jpg"))
				croped_image.save(output_imagefile, quality=95)
				saved_count += 1
				all_saved_count += 1

				if not is_minimize:
					center = (face_rect['x'] + (face_rect['w'] / 2), face_rect['y'] + (face_rect['h'] / 2))
					foot = parsed.inflate_rotate_degree * parsed.inflate_rotate_num
					head = -1 * foot
					for rotate_degree in range(head, foot, parsed.inflate_rotate_degree):
						if 0 == rotate_degree:
							continue
						image_ = copy.deepcopy(image)
						rotate_image = image_.rotate(rotate_degree, center=center, expand=False, resample=PIL.Image.BICUBIC)
						rotate_image = crop_image(rotate_image, face_rect, "fill")

						output_imagefile = os.path.join(
								parsed.output_dir,
								"{}_f{:02}_rotate{}{}".format(image_filename, t, rotate_degree, ".jpg"))
						rotate_image.save(output_imagefile, quality=95)
						saved_count += 1
						all_saved_count += 1

			except Exception:
				logging.exception('Failed to image: `%s`', image_filepath)
				continue
		if 0 == saved_count:
			continue

		imagefile_count += 1
		if -1 != parsed.max_num and parsed.max_num <= imagefile_count:
			break
		if 0 == (imagefile_count % 100):
			print("{:4} {:4} {:4}/{:4}".format(i, imagefile_count, all_saved_count, len(files)))


	print("end:{:4} {:4}/{:4}".format(imagefile_count, all_saved_count, len(files)))


if __name__ == '__main__':
	main()

