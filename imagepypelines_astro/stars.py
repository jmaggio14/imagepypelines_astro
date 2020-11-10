from .AstroBlock import AstroBlock

import random
import numpy as np
import matplotlib.pyplot as plt
from photutils import DAOStarFinder, CircularAperture, aperture_photometry
from imagepypelines import Block
from astropy.stats import sigma_clipped_stats
from astropy.table import Table

__all__ = ['DAOStarFinder','Sample','ViewSourceOutlines']

################################################################################
class DAOStarFinder(AstroBlock):
    """
    """
    def __init__(self, fwhm=5.0, threshold=20, sigma_clip=3.0, outer_mask_frac=.1):
        self.fwhm = fwhm
        self.threshold = threshold
        self.sigma_clip = sigma_clip
        self.outer_mask_frac = outer_mask_frac

        self.daofind = DAOStarFinder(self.fwhm, self.threshold)

        super().__init__()
        self.enforce('image', np.ndarray, [(None,None)])

    def _make_mask(self, image):
        height,width = image.shape[:2]

        top_idx = int(height * self.outer_mask_frac)
        bottom_idx = int(height - top_idx)
        left_idx = int(width * self.outer_mask_frac)
        right_idx = int(width - left_idx)

        mask = np.ones( (height,width), dtype=bool )
        mask[top_idx:bottom_idx, left_idx:right_idx] = 0
        return mask


    def process(self, image):
        mask = self._make_mask(image)
        mean, median, std = sigma_clipped_stats(image, self.sigma_clip)

        sources = self.daofind(image - median, mask=mask)
        return sources


################################################################################
class ViewSourceOutlines(AstroBlock):
    def __init__(self, radius, color='b', ax=None, label="Sources", title=None):
        self.radius = radius
        self.color = color
        self.label = label
        self.title = title

        if ax is None:
            _, self.ax = plt.subplots(111)
            if not (title is None):
                self.ax.set_title(label)
        else:
            self.ax = ax

        super().__init__(void=True)
        self.enforce('image', np.ndarray, [(None,None)])
        self.enforce('sources', Table)

    def process(self, image, sources):
        positions = np.transpose((sources['xcentroid'], sources['ycentroid']))
        apertures = CircularAperture(positions, r=self.radius)
        apertures.plot(self.ax, color=self.color, label=self.label)

        return None

################################################################################
class Sample(Block):
    def __init__(self, n_samples=1):
        super().__init__(batch_type='all')
        self.n_samples = n_samples
        self.enforce('image',)

    def process(self,images):
        samples = random.samples(images, self.n_samples)
        return samples
