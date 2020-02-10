# -*- coding: utf-8 -*

import os
import json
import operator
import numpy as np
import progressBar as pb

from PIL import Image
from PIL import ImageTk
from watershed_flooding import Watershed
from copy import deepcopy


class Projects(object):

    def __init__(self):

        self.IMG_SCALE = [0.125, 0.25, 0.5, 1, 2, 4, 8]

        self.watershed = Watershed()

        self.defaultPath = "Projects/"
        self.defaultExtension = ".neuronote"
        self.wradius = [50, 50, 2, "#000000"]
        self.grad = "Morphological"
        self.sobel3_peso = 1/16
        self.currScale = self.IMG_SCALE.index(1)
        self.appPath = os.path.dirname(os.path.realpath(__file__))

        self.labels = None
        self.users = None
        self.currUser = None
        self.currUserID = None
        self.currImgID = 0
        self.masks = []
        self.masks_clean = []
        self.annotation = []
        self.images = []
        self.original_images = []
        self.gradient_images = []
        self.imagePaths = None
        self.imagePath = None
        self.projectPath = None
        self.lastImagePath = None
        self.lastBatchPath = None
        self.selectedLb = -1
        self.clean = False
        self.grad_show = False
        
        self.createSettingsFile()
        self.createProjectsDir()
        self.openSettings()

