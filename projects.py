# -*- coding: utf-8 -*

'''
######## TODO ###########

self.lastImagePath -> está sem utilidade

fazer a ação sobre do menu

#########################
'''

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

        self.watershed = Watershed()
        
        self.IMG_SCALE = [0.125, 0.25, 0.5, 1, 2, 4, 8] # lista com as escalas disponíveis para zoom in/out
        self.currScale = self.IMG_SCALE.index(1) # salva o index onde a escala 1 está

        self.appPath = os.path.dirname(os.path.realpath(__file__)) + "/" # diretório onde o programa está localizado
        self.defaultPath = "Projects/"
        self.defaultExtension = ".neuronote"
        
        self.wradius = [50, 50, 2, "#000000"] #configuração da região de interesse
        self.gradientOptions = ["Morphological", "Sobel", "Sobel 3D"]
        self.grad = "Morphological"
        self.sobel3_peso = 1/16
        
        # Declarações de variáveis utilizadas pelo programa com valores vazios
        self.imagePaths = None # Diretório das imagens carregadas
        self.projectPath = None # Diretório do projeto atual
        self.lastImagePath = None # Salva o diretório da última imagem carregada
        self.lastStackPath = None # Salva o diretório onde o último conjunto de imagens foram carregadas

        self.labels = None # Lista com as informações dos rótulos do projeto atual da aplicação
        self.selectedLb = -1 # Guarda a informação de qual rótulo está sendo utilizado no momento
        self.users = None # Lista com as informações dos usuários do projeto atual da aplicação [username, diretorio da imagem, flag se é uma imagem ou stack ]
        self.currUser = None # Contem as informações do usuário atual da aplicação
        self.currUserID = None # Contem o index do usuário atual da aplicação
        
        self.masks = [] # Lista com as máscaras das imagens onde é armazenado as marcações em RGB
        self.masks_clean = [] # Lista com as máscaras das imagens em sua forma original
        self.annotation = [] # Lista com as máscaras das imagens onde é armazenado as marcações em escala de cinza contendo apenas o index do rótulo

        self.images = [] # Lista com as imagens utilizadas para exibição
        self.currImgID = 0 # Contêm o index da imagem atual sendo exibida na aplicação
        self.original_images = [] # Lista contendo as imagens carregadas
        self.gradient_images = [] # Lista contendo os gradientes das imagens carregadas
       
        self.clean = False # Flag para definir se exibe para o usuário a imagem limpa ou com as marcações
        self.grad_show = False # Flag para definir se exibe para o usuário a imagem original ou gradiente
        
        self.openSettings()
        self.createProjectsDir() 

    # Fluxo que retorna todas as variáves da classe com seus valores
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

    # Fluxo que atualiza todas as variáveis da classe através de um array formatado passado por parâmetro
    def __setstate__(self, state):
        self.__dict__.update(state)

    # Carrega o arquivo de configuração da aplicação para pegar o último projeto aberto
    def openSettings(self):
        file = open("settings", encoding='utf-8')
        
        try:
            self.projectPath = json.load(file)
        except ValueError:
            self.projectPath = ""

        file.close()

    # Verifica existência e cria um diretório de projetos para a aplicação
    def createProjectsDir(self):
        if (not os.path.isdir("Projects") ):
            os.makedirs("Projects")

    # Fluxo que inicia a execução do algoritmo de watershed
    def applyWatershed(self, coord, progressBar):
        size = self.getDimensionCurrImg()
        return self.watershed.start(self.gradient_images, size[0], size[1], coord[0], coord[1], self.wradius, self.getCurrImgID(), self.getQtdImage(), progressBar)

################################################################################################
########                                 GLOBALs                                        ########
################################################################################################
    
    #Atualiza o arquivo settings com o diretório do ultimo projeto carregado
    def updateLastProject(self):
        file = open("settings","w", encoding='utf-8')
        json.dump(self.projectPath, file, indent=4)
        file.close

    #Cria uma imagem RGBA com alfa 0 (transparente) do mesmo tamanho das imagens carregadas para salvar as marcações
    def createMask(self, size):
        return Image.new('RGBA', size, (0, 0, 0, 0))

    #Cria uma imagem escala cinza do mesmo tamanho das imagens carregadas para salvar as anotações
    def createAnnotation(self, size):
        return Image.new('L', size, 0)

