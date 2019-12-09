import numpy as np
from PIL import Image
from PIL import ImageFilter
from PIL import ImageChops
from imageio import imwrite
import sys
import time
import cv2
import operator
from copy import deepcopy
import os


class Watershed(object):

   def __init__(self):
      #self.kernel = np.ones((3,3), np.uint8)
      self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))

   def loadGradient(self):
      path = "Teste"
      images_ext = [".jpg",".gif",".png",".tiff"]

      listFiles = os.listdir(path)
      listFiles.sort()
      for filename in listFiles:
         ext = os.path.splitext(filename)[1]
         if ext.lower() not in images_ext:
            continue
         self.images_cv.append(Image.open(path + "/" + filename))

   def saveTestGradients(self, temp_img):
      kern_x = np.array([ [-1,0, 1],[-2,0,2],[-1,0,1] ])
      kern_y = np.array([ [1, 2, 1],[0,0,0],[-1,-2,-1] ])
      grad_x = cv2.filter2D(temp_img, -1, kern_x)
      grad_y = cv2.filter2D(temp_img, -1, kern_y)
      grad = cv2.addWeighted(grad_x, 1, grad_y, 1, 0)
      k = Image.fromarray(np.array(grad)).save("Teste/{}_sobel_test.png".format(len(self.images_cv)-1))

      # for tamK in [3,5,7,9]:
      #    kern = cv2.getStructuringElement(cv2.MORPH_RECT,(tamK, tamK))
      #    grad = cv2.morphologyEx(temp_img, cv2.MORPH_GRADIENT, kern)
      #    k = Image.fromarray(np.array(grad)).save("Teste/Morphology/Rect/{}/{}_{}x{}_morph_rect.png".format(tamK, len(self.images_cv)-1, tamK, tamK))

      #    kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(tamK, tamK))
      #    grad = cv2.morphologyEx(temp_img, cv2.MORPH_GRADIENT, kern)
      #    k = Image.fromarray(np.array(grad)).save("Teste/Morphology/Ellipse/{}/{}x{}_morph_ellip.png".format(tamK, len(self.images_cv)-1, tamK, tamK))

      #    kern = cv2.getStructuringElement(cv2.MORPH_CROSS,(tamK, tamK))
      #    grad = cv2.morphologyEx(temp_img, cv2.MORPH_GRADIENT, kern)
      #    k = Image.fromarray(np.array(grad)).save("Teste/Morphology/Cross/{}/{}x{}_morph_cross.png".format(tamK, len(self.images_cv)-1, tamK, tamK))

      #    ddepth = cv2.CV_16S
      #    grad = cv2.Laplacian(temp_img,ddepth, ksize=tamK)
      #    k = Image.fromarray(cv2.convertScaleAbs(np.array(grad))).save("Teste/Laplacian/{}/{}_{}x{}_lapla.png".format(tamK, len(self.images_cv)-1, tamK, tamK))
   
      #    grad = cv2.Sobel(temp_img,ddepth, 1, 0, ksize=tamK)
      #    k = Image.fromarray(cv2.convertScaleAbs(np.array(grad))).save("Teste/Sobel/x/{}/{}_{}x{}_sobel_x.png".format(tamK, len(self.images_cv)-1, tamK, tamK))

      #    grad = cv2.Sobel(temp_img,ddepth, 0, 1, ksize=tamK)
      #    k = Image.fromarray(cv2.convertScaleAbs(np.array(grad))).save("Teste/Sobel/y/{}/{}_{}x{}_sobel_y.png".format(tamK, len(self.images_cv)-1, tamK, tamK))

      #    grad = cv2.Sobel(temp_img,ddepth, 1, 1, ksize=tamK)
      #    k = Image.fromarray(cv2.convertScaleAbs(np.array(grad))).save("Teste/Sobel/xy/{}/{}_{}x{}_sobel_xy.png".format(tamK, len(self.images_cv)-1, tamK, tamK))
      
   def dilate_images(self, image, size):
      self.images_cv = []

      # self.loadGradient()
      # return

      #(image[0].convert('L')).save("Teste/Teste_gray.png")

      for i in image:
         #img_temp = cv2.GaussianBlur( np.array(i), (3, 3), 0)
         img_temp = np.array(i)
         temp_img =  cv2.cvtColor(  img_temp, cv2.COLOR_BGR2GRAY)
         #temp_img = img_temp
         gradient = cv2.morphologyEx( temp_img, cv2.MORPH_GRADIENT, self.kernel)
         k = Image.fromarray(np.array(gradient))
         self.images_cv.append( k )
         self.saveTestGradients(temp_img)
         
   def start(self, width, height, x, y, tam, index, dim):
      img = []
      
      left = max(0, x-tam[0])
      upper = max(0, y-tam[1])
      right = min(width, x+tam[0])
      bottom = min(height, y+tam[1])

      if( (index - tam[2] >= 0) ):
         z_start = index - tam[2]
         idx = tam[2]
      else:
         z_start = 0
         idx = index 
      z_start = max(0, index - tam[2])
      idx = min(index, tam[2])
      z_end = min(dim, index + tam[2]) + 1

      for i in self.images_cv[z_start:z_end]:
         img_crop = i.crop( (left, upper, right, bottom) ).convert('L')
         img.append(np.array(img_crop) )

      marker = [min(x, tam[0]), min(y, tam[1]), idx]
      size = img_crop.size

      return  self.watershed(img, len(img), size[0], size[1], marker)

   def watershed (self, image, qtd, width, height, marker):
      self.HFQ = []
      self.L = np.zeros((qtd, width, height), np.int32)
      lista = [[] for _ in range(qtd)]

      self.L [marker[2]] [marker[0]] [marker[1]] = 1
      self.HFQ.append( [ (marker[0], marker[1]), 0 , marker[2]] )
      lista[marker[2]].append( [marker[0], marker[1]])

      for k in range(height):
         self.L [marker[2]] [0] [k] = 2
         self.HFQ.append( [ (0, k), 0, marker[2]] )
         self.L [marker[2]] [width-1] [k] = 2
         self.HFQ.append( [ (width-1, k), 0, marker[2]] )

      for k in range(width):
         self.L [marker[2]] [k] [0] = 2
         self.HFQ.append( [ (k, 0), 0, marker[2]] )
         self.L [marker[2]] [k] [height-1] = 2
         self.HFQ.append( [ (k, height-1), 0, marker[2]] )
      #sort = 0
      #self.inicio = time.time()
      flag = False
      while len(self.HFQ) > 0:
         flag = False
         p = self.outHFQ()
         #for pixels in self.vizinhos[p[0][0]][p[0][1]]:
         for pixels in self.neighbors(width, height, ( p[0][0], p[0][1] ) ):
            if( (self.L [p[2]] [pixels[0]] [pixels[1]] == 0) and (pixels[1] >= 0 and pixels[1] < width) and (pixels[0] >= 0 and pixels[0] < height) ):
               self.L [p[2]] [pixels[0]] [pixels[1]] = self.L [p[2]] [p[0][0]] [p[0][1]]
               self.inHFQ( (pixels[0], pixels[1]), image[p[2]][pixels[1]][pixels[0]], p[2])
               flag = True
               if(self.L [p[2]] [p[0][0]] [p[0][1]] == 1):
                  lista[p[2]].append([pixels[0], pixels[1]])
         if(p[2] > 0):
            if( (self.L [p[2]-1] [p[0][0]] [p[0][1]] == 0) and (pixels[1] >= 0 and pixels[1] < width) and (pixels[0] >= 0 and pixels[0] < height) ):
               self.L [p[2]-1] [p[0][0]] [p[0][1]] = self.L [p[2]] [p[0][0]] [p[0][1]]
               self.inHFQ( (p[0][0], p[0][1]), image[p[2]][p[0][0]][p[0][1]], p[2] - 1)
               flag = True
               if(self.L [p[2]-1] [p[0][0]] [p[0][1]] == 1):
                  lista[p[2]-1].append([p[0][0], p[0][1]])
         if( p[2] < (qtd-1) ):
            if( (self.L [p[2]+1] [p[0][0]] [p[0][1]] == 0) and (pixels[1] >= 0 and pixels[1] < width) and (pixels[0] >= 0 and pixels[0] < height) ):
               self.L [p[2]+1] [p[0][0]] [p[0][1]] = self.L [p[2]] [p[0][0]] [p[0][1]]
               self.inHFQ( (p[0][0], p[0][1]), image[p[2]][p[0][0]][p[0][1]], p[2] + 1)
               flag = True
               if(self.L [p[2]+1] [p[0][0]] [p[0][1]] == 1):
                  lista[p[2]+1].append([p[0][0], p[0][1]])
         #sort_i = time.time()
         if(flag):
            self.sortHFQ()
         #sort_f = time.time()
         #sort = sort + (sort_f - sort_i)
      #self.fim = time.time()
      #geral = (self.fim - self.inicio) - sort
      #print("Tempo do sort: {}\nTempo do resto: {}\n####################\nTempo do sort: {}\nTempo do resto: {}".format(sort,geral,sort/60,geral/60))
      return lista

   def neighbors(self, width, height, pixel):
      return np.mgrid[
            max(0, pixel[0] - 1):min(width, pixel[0] + 2),
            max(0, pixel[1] - 1):min(height, pixel[1] + 2)
         ].reshape(2, -1).T

   def sortHFQ(self):
      self.HFQ.sort(key=operator.itemgetter(1))

   def inHFQ(self, pixels, prio, index):
      self.HFQ.append([pixels, prio, index])

   def outHFQ(self):
      element = self.HFQ[0]
      del self.HFQ[0]
      return element