################################################################################################
########                               Create Menu                                      ########
################################################################################################

    def newProject(self, projectName, userName):
        file = open(self.defaultPath + projectName + self.defaultExtension,"w", encoding='utf-8')

        self.users = [[userName, "/", -1]]
        self.currUser = self.users[0]
        self.currUserID = 0
        self.labels = [["Comment_1", "#ff0000"], ["Comment_2", "#00ff00"]]
        file.close

        self.projectPath = self.appPath + "/" + self.defaultPath + projectName + self.defaultExtension
        self.updateLastProject()

        json.dump(self.__getstate__(), file, indent=4)

    def saveProject(self, path = None):
        temp = self.projectPath

        if path != None:
            self.projectPath = path
            
        file = open(self.projectPath,"w", encoding='utf-8')
        json.dump(self.__getstate__(), file, indent=4)

        self.projectPath = temp
        file.close()

    def openImage(self,  tk_main, path = None):
        if(path == None):
            self.original_images = [(Image.open(self.currUser[1]))]
        else:
            self.original_images = [Image.open(path)]

        self.masks = [ (self.createMask(self.original_images[0].size) ) ]
        self.masks_clean = [ (self.createMask(self.original_images[0].size) ) ]
        self.annotation = [(self.createAnnotation(self.original_images[0].size))]
            
        self.currImgID = 0
        self.users[ self.currUserID ][1] = self.imagePaths
        self.users[ self.currUserID ][2] = -1
        self.currUser = self.users[ self.currUserID ]

        self.gradient_images = self.watershed.dilate_images(tk_main, self.original_images, self.wradius, self.grad, self.sobel3_peso)

        if(self.grad_show):
            self.images = self.gradient_images
        else:
            self.images = self.original_images

        self.resetImgScale()

    def openBatch(self, tk_main, path = None):
        limpar = 1
        images_ext = [".jpg",".gif",".png",".tiff"]

        if(path == None):
            listFiles = os.listdir(self.currUser[1])
        else:
            listFiles = os.listdir(path)
            
        listFiles.sort()
        for filename in listFiles:
            ext = os.path.splitext(filename)[1]
            if ext.lower() not in images_ext:
                continue
            
            if(limpar == 1):
                self.imagePaths = []
                self.original_images = []
                self.gradient_images = []
                self.masks = []
                self.mask_clean = []
                self.annotation = []
                
                if(path == None):
                    self.currImgID = int(self.currUser[2])
                    path = self.currUser[1]
                else:
                    self.currImgID = 0
                
                limpar = 0

            self.original_images.append(Image.open(path + "/" + filename))

            self.masks.append(self.createMask(self.original_images[-1].size) )
            self.masks_clean.append(self.createMask(self.original_images[-1].size) )
            self.annotation.append(self.createAnnotation(self.original_images[-1].size))
            self.imagePaths.append(path + "/" + filename)

        self.lastBatchPath = path

        self.users[ self.currUserID ][1] = path
        self.users[ self.currUserID ][2] = 0
        self.currUser = self.users[ self.currUserID ]
        
        self.gradient_images = self.watershed.dilate_images(tk_main, self.original_images, self.wradius, self.grad, self.sobel3_peso)

        if(self.grad_show):
            self.images = self.gradient_images
        else:
            self.images = self.original_images

        self.resetImgScale()

        return limpar

    def loadAnnotation(self):
        if(self.isBatchImg()):
            path = self.imagePaths[0]
        else:
            path = self.imagePaths

        pos = [path.replace("\\", "/")[::-1].find("/"), path[::-1].find(".")]
        diretorio = path[:-pos[0]] + "gt_" + self.currUser[0]

        if (not os.path.isdir(diretorio) ):
            return

        images_ext = [".png"]

        listFiles = os.listdir(diretorio)
        listFiles.sort()
        f = 0 
        self.annotation = [ [] for x in range(len(self.images)) ]
        for filename in listFiles:
            ext = os.path.splitext(filename)[1]
            if ext.lower() not in images_ext:
                continue
            self.setAnnotation(f, Image.open(diretorio + "/" + filename))
            f += 1
            if(f >= len(self.images)):
                break

        self.loadMask()

    def saveAnnotation(self):
        if(self.isBatchImg()):
            path = self.imagePaths[0]
        else:
            path = self.imagePaths

        pos = [path.replace("\\", "/")[::-1].find("/"), path[::-1].find(".")]
        diretorio = path[:-pos[0]] + "gt_" + self.currUser[0]

        if (not os.path.isdir(diretorio) ):
            os.makedirs(diretorio)

        if (self.isBatchImg()):
            annotationDir = []
            for imageBath in self.imagePaths:
                annotationDir.append(diretorio + "/gt_" + imageBath[-pos[0]:-pos[1]] + "png")
        else:
            annotationDir = [diretorio + "/gt_" + path[-pos[0]:-pos[1]] + "png"]

        for i in range(len(self.annotation)):
            self.annotation[i].save(annotationDir[i])

    def clearImage(self):
        self.masks = deepcopy(self.masks_clean)

    def exportCount(self, tb_main, countDir):
        if(self.isBatchImg()):
            path = self.imagePaths[0]
        else:
            path = self.imagePaths

        pos = [path.replace("\\", "/")[::-1].find("/"), path[::-1].find(".")]
        img_dir = path[:-pos[0]]

        count_file = open(countDir,"w", encoding='utf-8')

        count_file.write("## File generated by Neuronote Software\n")
        count_file.write("## Avaliable from https://github.com/OdiegoS/TCC\n")
        count_file.write("##\n")
        count_file.write("# User: {}\n".format(self.currUser[0]) )
        count_file.write("# Path: {}\n".format(img_dir) )
        count_file.write("##\n")
        count_file.write("## ID;\tComment;\tCount;\n")

        total_count = 0
        count_t = self.count(tb_main)
        for i in range(len(self.labels)):
            count_file.write("\t{};\t{};\t{};\n".format(i, self.labels[i][0], count_t[i]) )
            total_count += count_t[i]

        count_file.write("\t ;\tTOTAL;\t{};\n".format(total_count) )

        count_file.close

    def configure(self, win_x, win_y, win_z, color, gradient, peso = None):
        self.wradius = [win_x, win_y, win_z, color]
        
        if( (self.grad != gradient) or (self.sobel3_peso != peso) ):
            self.grad = gradient
            if(peso != None):
                self.sobel3_peso = float(peso)
            return True
        return False

    def changeGradient(self, tk_main):
        self.gradient_images = self.watershed.dilate_images(tk_main,self.original_images, self.wradius, self.grad, self.sobel3_peso)

        if(self.grad_show):
            self.images = self.gradient_images
            return True
        return False

