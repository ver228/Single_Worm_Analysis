import sys
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt4.QtCore import QDir, QTimer, Qt, QPointF
from PyQt4.QtGui import QPixmap, QImage
from PyQt4.QtGui import QPixmap, QImage, QPainter, QColor, QFont, QPolygonF, QPen
#from PyQt4.QtGui import QPixmap, QImage, QApplication, QMainWindow, QFileDialog, QMessageBox
#from PyQt4.QtCore import QDir, QTimer, Qt

from MWTracker.GUI_Qt4.HDF5videoViewer.HDF5videoViewer_GUI import HDF5videoViewer_GUI
from ManualResults_ui import Ui_ImageViewer

import tables
import os
import numpy as np

class ManualResults_GUI(HDF5videoViewer_GUI):
    def __init__(self, ui = '', mask_file = ''):
        if not ui:
            super().__init__(Ui_ImageViewer())
        else:
            super().__init__(ui)

        if mask_file:
            self.vfilename = mask_file
            self.updateVideoFile()

    def updateImage(self):
        self.readImage()
        self.drawSkel(self.frame_img, self.frame_qimg)
        self.pixmap = QPixmap.fromImage(self.frame_qimg)
        self.ui.imageCanvas.setPixmap(self.pixmap);


    def drawSkel(self, worm_img, worm_qimg):
        c_ratio_y = worm_qimg.width()/worm_img.shape[1];
        c_ratio_x = worm_qimg.height()/worm_img.shape[0];
        
        qPlg = {}
        with tables.File(self.vfilename, 'r') as ske_file_id:
            head_coord = ske_file_id.get_node('/head_coord')[self.frame_number];
            head_coord[0] = head_coord[0]*c_ratio_x
            head_coord[1] = head_coord[1]*c_ratio_y

            tail_coord = ske_file_id.get_node('/tail_coord')[self.frame_number];
            tail_coord[0] = tail_coord[0]*c_ratio_x
            tail_coord[1] = tail_coord[1]*c_ratio_y
            
            for tt in ['skeleton', 'contour_side1', 'contour_side2']:
                dat = ske_file_id.get_node('/' + tt)[self.frame_number];
                dat[:,0] = dat[:,0]*c_ratio_x
                dat[:,1] = dat[:,1]*c_ratio_y
            
                qPlg[tt] = QPolygonF()
                for p in dat:
                    qPlg[tt].append(QPointF(*p))
        
        self.skel_colors = {'skeleton':(27, 158, 119 ), 
            'contour_side1':(217, 95, 2), 'contour_side2':(231, 41, 138)}

        pen = QPen()
        pen.setWidth(2)
        
        painter = QPainter()
        painter.begin(worm_qimg)
    
        for tt, color in self.skel_colors.items():
            pen.setColor(QColor(*color))
            painter.setPen(pen)
            painter.drawPolyline(qPlg[tt])
        
        pen.setColor(Qt.black)
        
        painter.setPen(pen)
        radius = 3

        painter.setBrush(Qt.green)
        painter.drawEllipse(QPointF(*head_coord), radius, radius)
        
        painter.setBrush(Qt.red)    
        painter.drawRect(*tail_coord, 5, 5)
        
        painter.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    ui = ManualResults_GUI(mask_file=sys.argv[1])
    ui.show()
    
    sys.exit(app.exec_())