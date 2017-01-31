import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Circle
import os
import tempfile
import subprocess

def add_event_2_ax(event, ax, mask=None, color='b'):
    xyt = event.photon_stream.flatten()

    xyt[:,2] *= 1e9
    min_time = xyt[:,2].min()
    max_time = xyt[:,2].max()

    if mask is not None:
        xyt = xyt[mask]

    ax.set_title('Night '+str(event.run.night)+', Run '+str(event.run.id)+', Event '+str(event.id))
    fovR = event.photon_stream.geometry['fov_radius']
    p = Circle((0, 0), fovR, edgecolor='k', facecolor='none', lw=1.)
    ax.add_patch(p)
    art3d.pathpatch_2d_to_3d(p, z=min_time, zdir="z")
    ax.set_xlim(-fovR, fovR)
    ax.set_ylim(-fovR, fovR)
    ax.set_zlim(min_time, max_time)
    ax.set_xlabel('azimuth/deg')
    ax.set_ylabel('zenith/deg')
    ax.set_zlabel('t/ns')
    ax.scatter(
        xyt[:,0],
        xyt[:,1],
        xyt[:,2],
        lw=0,
        alpha=0.075,
        s=55.,
        c=color)

def save_image_sequence(
    event, 
    path,
    steps=27, 
    start_number=0, 
    start_azimuth=0.0, 
    end_azimuth=360.0,
    mask=None):
    plt.rcParams.update({'font.size': 12})
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    fig = plt.figure(figsize=(12, 6.75))
    ax = fig.gca(projection='3d')

    add_event_2_ax(event, ax, mask=mask)
    azimuths = np.linspace(start_azimuth, end_azimuth, steps, endpoint=False)
    step = start_number
    for azimuth in azimuths:
        ax.view_init(elev=15., azim=azimuth)
        plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        plt.savefig(
            os.path.join(
                path, 
                '3D_'+str(step).zfill(6) + '.png'), 
            dpi=180)
        step += 1

    plt.close()

def save_video(event, path, mask=None ,steps=12, fps=25, threads='auto'):
    with tempfile.TemporaryDirectory() as work_dir:
        
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
            os.path.splitext(path)[0] + '.mp4'
        ]
        subprocess.call(avconv_command)