################################################################################################
########                               Frame Label                                      ########
################################################################################################

    def addLabel(self, comment, color):
        self.labels.append( [comment, color] )

    def removeLabel(self):
        del self.labels[-1]

    def addUser(self, name):
        self.users.append( [name, "/", -1] )
        self.users.sort()
        self.findCurrUser()

    def removeUser(self, pos):
        del self.users[pos]
        self.findCurrUser()

################################################################################################
########                               Add Bind                                         ########
################################################################################################

    def applyWatershed(self, coord, progressBar):
        size = self.getDimensionCurrImg()
        return self.watershed.start(self.gradient_images, size[0], size[1], coord[0], coord[1], self.wradius, self.getCurrImgID(), self.getQtdImage(), progressBar)

    def changeMaskClean(self):
        self.clean = not self.clean

    def changeGradImg(self):
        self.grad_show = not self.grad_show

        if(self.grad_show):
            self.images = self.gradient_images
        else:
            self.images = self.original_images

    def increaseImgScale(self):
        newScale = self.currScale + 1

        if( newScale >= len(self.IMG_SCALE)):
            return False
        
        self.currScale = newScale
        return True

    def decreaseImgScale(self):
        newScale = self.currScale - 1
        if( newScale < 0):
            return False
        
        self.currScale = newScale
        return True
    
################################################################################################
########                               Open Settings                                    ########
################################################################################################

    def openSettings(self):
        file = open("settings","r", encoding='utf-8')
        
        try:
            self.projectPath = json.load(file)
        except ValueError:
            self.projectPath = ""

        file.close()

    def loadSettings(self):
        file = open(self.projectPath,"r", encoding='utf-8')

        self.__setstate__(json.load(file))

        file.close()

    def loadComments(self, data):

        del self.labels
        self.labels = [ [ [],[] ] for i in range(1) ]
        
        for label in data:
            sep = label.split(" ")
            color = sep[1]
            
            del sep[1]
            del sep[0]

            self.labels.append( [" ".join(sep), color ] )
        del self.labels[0]


