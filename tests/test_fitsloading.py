




def test_fits():
    import imagepypelines as ip
    import matplotlib.pyplot as plt
    import numpy as np
    import time
    import cv2
    ip.require('astro')

    @ip.blockify(batch_type='each')
    def resize(img):
        return cv2.resize(img, (512,512))




    moon_fname = ip.astro.moon()


    tasks = {
            'filenames':ip.Input(0),
            ('headers','images'): (ip.astro.LoadPrimaryHDU(),'filenames'),
            'small' : (resize,'images'),
            }
    fits_loader = ip.Pipeline(tasks)


    headers,data = fits_loader.process_and_grab([moon_fname],
                                                    fetch=['headers','small'])


    assert isinstance(data[0], np.ndarray)
    assert len(data) == len(headers) == 1

    # display the image
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.imshow(data[0])
    plt.ion()
    plt.show()
    import pdb; pdb.set_trace()
