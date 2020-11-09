import random
import numpy as np
from PIL import Image,ImageDraw

from .AstroBlock import AstroBlock
from photoutils import DAOStarFinder
from astropy.stats import sigma_clipped_stats
from imagepypelines import Block

class DaoFinder(AstroBlock):
    """
    """
    def __init__(self, fwhm=5.0, threshold=20, sigma_clip=3.0, outer_mask_frac=.1):
        super().__init__()
        self.sigma_clip = sigma_clip
        self.fwhm = fwhm
        self.threshold = threshold
        self.outer_mask_frac = outer_mask_frac
        self.daofind = DAOStarFinder(fwhm=self.fwhm, threshold=self.threshold)

    def _make_mask(self, image):
        height,width = image.shape[:2]

        top_idx = height * self.outer_mask_frac
        bottom_idx = height - top_idx
        left_idx = width * self.outer_mask_frac
        right_idx = width - left_idx

        mask = np.ones( (height,width), dtype=bool )
        mask[top_idx:bottom_idx, left_idx:right_idx] = 0
        return mask


    def process(self, image):
        mask = self._make_mask(image)
        mean, median, std = sigma_clipped_stats(image, self.sigma_clip)

        sources = self.daofind(image - median, mask=mask)
        return sources


class OutlineSources(AstroBlock):
    __COLORS = {'red':(255,0,0)}
    def __init__(self):
        self.shape = 'circle'
        self.color = __COLORS['red']


    def process(self, image, source):
        im = Image.fromarray(image).convert('RGB')
        draw = ImageDraw.Draw(im)
        for 


class Sample(Block):
    def __init__(self, fraction=.1):
        super().__init__(batch_type='all')
        self.fraction = fraction

    def process(self,images):
        n_samples = int(len(images) * self.fraction)
        samples = random.samples(images, n_samples)
        return samples
