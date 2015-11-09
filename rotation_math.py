# rotation_math.py
# Math functions to transform Raven rotation data.
# Created on 11/3/2015
# Author: Daniel Chen (dchen8@illinois.edu)

from math import cos, sin, sqrt, acos, asin, atan2, pow as pow_f



def r_to_tsp(R_str):
    param = R_str.split(',')
    R00 = float(param[0])
    R02 = float(param[2])
    R10 = float(param[3])
    R20 = float(param[6])
    R21 = float(param[7])
    R22 = float(param[8])

    theta = -asin(R20)
    sai = atan2(R21/cos(theta), R22/cos(theta))
    phi = atan2(R10/cos(theta), R00/cos(theta))

    tsp_str = (theta,sai,phi)

    return tsp_str


def tsp_to_r(tsp):
    my_tsp = tsp.split(',')
    t = float(my_tsp[0])
    s = float(my_tsp[1])
    p = float(my_tsp[2])

    R00 = cos(t)*cos(p)
    R01 = sin(s)*sin(t)*cos(p)-cos(s)*sin(p)
    R02 = cos(s)*sin(t)*cos(p)+sin(s)*sin(p)

    R10 = cos(t)*sin(p)
    R11 = sin(s)*sin(t)*sin(p)+cos(s)*cos(p)
    R12 = cos(s)*sin(t)*sin(p)-sin(s)*cos(p)

    R20 = -sin(t)
    R21 = sin(s)*cos(t)
    R22 = cos(s)*cos(t)
    R = '%5f;%5f;%5f;%5f;%5f;%5f;%5f;%5f;%5f' % \
            (R00, R01, R02, R10, R11, R12, R20, R21, R22)

    return R


