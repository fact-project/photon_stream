from scoop import shared
from scoop import futures
import scoop as sc

import numpy as np
import json
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Circle
import tempfile
import subprocess
from sklearn.cluster import DBSCAN
from sklearn import metrics
from tqdm import tqdm

class SimulatuionTruth(object):
    def __init__(self, eventDict):
        self.energyGeV = eventDict['MCorsikaEvtHeader.fTotalEnergy']      


class Event(object):

    def __init__(self, eventDict, geometry):
        self.minArrivalTime = 12.5
        self.maxArrivalTime = 42.5#115.0
        self.degOverNs=0.15
        self.geometry = geometry
        self.photonStream = self.__makePhotonStream(eventDict, geometry)
        self.cluster = Cluster(self, degOverNs=self.degOverNs)
        self.dict = eventDict

        self.classicPhotonCharge = np.array(self.dict['photoncharge'])

        try:
            self.simulationTruth = SimulatuionTruth(eventDict)
        except:
            pass

    def __repr__(self):
        out = 'Event('+str(self.photonStream.shape[0])+' p.e.)\n'
        return out

    def summaryString(self):
        info = ""
        info+= "photons "+str(self.photonStream.shape[0])
        if self.simulationTruth is not None:
            info+= ", Energy "+str(round(self.simulationTruth.energyGeV))+" GeV"
        return info

    def __makePhotonStream(self, event, geometry):
        photonArrivals = event['PhotonArrivals']
        phs = []
        self.singlePulsPhotonCharge = []
        for pix, photonArrivalsInPixel in enumerate(photonArrivals):

            self.singlePulsPhotonCharge.append(len(photonArrivalsInPixel))
            for photonArrivalSlice in photonArrivalsInPixel:
                photonArrivalTime = photonArrivalSlice*0.5
                if self.minArrivalTime < photonArrivalTime < self.maxArrivalTime:
                    phs.append(np.array([
                        geometry.dirX[pix], 
                        geometry.dirY[pix], 
                        photonArrivalTime
                        ]))
        phs = np.array(phs)
        self.singlePulsPhotonCharge = np.array(self.singlePulsPhotonCharge)

        return phs

class Run(object):
    def __init__(self, RunPath, geometryPath):
        self.__path = os.path.abspath(RunPath)
        evtDicts = self.readEvtDicts(self.__path)   
        self.geometry = Geometry(os.path.abspath(geometryPath))
        self.events = []
        for evtDict in evtDicts:
            self.events.append(Event(evtDict, self.geometry))

    def readEvtDicts(self, RunPath):
        with open(RunPath) as file:
            return json.load(file)

    def __getitem__(self, index):
        """
        Returns the index-th event of the run.

        Parameters
        ----------
        index       The index of the event to be returned.  
        """
        return self.events[index]

    def __repr__(self):
        out = 'Run('
        out += "path='" + self.__path + "', "
        out += str(len(self.events)) + ' events)\n'
        return out

def addEvent2Ax(event, ax):
    ax.set_title(event.summaryString())
    fovR = event.geometry.fovRadius
    minTime = event.photonStream[:,2].min()
    maxTime = event.photonStream[:,2].max()
    p = Circle((0, 0), fovR, edgecolor='k', facecolor='none', lw=1.)
    ax.add_patch(p)
    art3d.pathpatch_2d_to_3d(p, z=minTime, zdir="z")
    ax.set_xlim(-fovR, fovR)
    ax.set_ylim(-fovR, fovR)
    ax.set_zlim(minTime, maxTime)
    ax.set_xlabel('X/deg')
    ax.set_ylabel('Y/deg')
    ax.set_zlabel('t/ns')
    ax.scatter(
        event.photonStream[:,0],
        event.photonStream[:,1],
        event.photonStream[:,2],
        lw=0,
        alpha=0.075,
        s=55.)    

