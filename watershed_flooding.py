import numpy as np
from PIL import Image
from PIL import ImageFilter
from PIL import ImageChops
from imageio import imwrite
import sys
import time
import cv2
import operator
import ProgressBar as pb


class Watershed(object):

   def __init__(self):
      self.kernel = np.ones((3,3), np.uint8)
      self.kern_x = np.asanyarray(np.array([ [-1,0, 1],[-2,0,2],[-1,0,1] ]), np.float32)
      self.kern_y = np.asanyarray(np.array([ [1, 2, 1],[0,0,0],[-1,-2,-1] ]), np.float32)
      self.kernel_z = np.asanyarray(np.array([ [1, 2, 1],[2, 4, 2],[1, 2, 1] ]), np.float32)

   def sobel_grad(self, temp_img):
      grad_x = cv2.filter2D(temp_img, cv2.CV_32F, self.kern_x, None, (-1,-1), 0, cv2.BORDER_REFLECT)
      grad_y = cv2.filter2D(temp_img, cv2.CV_32F, self.kern_y, None, (-1,-1), 0, cv2.BORDER_REFLECT)

      grad_x = np.abs(grad_x)
      grad_y = np.abs(grad_y)

      grad = grad_x + grad_y

      return grad

   def sobel_z(self, image, idx):

      if(idx == 0):
         temp_img1 = np.array(image[0])
      else:
         temp_img1 =  np.array(image[idx-1])

      if(idx == (len(image)-1) ):
         temp_img2 = np.array(image[len(image)-1])
      else:
         temp_img2 = np.array(image[idx+1])

      temp_img1 =  cv2.cvtColor(temp_img1, cv2.COLOR_BGR2GRAY)
      temp_img2 =  cv2.cvtColor(temp_img2, cv2.COLOR_BGR2GRAY)

      grad_1 = cv2.filter2D(temp_img1, cv2.CV_32F, self.kernel_z, None, (-1,-1), 0, cv2.BORDER_REFLECT)
      grad_2 = cv2.filter2D(temp_img2, cv2.CV_32F, self.kernel_z, None, (-1,-1), 0, cv2.BORDER_REFLECT)

      # grad_1 = np.abs(grad_1)
      # grad_2 = np.abs(grad_2)
      # grad = grad_1 - grad_2

      grad = grad_1 - grad_2
      grad = np.abs(grad)

      return grad

   def sobel3d_grad(self, image, progressBar):
      images_cv = []

      n_progressBar = 100 // len(image)
      for i in range(len(image)):
         temp_img =  np.array(image[i])
         temp_img =  cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)

         gradient_xy = self.sobel_grad(temp_img)
         if(len(image) > 1):
            gradient_z = self.sobel_z(image,i)
            grad = gradient_xy + gradient_z
         else:
            grad = gradient_xy
         progressBar.updatingBar(n_progressBar)

         images_cv.append( Image.fromarray(grad) )
      progressBar.close()
      return images_cv

   def morph_grad(self, temp_img):
      grad = cv2.morphologyEx(temp_img, cv2.MORPH_GRADIENT, self.kernel)
      return np.array(grad)

   def dilate_images(self, tk_main, image, size, tp_grad, peso):
      images_cv = []

      progressBar = pb.ProgressBar(tk_main)

      if(tp_grad == "Morphological"):
         grad_func = self.morph_grad
      elif(tp_grad == "Sobel"):
         grad_func = self.sobel_grad
      elif(tp_grad == "Sobel 3D"):
         self.kernel_z = peso * self.kernel_z
         images_cv = self.sobel3d_grad(image, progressBar)
         return images_cv

      n_progressBar = 100 // len(image)
      for i in image:
         #img_temp = cv2.GaussianBlur( np.array(i), (3, 3), 0)
         temp_img =  np.array(i)
         temp_img =  cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)
         gradient = grad_func(temp_img)
         images_cv.append( Image.fromarray(gradient) )
         progressBar.updatingBar(n_progressBar)

      progressBar.close()

      # self.vizinhos = [[0 for y in range(size)] for x in range(size) ] 
      # for x in range(size):
      #    for y in range(size):
      #       self.vizinhos[x][y] = self.neighbors(size, size, (x,y))

      return images_cv

   def start(self, images_cv, width, height, x, y, tam, index, dim, progressBar):
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

      for i in images_cv[z_start:z_end]:
         img_crop = i.crop( (left, upper, right, bottom) ).convert('L')
         img.append(np.array(img_crop) )

      marker = [min(x, tam[0]), min(y, tam[1]), idx]
      size = img_crop.size

      return  self.watershed(img, len(img), size[0], size[1], marker, progressBar)

   def watershed (self, image, qtd, width, height, marker, progressBar):
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
         progressBar.updatingBar()
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