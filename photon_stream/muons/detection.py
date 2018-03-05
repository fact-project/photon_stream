import numpy as np
from skimage.measure import ransac
from skimage.measure import CircleModel
from scipy.ndimage import convolve

from .tools import circle_overlapp
from .tools import tight_circle_on_off_region
from .tools import xy2polar

deg2rad = np.deg2rad(1)


def detection(
    event,
    clusters,
    initial_circle_model_min_samples=3,
    initial_circle_model_residual_threshold=0.25,
    initial_circle_model_max_trails=15,
    initial_circle_model_min_photon_ratio=0.6,
    density_circle_model_residual_threshold=0.20,
    density_circle_model_min_on_off_ratio=3.5,
    density_circle_model_max_ratio_photon_inside_ring=0.25,
    min_circumference_of_muon_ring_in_field_of_view=1.5,
    max_arrival_time_stddev=5e-9,
    min_overlap_of_muon_ring_with_field_of_view=0.2,
    min_muon_ring_radius=0.45,
    max_muon_ring_radius=1.6):
    """
    Detects muon events.
    A dictionary of muon relevant features is returned.

    Parameter
    ---------

    event       FACT event.

    clusters    Photons-stream cluster of the event.
    """
    initial_circle_model_residual_threshold *= deg2rad
    density_circle_model_residual_threshold *= deg2rad
    min_muon_ring_radius *= deg2rad
    max_muon_ring_radius *= deg2rad
    min_circumference_of_muon_ring_in_field_of_view *= deg2rad

    ret = {}
    ret['is_muon'] = False

    field_of_view_radius = event.photon_stream.geometry.fov_radius

    full_cluster_mask = clusters.labels >= 0
    number_of_photons = full_cluster_mask.sum()

    ret['number_of_photons'] = number_of_photons
    if number_of_photons < initial_circle_model_min_samples:
        return ret

    flat_photon_stream = clusters.point_cloud
    full_clusters_fps = flat_photon_stream[full_cluster_mask]

    circle_model, inliers = ransac(
        data=full_clusters_fps[:, 0:2], # only cx and cy not the time
        model_class=CircleModel,
        min_samples=initial_circle_model_min_samples,
        residual_threshold=initial_circle_model_residual_threshold,
        max_trials=initial_circle_model_max_trails)

    cx = circle_model.params[0]
    cy = circle_model.params[1]
    r = circle_model.params[2]

    ret['muon_ring_cx'] = cx
    ret['muon_ring_cy'] = cy
    ret['muon_ring_r'] = r

    muon_ring_overlapp_with_field_of_view = circle_overlapp(
        cx1=0.0,
        cy1=0.0,
        r1=field_of_view_radius,
        cx2=cx,
        cy2=cy,
        r2=r)

    if r < min_muon_ring_radius or r > max_muon_ring_radius:
        return ret

    ret['muon_ring_overlapp_with_field_of_view'] = (
        muon_ring_overlapp_with_field_of_view
    )
    if (
        muon_ring_overlapp_with_field_of_view <
        min_overlap_of_muon_ring_with_field_of_view
    ):
        return ret

    arrival_time_stddev = full_clusters_fps[:, 2].std()
    ret['arrival_time_stddev'] = arrival_time_stddev
    if arrival_time_stddev > max_arrival_time_stddev:
        return ret

    ret['mean_arrival_time_muon_cluster'] = full_clusters_fps[:, 2].mean()

    number_of_ring_photons = inliers.sum()
    initial_circle_model_photon_ratio = (
        number_of_ring_photons/number_of_photons
    )
    ret['initial_circle_model_photon_ratio'] = (
        initial_circle_model_photon_ratio
    )
    if (
        initial_circle_model_photon_ratio <
        initial_circle_model_min_photon_ratio
    ):
        return ret

    visible_ring_circumfance = r*2*np.pi*muon_ring_overlapp_with_field_of_view
    ret['visible_muon_ring_circumfance'] = visible_ring_circumfance
    if (
        visible_ring_circumfance <
        min_circumference_of_muon_ring_in_field_of_view
    ):
        return ret

    # circle model ON/OFF ratio
    # -------------------------

    onoff = tight_circle_on_off_region(
        cx=cx,
        cy=cy,
        r=r,
        residual_threshold=density_circle_model_residual_threshold,
        xy=full_clusters_fps[:, 0:2])

    on_density = onoff['on'].sum()/onoff['area_on']
    inner_off_density = onoff['inner_off'].sum()/onoff['area_inner_off']
    outer_off_density = onoff['outer_off'].sum()/onoff['area_outer_off']

    off_density = (outer_off_density + inner_off_density)/2
    on_off_ratio = on_density/off_density

    ret['density_circle_model_on_off_ratio'] = on_off_ratio
    if on_off_ratio < density_circle_model_min_on_off_ratio:
        return ret

    number_of_photons_inside_ring_off = onoff['inside_off'].sum()
    ratio_inside_circle = number_of_photons_inside_ring_off/number_of_photons
    ret['density_circle_model_inner_ratio'] = ratio_inside_circle
    if ratio_inside_circle > density_circle_model_max_ratio_photon_inside_ring:
        return ret

    # ring population
    #----------------
    xy_relative_to_ring_center = full_clusters_fps
    xy_relative_to_ring_center[:, 0] -= cx
    xy_relative_to_ring_center[:, 1] -= cy

    rphi = xy2polar(xy=xy_relative_to_ring_center[:, 0:2])

    number_bins = 3*int(np.ceil(np.sqrt(number_of_photons)))
    phi_bin_edgeds = np.linspace(-np.pi, np.pi, number_bins)
    ring_population_hist, phi_bin_edgeds = np.histogram(
        rphi[:, 1],
        bins=phi_bin_edgeds)

    phi_bin_centers = phi_bin_edgeds[: -1]
    bin_pos_x = np.cos(phi_bin_centers)*r + cx
    bin_pos_y = np.sin(phi_bin_centers)*r + cy
    bins_inside_fov = (
        np.sqrt(bin_pos_x**2 + bin_pos_y**2) <
        field_of_view_radius
    )
    mean_photons = ring_population_hist[bins_inside_fov].mean()

    # continues ring population
    # -------------------------
    min_ring_circumfance = 2.5*deg2rad
    ring_circumfance = 2*r*np.pi
    min_ring_fraction = min_ring_circumfance/ring_circumfance

    if min_ring_fraction < 0.33:
        min_ring_fraction = 0.33

    number_of_fraction_bins = int(np.round(min_ring_fraction*number_bins))

    is_populated_evenly = False
    is_populated_at_all = False
    most_even_population_std = 1e99
    for i in range(ring_population_hist.shape[0]):
        section = np.take(
            ring_population_hist,
            range(i, i+number_of_fraction_bins),
            mode='wrap')

        if (section > 0).sum() >= 0.5*number_of_fraction_bins:
            is_populated_at_all = True
            rel_std = section.std()/section.mean()
            if rel_std < most_even_population_std:
                most_even_population_std = rel_std

    if is_populated_at_all and most_even_population_std < 0.8:
        is_populated_evenly = True

    if is_populated_evenly:
        ret['is_muon'] = True

    return ret
