import numpy as np


def circle_overlapp(cx1, cy1, r1, cx2, cy2, r2):
    if r1 >= r2:
        return circle_overlapp_r1_gt_r2(cx1, cy1, r1, cx2, cy2, r2)
    else:
        return circle_overlapp_r1_gt_r2(cx2, cy2, r2, cx1, cy1, r1)


def circle_overlapp_r1_gt_r2(cx1, cy1, r1, cx2, cy2, r2):
    """
    Returns the fraction [0,1] of the circumference of circle 2 with circle 1.

    Parameter
    ---------
    cx1         x position of center of circle 1.

    cy1         y position of center of circle 1.

    r1          radius of circle 1.

    cx2         x position of center of circle 2.

    cy2         y position of center of circle 2.

    r2          radius of circle 2.
    """
    d = np.sqrt((cx2 - cx1)**2 + (cy2 - cy1)**2)

    r1_sq = r1**2
    r2_sq = r2**2
    d_sq = d**2

    if d > r1 + r2:
        return 0.0
    elif d <= np.abs(r1 - r2):
        return 1.0
    else:
        # http://mathworld.wolfram.com/Circle-CircleIntersection.html
        a = 1/d * np.sqrt(4*d_sq*r1_sq - (d_sq - r2_sq + r1_sq)**2)

        x = np.sqrt(r1**2 - r2**2)

        if d >= x:
            overlapp_angle = 2*np.arcsin((a/2)/r2)
        else:
            overlapp_angle = 2*np.pi - 2*np.arcsin((a/2)/r2)

        overlapp_ratio = overlapp_angle/(2*np.pi)
        return overlapp_ratio


def tight_circle_on_off_region(cx, cy, r, residual_threshold, xy):
    """
    Returns masks for the 2D points in 'xy' whether they belong to the
    circle model or not.
    """
    x = xy[:, 0] - cx
    y = xy[:, 1] - cy
    R = np.sqrt(x*x + y*y)

    r_inner_off_start = r - 1.5*residual_threshold
    r_on_start = r - 0.5*residual_threshold
    r_on_end = r + 0.5*residual_threshold
    r_outer_off_end = r + 1.5*residual_threshold

    A_inner_off = np.pi*(r_on_start**2 - r_inner_off_start**2)
    A_on = np.pi*(r_on_end**2 - r_on_start**2)
    A_outer_off = np.pi*(r_outer_off_end**2 - r_on_end**2)

    mask_outer_off = (R > r_on_end)*(R <= r_outer_off_end)
    mask_inner_off = (R > r_inner_off_start)*(R <= r_on_start)
    mask_on = (R > r_on_start)*(R <= r_on_end)

    inside_off = (R < r_on_start)

    return {
        'area_inner_off': A_inner_off,
        'area_outer_off': A_outer_off,
        'area_on': A_on,
        'on': mask_on,
        'outer_off': mask_outer_off,
        'inner_off': mask_inner_off,
        'inside_off': inside_off
    }


def xy2polar(xy):
    """
    Returns the radius and azimuth for 2D points 'xy' in polar coordinates.
    """
    rphi = np.zeros(shape=xy.shape)
    rphi[:, 0] = np.sqrt(xy[:, 0]**2, xy[:, 1]**2)
    rphi[:, 1] = np.arctan2(xy[:, 1], xy[:, 0])
    return rphi