################################################################################################
########                               Menu Project                                     ########
################################################################################################

    # Fluxo para criar um novo projeto na aplicação
    def newProject(self, projectName, userName):
        self.projectPath = self.appPath + self.defaultPath + projectName + self.defaultExtension # Monta o diretório

        file = open(self.projectPath,"w", encoding='utf-8') # Cria o arquivo do projeto

        # Inicia usuário e rótulos com valores padrões
        self.users = [[userName, "/", -1]]
        self.currUser = self.users[0]
        self.currUserID = 0
        self.labels = [["Comment_1", "#ff0000"], ["Comment_2", "#00ff00"]]

        json.dump(self.__getstate__(), file, indent = 4) # Salva os dados do projeto no arquivo criado
        file.close

        self.updateLastProject()

    # Fluxo para carregar os dados de um projeto
    def loadProject(self):
        file = open(self.projectPath,"r", encoding='utf-8') # Abre o arquivo do projeto
        self.__setstate__(json.load(file)) # Carrega as variáveis da aplicação com os valores do arquivo
        file.close()

    # Fluxo para salvar um projeto
    def saveProject(self, path = None):
        # Se o parâmetro for diferente de None então foi utilizado a opção de Save As
        if path == None:
            path = self.projectPath
            
        file = open(path,"w", encoding='utf-8') # Cria o arquivo
        json.dump(self.__getstate__(), file, indent=4) # Salva os dados no arquivo
        file.close()

    # Fluxo para atualizar os dados de configuração do projeto
    def configure(self, win_x, win_y, win_z, color, gradient, peso = None):
        self.wradius = [win_x, win_y, win_z, color]
        
        if( (self.grad != gradient) or (self.sobel3_peso != peso) ):
            self.grad = gradient
            if(peso != None):
                self.sobel3_peso = float(peso)
            return True
        return False

    # Fluxo que atualiza as imagens gradiente ao modificar o tipo de gradiente utilizado no projeto
    def changeGradient(self, progressBar):
        self.gradient_images = self.watershed.gradient(progressBar,self.original_images, self.wradius, self.grad, self.sobel3_peso)
        
        if(self.grad_show):
            self.images = self.gradient_images
            return True
        return False