################################################################################################
########                                  Gets, IS                                      ########
################################################################################################

    def getAppPath(self):
        return self.appPath

    def getProjectName(self):
        name = (self.projectPath.replace("\\", "/")).split("/")[-1]
        name = (name.split("."))[:-1]
        name = "".join(name)
        return name

    def getQtdImage(self):
        return len(self.images)

    def getExportPath(self):
        path = self.getPathCurrImg()
        pos = [path.replace("\\", "/")[::-1].find("/"), path[::-1].find(".")]
        diretorio = path[:-pos[0]] + "gt_" + self.currUser[0]

        if (os.path.isdir(diretorio)):
            path = diretorio
        else:
            path = path[:-pos[0]]

        return path

    def getCurrUserName(self):
        return self.currUser[0]

    def getNextColor(self, tam):
        if(tam<8):
            switcher = {
                0: "#ff0000",
                1: "#00ff00",
                2: "#0000ff",
                3: "#ffff00",
                4: "#ff00ff",
                5: "#00ffff",
                6: "#ffa500",
                7: "#a020f0"
            }
            return switcher.get(tam)
            
        return '#%02x%02x%02x' %( (tam*35)%255, (tam*55)%255, (tam*15)%255)

    def getQtdLabel(self):
        if(self.labels):
            return len(self.labels)
        else:
            return 0

    def getQtdUser(self):
        return len(self.users)

    def getUserName(self, pos):
        return self.users[pos][0]

    def getCurrUserID(self):
        return self.currUserID

    def getImgScale(self):
        return self.IMG_SCALE[self.currScale]

    def getSelectedLb(self):
        return self.selectedLb

    def getLabels(self, pos):
        return self.labels[pos]

    def getMask(self, pos):
        return self.masks[pos]

    def getCurrImgID(self):
        return self.currImgID

    def getAnnotation(self, pos):
        return self.annotation[pos]

    def getDimensionCurrImg(self):
        img = self.getCurrImg() 
        return [img.width(), img.height() ]

    def getCurrImg(self):
        img = ImageTk.PhotoImage(self.images[ self.currImgID ])
        return img

    def getCurrMask(self):
        if(self.clean):
            img = ImageTk.PhotoImage(self.masks_clean[ self.currImgID ] )
        else:
             img = ImageTk.PhotoImage(self.masks[ self.currImgID ] )
        return img

    def getPathCurrImg(self):
        if( type(self.imagePaths) is list):
            return self.imagePaths[ self.currImgID ]
        else:
            return self.imagePaths

    def getCurrImgResize(self, size):
        img = self.images[ self.currImgID ]
        newImg = ImageTk.PhotoImage(img.resize(size))
        return newImg

    def getCurrMaskResize(self,size):
        if(self.clean):
            img = self.masks_clean [ self.currImgID ]
        else:
            img = self.masks [ self.currImgID ]
        newImg = ImageTk.PhotoImage(img.resize(size))
        return newImg

    def getImage(self, pos):
        return self.images[pos]

    def getLastImagePath(self):
        return self.lastImagePath

    def getWradius(self):
        return self.wradius

    def getSobel3Peso(self):
        return self.sobel3_peso

    def isCurrUser(self, value):
        if(type(value) is int):
            if(self.currUserID == value):
                return True
        return False

    def isBatchImg(self):
        if(self.currUser[2] == -1):
            return False
        return True

    def isProjectExist(self):
        if len(self.projectPath) == 0:
            return False
        else:
            return True

    def isRecentProjectExist(self):
        return os.path.isfile(self.projectPath)

    def existImagePaths(self):
        if(self.imagePaths != "/"):
            return True
        return False

################################################################################################
########                             Sets, Update                                       ########
################################################################################################

    def setMask(self, pos, mask):
        self.masks[pos] = mask

    def setAnnotation(self, pos, annotation):
        self.annotation[pos] = annotation

    def setSelectedLb(self, key):
        self.selectedLb = key

    def setLabelComment(self, pos, comment):
        self.labels[pos][0] = comment

    def setLabelColor(self, pos, color):
        self.labels[pos][1] = color

    def setCurrUser(self, pos):
        self.currUser = self.users[pos]
        self.currUserID = pos

    def setProjectPath(self, path):
        self.projectPath = path
        self.updateLastProject()

    def updateUserImg(self):
        self.users[ self.currUserID ][2] = self.getCurrImgID()
        self.currUser = self.users[ self.currUserID ]

    def updateImagePaths(self, path = None):
        if path == None:
            self.imagePaths = self.currUser[1]
            
            if(self.imagePaths == '/'):
                del self.images[:]
                del self.masks[:]
                del self.masks_clean[:]
                del self.annotation[:]
                
        else:
            self.imagePaths = path

    def updateCurrImg(self, info):
        if(info == "add"):
            self.currImgID += 1
        elif info == "sub":
            self.currImgID -= 1
        else:
            self.currImgID = self.currUser[2]

    def updateLastProject(self):
        file = open("settings","w", encoding='utf-8')
        json.dump(self.projectPath, file, indent=4)
        file.close

