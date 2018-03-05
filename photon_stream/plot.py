import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Circle
import os
import tempfile
import subprocess
from .geometry import GEOMETRY


def event(event, mask=None):
    """
    Creates a new figure with 3D axes to show the photon-stream of the
    event.
    """
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    add_event_2_ax(event=event, ax=ax, mask=mask)


def add_event_2_ax(event, ax, mask=None, color='b'):
    xyt = event.photon_stream.point_cloud
    if mask is not None:
        xyt = xyt[mask]
    ax.set_title(event._info())
    fov_radius = event.photon_stream.geometry.fov_radius
    add_point_cloud_2_ax(
        point_cloud=xyt,
        fov_radius=fov_radius,
        ax=ax,
        color=color
    )


def point_cloud(point_cloud):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    add_point_cloud_2_ax(point_cloud=point_cloud, ax=ax)


def add_point_cloud_2_ax(
    point_cloud,
    ax,
    fov_radius=GEOMETRY.fov_radius,
    color='b'
):
    fov_radius_deg = np.rad2deg(fov_radius)
    pcl = point_cloud.copy()
    pcl[:, 0] = np.rad2deg(pcl[:, 0]) # to deg
    pcl[:, 1] = np.rad2deg(pcl[:, 1]) # to deg
    pcl[:, 2] *= 1e9 # to nano seconds

    min_time = pcl[:, 2].min()
    max_time = pcl[:, 2].max()

    add_ring_2_ax(x=0.0, y=0.0, z=min_time, r=fov_radius_deg, ax=ax)
    ax.set_xlim(-fov_radius_deg, fov_radius_deg)
    ax.set_ylim(-fov_radius_deg, fov_radius_deg)
    ax.set_zlim(min_time, max_time)
    ax.set_xlabel('x/deg')
    ax.set_ylabel('y/deg')
    ax.set_zlabel('t/ns')
    ax.scatter(
        pcl[:, 0],
        pcl[:, 1],
        pcl[:, 2],
        lw=0,
        alpha=0.075,
        s=55.,
        c=color
    )


def add_ring_2_ax(x, y, z, r, ax, color='k', line_width=1.0):
    p = Circle((x, y), r, edgecolor=color, facecolor='none', lw=line_width)
    ax.add_patch(p)
    art3d.pathpatch_2d_to_3d(p, z=z, zdir="z")


def save_image_sequence(
    event,
    path,
    steps=27,
    start_number=0,
    start_azimuth=0.0,
    end_azimuth=360.0,
    mask=None,
    image_format='png'):

    fig = plt.figure(figsize=(12, 6.75))
    ax = fig.gca(projection='3d')

    add_event_2_ax(event, ax, mask=mask)
    azimuths = np.linspace(start_azimuth, end_azimuth, steps, endpoint=False)
    step = start_number
    for azimuth in azimuths:
        ax.view_init(elev=25., azim=azimuth)
        plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        plt.savefig(
            os.path.join(
                path,
                '3D_'+str(step).zfill(6) + '.' + image_format),
            dpi=180)
        step += 1

    plt.close()


def save_video(
    event,
    outpath,
    mask=None,
    steps=12,
    fps=25,
    threads='auto',
    work_dir=None):
    """
    Saves a H264 1080p video of a 3D rendering of a photon-stream event to the
    outputpath. In the 3D rendering the event is rotated 360 degrees around the
    optical axis of the telescope.

    Parameters
    ----------

    event       The photon-stream event.

    outpath     The output path of the video file.

    mask        A photon-stream mask. If the mask is not None, the rendering
                will alternatingly in 10 degree intervalls show the full
                photon-stream and only the masked part of the photon-stream.
                (Default is None)

    steps       The number of images used within an 10 degree intervall.
                (Default is 12, which results in 12*36=432 images)

    threads     Tells the avconv video converter to use multiple threads or
                not. (Default is avconv's 'auto' option)

    work_dir    The intermediate working directory to host the raw images of
                the video sequence. If work_dir is None, a temporary
                directory is created automatically, otherwise the work_dir
                remains after the video processing to access the raw images.
                (Default is None)
    """

    if work_dir is None:
        work_dir_instance = tempfile.TemporaryDirectory(
            prefix='photon_stream_video')
        work_dir = work_dir_instance.name
        work_dir_has_to_be_removed_again = True
    else:
        os.mkdir(work_dir)
        work_dir_has_to_be_removed_again = False

    azimuths = np.linspace(0, 360, 10, endpoint=False)
    for i, az in enumerate(azimuths):

        save_image_sequence(
            event=event,
            path=work_dir,
            steps=steps,
            start_azimuth=az,
            end_azimuth=az+18,
            start_number=(i*steps*2),
            mask=mask)

        save_image_sequence(
            event=event,
            path=work_dir,
            steps=steps,
            start_azimuth=az+18,
            end_azimuth=az+36,
            start_number=(i*steps*2)+steps)

    if threads != 'auto':
        threads = str(threads)

    avconv_command = [
        'avconv',
        '-y',  # force overwriting of existing output file
        '-framerate', str(int(fps)),  # Frames per second
        '-f', 'image2',
        '-i', os.path.join(work_dir, '3D_%06d.png'),
        '-c:v', 'h264',
        '-s', '1920x1080',  # sample images to FullHD 1080p
        '-crf', '23',  # high quality 0 (best) to 53 (worst)
        '-crf_max', '25',  # worst quality allowed
        '-threads', threads,
        os.path.splitext(outpath)[0] + '.mp4'
    ]
    subprocess.call(avconv_command)

    if work_dir_has_to_be_removed_again:
        work_dir_instance.cleanup()
