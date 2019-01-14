"""
The MIT License (MIT)

Copyright (c) 2014-2015 vingtcinq.io
Modified by Stefan Tapper 14/01/2018
- use numpy math
- return RGBA images from resize_contain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import numpy as np
from PIL import Image


class Resize:
    @staticmethod
    def resize_crop(image, size):
        """
        Crop the image with a centered rectangle of the specified size
        image:      a Pillow image instance
        size:       a list of two integers [width, height]
        """
        img_format = image.format
        image = image.copy()
        old_size = image.size
        left = (old_size[0] - size[0]) / 2
        top = (old_size[1] - size[1]) / 2
        right = old_size[0] - left
        bottom = old_size[1] - top
        rect = [int(np.math.ceil(x)) for x in (left, top, right, bottom)]
        left, top, right, bottom = rect
        crop = image.crop((left, top, right, bottom))
        crop.format = img_format
        return crop

    @classmethod
    def resize_cover(cls, image, size, resample=Image.LANCZOS):
        """
        Resize image according to size.
        image:      a Pillow image instance
        size:       a list of two integers [width, height]
        """
        img_format = image.format
        img = image.copy()
        img_size = img.size
        ratio = max(size[0] / img_size[0], size[1] / img_size[1])
        new_size = [
            int(np.math.ceil(img_size[0] * ratio)),
            int(np.math.ceil(img_size[1] * ratio))
            ]
        img = img.resize((new_size[0], new_size[1]), resample)
        img = cls.resize_crop(img, size)
        img.format = img_format
        return img

    @staticmethod
    def resize_thumbnail(image, size, resample=Image.LANCZOS):
        """
        Resize image according to size.
        image:      a Pillow image instance
        size:       a list of two integers [width, height]
        """

        img_format = image.format
        img = image.copy()
        img.thumbnail((size[0], size[1]), resample)
        img.format = img_format
        return img

    @staticmethod
    def resize_contain(image, size, resample=Image.LANCZOS, bg_color=(255, 255, 255, 0)):
        """
        Resize image according to size.
        image:      a Pillow image instance
        size:       a list of two integers [width, height]
        """
        image.thumbnail((size[0], size[1]), resample)
        background = Image.new('RGBA', (size[0], size[1]), bg_color)
        img_position = (
            int(np.math.ceil((size[0] - image.size[0]) / 2)),
            int(np.math.ceil((size[1] - image.size[1]) / 2))
        )
        background.paste(image, img_position)
        return background

    @staticmethod
    def resize_width(image, size, resample=Image.LANCZOS):
        """
        Resize image according to size.
        image:      a Pillow image instance
        size:       an integer or a list or tuple of two integers [width, height]
        """
        width = size[0]
        img_format = image.format
        img = image.copy()
        img_size = img.size
        # If the original image has already the good width, return it
        # fix issue #16
        if img_size[0] == width:
            return image
        new_height = int(np.math.ceil((width / img_size[0]) * img_size[1]))
        img.thumbnail((width, new_height), resample)
        img.format = img_format
        return img

    @staticmethod
    def resize_height(image, size, resample=Image.LANCZOS):
        """
        Resize image according to size.
        image:      a Pillow image instance
        size:       an integer or a list or tuple of two integers [width, height]
        """
        height = size[1]
        img_format = image.format
        img = image.copy()
        img_size = img.size
        # If the origial image has already the good height, return it
        # fix issue #16
        if img_size[1] == height:
            return image
        new_width = int(np.math.ceil((height / img_size[1]) * img_size[0]))
        img.thumbnail((new_width, height), resample)
        img.format = img_format
        return img
