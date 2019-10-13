import numpy as np
from PIL import Image
from PIL import ImageFilter
from PIL import ImageChops
from imageio import imwrite
import sys
import matplotlib.pyplot as plt
from skimage import filters
from scipy import ndimage
import time
import cv2
import operator


class Watershed(object):

   def __init__(self):
      self.kernel = np.ones((3,3), np.uint8)
      
   def dilate_images(self, image, size):
      self.images_cv = []
      for i in image:
         temp_img =  np.array(i)
         gradient = cv2.morphologyEx(temp_img, cv2.MORPH_GRADIENT, self.kernel)
         self.images_cv.append( Image.fromarray(np.array(gradient)) )

      self.vizinhos = [[0 for y in range(size)] for x in range(size) ] 
      for x in range(size):
         for y in range(size):
            self.vizinhos[x][y] = self.neighbors(size, size, (x,y))

   def start(self, width, height, x, y, tam, index):
      img = []
      
      left = max(0, x-tam)
      upper = max(0, y-tam)
      right = min(width, x+tam)
      bottom = min(height, y+tam)

      for i in self.images_cv:
         img_crop = i.crop( (left, upper, right, bottom) ).convert('L')
         img.append(np.array(img_crop) )

      marker = [min(y, tam), min(x, tam), index]
      size = img_crop.size

      return  self.watershed(img, len(img), size[0], size[1], marker)

   def watershed (self, image, qtd, width, height, marker):
      self.HFQ = []
      self.L = np.zeros((qtd, height, width), np.int32)
      lista = [[] for _ in range(qtd)]

      self.L [marker[2]] [marker[0]] [marker[1]] = 1
      self.HFQ.append( [ (marker[0], marker[1]), 0 , marker[2]] )
      lista[marker[2]].append( [marker[0], marker[1]])

      for k in range(width):
         self.L [marker[2]] [0] [k] = 2
         self.HFQ.append( [ (0, k), 0, marker[2]] )
         self.L [marker[2]] [height-1] [k] = 2
         self.HFQ.append( [ (height-1, k), 0, marker[2]] )

      for k in range(height):
         self.L [marker[2]] [k] [0] = 2
         self.HFQ.append( [ (k, 0), 0, marker[2]] )
         self.L [marker[2]] [k] [width-1] = 2
         self.HFQ.append( [ (k, width-1), 0, marker[2]] )
      #sort = 0
      #self.inicio = time.time()
      flag = False
      while len(self.HFQ) > 0:
         flag = False
         p = self.outHFQ()
         for pixels in self.vizinhos[p[0][0]][p[0][1]]:
            if( (self.L [p[2]] [pixels[0]] [pixels[1]] == 0) and (pixels[0] >= 0 and pixels[0] <= height) and (pixels[1] >= 0 and pixels[1] <= width) ):
               self.L [p[2]] [pixels[0]] [pixels[1]] = self.L [p[2]] [p[0][0]] [p[0][1]]
               self.inHFQ( (pixels[0], pixels[1]), image[p[2]][pixels[0]][pixels[1]], p[2])
               flag = True
               if(self.L [p[2]] [p[0][0]] [p[0][1]] == 1):
                  lista[p[2]].append([pixels[1], pixels[0]])
         if(p[2] > 0):
            if( (self.L [p[2]-1] [p[0][0]] [p[0][1]] == 0) and (pixels[0] >= 0 and pixels[0] <= height) and (pixels[1] >= 0 and pixels[1] <= width) ):
               self.L [p[2]-1] [p[0][0]] [p[0][1]] = self.L [p[2]] [p[0][0]] [p[0][1]]
               self.inHFQ( (p[0][0], p[0][1]), image[p[2]][p[0][0]][p[0][1]], p[2] - 1)
               flag = True
               if(self.L [p[2]-1] [p[0][0]] [p[0][1]] == 1):
                  lista[p[2]-1].append([p[0][1], p[0][0]])
         if( p[2] < (qtd-1) ):
            if( (self.L [p[2]+1] [p[0][0]] [p[0][1]] == 0) and (pixels[0] >= 0 and pixels[0] <= height) and (pixels[1] >= 0 and pixels[1] <= width) ):
               self.L [p[2]+1] [p[0][0]] [p[0][1]] = self.L [p[2]] [p[0][0]] [p[0][1]]
               self.inHFQ( (p[0][0], p[0][1]), image[p[2]][p[0][0]][p[0][1]], p[2] + 1)
               flag = True
               if(self.L [p[2]+1] [p[0][0]] [p[0][1]] == 1):
                  lista[p[2]+1].append([p[0][1], p[0][0]])
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
            max(0, pixel[0] - 1):min(height, pixel[0] + 2),
            max(0, pixel[1] - 1):min(width, pixel[1] + 2)
         ].reshape(2, -1).T

   def sortHFQ(self):
      self.HFQ.sort(key=operator.itemgetter(1))

   def inHFQ(self, pixels, prio, index):
      self.HFQ.append([pixels, prio, index])

   def outHFQ(self):
      element = self.HFQ[0]
      del self.HFQ[0]
      return element