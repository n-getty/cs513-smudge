import numpy as np
from skimage import io, feature
from scipy import ndimage
import os
from skimage.feature import match_template
import sys
from time import time
from multiprocessing import Pool
from skimage.transform import rescale
import argparse


data = "sample_drive-1"


def load_cam_imgs(cam, skip, sc):
    base = 'cam_'
    path = os.path.join(data, base+cam)
    imgs = []
    c = 0
    for f in os.listdir(path):
        if c==0 or c%skip==0:
            img = rescale(io.imread(os.path.join(path,f), as_grey=True), 1.0/sc)
            imgs.append(img)
        c+=1
    return imgs


def work(a):
    i = a[0]
    d = a[1]
    col = a[2]
    im1 = a[3]
    im2 = a[4]

    cor = [0] * len(range(d, col - (d + 1)))
    for j in range(d, col - (d + 1)):
        cor[j] = match_template(im1[i - d: i + d + 1,
                                           j - d: j + d + 1],
                                           im2[i - d: i + d + 1,
                                           j - d: j + d + 1])
    return cor


def get_parser():
    parser = argparse.ArgumentParser(description='Detect smudge on camera given sequence of images')
    parser.add_argument("--cam", default='0', type=str, help="which camera")
    parser.add_argument("--d", default=11, type=int, help="correlation window size")
    parser.add_argument("--skip", default=100, type=int, help="frame interval use")
    parser.add_argument("--scale", default=4.0, type=float, help="how much to scale image")
    parser.add_argument("--t", default=0.2, type=float, help="correlation threshhold")
    parser.add_argument("--num", default=10, type=int, help="number of images to correlate")

    return parser


def main():
    #Parse arguments
    parser = get_parser()
    args = parser.parse_args()
    d = args.d
    cam = args.cam
    skip = args.skip
    sc = args.scale
    t = args.t
    n = args.num

    imgs = load_cam_imgs(cam, skip, sc)
    print "Loaded cam images"

    '''p = 8
    pool = Pool(p)
    iwork = range(d, row - (d + 1))
    allwork = zip(iwork, [d] * len(iwork), [col] * len(iwork), im1 * len(iwork), im2 * len(iwork))
    for i, r in enumerate(pool.imap_unordered(work, allwork)):
        sys.stderr.write('\rdone {0:%}'.format(float(i+1) / len(iwork)))
        correlation[i] = r'''

    corrs = []
    #Iterate over subsequent images to compute correlations
    for x in range(len(imgs[:2])-1):
        im1 = imgs[x]
        im2 = imgs[x+1]
        #correlation = np.zeros_like(im1)
        row, col = im1.shape
        '''for i in range(d, row - (d + 1)):
            sys.stderr.write('\rdone {0:%}'.format(float(i + 1) / len(im1)))
            for j in range(d, col - (d + 1)):
                correlation[i, j] = match_template(im1[i - d: i + d + 1,
                                                            j - d: j + d + 1],
                                                            im2[i - d: i + d + 1,
                                                            j - d: j + d + 1])'''

        r = range(d, col - (d + 1))
        #Computer correlation matrix with given pixel window
        correlation = np.array([[match_template(im1[i - d: i + d + 1, j - d: j + d + 1], im2[i - d: i + d + 1, j - d: j + d + 1]) for j in r] for i in r])
        
        print "Computed correlation"
        #Zero below threshold
        correlation[correlation < t] == 0
        corrs.append(correlation)
    
    #Accumulate correlation maps
    correlation = corrs[0]
    for x in corrs[1:]:
        correlation = np.add(correlation, x)

    correlation = correlation / float(len(corrs))
    
    # Zero below threshold
    correlation[correlation < t] == 0
    
    # Show result
    io.imshow(correlation, cmap='gray')
    io.show()


if __name__ == '__main__':
    main()