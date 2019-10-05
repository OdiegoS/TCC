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

   def start_3D(self, width, height, x, y, tam, index):
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

      return  self.watershed_3D(img, len(img), size[0], size[1], marker)
      
   def start(self, image, width, height, x, y, tam):
      img = image.crop( (max(0, x-tam), max(0, y-tam), min(width, x+tam), min(height, y+tam)) )
      cent = [min(y, tam), min(x, tam)]
      size = img.size
      img = img.convert('L')

      kernel = np.ones((3,3), np.uint8)

      img = np.array(img) 
      gradient = cv2.morphologyEx(img,cv2.MORPH_GRADIENT, kernel)
      image = np.array(gradient)

      return  self.watershed(image, size[0], size[1], cent)

   def watershed (self, image, width, height, cent):
      self.L = np.zeros((height, width), np.int32)
      lista = []
      
      self.L[cent[0]][cent[1]] = 1
      self.HFQ.append([(cent[0],cent[1]), 0])
      lista.append([cent[1],cent[0]])

      for k in range(width):
         self.L[0][k] = 2
         self.HFQ.append([(0,k), 0])
         self.L[height-1][k] = 2
         self.HFQ.append([(height-1,k), 0])

      for k in range(height):
         self.L[k][0] = 2
         self.HFQ.append([(k,0), 0])
         self.L[k][width-1] = 2
         self.HFQ.append([(k,width-1), 0])
      
      while len(self.HFQ) > 0:
         p = self.outHFQ()
         vizinhos = self.neighbors(width, height, p[0])
         for pixels in vizinhos:
            if(self.L[pixels[0]][pixels[1]] == 0):
               self.L[pixels[0]][pixels[1]] = self.L[p[0][0]][p[0][1]]
               self.inHFQ(pixels, image[pixels[0]][pixels[1]])
               if(self.L[p[0][0]][p[0][1]] == 1):
                  lista.append([pixels[1], pixels[0]])

      return lista

   def watershed_3D (self, image, qtd, width, height, marker):
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
      
      flag = False
      while len(self.HFQ) > 0:
         flag = False
         p = self.outHFQ()
         for pixels in self.vizinhos[p[0][0]][p[0][1]]:
            if( (self.L [p[2]] [pixels[0]] [pixels[1]] == 0) and (pixels[0] >= 0 and pixels[0] <= height) and (pixels[1] >= 0 and pixels[1] <= width) ):
               self.L [p[2]] [pixels[0]] [pixels[1]] = self.L [p[2]] [p[0][0]] [p[0][1]]
               self.inHFQ_3D( (pixels[0], pixels[1]), image[p[2]][pixels[0]][pixels[1]], p[2])
               flag = True
               if(self.L [p[2]] [p[0][0]] [p[0][1]] == 1):
                  lista[p[2]].append([pixels[1], pixels[0]])
         if(p[2] > 0):
            if( (self.L [p[2]-1] [p[0][0]] [p[0][1]] == 0) and (pixels[0] >= 0 and pixels[0] <= height) and (pixels[1] >= 0 and pixels[1] <= width) ):
               self.L [p[2]-1] [p[0][0]] [p[0][1]] = self.L [p[2]] [p[0][0]] [p[0][1]]
               self.inHFQ_3D( (p[0][0], p[0][1]), image[p[2]][p[0][0]][p[0][1]], p[2] - 1)
               flag = True
               if(self.L [p[2]-1] [p[0][0]] [p[0][1]] == 1):
                  lista[p[2]-1].append([p[0][1], p[0][0]])
         if( p[2] < (qtd-1) ):
            if( (self.L [p[2]+1] [p[0][0]] [p[0][1]] == 0) and (pixels[0] >= 0 and pixels[0] <= height) and (pixels[1] >= 0 and pixels[1] <= width) ):
               self.L [p[2]+1] [p[0][0]] [p[0][1]] = self.L [p[2]] [p[0][0]] [p[0][1]]
               self.inHFQ_3D( (p[0][0], p[0][1]), image[p[2]][p[0][0]][p[0][1]], p[2] + 1)
               flag = True
               if(self.L [p[2]+1] [p[0][0]] [p[0][1]] == 1):
                  lista[p[2]+1].append([p[0][1], p[0][0]])
         if(flag):
            self.sortHFQ()
      return lista

   def neighbors(self, width, height, pixel):
      return np.mgrid[
            max(0, pixel[0] - 1):min(height, pixel[0] + 2),
            max(0, pixel[1] - 1):min(width, pixel[1] + 2)
         ].reshape(2, -1).T

   def neighbors_3D(self, width, height, pixel, profundidade, qtde):
      temp = np.mgrid[
            max(0, pixel[0] - 1):min(height, pixel[0] + 2),
            max(0, pixel[1] - 1):min(width, pixel[1] + 2)
         ].reshape(2, -1).T
      coord = np.full((temp.shape[0],3), profundidade)
      coord[:,:-1] = temp
      temp2 = []
      if(profundidade > 0):
         temp2.append([pixel[0], pixel[1], profundidade - 1])
      if(profundidade < (qtde - 1) ):
         temp2.append([pixel[0], pixel[1], profundidade + 1])
      return np.append(coord, temp2, 0)

   def inHFQ(self, pixels, prio):
      self.HFQ.append([pixels, prio])
      self.HFQ.sort(key=lambda k: (k[1], -k[1]))
      
   def sortHFQ(self):
      self.HFQ.sort(key=lambda k: (k[1], -k[1]))

   def inHFQ_3D(self, pixels, prio, index):
      self.HFQ.append([pixels, prio, index])

   def outHFQ(self):
      element = self.HFQ[0]
      del self.HFQ[0]
      return element