def addEventWithCluster2Ax(event, ax):

    ax.set_title(event.summaryString())
    fovR = event.geometry.fovRadius
    minTime = event.photonStream[:,2].min()
    maxTime = event.photonStream[:,2].max()
    p = Circle((0, 0), fovR, edgecolor='k', facecolor='none', lw=1.)
    ax.add_patch(p)
    art3d.pathpatch_2d_to_3d(p, z=minTime, zdir="z")
    ax.set_xlim(-fovR, fovR)
    ax.set_ylim(-fovR, fovR)
    ax.set_zlim(minTime, maxTime)
    ax.set_xlabel('X/deg')
    ax.set_ylabel('Y/deg')
    ax.set_zlabel('t/ns')

    # Black removed and is used for noise instead.
    unique_labels = set(event.cluster.labels)
    colors = plt.cm.brg(np.linspace(0, 1, len(unique_labels)))

    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = 'k'

        class_member_mask = (event.cluster.labels == k)

        xyz = event.photonStream[
            class_member_mask & event.cluster.coreSamplesMask]
        ax.scatter(xyz[:,0],xyz[:,1],xyz[:,2], lw=0, alpha=0.075, s=55., c=col)

        xyz = event.photonStream[
            class_member_mask & ~event.cluster.coreSamplesMask]
        ax.scatter(xyz[:,0],xyz[:,1],xyz[:,2], lw=0, alpha=0.05, s=25., c=col)

def saveImageSequence(
    event, 
    path, 
    cluster=False, 
    steps=27, 
    startNumber=0, 
    startAzimuth=0.0, 
    endAzimuth=360.0):
    plt.rcParams.update({'font.size': 12})
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    fig = plt.figure(figsize=(12, 6.75))
    ax = fig.gca(projection='3d')
    if cluster:
        addEventWithCluster2Ax(event, ax)
    else:
        addEvent2Ax(event, ax)

    azimuths = np.linspace(startAzimuth, endAzimuth, steps, endpoint=False)
    step = startNumber
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

def saveVideo(event, path, steps=12, fps=25, threads='auto'):
    with tempfile.TemporaryDirectory() as work_dir:
        
        azimuths = np.linspace(0, 360, 10, endpoint=False)
        for i, az in tqdm(enumerate(azimuths)):

            saveImageSequence(
                event=event,
                path=work_dir,
                steps=steps,
                cluster=False,
                startAzimuth=az,
                endAzimuth=az+18,
                startNumber=(i*steps*2))
            
            saveImageSequence(
                event=event,
                path=work_dir,
                steps=steps,
                cluster=True,
                startAzimuth=az+18,
                endAzimuth=az+36,
                startNumber=(i*steps*2)+steps)

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

def plot(event, cluster=False):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    if cluster:
        addEventWithCluster2Ax(event, ax)
    else:
        addEvent2Ax(event, ax)

"""
def output_path():
    return sc.shared.getConst('output_path', timeout=5)

def saveVideoOnCluster(event):
    eventNumber = event.dict['EventNum']
    saveVideo(
        event, 
        os.path.join(output_path(), str(eventNumber)),
        steps=12,
        threads=1)

if __name__ == '__main__':
    
    sc.shared.setConst(output_path='/home/sebastian/photon_stream_video')

    if not os.path.exists(output_path()):
        os.mkdir(output_path())

    run = Run(
        '/home/sebastian/Desktop/hadronic_rain_gammas.txt', 
        '/home/sebastian/Desktop/pixel-map.csv')
     
    result = list(sc.futures.map(saveVideoOnCluster, run))
"""

def plotSinglePeVsClassicPe(run, path):
    xedges = np.linspace(0,99,100)
    yedges = np.linspace(0,99,100)

    classicCharge = []
    singlePCharge = []
    for evt in run:
        classicCharge.append(evt.classicPhotonCharge)
        singlePCharge.append(evt.singlePulsPhotonCharge)

    classicCharge = np.concatenate(classicCharge, axis=0)
    singlePCharge = np.concatenate(singlePCharge, axis=0)

    H, xedges, yedges = np.histogram2d(
        singlePCharge, 
        classicCharge, 
        bins=(xedges, yedges))
    my_dpi = 350.0
    width = 1280/my_dpi
    hight = 1280/my_dpi

    fig, ax = plt.subplots(figsize=(width, hight))
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.rcParams.update({'font.size': 8})
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.tick_left()
    ax.xaxis.tick_bottom()   
    ax.set_ylabel('single pulse extractor [p.e.]')
    ax.set_xlabel('classic pulse extractor [p.e.]')
    #ax.set_title(titel)
    im = plt.imshow(
        np.log(H+1), 
        interpolation='none',
        origin='low', 
        extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], 
        aspect='equal')    
    im.set_cmap('viridis')
    ax.plot([0,99],[0,99],'r')
    fig.savefig(path, dpi=my_dpi)