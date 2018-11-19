# -*- coding: utf-8 -*-
import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pandas as pd
import pyqtgraph.exporters
#todo:
#   Add x-axis lock across plots
#   Select/Toggle plots via GUI
#   Easier parsing/updating
configs={}
plotList=[]
downsamp = 0
autoExport = 1  #move to config
legendEnable = 1

def parsePlot(configFile='plotconfig.py'):
    execfile(configFile,configs)    #have to handle local python scope issues with execfile by passing to dict and accessing key value           
    data = pd.read_csv(filename,parse_dates=['ts'])
    x = np.float32(data['ts'])
    #temp filter for speed inputs
    #data['Drive_motor speed 2 '] = data['Drive_motor speed 2 '][(data['Drive_motor speed 2 '] >= 0) & (data['Drive_motor speed 2 '] <= 1000)]
    #data['Drive_motor speed 1 '] = data['Drive_motor speed 1 '][(data['Drive_motor speed 1 '] >= 0) & (data['Drive_motor speed 1 '] <= 1000)]
    pg.setConfigOption('background', 'w')
    app = QtGui.QApplication([])
    genPenList = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w','b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    win = pg.GraphicsWindow(title="Basic plotting examples")
    win.resize(1400,1000)
    win.setWindowTitle('pyqtgraph example: Plotting')

    pg.setConfigOptions(antialias=True)     # Enable antialiasing for prettier plots

    for i in configs['plotConfig']:
        plotList.append(win.addPlot(title=i["name"]))
        if legendEnable:
            plotList[len(plotList)-1].addLegend()
        plotList[len(plotList)-1].showGrid(1,1)
        
        win.nextRow()

    for i in configs['varList']:
        print i['name']
        if i['type'] == 'data':
            plotList[i['plot']-1].plot(x,np.array(data[i['name']]), pen=i['color'], name=i['name'])
            
        if i['type'] == 'net drive current':
            net = np.array(data['Drive Motor Current 1 '])+np.array(data['Drive Motor Current 2 '])
            plotList[i['plot']-1].plot(x,net, pen=i['color'], name=i['name'])
                    
        if i['type'] == 'net deck current':    
            net = np.array(data['Deck Motor Current 1 '])+np.array(data['Deck Motor Current 2 '])+np.array(data['Deck Motor Current 3 '])        
            plotList[i['plot']-1].plot(x,net, pen=i['color'], name=i['name'])
            
        if configs['xMax'] or configs['xMin']:
            plotList[i['plot']-1].setLimits(xMin=configs['xMin'],xMax=configs['xMax'])
        try:
            if i['ymin']:
                plotList[i['plot']-1].setLimits(yMin=i['ymin'])
        except:pass                
        try:
            if i['ymax']:
                plotList[i['plot']-1].setLimits(yMax=i['ymax'])
        except:pass
         
        if downsamp:
            plotList[i['plot']-1].setDownsampling(ds=2,mode='subsample')
            
    print "BinState:"
    for j in configs['binlist']:
        plotBinList=[]
        plotBinList.append(win.addPlot(title="State Data"))
        plotBinList[len(plotBinList)-1].addLegend()
        win.nextRow()
        for idx,i in enumerate(j):
            print i
            y =(np.array(data[i])*.9+idx)
            plotBinList[len(plotBinList)-1].plot(x,y, pen=genPenList[idx], name=i)
            #y =np.array(data[i])*(idx+2)                           #blocky...
            #plotBinList[len(plotBinList)-1].addItem(pg.PlotDataItem(x,y, pen=None,symbol='s',symbolBrush=genPenList[idx],symbolPen=genPenList[idx],name=i))
            if configs['xMax'] or configs['xMin']:                
                plotBinList[len(plotBinList)-1].setLimits(xMin=configs['xMin'],xMax=configs['xMax'])
    
def exporter():
    print "exporting"
    for idx,i in enumerate(configs['plotConfig']):
        exporter = pg.exporters.ImageExporter(plotList[idx])
        #exporter.parameters()['height'] = 400   # (note this also affects width parameter)
        exporter.parameters()['width'] = 2000   # (note this also affects height parameter)
        exporter.export("auto_png_export\\"+i['name']+'.png')            
        idx+=1
    
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    filename = "Parsed\\20150722_Log4.csv"    
   
    if len(sys.argv)>1: 
        filename = sys.argv[1]    
    if len(sys.argv)>2: 
        configFile = sys.argv[2]                
        parsePlot(configFile)
    else:
        parsePlot()
    
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        if autoExport:
            try:
                os.mkdir("auto_png_export")
            except:pass #dir exists
            
            QtGui.QApplication.processEvents()
            exporter()
            print "\n\nAuto Export Enabled. Check the 'auto_png_export' directory for image exports"
        else:
            QtGui.QApplication.instance().exec_()
            