################################################################################################
########                               Menu Image                                       ########
################################################################################################

    # Fluxo que preenche as máscaras de acordo com as imagens de anotações carregadas
    def loadMask(self):
        for i in range(len(self.annotation)):
            m = self.getMask(i)
            width, height = self.annotation[i].size
            for x in range(width):
                for y in range(height):
                    pixel_value = self.annotation[i].getpixel((x, y)) # Pega o valor do pixel da anotação que representa o index do rótulo (label)
                    if( (pixel_value > 0) and (pixel_value <= len(self.labels)) ):
                         colorHex = self.getLabel(pixel_value - 1)[1] # Recupera a cor hexadecimal do rótulo dado um index
                         colorRGB = tuple(int(colorHex.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4)) # Transforma a cor hexadecimal em RGB
                         m.putpixel( (x, y), colorRGB ) # Pinta a cor RGB encontradas no pixel verificado
            self.setMask(i, m) # Atualiza a máscara no projeto

    # Fluxo para carregar os dados de anotações do usuário em um projeto
    def loadAnnotation(self):
        if(self.isStackImg()):
            path = self.imagePaths[0]
        else:
            path = self.imagePaths

        # Monta o diretório para ler o arquivo
        pos = [path.replace("\\", "/")[::-1].find("/"), path[::-1].find(".")]
        diretorio = path[:-pos[0]] + "gt_" + self.currUser[0]

        if (not os.path.isdir(diretorio) ):
            return

        images_ext = [".png"]

        listFiles = os.listdir(diretorio) # Pega todos os arquivos no diretorio
        listFiles.sort() # Ordena pelo nome os arquivos
        index = 0 
        self.annotation = [ [] for x in range(len(self.images)) ]
        for filename in listFiles:
            ext = os.path.splitext(filename)[1]
            if ext.lower() not in images_ext: # Verificar se o arquivo tem a extensão .png
                continue
            self.setAnnotation(index, Image.open(diretorio + "/" + filename)) # Carrega a imagem
            index += 1
            if(index >= len(self.images)):
                break

        self.loadMask()

    # Fluxo para abrir apenas uma imagem no projeto
    def openImage(self,  progressBar, path = None):
        if(path == None):
            path = self.currUser[1] # Se não tiver path, então está sendo carregado um novo usuário

        self.original_images = [Image.open(path)] # Carrega a imagem
        image_size = self.original_images[0].size

        self.masks = [ (self.createMask(image_size) ) ] # Cria as máscaras
        self.masks_clean = [ (self.createMask(image_size) ) ] # Cria um segundo conjunto de máscaras
        self.annotation = [ (self.createAnnotation(image_size)) ] # Cria as imagens para salvar as anotações
            
        self.currImgID = 0 # Seta o index para a primeira (e unica) imagem carregada
        self.users[ self.currUserID ][1] = self.imagePaths # Atualiza o camianho da imagem carregada nos dados do usuário
        self.users[ self.currUserID ][2] = -1 # Flag para indicar que está sendo carregado apenas uma imagem
        self.currUser = self.users[ self.currUserID ] # Atualizando o usuário carregado no projeto

        # Fluxo que processa todas as imagens e retorna as imagens gradiente de acordo com as configurações selecionadas
        self.gradient_images = self.watershed.gradient(progressBar, self.original_images, self.wradius, self.grad, self.sobel3_peso)

        if(self.grad_show):
            self.images = self.gradient_images
        else:
            self.images = self.original_images

        self.setImgScale()

    # Fluxo para abrir um conjunto de imagens no projeto
    def openStack(self, progressBar, path = None):
        flag_open = False
        images_ext = [".jpg",".gif",".png",".tiff"]

        currImgID = 0
        if(path == None):
            currImgID = int(self.currUser[2])
            path = self.currUser[1]

        listFiles = os.listdir(path) # Carrega todos os arquivos no diretório path
        listFiles.sort() # Ordena os arquivos
        for filename in listFiles:
            ext = os.path.splitext(filename)[1]
            if ext.lower() not in images_ext: # Verificar os arquivos que fazem parte das extensões utilizadas
                continue
            
            # Limpeza das variáveis na primeira execução
            if not flag_open:
                self.imagePaths = []
                self.original_images = []
                self.gradient_images = []
                self.masks = []
                self.mask_clean = []
                self.annotation = []
                self.currImgID = currImgID
                flag_open = True

            image_path = path + "/" + filename
            self.original_images.append(Image.open(image_path)) # Carrega as imagens

            image_size = self.original_images[-1].size
            self.masks.append( self.createMask(image_size) ) # Cria as máscaras
            self.masks_clean.append( self.createMask(image_size) ) # Cria um segundo conjunto de máscaras
            self.annotation.append( self.createAnnotation(image_size) ) # Cria as imagens para salvar as anotações
            self.imagePaths.append(image_path) # Salva o diretório de cada imagem

        if not flag_open: # Se nenhuma imagem foi encontrada, retorna falso
            return False

        self.lastStackPath = path
        self.users[ self.currUserID ][1] = path # Atualiza o diretório das imagens carregadas nos dados do usuário
        self.users[ self.currUserID ][2] = 0 # Flag para indicar que está sendo carregado um conjunto de imagens
        self.currUser = self.users[ self.currUserID ] # Atualizando o usuário carregado no projeto
        
        # Fluxo que processa todas as imagens e retorna as imagens gradiente de acordo com as configurações selecionadas
        self.gradient_images = self.watershed.gradient(progressBar, self.original_images, self.wradius, self.grad, self.sobel3_peso)

        if(self.grad_show):
            self.images = self.gradient_images
        else:
            self.images = self.original_images

        self.setImgScale()

        return True

