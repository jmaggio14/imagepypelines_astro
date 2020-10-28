def test_fits():
    import imagepypelines as ip
    import matplotlib.pyplot as plt
    import numpy as np
    import time
    import cv2
    ip.require('astro')

    @ip.blockify(batch_type='each')
    def resize(img):
        return cv2.resize(img, (512,512), interpolation=cv2.INTER_CUBIC)




    moon_fname = ip.astro.moon()


    tasks = {
            'filenames':ip.Input(0),
            'unused':ip.Input(1),
            ('headers','images'): (ip.astro.LoadPrimaryHDU(),'filenames'),
            'small' : (resize,'images'),
            'normalized_0_255'    : (ip.image.NormDtype(np.uint8),'small'),
            }
    fits_loader = ip.Pipeline(tasks)


    # headers,data = fits_loader.process_and_grab([moon_fname],
    #                                                 fetch=['headers',' small'])
    processed = fits_loader.process([moon_fname],[None])
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
    import pdb; pdb.set_trace()
