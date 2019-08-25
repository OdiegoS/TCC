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


class Watershed(object):

   def __init__(self):
      self.HFQ = []
      
   def start(self, image, width, height, x, y, tam):
      img = image.crop( (max(0, x-tam), max(0, y-tam), min(width, x+tam), min(height, y+tam)) )
      cent = [min(y, tam), min(x, tam)]
      size = img.size
      img = img.convert('L')

      dilate = img.filter(ImageFilter.MaxFilter(3))
      erode = img.filter(ImageFilter.MinFilter(3))

      gradient = ImageChops.difference(dilate, erode)

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

   dilate = img.filter(ImageFilter.MaxFilter(3))
   erode = img.filter(ImageFilter.MinFilter(3))

   gradient = ImageChops.difference(dilate, erode)
   gradient2 = ImageChops.difference(erode, dilate)

   #gradient.show()
   #plt.imshow(gradient)
   #plt.show()
   
   width, height = img.size
   

   image = np.array(gradient)

   start = time.time()
   image = w.start (image, height, width, 50)

   end = time.time()
   print(end - start)
   
   for h in range(height):
      for w in range(width):
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