################################################################################################
########                               Menu Annotations                                 ########
################################################################################################

    # Limpa as marcações realiza pela aplicação (nas máscaras)
    def clearImage(self):
        del self.masks[:]
        self.masks = deepcopy(self.masks_clean)

    # Fluxo que salva as localizações e indexes das marcações realizadas em um arquivo
    def saveAnnotation(self):
        if(self.isStackImg()):
            path = self.imagePaths[0]
        else:
            path = self.imagePaths

        # Monta o diretório para salvar o arquivo
        pos = [path.replace("\\", "/")[::-1].find("/"), path[::-1].find(".")]
        diretorio = path[:-pos[0]] + "gt_" + self.currUser[0]

        if (not os.path.isdir(diretorio) ):
            os.makedirs(diretorio)

        if (self.isStackImg()):
            qtd_annot = 0
            for imageStack in self.imagePaths:
                self.annotation[qtd_annot].save( diretorio + "/gt_" + imageStack[-pos[0]:-pos[1]] + "png" ) # Salva a imagem anotada
                qtd_annot += 1
        else:
            self.annotation[0].save( diretorio + "/gt_" + self.imagePaths[-pos[0]:-pos[1]] + "png" ) # Salva a imagem anotada

    # Fluxo que realiza a contagem de elementos conexos das imagens do projeto
    def count(self, progressBar):
        count = np.zeros(1000, dtype=int)
        img_temp = deepcopy(self.annotation)

        n_progressBar = 100 // self.getQtdImage() # Divide a barra de progresso pela qtd de imagens

        for z in range(self.getQtdImage()): # Para cada imagem verifica a quantidade de elementos conexos por valor de rótulo (label)
            img = self.getImage(z)
            width, height = img.size

            for x in range(width):
                for y in range(height):
                    label = img_temp[z].getpixel((x,y))

                    if label <= 0: # Pixel que não teve marcação
                        continue

                    array_temp = [ [z,x,y] ]
                    # Percorre, preenche e deleta itens no array temp para encontrar e marcar todos os pixels que fazem parte da mesma região z,x,y
                    while len(array_temp) > 0:
                        z_t = array_temp[0][0]
                        x_t = array_temp[0][1]
                        y_t = array_temp[0][2]

                        if(img_temp[z_t].getpixel((x_t, y_t)) == label):
                            w, h = self.getImage(z_t).size
                            # Verificando se os pixels vizinhos possuem o mesmo valor de label
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

                            img_temp[z_t].putpixel( (x_t,y_t), 0 ) # Setando o pixel verificado como 0 representando que já foi lido
                        del array_temp[0] # Removendo o pixel verificado do array de checks
                        array_temp.sort(key=operator.itemgetter(0))
                    count[label-1] = count[label-1] + 1 # Contabilizando a contagem para o rótulo verificado
            progressBar.updatingBar(n_progressBar) # Atualizando a barra de progresso
        return count

    # Chama o fluxo de contagem das marcações e com o resultado salva os dados em um arquivo
    def exportCount(self, progressBar, export_dir):
        if(self.isStackImg()):
            path = self.imagePaths[0]
        else:
            path = self.imagePaths

        # Monta o diretório para exportar o arquivo
        pos = [path.replace("\\", "/")[::-1].find("/"), path[::-1].find(".")]
        img_dir = path[:-pos[0]]

        total_count = 0
        count_t = self.count(progressBar)

        export_file = open(export_dir,"w", encoding='utf-8')

        # Escreve os dados no arquivo
        export_file.write("## File generated by Neuronote Software\n")
        export_file.write("## Avaliable from https://github.com/OdiegoS/TCC\n")
        export_file.write("##\n")
        export_file.write("# User: {}\n".format(self.currUser[0]) )
        export_file.write("# Path: {}\n".format(img_dir) )
        export_file.write("##\n")
        export_file.write("## ID;\tComment;\tCount;\n")

        for i in range(len(self.labels)):
            export_file.write("\t{};\t{};\t{};\n".format(i, self.labels[i][0], count_t[i]) )
            total_count += count_t[i]

        export_file.write("\t ;\tTOTAL;\t{};\n".format(total_count) )
        export_file.close


