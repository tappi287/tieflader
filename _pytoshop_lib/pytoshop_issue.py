""" Renaming issue when duplicating layers inside Photoshop example """
from pathlib import Path

import numpy as np
from pytoshop.enums import ColorChannel, ColorMode
from pytoshop.user import nested_layers

# Color channel types RGBA
CHANNEL_TYPES = [ColorChannel.red, ColorChannel.green, ColorChannel.blue, ColorChannel.transparency]

# Create Image Layer
layer = nested_layers.Image(name='.Test_Layer:', color_mode=ColorMode.rgb)
# Fill Layer with random image data
img_np = np.array(np.random.rand(256, 256, 3) * 255, dtype=np.uint8)

num_channels = range(0, img_np.shape[2])
for channel_type, channel_idx in zip(CHANNEL_TYPES, num_channels):
    layer.set_channel(channel_type, img_np[..., channel_idx])

layer_grp = nested_layers.Group(name='layer_group', layers=[layer])

# Create PsdFile from layer list
psd_obj = nested_layers.nested_layers_to_psd(layers=[layer_grp], color_mode=ColorMode.rgb)

psd_file = Path(__file__).parent / 'test_psd.psd'

with open(psd_file, 'wb') as file:
    psd_obj.write(file)