################################################################################################
########                                                                                ########
################################################################################################

    def createSettingsFile(self):
        if (not os.path.isfile("settings") ):
            file = open("settings","w", encoding='utf-8')
            file.close
    
    def createProjectsDir(self):
        if (not os.path.isdir("Projects") ):
            os.makedirs("Projects")

    def createMask(self, size):
        return Image.new('RGBA', size, (0, 0, 0, 0))

    def createAnnotation(self, size):
        return Image.new('L', size, 0)

    def findCurrUser(self):
        for i in range (0,self.getQtdUser() ):
            if(self.currUser == self.users[i]):
                self.currUserID = i
                return

    def loadMask(self):
        for i in range(len(self.annotation)):
            m = self.getMask(i)
            width, height = self.annotation[i].size
            for x in range(width):
                for y in range(height):
                    pixel_value = self.annotation[i].getpixel((x, y))
                    if( (pixel_value > 0) and (pixel_value <= len(self.labels)) ):
                         colorHex = self.getLabels(pixel_value - 1)[1]
                         colorRGB = tuple(int(colorHex.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))
                         m.putpixel( (x, y), colorRGB )
            self.setMask(i, m)

    def resetImgScale(self):
        self.currScale = self.IMG_SCALE.index(1)

    def count(self, tb_main):
        count = np.zeros(1000, dtype=int)
        img_temp = deepcopy(self.annotation)

        progressBar = pb.ProgressBar(tb_main)
        n_progressBar = 100 // self.getQtdImage()

        for z in range(self.getQtdImage()):
            img = self.getImage(z)
            width, height = img.size

            for x in range(width):
                for y in range(height):
                    label = img_temp[z].getpixel((x,y))
                    if(label > 0):
                        array_temp = [ [z,x,y] ]
                        while len(array_temp) > 0:
                            z_t = array_temp[0][0]
                            x_t = array_temp[0][1]
                            y_t = array_temp[0][2]

                            if(img_temp[z_t].getpixel((x_t, y_t)) == label):

                                w, h = self.getImage(z_t).size

                                if( (x_t  > 0) and (y_t > 0) and (img_temp[z_t].getpixel((x_t - 1, y_t -1)) == label) ):
                                    array_temp.append( [z_t,x_t - 1, y_t -1] )
                                if( (y_t > 0) and (img_temp[z_t].getpixel((x_t, y_t -1)) == label) ):
                                    array_temp.append( [z_t,x_t, y_t -1] )
                                if( (x_t  < (w-1) ) and (y_t > 0) and (img_temp[z_t].getpixel((x_t + 1, y_t -1)) == label) ):
                                    array_temp.append( [z_t,x_t + 1, y_t -1] )

                                if( (x_t  > 0) and (y_t < (h-1) ) and (img_temp[z_t].getpixel((x_t - 1, y_t + 1)) == label) ):
                                    array_temp.append( [z_t,x_t - 1, y_t + 1] )
                                if( (y_t < (h-1) ) and (img_temp[z_t].getpixel((x_t, y_t + 1)) == label) ):
                                    array_temp.append( [z_t,x_t, y_t + 1] )
                                if( (x_t  < (w-1) ) and (y_t < (h-1) ) and (img_temp[z_t].getpixel((x_t + 1, y_t + 1)) == label) ):
                                    array_temp.append( [z_t,x_t + 1, y_t + 1] )

                                if( (x_t  > 0) and (img_temp[z_t].getpixel((x_t - 1, y_t)) == label) ):
                                    array_temp.append( [z_t,x_t - 1, y_t] )
                                if( (x_t  < (w-1) ) and (img_temp[z_t].getpixel((x_t + 1, y_t)) == label) ):
                                    array_temp.append( [z_t,x_t + 1, y_t] )

                                if( (z_t  > 0 ) and (img_temp[z_t-1].getpixel((x_t, y_t)) == label) ):
                                    array_temp.append( [z_t-1,x_t, y_t] )
                                if( (z_t  < (self.getQtdImage()-1) ) and (img_temp[z_t+1].getpixel((x_t, y_t)) == label) ):
                                    array_temp.append( [z_t+1,x_t, y_t] )

                                img_temp[z_t].putpixel( (x_t,y_t), 0 )
                            del array_temp[0]
                            array_temp.sort(key=operator.itemgetter(0))

                        count[label-1] = count[label-1] + 1
            progressBar.updatingBar(n_progressBar)
        progressBar.close()
        return count

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['images']
        del state['original_images']
        del state['gradient_images']
        del state['imagePaths']
        del state['masks']
        del state['masks_clean']
        del state['annotation']
        del state['watershed']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)