################################################################################################
########                                 GETs                                           ########
################################################################################################

    # Retorna o diretório da aplicação
    def getAppPath(self):
        return self.appPath

    # Retorna o diretório padrão do folder de projetos
    def getDefaultPath(self):
        return self.defaultPath
    
    # Retorna a extensão padrão dos arquivos de projeto
    def getDefaultExtension(self):
        return self.defaultExtension

    # Retorna a qtd de usuários cadastrados no projeto
    def getQtdUser(self):
        return len(self.users)

    # Retorna o nome do usuário que está no index pos passado como parâmetro
    def getUserName(self, pos):
        return self.users[pos][0]

    # Retorna o index do usuário atual do projeto
    def getCurrUserID(self):
        return self.currUserID

    # Retorna a qtd de rótulos (labels) inseridos no projeto
    def getQtdLabel(self):
        if(self.labels):
            return len(self.labels)
        else:
            return 0

    # Retorna os dados de um rótulo (label) que está no index pos passado como parâmetro
    def getLabel(self, pos):
        return self.labels[pos]

    # Retorna o index do rótulo (label) que está selecionado
    def getSelectedLb(self):
        return self.selectedLb

    # Retorna os dados do retângulo RoI
    def getWradius(self, idx = None):
        if idx == None:
            return self.wradius
        else:
            return self.wradius[idx]

    # Retorna as opções de gradiente suportada pela aplicação
    def getGradientOptions(self):
        return self.gradientOptions

    # Retorna a qtd de imagens lidas no projeto do usuário atual
    def getQtdImage(self):
        return len(self.images)

    # Retorna se a opção de exibir a imagem gradiente ao invés da original está habilitada
    def getGradShow(self):
        return self.grad_show

    # Retorna a máscara que está no index pos passado como parâmetro
    def getMask(self, pos):
        return self.masks[pos]

    # Retorna uma cor hexadecimal de acordo com o indice passado como parâmetro
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

    # Retorna o diretório onde está localizada as imagens
    def getImagePaths(self):
        if(self.imagePaths != "/"):
            return self.imagePaths
        return None

    # Retorna o nome do projeto
    def getProjectName(self):
        name = (self.projectPath.replace("\\", "/")).split("/")[-1]
        name = (name.split("."))[:-1]
        name = "".join(name)
        return name

    # Retorna o valor da escala atual exibida para o usuário
    def getImgScale(self):
        return self.IMG_SCALE[self.currScale]

    # Retorna a imagem atual
    def getCurrImg(self):
        img = ImageTk.PhotoImage(self.images[ self.currImgID ])
        return img

    # Retorna a máscara associada a imagem atual
    def getCurrMask(self):
        if(self.clean):
            img = ImageTk.PhotoImage(self.masks_clean[ self.currImgID ] )
        else:
             img = ImageTk.PhotoImage(self.masks[ self.currImgID ] )
        return img

    # Retorna as dimensões da imagem atual
    def getDimensionCurrImg(self):
        img = self.getCurrImg() 
        return [img.width(), img.height() ]

    # Retorna o index da imagem atual
    def getCurrImgID(self):
        return self.currImgID

    # Retorna a imagem de anotação que está no index pos passado como parâmetro
    def getAnnotation(self, pos):
        return self.annotation[pos]

    # Retorna a imagem atual com tamanho reajustado de acordo com o size passado como parâmetro
    def getCurrImgResize(self, size):
        img = self.images[ self.currImgID ]
        newImg = ImageTk.PhotoImage(img.resize(size))
        return newImg

    # Retorna a máscara associada a imagem atual com tamanho reajustado de acordo com o size passado como parâmetro
    def getCurrMaskResize(self,size):
        if(self.clean):
            img = self.masks_clean [ self.currImgID ]
        else:
            img = self.masks [ self.currImgID ]
        newImg = ImageTk.PhotoImage(img.resize(size))
        return newImg

    # Retorna o diretório da imagem atual
    def getPathCurrImg(self):
        if( type(self.imagePaths) is list):
            return self.imagePaths[ self.currImgID ]
        else:
            return self.imagePaths

    # Retorna o diretório onde as imagens de anotações serão salvas
    def getExportPath(self):
        path = self.getPathCurrImg()
        pos = [path.replace("\\", "/")[::-1].find("/"), path[::-1].find(".")]
        diretorio = path[:-pos[0]] + "gt_" + self.currUser[0]

        if (os.path.isdir(diretorio)):
            path = diretorio
        else:
            path = path[:-pos[0]]

        return path

    # Retorna o nome do usuário atual
    def getCurrUserName(self):
        return self.currUser[0]

    # Retorna a imagem no index pos passado como parâmetro
    def getImage(self, pos):
        return self.images[pos]

    # Retorna o diretório da última imagem lida pelo usuário
    def getLastImagePath(self):
        return self.lastImagePath

    # Retorna o valor de peso do sobel 3D
    def getSobel3Peso(self):
        return self.sobel3_peso

    # Retorna se o usuário atual carregou um conjunto (stack) de imagens
    def isStackImg(self):
        if(self.currUser[2] == -1):
            return False
        return True

    # Retorna se o usuário atual tem index igual ao value passado como parâmetro
    def isCurrUser(self, value):
        if(type(value) is int):
            if(self.currUserID == value):
                return True
        return False

    # Retorna se algum projeto foi carregado pela aplicação
    def isProjectExist(self):
        if len(self.projectPath) == 0:
            return False
        else:
            return True

    # Retorna se um arquivo de projeto existe verificando seu diretório
    def isRecentProjectExist(self):
        return os.path.isfile(self.projectPath)

