from pathlib import Path
from typing import Union, Tuple, List

import pytoshop
import numpy as np
from PIL import Image
from imageio import imread
from pytoshop.enums import ColorChannel, ColorMode
from pytoshop.user import nested_layers

from modules.image_resize import Resize
from modules.log import init_logging

LOGGER = init_logging(__name__)


class PyShop:
    # Enums describing the type/name of the color channel
    # in NumPy Pillow array order
    color_channels = [
        ColorChannel.red,
        ColorChannel.green,
        ColorChannel.blue,
        ColorChannel.transparency
        ]

    # Global color mode
    color_mode = ColorMode.rgb

    # --- Default Image size ---
    default_img_size = (1920, 1080)

    # --- Supported image file suffixes/image types ---
    supported_img = ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff']

    # --- Resampling method ---
    default_resample_filter = Image.BICUBIC

    def __init__(self,
                 target_size: Tuple[int, int]=(1920, 1080), resampling_filter=None, resize_mode=None
                 ):
        # --- List holding Psd layers ---
        self.layer_ls: List[nested_layers.Layer] = list()

        self.group_id = 0

        # --- PSD Image Size ---
        self.size: Tuple[int, int] = self.default_img_size
        if target_size:
            self.size = target_size

        # --- Pillow Resampling Filter ---
        self.resample_filter = self.default_resample_filter
        if resampling_filter:
            self.resample_filter = resampling_filter

    @staticmethod
    def _add_layers_from_existing_psd(psd_file_obj) -> List[nested_layers.Layer]:
        """ Create List of Layers from opened PsdFile file object """
        existing_psd = pytoshop.read(psd_file_obj)
        existing_layers = nested_layers.psd_to_nested_layers(existing_psd)

        return existing_layers

    def _resize_image(self, pil_img: Image):
        """ Resize Layer content image to psd instance size if necessary """
        if pil_img.size != self.size:
            return Resize.resize_contain(pil_img, self.size, resample=self.resample_filter,
                                         bg_color=(0, 0, 0, 0)
                                         )

        return pil_img

    @staticmethod
    def _open_with_imageio(file: Path) -> Union[None, Image.Image]:
        """ Open image files failed in Pillow with imageio """
        try:
            LOGGER.info('Loading image file with imageio.')
            img = imread(file.as_posix())
        except Exception as e:
            LOGGER.error(e)
            return None

        # Convert none 8bit depth images
        if img.dtype == np.float32:
            # Convert 32bit float images to 8bit integer
            img = np.uint8(img * 255)
        elif img.dtype == np.uint16:
            # Convert 16bit integer[0 - 65535] to 8bit integer [0-255]
            img = np.uint8(img / 256)

        return Image.fromarray(img)

    def _open_image(self, fb, file: Path) -> Union[None, Image.Image]:
        """ Try to load an image file to pil.Image object using PIL or imageio """
        img = None

        try:
            # Try to load image using Pillow
            img = Image.open(fb)
        except Exception as e:
            LOGGER.error(e)

            # Try to use imageio on 16/32bit tiff images
            # Open with libtiff
            img = self._open_with_imageio(file)

        return img

    def _load_image_to_numpy_channels(self, image_file: Path):
        """ Open Image file with Pillow and create list containing each channel as NumPy array """
        with open(image_file.as_posix(), 'rb') as f:
            img = self._open_image(f, image_file)

            # Resize image with Pillow if necessary
            img = self._resize_image(img)

            # Convert to RGBA
            if img.mode == 'P':
                img = img.convert('RGBA')

            # Convert Image to NumPy array
            img_np = np.array(img)

            # Get number of channels
            img_channel_num = 0
            if len(img_np.shape) > 2:
                img_channel_num = img_np.shape[2]

            # Create list of image channels
            # len(3) - R G B
            # len(4) - R G B A
            img_channels = list()
            for c in range(0, img_channel_num):
                img_channels.append(img_np[..., c])

        del img, f

        return img_channels

    def _layer_from_image(self, image_file: Path) -> nested_layers.Layer:
        """ Open an Image as NumPy Array and create a new pytoshop Layer object """
        img_channels = self._load_image_to_numpy_channels(image_file)

        # Create an empty layer
        layer = nested_layers.Image(
            name=image_file.stem,
            color_mode=self.color_mode,
            )

        # Transfer the image data to the Psd layer
        # color_channel describes the channel type R/G/B/A
        # img_channel contains the actual image data as NumPy array
        for color_channel, img_channel in zip(self.color_channels, img_channels):
            layer.set_channel(color_channel, img_channel)

        return layer

    def add_image_as_layer(self, image_file: Union[Path, str]):
        """ Append an image to the PSD file """
        image_file = Path(image_file)

        # Test if image exists and is supported
        if not image_file.exists() or image_file.suffix.casefold() not in self.supported_img:
            LOGGER.info('Skipping non-existent or unsupported file: %s', image_file.name)
            return False

        new_layer = self._layer_from_image(image_file)
        self.layer_ls.insert(0, new_layer)

        return True

    def create_psd_from_existing(self, existing_psd_file: Union[Path, str], psd_file: Union[Path, str]) -> str:
        """ Create PSD keeping all layers of an existing PSD file.

        :param existing_psd_file: Path to the existing Psd file
        :param psd_file: Path to the Psd file to create
        :return: Path of the created file or error message.
        """
        existing_psd_file = Path(existing_psd_file)
        psd_file = Path(psd_file)

        if not existing_psd_file.exists() or existing_psd_file.suffix.casefold() != '.psd':
            return 'Existing PSD file does not exists.'

        existing_psd = open(existing_psd_file, 'rb')
        self.layer_ls += self._add_layers_from_existing_psd(existing_psd)

        out_psd_file = self.create_psd(psd_file)
        existing_psd.close()

        return out_psd_file

    def create_psd(self, psd_file: Union[Path, str]) -> str:
        """ Create PSD file at provided path containing all layers previously added to this instance.

        :param psd_file: Path to the Psd file to create
        :return: Path of the created file or error message.
        """
        if not self.layer_ls:
            return 'Can not create PSD file without layer content.'

        psd_file = Path(psd_file)

        nested_layers.pprint_layers(self.layer_ls)

        psd_stacked = nested_layers.nested_layers_to_psd(
            layers=self.layer_ls,
            color_mode=ColorMode.rgb,
            version=pytoshop.enums.Version.psd,
            compression=pytoshop.enums.Compression.rle,
            size=self.size
            )

        try:
            # TODO: Alternative location when write only location
            with open(psd_file, 'wb') as file:
                psd_stacked.write(file)
        except Exception as e:
            LOGGER.error('Error writing Photoshop file: %s', e)

        return psd_file.as_posix()
