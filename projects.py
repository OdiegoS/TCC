# -*- coding: utf-8 -*

import os
from PIL import Image
from PIL import ImageTk
import json

class Projects(object):

    def __init__(self):

        self.labels = None
        self.users = None
        self.currUser = None
        self.currUserID = None
        self.currImgID = 0
        self.masks = []
        self.annotation = []
        self.images = []
        self.imagePaths = None
        self.defaultPath = "Projects/"
        self.defaultExtension = ".neuronote"
        self.imagePath = None
        self.projectPath = None
        self.lastImagePath = None
        self.lastBatchPath = None
        self.selectedLb = -1
        self.TAM = 50

        self.imgScale = [0.125, 0.25, 0.5, 1, 2, 4, 8]
        self.currScale = self.imgScale.index(1)

        # self.imgScale = 1.0
        # self.maxScale = 5.0
        # self.minScale = 0.25
        # self.scaleRate = 0.25
        self.appPath = os.path.dirname(os.path.realpath(__file__))

        if (not os.path.isfile("settings") ):
            file = open("settings","w", encoding='utf-8')
            file.close

        if (not os.path.isdir("Projects") ):
            os.makedirs("Projects")

        self.openSettings()

    def getAppPath(self):
        return self.appPath

    def colorDefault(self, tam):

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

    def addLabel(self, comment, color):
        self.labels.append( [comment, color] )

    def createMask(self, size):
        return Image.new('RGBA', size, (0, 0, 0, 0))

    def createAnnotation(self, size):
        return Image.new('L', size, 0)

    def removeLabel(self):
        del self.labels[-1]

    def updateLabelComment(self, pos, comment):
        self.labels[pos][0] = comment

    def updateLabelColor(self, pos, color):
        self.labels[pos][1] = color

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

    def sizeLabels(self):
        if(self.labels):
            return len(self.labels)
        else:
            return 0

    def getLabels(self, pos):
        return self.labels[pos]

    def addUser(self, name):
        self.users.append( [name, "/", -1] )
        self.users.sort()
        self.findCurrUser()

    def findCurrUser(self):
        for i in range (0,self.sizeUsers() ):
            if(self.currUser == self.users[i]):
                self.currUserID = i
                return

    def isCurrUser(self, value):
        if(type(value) is int):
            if(self.currUserID == value):
                return True
        '''
        elif (self.currUser[0] == value):
                return True
        '''
        return False

    def updateCurrUser(self, pos):
        self.currUser = self.users[pos]
        self.currUserID = pos

    def sizeUsers(self):
        return len(self.users)

    def getUserName(self, pos):
        return self.users[pos][0]

    def removeUser(self, pos):
        del self.users[pos]
        self.findCurrUser()

    def getCurrUserID(self):
        return self.currUserID

    def getCurrUserName(self):
        return self.currUser[0]

    def getCurrImgID(self):
        return self.currImgID

    def updateCurrImg(self, pos):
        if(pos == "add"):
            self.currImgID += 1
        elif pos == "sub":
            self.currImgID -= 1
        else:
            self.currImgID = self.currUser[2]

    def sizeImages(self):
        return len(self.images)

    def isBatchImg(self):
        
        if(self.currUser[2] == -1):
            return False
        return True

    def getDimensionCurrImg(self):
        img = self.getCurrImg() 
        return [img.width(), img.height() ]

    def getCurrImg(self):
        img = ImageTk.PhotoImage(self.images[ self.currImgID ])
        return img

    def getCurrMask(self):
        img = ImageTk.PhotoImage(self.masks[ self.currImgID ] )
        return img

    def getImage(self, pos):
        return self.images[pos]

    def getMask(self, pos):
        return self.masks[pos]

    def getAnnotation(self, pos):
        return self.annotation[pos]

    def setMask(self, pos, mask):
        self.masks[pos] = mask

    def setAnnotation(self, pos, annotation):
        self.annotation[pos] = annotation

    def setImage(self, pos, img):
        self.images[pos] = img
        self.masks[pos] = self.createMask(img.size)
        self.annotation[pos] = self.createAnnotation(img.size)

    def getPathCurrImg(self):
        if( type(self.imagePaths) is list):
            return self.imagePaths[ self.currImgID ]
        else:
            return self.imagePaths

    def updateUserImg(self):
        self.users[ self.currUserID ][2] = self.getCurrImgID()
        self.currUser = self.users[ self.currUserID ]

        #self.saveProject()

    def openSettings(self):
        file = open("settings","r", encoding='utf-8')
        # self.projectPath = file.read()
        # self.projectPath = self.projectPath

        try:
            self.projectPath = json.load(file)
        except ValueError:
            self.projectPath = ""

        # self.__setstate__(json.load(file))
        
        file.close()

    def notExistProject(self):
        if len(self.projectPath) == 0:
            return True
        else:
            return False

    def getProjectPath(self):
        return self.projectPath

    def isProjectExist(self):
        return os.path.isfile(self.projectPath)

    def loadSettings(self):
        file = open(self.projectPath,"r", encoding='utf-8')

        self.__setstate__(json.load(file))

        # project = file.read().splitlines()
        file.close()

        # self.users = [[0,0,0]]
        #
        # for i in range(2, 2*int(project[1])+int(project[1])+1, 3) :
        #     if project[0] == project[i]:
        #         self.currUserID = self.sizeUsers() - 1
        #
        #     self.users.append( [project[i], project[i+1], int(project[i+2]) ] )
        #
        # del self.users[0]
        # self.updateCurrUser(self.currUserID)
        #
        # data = project[2*int(project[1])+int(project[1])+2 : ]
        #
        # self.loadComments(data)

    def updateImagePaths(self, path = None):
        if path == None:
            self.imagePaths = self.currUser[1]
            
            if(self.imagePaths == '/'):
                del self.images[:]
                del self.masks[:]
                del self.annotation[:]
                
        else:
            self.imagePaths = path


    def existImagePaths(self):
        if(self.imagePaths != "/"):
            return True
        return False

    def newProject(self, projectName, userName):
        file = open(self.defaultPath + projectName + self.defaultExtension,"w", encoding='utf-8')
        # file.write(userName + "\n1\n" + userName + "\n/\n-1\n")
        # file.write("1 #ff0000 Comment_1\n2 #00ff00 Comment_2")
        # file.flush()

        self.users = [[userName, "/", -1]]
        self.currUser = self.users[0]
        self.currUserID = 0
        self.labels = [["Comment_1", "#ff0000"], ["Comment_2", "#00ff00"]]
        file.close

        self.projectPath = self.appPath + "/" + self.defaultPath + projectName + self.defaultExtension
        self.updateLastProject()

        json.dump(self.__getstate__(), file, indent=4)

    def updateLastProject(self):
        file = open("settings","w", encoding='utf-8')
        # file.write(self.projectPath)
        # file.flush()
        json.dump(self.projectPath, file, indent=4)
        file.close

    def updateProjectPath(self, path):
        self.projectPath = path
        self.updateLastProject()

    def getLastImagePath(self):
        return self.lastImagePath

    def openImage(self, path = None):
        if(path == None):
            self.images = [(Image.open(self.currUser[1]))]
        else:
            self.images = [Image.open(path)]

        self.masks = [ (self.createMask(self.images[0].size) ) ]
        self.annotation = [(self.createAnnotation(self.images[0].size))]
            
        #self.currImg = -1
        self.currImgID = 0
        self.users[ self.currUserID ][1] = self.imagePaths
        self.users[ self.currUserID ][2] = -1
        self.currUser = self.users[ self.currUserID ]

        self.resetImgScale()

        #self.saveProject()

    def openBatch(self, path = None):
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
                self.images = []
                self.masks = []
                self.annotation = []
                
                if(path == None):
                    self.currImgID = int(self.currUser[2])
                    path = self.currUser[1]
                else:
                    self.currImgID = 0
                
                limpar = 0

            self.images.append(Image.open(path + "/" + filename))

            self.masks.append(self.createMask(self.images[-1].size) )
            self.annotation.append(self.createAnnotation(self.images[-1].size))
            self.imagePaths.append(path + "/" + filename)

        self.lastBatchPath = path

        self.users[ self.currUserID ][1] = path
        self.users[ self.currUserID ][2] = 0
        self.currUser = self.users[ self.currUserID ]

        self.resetImgScale()

        #self.saveProject()

        return limpar

    def saveProject(self, path = None):
        if path == None:
            file = open(self.projectPath,"w", encoding='utf-8')
        else:
            file = open(path,"w", encoding='utf-8')

        # file.write(self.currUser[0] + "\n%d\n" %(len(self.users)) )
        #
        # for i in range(len(self.users)):
        #     file.write("%s\n%s\n%d\n" %( self.users[i][0], self.users[i][1], self.users[i][2] ) )
        #
        # for i in range(len(self.labels)):
        #     file.write("%d %s %s\n" %( i+1, self.labels[i][1], self.labels[i][0] ) )
        #
        # file.flush()

        json.dump(self.__getstate__(), file, indent=4)
        file.close()

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


    def setSelectedLb(self, key):
        self.selectedLb = key

    def getSelectedLb(self):
        return self.selectedLb

    def getCurrImgResize(self, size):
        img = self.images[ self.currImgID ]
        newImg = ImageTk.PhotoImage(img.resize(size))
        return newImg

    def getCurrMaskResize(self,size):
        img = self.masks [ self.currImgID ]
        newImg = ImageTk.PhotoImage(img.resize(size))
        return newImg

    def increaseImgScale(self):
        # newScale = self.imgScale + self.scaleRate

        newScale = self.currScale + 1

        if( newScale >= len(self.imgScale)):
            return False
        
        self.currScale = newScale
        return True

    def decreaseImgScale(self):
        # newScale = self.imgScale - self.scaleRate
        newScale = self.currScale - 1
        if( newScale < 0):
            return False
        
        self.currScale = newScale
        return True

    def getImgScale(self):
        return self.imgScale[self.currScale]

    def resetImgScale(self):
        self.currScale = self.imgScale.index(1)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['images']
        del state['imagePaths']
        del state['masks']
        del state['annotation']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)