################################################################################################
########                                 SETs                                           ########
################################################################################################

    # Atualiza o diretório do projeto atual e do último projeto lido
    def setProjectPath(self, path):
        self.projectPath = path
        self.updateLastProject()

    # Atualiza o usuário atual
    def setCurrUser(self, pos):
        self.currUser = self.users[pos]
        self.currUserID = pos

    # Atualiza o diretório das imagens
    def setImagePaths(self, path = None):
        if path == None:
            self.imagePaths = self.currUser[1]
            
            if(self.imagePaths == '/'):
                del self.images[:]
                del self.masks[:]
                del self.masks_clean[:]
                del self.annotation[:]
                
        else:
            self.imagePaths = path

    # Atualiza a escala das imagens exibida para o usuário
    def setImgScale(self, index = None):
        if index == None:
            index = self.IMG_SCALE.index(1)
        self.currScale = index

    # Atualiza a máscara de index pos pela iamgem mask passados como parâmetro
    def setMask(self, pos, mask):
        self.masks[pos] = mask

    # Atualiza o index do rótulo (label) que está selecionado
    def setSelectedLb(self, key):
        self.selectedLb = key

    # Atualiza o comentário do rótulo (label) no index pos com o valor comment passados como parâmetro
    def setLabelComment(self, pos, comment):
        self.labels[pos][0] = comment

    # Atualiza a cor do rótulo (label) no index pos com o valor color passados como parâmetro
    def setLabelColor(self, pos, color):
        self.labels[pos][1] = color

    # Atualiza a imagem de anotação no index pos com a imagem annotation passados como parâmetro
    def setAnnotation(self, pos, annotation):
        self.annotation[pos] = annotation

    # Atualiza o index da imagem atual de acordo com o parâmetro info
    def updateCurrImg(self, info):
        if(info == "add"):
            self.currImgID += 1
        elif info == "sub":
            self.currImgID -= 1
        else:
            self.currImgID = self.currUser[2]

    # Atualiza a imagem atual de um usuário
    def updateUserImg(self):
        self.users[ self.currUserID ][2] = self.getCurrImgID()
        self.currUser = self.users[ self.currUserID ]

    # Atualiza a flag que define se está utilizando máscara com marcações ou não
    def changeMaskClean(self):
        self.clean = not self.clean

    # Atualiza a flag que define se será exibido para o usuário a imagem original ou sua gradiente
    def changeGradImg(self):
        self.grad_show = not self.grad_show

        if(self.grad_show):
            self.images = self.gradient_images
        else:
            self.images = self.original_images

    # Aumenta o valor de escala da imagem para o usuário
    def increaseImgScale(self):
        newScale = self.currScale + 1

        if( newScale >= len(self.IMG_SCALE)):
            return False
        
        self.currScale = newScale
        return True

    # Diminui o valor de escala da imagem para o usuário
    def decreaseImgScale(self):
        newScale = self.currScale - 1
        if( newScale < 0):
            return False
        
        self.currScale = newScale
        return True

################################################################################################
########                               Label Frame                                      ########
################################################################################################

    # Remove o último rótulo (label) cadastrado
    def removeLabel(self):
        del self.labels[-1]

    # Adiciona no final da lista um novo rótulo (label)
    def addLabel(self, comment, color):
        self.labels.append( [comment, color] )

################################################################################################
########                                User Frame                                      ########
################################################################################################

    # Fluxo que procura o usuário atual na lista dos usuário cadastrado para atualiza o index
    def findCurrUser(self):
        for i in range (0,self.getQtdUser() ):
            if(self.currUser == self.users[i]):
                self.currUserID = i
                return

    # Adiciona um usuário no projeto com o username passado como parâmetro e os outros valores padrões
    def addUser(self, username):
        self.users.append( [username, "/", -1] )
        self.users.sort()
        self.findCurrUser()

    # Remove um usuário do projeto através do index pos passado como parâmetro
    def removeUser(self, pos):
        del self.users[pos]
        self.findCurrUser()