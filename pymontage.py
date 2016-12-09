#!/usr/bin/python3

# pymontage - generate image montages
# Copyright (C) 2016 Benjamin Abendroth
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# TODO:
#   - make script usable for non-jpg files

import os
import sys
import math
import argparse
from string import Template
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

argp = argparse.ArgumentParser()
argp.add_argument('--columns', type=int, default=4, help="columns")
argp.add_argument('--margin', type=int, default=3, help="margin")
argp.add_argument('--height', type=int, default=400, help="thumb height")
argp.add_argument('--width', type=int, default=500, help="thumb width")
argp.add_argument('--font', default="/usr/share/fonts/TTF/DejaVuSans.ttf", help="font file")
argp.add_argument('--text-format', type=Template, default='[$index] $basename', help="text format")
argp.add_argument('--fit', action='store_true', help='reorder images')
argp.add_argument('dir', help='read images from dir')
argp.add_argument('out', help='outfile')

def generate_images(from_dir, height, width, font_file):
    font_place = (10, 200)

    image_files = list(
        filter(lambda f: f.endswith('.jpg'),
            map(lambda f: f.name,
                os.scandir(from_dir)
            )
        )
    )

    for i, f in enumerate(image_files):
        basename = f.replace('.jpg', '')
        full_path = os.path.join(from_dir, f)

        try:
            image = Image.open(full_path)
            image.thumbnail((height, width))

            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font_file, 16)

            filled_template = args.text_format.substitute(
                index=i, basename=basename
            )

            draw.text(font_place, filled_template, (255,255,255),font=font)
            print('[%d] %s' % (i, basename))

            yield image
        except Exception as e:
            print("(skipping %s) Error: %s" % (f, str(e)), file=sys.stderr)


def generate_montage(images, columns, margin):
    def pick_n(iterator, n):
        while True:
            try:
                picked = [next(iterator)]
            except StopIteration:
                return

            for i in range(n-1):
                try:
                    picked.append(next(iterator))
                except StopIteration:
                    break

            yield picked

    def generate_row(row_images):
        max_height = max(map(lambda i: i.size[1], row_images))
        width = sum(map(lambda i: i.size[0], row_images)) + columns*margin

        row = Image.new(mode='RGBA', size=(width, max_height), color=(0,0,0,0))

        offset_x = 0
        for image in row_images:
            row.paste(image, (offset_x, 0))
            offset_x += image.size[0] + margin

        return row

    rows = []
    for row_images in pick_n(iter(images), columns):
        rows.append( generate_row(row_images) )

    height = sum(map(lambda i: i.size[1], rows)) + len(rows)*margin
    max_width = max(map(lambda i: i.size[0], rows))

    montage = Image.new(mode='RGBA', size=(max_width, height), color=(0,0,0,0))

    offset_y = 0
    for row in rows:
        montage.paste(row, (0, offset_y))
        offset_y += row.size[1] + margin

    return montage


if __name__ == '__main__':
    args = argp.parse_args()

    thumbs = list(generate_images(
        args.dir,
        args.height,
        args.width,
        args.font
    ))

    if (args.fit):
        thumbs = sorted(thumbs, key=lambda i: i.size[0], reverse=True)
        thumbs = sorted(thumbs, key=lambda i: i.size[1])

    montage = generate_montage(
        thumbs,
        args.columns,
        args.margin
    )

    montage.save(args.out)
