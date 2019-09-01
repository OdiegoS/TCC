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
      self.HFQ = []
      
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

   def neighbors(self, width, height, pixel):
      return np.mgrid[
            max(0, pixel[0] - 1):min(height, pixel[0] + 2),
            max(0, pixel[1] - 1):min(width, pixel[1] + 2)
         ].reshape(2, -1).T

   def inHFQ(self, pixels, prio):
      self.HFQ.append([pixels, prio])
      self.HFQ.sort(key=lambda k: (k[1], -k[1]))

   def outHFQ(self):
      element = self.HFQ[0]
      del self.HFQ[0]
      return element

'''
if __name__ == "__main__":
   
   w = Watershed()
   img = Image.open("demo-wsh.png").convert('L')
   img2 = Image.open("demo-wsh.png").convert('RGBA')
   img3 = Image.open("demo-wsh.png").convert('RGBA')

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

   image = w.watershed(gradient, size[0], size[1], cent)

   for h in range(size[1]):
      for w in range(size[0]):
         color = img3.getpixel((h,w))
         color = list(color)
         color[3] = 0
         img3.putpixel((h,w), tuple(color) )

   for l in image:
      color = (255,0,0,40)
      img3.putpixel( (l[1],l[0]), color )

   img2.paste(img3, (0, 0), img3)

   #img2.save("demo-wsh_result.png")

   plt.imshow(img2)
   plt.show()
'''