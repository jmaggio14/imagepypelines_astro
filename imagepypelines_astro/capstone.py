import imagepypelines as ip
import matplotlib.pyplot as plt
import numpy as np
import time
import cv2
ip.require('image', 'astro')


moon_fname = ip.astro.moon()

tasks = {
        'filenames':ip.Input(0),
        ('headers','images'): (ip.astro.LoadPrimaryHDU(),'filenames'),
        'small' : (ip.image.Resize(scale_w=1/8,scale_h=1/8),'images'),
        'normalized_0_255' : (ip.image.NormDtype(np.uint8),'small'),
        'star_locs' : (ip.astro)
        }
fits_loader = ip.Pipeline(tasks)


# headers,data = fits_loader.process_and_grab([moon_fname],
#                                                 fetch=['headers',' small'])
processed = fits_loader.process([moon_fname])
data = processed['normalized_0_255']
headers = processed['headers']

assert isinstance(data[0], np.ndarray)
assert len(data) == len(headers) == 1

moon = processed['normalized_0_255'][0]

# display the image
fig = plt.figure()
ax = fig.add_subplot(111)
plt.imshow(moon, cmap='gray')
plt.ion()
plt.show()
plt.pause(0.1)