'''
if __name__ == "__main__":
   
   w = Watershed()
   img = Image.open("a12AL1_000.jpg").convert('L')
   #img = Image.open("demo-wsh.png").convert('L')
   #img2 = Image.open("demo-wsh.png").convert('RGBA')
   #img3 = Image.open("demo-wsh.png").convert('RGBA')
   
   cent = [50, 50]
   size = img.size
   img = np.array(img) 
   ksize = 3
   kernel = np.ones((ksize,ksize), np.uint8)
   gradient = cv2.morphologyEx(img,cv2.MORPH_GRADIENT, kernel)

   #gradient = cv2.Laplacian(img, cv2.CV_64F, ksize = ksize)
   #gradient = np.uint8(np.absolute( cv2.Laplacian(img, cv2.CV_64F, ksize = ksize) ))
   #gradient = np.int32(np.absolute( cv2.Laplacian(img, cv2.CV_64F, ksize = ksize) ))  #ksize 7
   
   #gradient = cv2.Sobel(img,cv2.CV_64F,1,0,ksize= ksize)
   #gradient = np.uint8(np.absolute( cv2.Sobel(img,cv2.CV_64F,1,0,ksize= ksize) ))
   #gradient = np.int32(np.absolute( cv2.Sobel(img,cv2.CV_64F,1,0,ksize= ksize) )) #ksize 7,9,11,13,15

   #gradient = cv2.Sobel(img,cv2.CV_64F,0,1,ksize= ksize)
   #gradient = np.uint8(np.absolute( cv2.Sobel(img,cv2.CV_64F,0,1,ksize= ksize) ))
   #gradient = np.int32(np.absolute( cv2.Sobel(img,cv2.CV_64F,0,1,ksize= ksize) )) #ksize 9
   
   #gradient = cv2.Sobel(img,cv2.CV_64F,1,1,ksize= ksize)
   #gradient = np.uint8(np.absolute( cv2.Sobel(img,cv2.CV_64F,0,1,ksize=ksize) ))
   #gradient = np.int32(np.absolute( cv2.Sobel(img,cv2.CV_64F,0,1,ksize=ksize) )) #ksize 9
'''
'''
   image = w.watershed(gradient, size[0], size[1], cent)

   for h in range(size[1]):
      for w in range(size[0]):
         color = img3.getpixel((h,w))
         color = list(color)
         color[3] = 0
         img3.putpixel((h,w), tuple(color) )

   for l in image:
      color = (255,255,255,20)
      img3.putpixel( (l[1],l[0]), color )

   img2.paste(img3, (0, 0), img3)

   #img2.save("demo-wsh_result.png")

   plt.imshow(img2)
   plt.show()
'''