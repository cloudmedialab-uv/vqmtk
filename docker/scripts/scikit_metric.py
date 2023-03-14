#!/usr/bin/env python
import sys
import shutil as sh
import argparse
import subprocess
import json
import numpy as np

# check for skvideo lib
try:
    import skvideo.io
    import skvideo.datasets
    import skvideo.measure
except ImportError:
    sys.stderr.write("Error: Missing package 'python2 skvideo'\n")
    sys.exit(1)

distortedPath = None
referencePath = None
metric = None


def readArgs():
    try:
        # Distorted video
        distortedPath = sys.argv[1]
        # Reference Video
        referencePath = sys.argv[2]
        # Metric to analyzed
        metric = sys.argv[3]

        return distortedPath, referencePath, metric
    except:
        sys.stderr.write(
            "Error: Error in passing arguments. \n Example: ./scikit-metric distorted.mp4 reference.mp4 msssim \n")
        sys.exit(1)

def qualityMetric(distorted,reference,metric):
    videodistorted = skvideo.io.vreader(distorted, as_grey=True)
    videoreference = skvideo.io.vreader(reference, as_grey=True)

    if metric == "msssim":    
        aux_msssim = []
        msssim = []
        i = 0
        for distorted, reference in zip(videodistorted, videoreference):
            aux_msssim.append(skvideo.measure.msssim(reference, distorted))
            i += 1
        for item in range(i):
            msssim.append(aux_msssim[item][0])
        print np.mean(msssim)
    
    elif metric == "mse":
        aux_mse = []
        mse = []
        i = 0
        for distorted, reference in zip(videodistorted, videoreference):
            aux_mse.append(skvideo.measure.mse(reference, distorted))
            i += 1
            
        for item in range(i):
            mse.append(aux_mse[item][0])

        print np.mean(mse)
    
    elif metric == "ssim":
      
        aux_ssim = []
        ssim = []
        i = 0
        for distorted, reference in zip(videodistorted, videoreference):
            aux_ssim.append(skvideo.measure.ssim(reference, distorted))
            i += 1

        for item in range(i):
            ssim.append(aux_ssim[item][0])

        print np.mean(ssim)

    elif metric == "psnr":
      
        aux_psnr = []
        psnr = []
        i = 0
        for distorted, reference in zip(videodistorted, videoreference):
            aux_psnr.append(skvideo.measure.psnr(reference, distorted,bitdepth=8))
            i += 1


        for item in range(i):
            psnr.append(aux_psnr[item][0])

        print np.mean(psnr)

    elif metric == "niqe":
      vid = skvideo.io.vread(distorted, outputdict={"-pix_fmt": "gray"})[:, :, :, 0]
      vid = skvideo.utils.vshape(vid)
      print np.mean(skvideo.measure.niqe(vid))

    elif metric == "brisque":
      vid = skvideo.io.vread(distorted, outputdict={"-pix_fmt": "gray"})[:, :, :, 0]
      vid = skvideo.utils.vshape(vid)
      print np.mean(skvideo.measure.brisque_features(vid))
    
    elif metric == "strred":
      reference = skvideo.io.vread(reference, outputdict={"-pix_fmt": "gray"})[:, :, :, 0]
      distorted = skvideo.io.vread(distorted, outputdict={"-pix_fmt": "gray"})[:, :, :, 0]
      result=[]
      
      result=skvideo.measure.strred(reference, distorted)
      print result[1],",",result[2]

      
    elif metric == "viideo":
        vid = skvideo.io.vread(distorted, outputdict={"-pix_fmt": "gray"})[:, :, :, 0]
        vid = skvideo.utils.vshape(vid)
        print skvideo.measure.viideo_score(vid, blocksize=(18, 18), blockoverlap=(8, 8), filterlength=7)
    
    else:
        print '-- No support for',metric,'metric'


if __name__ == "__main__":
    distorted, reference, metric = readArgs()
    if metric is None:
        print ('Error metric')
    else:
        qualityMetric(distorted,reference,metric)
