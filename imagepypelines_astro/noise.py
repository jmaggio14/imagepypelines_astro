from .AstroBlock import AstroBlock
from .imports import import_opencv

cv2 = import_opencv()
import random
import numpy as np
import matplotlib.pyplot as plt
from imagepypelines import Block

__all__ = [
            'HorizontalMedian',
            'VerticalMedian',
            'Quick1DPlot',
            ]

class HorizontalMedian(AstroBlock):
    def __init__(self):
        super().__init__()
        self.enforce('image',np.ndarray,[(None,None)])

    def process(self,image):
        return np.median(image, axis=0)


class VerticalMedian(AstroBlock):
    def __init__(self):
        super().__init__()
        self.enforce('image',np.ndarray,[(None,None)])

    def process(self,image):
        return np.median(image, axis=1)


class Quick1DPlot(AstroBlock):
    def __init__(self):
        super().__init__()
        self.enforce('arr',np.ndarray,[(None,)])

    def process(self, arr):
        plt.figure()
        plt.plot(arr)
        plt.ion()
        plt.show()
