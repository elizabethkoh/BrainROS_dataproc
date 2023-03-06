# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 11:39:55 2022

@author: elizabeth koh
"""
import regex as re
import pandas as pd
import os
import matplotlib.pyplot as plt
from PyQt5.Qt import *
from fileopen2 import Ui_Form
import sys
# from https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way
from scipy.signal import savgol_filter # use Savitzky-Golay filter 
filterFlag=True # turns on filtering

def velPlotter(df, ax=None, label=[''],title='',xlabel='time [ms]',ylabel='[inch/s]'):
    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6,6), dpi=600)
    if (filterFlag):
        plt.plot(df['timestamp'],savgol_filter(df['xvel'],11,3), marker='o',linestyle = '-',axes=ax)  
        plt.plot(df['timestamp'],savgol_filter(df['yvel'],11,3),marker='*', linestyle = '-',axes=ax)  
    else:
        plt.plot(df['timestamp'],df['xvel'], marker='o',linestyle = '-',axes=ax)        
        plt.plot(df['timestamp'],df['yvel'], marker='*',linestyle = '-',axes=ax)
    #ymin = np.round(dplt['xvel'].min()*1.2)
    #ymax = np.round(dplt['xvel'].max()*.12)
    plt.grid()
    plt.legend(label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    #plt.ylim(ymin,ymax)

def distPlotter(df, ax=None, label=[''],title='',xlabel='time [ms]',ylabel='[inch]'):
    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6,6), dpi=600)
    plt.plot(df['timestamp'],df['xpos'], marker='o',linestyle = '-',axes=ax)        
    plt.plot(df['timestamp'],df['ypos'], marker='*',linestyle = '-',axes=ax)
    #ymin = np.round(dplt['xvel'].min()*1.2)
    #ymax = np.round(dplt['xvel'].max()*.12)
    plt.grid()
    plt.legend(label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    #plt.ylim(ymin,ymax)



class Window(QWidget,Ui_Form):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ui study")
        #self.resize(800, 600)
        self.setupUi(self) # change it

    def fileopen2(self):
        # print("button clicked!")
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        print(fname[0])
        self.lineEdit.setText(fname[0])
        self.file_str1 = fname[0]
        # self.lineEdit.adjustSize()
        # self.adjustSize()
        print(fname[0])
        self.plotCapturedFile(fname[0])
        
    def plotCapturedFile(self,file_str1):
        # for data processing of the odom data
        #file_str1 = r'C:\Users\koh46433\Downloads\vex4.cap'
        file1 = open(file_str1)
        lines = file1.readlines()
        file1.close()
        
        timelst = []
        yawlst = []
        xlist = []
        ylist = []
        linelist= []
        velxlist= []
        velylist= []
        speedlist = []
        imglist = []
        xlsxfileout =  os.path.splitext(file_str1)[0] + '.xlsx'
        writer = pd.ExcelWriter(xlsxfileout, engine='xlsxwriter')
        
        df = pd.DataFrame()
        df.to_excel(writer,sheet_name = 'odom')
        worksheet = writer.sheets['odom']
        
        raw = {'timestamp':[],'yaw':[],'xpos':[],'ypos':[],'xvel':[],'yvel':[],'vex_print':[]}
        df1 = pd.DataFrame(raw)
        dataLine = False # prev data line
        validCount = 0
        indStart = 1000
        indStop = 0
        indCount = 0
        ax = None
        graphInd = 0
        
        
        for line in lines:
            print('%s'%line)
            m = re.search(r'\((.+)\)', line) # gets the yaw, x, and y positionss
            if (m): #
                # if previous line is not a data line, add in a blank line
                if (dataLine == False):
                    yawlst.append('')
                    yawlst.append('yaw')
                    xlist.append('')
                    xlist.append('xpos')
                    ylist.append('')
                    ylist.append('ypos')
                    timelst.append('')
                    timelst.append('time')
                    linelist.append('')
                    linelist.append('vexPrint')
                    indStart = indCount
                    
                    
                yaw, xpos, ypos = m.group(1).split(',')
                yawlst.append(yaw)
                xlist.append(xpos)
                ylist.append(ypos)
                
                m1 = re.search(r'(.+) \(',line) # get the timestamp
                timelst.append(m1.group(1))
                
                m2 = re.search(r'\) (.+)',line)
                
                linelist.append(m2.group(1))
                
                yaw=float(yaw)
                xpos = float(xpos)
                ypos = float(ypos)
                timeStamp = float(m1.group(1))
                
                
                if ((indCount - indStart) >= 1):
                    print('compute velocity')
                    deltaT = timeStamp - df1.iloc[indCount-1]['timestamp'] 
                    xvel = xpos - df1.iloc[indCount-1]['xpos'] 
                    yvel = ypos - df1.iloc[indCount-1]['ypos'] 
                    xvel = xvel*1000.0/deltaT
                    yvel = yvel*1000.0/deltaT
                    dict1 = {'timestamp':float(m1.group(1)),'yaw': float(yaw),'xpos':float(xpos),
                            'ypos':float(ypos),'xvel':xvel,'yvel':yvel,'vex_print':m2.group(1)}
                
                else:
                    dict1 = {'timestamp':float(m1.group(1)),'yaw': float(yaw),'xpos':float(xpos),
                            'ypos':float(ypos),'xvel':0.,'yvel':0.,'vex_print':m2.group(1)}
                df1 = df1.append(dict1,ignore_index=True)

                
                dataLine = True
            else:
                if (dataLine ==True): # put in a blank line
                    timelst.append('')
                    yawlst.append('')
                    xlist.append('')
                    ylist.append('')
                    linelist.append('')
                    dict1 = {'timestamp':'','yaw': '','xpos':'','ypos':'','vex_print':''}
                    df1 = df1.append(dict1,ignore_index=True)
                    
                    indStop = indCount-1
                    indCount = indCount + 1
                    # plot the velocity curve
                    #plt.clf()
                    dplt = df1.iloc[indStart+1:indStop]
                    velPlotter(dplt,label=['xvel','yvel'],ax=None,title = str(indStart))
                    imgdir = os.path.dirname(file_str1) + '\\velplot_'+str(indStart) +'.png'
                    plt.savefig(imgdir)
                    imgPos = 'I%d'%indStart
                    imglist.append(imgdir)
                    worksheet.insert_image(imgPos, imgdir)
                    plt.close()
                    #plot the dist curve
                    distPlotter(dplt,label=['xpos','ypos'],ax=None,title = str(indStart))
                    imgdir = os.path.dirname(file_str1) + '\\displot_'+str(indStart) +'.png'
                    plt.savefig(imgdir)
                    imgPos = 'R%d'%indStart
                    imglist.append(imgdir)
                    worksheet.insert_image(imgPos, imgdir)
                    plt.close()
        
                    
                #timelst.append(line)
                timelst.append('')
                yawlst.append('')
                xlist.append('')
                ylist.append('')
                linelist.append(line)
                dict1 = {'timestamp':'','yaw': '','xpos':'','ypos':'','vex_print':line}
                df1 = df1.append(dict1,ignore_index=True)

                dataLine = False
                
            indCount = indCount+1
        
        #plot the last data set
        if indCount > len(lines) & (dataLine):
            indStop = indCount
            dplt = df1.iloc[indStart+1:indStop]
            velPlotter(dplt,label=['xvel','yvel'])
            imgdir = os.path.dirname(file_str1) + '\\velplot_'+str(indStart) +'.png'
            plt.savefig(imgdir)
            imgPos = 'I%d'%indStart
            imglist.append(imgdir)
            worksheet.insert_image(imgPos, imgdir)
            plt.close()
            #plot the dist curve
            distPlotter(dplt,label=['xpos','ypos'],ax=None,title = str(indStart))
            imgdir = os.path.dirname(file_str1) + '\\displot_'+str(indStart) +'.png'
            plt.savefig(imgdir)
            imgPos = 'R%d'%indStart
            imglist.append(imgdir)
            worksheet.insert_image(imgPos, imgdir)
            plt.close()
            
        df['time'] = timelst
        df['yaw'] = yawlst
        df['xpos'] = xlist
        df['ypos'] = ylist
        df['vexPrint'] = linelist
        df1.to_excel(writer,'odom',index=False)
        writer.close()
        for ig in imglist:
            os.remove(ig)

if __name__ == '__main__':
    
    
    app = QApplication(sys.argv)
    print(app.arguments())
    print(qApp.arguments())
    window = Window()
    window.show()
    #print(dir(window))
    sys.exit(app.exec_())