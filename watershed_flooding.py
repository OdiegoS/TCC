import cv2
import operator
import numpy as np
import progressBar as pb

from PIL import Image


class Watershed(object):
   
   def __init__(self):
      self.kernel = np.ones((3, 3), np.uint8) # Definindo janela 3x3 de valores 1 para ser utilizado no gradiente morfológico
      # Definições do kernel 3x3 do eixo X e Y para o Sobel e do eixo Z para o Sobel 3D
      self.kern_x = np.asanyarray(np.array([ [-1, 0, 1],[-2, 0, 2],[-1, 0, 1] ]), np.float32)
      self.kern_y = np.asanyarray(np.array([ [1, 2, 1],[0, 0, 0],[-1, -2, -1] ]), np.float32)
      self.kernel_z = np.asanyarray(np.array([ [1, 2, 1],[2, 4, 2],[1, 2, 1] ]), np.float32)

   
   # Fluxo que calcula o gradiente sobel no eixo Z
   def sobel_z(self, image, idx):

      if(idx == 0): # Se a imagem a ser calcula é a primeira, então a própria imagem é a sua antecessora
         temp_img1 = np.array(image[0])
      else:
         temp_img1 =  np.array(image[idx-1])

      if(idx == (len(image)-1) ): # Se a imagem a ser calcula é a última, então a própria imagem é a sua posterior
         temp_img2 = np.array(image[len(image)-1])
      else:
         temp_img2 = np.array(image[idx+1])

      # Transformando as duas imagens em escala de cinza
      temp_img1 =  cv2.cvtColor(temp_img1, cv2.COLOR_BGR2GRAY)
      temp_img2 =  cv2.cvtColor(temp_img2, cv2.COLOR_BGR2GRAY)

      # Aplicando o kernel Z em cada um das imagens
      grad_1 = cv2.filter2D(temp_img1, cv2.CV_32F, self.kernel_z, None, (-1,-1), 0, cv2.BORDER_REFLECT)
      grad_2 = cv2.filter2D(temp_img2, cv2.CV_32F, self.kernel_z, None, (-1,-1), 0, cv2.BORDER_REFLECT)

      grad = grad_1 - grad_2 # Diferença entre as duas
      grad = np.abs(grad) # Valor absoluto

      return grad

   # Fluxo que calcula o gradiente Sobel 3D
   def sobel3d_grad(self, image, progressBar):
      images_cv = []
      n_progressBar = 100 // len(image) # Calcula o tamanho do intervalo que a barra de progressão irá atualizar por imagem

      for i in range(len(image)):
         temp_img =  np.array(image[i])
         temp_img =  cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)

         gradient_xy = self.sobel_grad(temp_img) # Calculando o gradiente sobel 2D
         if(len(image) > 1): # Se a aplicação carregou mais de uma imagem então é calculado o sobel 3D que é a soma do sobel 2D com o sobel na direção Z
            gradient_z = self.sobel_z(image,i)
            grad = gradient_xy + gradient_z
         else: # Se a aplicação carregou apenas uma imagem, apenas o sobel 2D é calculado
            grad = gradient_xy 
         progressBar.updatingBar(n_progressBar) # Atualizando a barra de progresso por imagem processada
         images_cv.append( Image.fromarray(grad) )

      progressBar.close()
      return images_cv

   # Fluxo que calcula o gradiente do Sobel 2D
   def sobel_grad(self, temp_img):
      grad_x = cv2.filter2D(temp_img, cv2.CV_32F, self.kern_x, None, (-1,-1), 0, cv2.BORDER_REFLECT) # Aplica o kernel X no eixo X da imagem
      grad_y = cv2.filter2D(temp_img, cv2.CV_32F, self.kern_y, None, (-1,-1), 0, cv2.BORDER_REFLECT) # Aplica o Kernel Y no eixo Y da imagem

      # Transformo todos os valores em absoluto
      grad_x = np.abs(grad_x) 
      grad_y = np.abs(grad_y)

      grad = grad_x + grad_y # O Sobel 2D é a soma do gradiente nas duas direções (X e Y)

      return grad

   # Fluxo que calcula o gradiente morfológico
   def morph_grad(self, temp_img):
      grad = cv2.morphologyEx(temp_img, cv2.MORPH_GRADIENT, self.kernel)
      return np.array(grad)

   # Fluxo que calcula o gradiente das imagens passadas como parâmetro
   def gradient(self, progressBar, image, size, tp_grad, peso):
      images_cv = []

      # Chama o fluxo que calcula o Sobel 3D
      if(tp_grad == "Sobel 3D"):
         self.kernel_z = peso * self.kernel_z
         images_cv = self.sobel3d_grad(image, progressBar)
         return images_cv

      if(tp_grad == "Morphological"): # Seta para usar o fluxo do gradiente morfológico
         grad_func = self.morph_grad
      elif(tp_grad == "Sobel"): # Seta para usar o fluxo do gradiente sobel 2D
         grad_func = self.sobel_grad
      else:
         return []
         
      n_progressBar = 100 // len(image) # Calcula o tamanho do intervalo que a barra de progressão irá atualizar por imagem
      for i in image:
         #img_temp = cv2.GaussianBlur( np.array(i), (3, 3), 0)
         temp_img =  np.array(i)
         temp_img =  cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY) # Transforma a imagem em escala de cinza
         gradient = grad_func(temp_img) # Chama o fluxo do gradiente setado
         images_cv.append( Image.fromarray(gradient) )
         progressBar.updatingBar(n_progressBar) # Atualiza a barra de progresso

      return images_cv

   # Função que retira da imagem uma subimagem para ser processada pelo algoritmo
   def start(self, images_cv, width, height, x, y, tam, index, dim, progressBar):
      img = []
      
      # Calcula a região da subimagem
      left = max(0, x-tam[0])
      upper = max(0, y-tam[1])
      right = min(width, x+tam[0])
      bottom = min(height, y+tam[1])

      # Verifica os limites no eixo Z
      if( (index - tam[2] >= 0) ):
         z_start = index - tam[2]
         idx = tam[2]
      else:
         z_start = 0
         idx = index 
      z_start = max(0, index - tam[2])
      idx = min(index, tam[2])
      z_end = min(dim, index + tam[2]) + 1

      # Para cada imagem a ser processada é recortado da original o RoI para ser processado
      for i in images_cv[z_start:z_end]:
         img_crop = i.crop( (left, upper, right, bottom) ).convert('L')
         img.append(np.array(img_crop) )

      marker = [min(x, tam[0]), min(y, tam[1]), idx] # Coordenada do pixel onde foi realizado o clique do mouse
      size = img_crop.size # Tamanho da subimagem

      return  self.watershed(img, len(img), size[0], size[1], marker, progressBar)

   # Algoritmo que calcula o watershed da imagem passada por parâmetro através de marcadores
   def watershed (self, image, qtd, width, height, marker, progressBar):
      self.HFQ = [] # Fila para controlar pixels que ainda não foram verificados
      self.L = np.zeros((qtd, width, height), np.int32) # Imagem que o algoritmo watershed irá gerar o resultado
      lista = [[] for _ in range(qtd)] # Lista que irá armazenar os pixels marcados

      # Inicialmente é colocado na imagem o pixel onde foi realizado o clique que é o centro da subimagem
      self.L [marker[2]] [marker[0]] [marker[1]] = 1
      self.HFQ.append( [ (marker[0], marker[1]), 0 , marker[2]] )
      lista[marker[2]].append( [marker[0], marker[1]])

      # O segundo marcador irá abranger todos os pixels que fazem parte do limite da região
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

      while len(self.HFQ) > 0: # O algoritmo irá executar enquando a fila tiver itens
         flag = False # Flag para verificar se houve inserção para ordenar a fila
         p = self.outHFQ() # Retira um elemento da fila
         for pixels in self.neighbors(width, height, ( p[0][0], p[0][1] ) ): # Para cada pixel vizinho a esse elemento...
            # É verificado se está dentro dos limites da imagem
            if( (self.L [p[2]] [pixels[0]] [pixels[1]] == 0) and (pixels[1] >= 0 and pixels[1] < width) and (pixels[0] >= 0 and pixels[0] < height) ):
               self.L [p[2]] [pixels[0]] [pixels[1]] = self.L [p[2]] [p[0][0]] [p[0][1]] # Replica o marcador do pixel inicial do loop com o verificado
               self.inHFQ( (pixels[0], pixels[1]), image[p[2]][pixels[1]][pixels[0]], p[2]) # Insere o pixel verificado na fila
               flag = True
               if(self.L [p[2]] [p[0][0]] [p[0][1]] == 1): # Se o pixel verificado for uma inundação do marcador central
                  lista[p[2]].append([pixels[0], pixels[1]]) # Insere na lista da marcação realizada pelo clique
         
         if(p[2] > 0): # Verifica se existe uma dimensão a frente
            # Valida se está dentro dos limites
            if( (self.L [p[2]-1] [p[0][0]] [p[0][1]] == 0) and (pixels[1] >= 0 and pixels[1] < width) and (pixels[0] >= 0 and pixels[0] < height) ):
               self.L [p[2]-1] [p[0][0]] [p[0][1]] = self.L [p[2]] [p[0][0]] [p[0][1]] # Replica o marcador do pixel inicial do loop com o verificado
               self.inHFQ( (p[0][0], p[0][1]), image[p[2]][p[0][0]][p[0][1]], p[2] - 1) # Insere o pixel verificado na fila
               flag = True
               if(self.L [p[2]-1] [p[0][0]] [p[0][1]] == 1): # Se o pixel verificado for uma inundação do marcador central
                  lista[p[2]-1].append([p[0][0], p[0][1]]) # Insere na lista da marcação realizada pelo clique

         if( p[2] < (qtd-1) ): # Verifica se existe uma dimensão atrás
            # Valida se está dentro dos limites
            if( (self.L [p[2]+1] [p[0][0]] [p[0][1]] == 0) and (pixels[1] >= 0 and pixels[1] < width) and (pixels[0] >= 0 and pixels[0] < height) ):
               self.L [p[2]+1] [p[0][0]] [p[0][1]] = self.L [p[2]] [p[0][0]] [p[0][1]] # Replica o marcador do pixel inicial do loop com o verificado
               self.inHFQ( (p[0][0], p[0][1]), image[p[2]][p[0][0]][p[0][1]], p[2] + 1) # Insere o pixel verificado na fila
               flag = True
               if(self.L [p[2]+1] [p[0][0]] [p[0][1]] == 1): # Se o pixel verificado for uma inundação do marcador central
                  lista[p[2]+1].append([p[0][0], p[0][1]]) # Insere na lista da marcação realizada pelo clique
         if(flag):
            self.sortHFQ()
         progressBar.updatingBar() # Atualiza a barra de progressão
      return lista

   # Calcula as coordenadas dos vizinhos de um pixel passado por parâmetro
   def neighbors(self, width, height, pixel):
      return np.mgrid[
            max(0, pixel[0] - 1):min(width, pixel[0] + 2),
            max(0, pixel[1] - 1):min(height, pixel[1] + 2)
         ].reshape(2, -1).T

   # Ordena a fila
   def sortHFQ(self):
      self.HFQ.sort(key=operator.itemgetter(1))

   # Inserir um elemento no final da fila
   def inHFQ(self, pixels, prio, index):
      self.HFQ.append([pixels, prio, index])

   # Remove o primeiro elemento da fila
   def outHFQ(self):
      element = self.HFQ[0]
      del self.HFQ[0]
      return element