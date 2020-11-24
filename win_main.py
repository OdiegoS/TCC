# -*- coding: utf-8 -*

import tkinter
import numpy as np
import progressBar as pb

from tkinter import filedialog
from tkinter import colorchooser
from tkinter import ttk
from projects import Projects

from tkinter.simpledialog import SimpleDialog
from watershed_flooding import Watershed


class win_main(tkinter.Frame):

    def __init__(self,parent):
        tkinter.Frame.__init__(self,parent)

        self.parent = parent
        self.parent.protocol('WM_DELETE_WINDOW', self.sair)

        self.projects = Projects() # Cria um objeto da classe Projetos
        self.initialize() 

    # Fluxo para inicializar cada componente da aplicação
    def initialize(self):

        #criando menu
        self.createMenu()

        #Frame principal (onde aparece a imagem)
        self.imageFrame()

        #Frame de status
        self.statusFrame()

        # Criação do frame direito da aplicação para rótulos (labels) e usuários
        self.rightFrame() # Frame completo
        self.labelFrame() # Parte superior que exibe os rótulos
        self.userFrame() # Parte inferior que exibe os usuários

        # Adiciona as Key Binds
        self.addBind()

        # Abre o arquivo de settings (se houver) para carregar último projeto aberto
        self.openSettings()

        self.parent.focus_force()

################################################################################################
########                               Create Menu                                      ########
################################################################################################

    # Cria o menu da aplicação
    def createMenu(self):
        self.top = self.winfo_toplevel()
        self.menuBar = tkinter.Menu(self.top)

        #Criação do menu Project e suas opções 
        mnuProject = tkinter.Menu(self.menuBar, tearoff=0)
        mnuProject.add_command(label = "Create new project", command = self.createProj) # Criar projeto
        mnuProject.add_command(label = "Open project file", command = self.openProj) # Abrir projeto
        mnuProject.add_command(label = "Save Project",  command = self.saveProject) # Salvar projeto (no mesmo arquivo)
        mnuProject.add_command(label = "Save Project As", command = self.saveProjectAs) # Salvar projeto como (pode ser arquivo diferente)
        mnuProject.add_separator()
        mnuProject.add_command(label = "Configure", command = self.configure) # Configuração
        mnuProject.add_separator()
        mnuProject.add_command(label = "Quit", command = self.sair) # Fechar o programa

        self.menuBar.add_cascade(label = "Project", menu = mnuProject)

        #Criação do menu Image e suas opções
        self.mnuImage = tkinter.Menu(self.menuBar, tearoff=0)
        self.mnuImage.add_command(label="Open Image", command=self.openImage) # Abrir apenas uma única imagem
        self.mnuImage.add_command(label="Open Stack", command=self.openImageStack) # Abrir um conjunto de imagens
        self.menuBar.add_cascade(label="Image", menu=self.mnuImage)
 
        #Criação do menu Annotation e suas opções
        self.mnuAnnotation = tkinter.Menu(self.menuBar, tearoff=0)
        self.mnuAnnotation.add_command(label="Clear Annotation", command=self.reset) # Limpar todas as marcações feitas no projeto pelo usuário
        self.mnuAnnotation.add_command(label="Save Annotation", command=self.saveAnnotation) # Salvar as  marcações realizadas pelo usuário
        self.mnuAnnotation.add_command(label="Export Count", command=self.exportCount) # Salvar em um arquivo a quantidade de marcações de cada tipo realizada no projeto
        self.menuBar.add_cascade(label="Annotation", menu=self.mnuAnnotation, state="disabled")

        #Criação do menu Help e suas opções
        mnuAjuda = tkinter.Menu(self.menuBar, tearoff=0)
        mnuAjuda.add_command(label="About", command=self.sobre) # Exibe informações sobre a aplicação
        mnuAjuda.add_command(label="Keyboard Shortcuts", command=self.shortcuts) # Exibe os atalhos suportados pela aplicação
        self.menuBar.add_cascade(label="Help", menu=mnuAjuda)

        self.top.config(menu=self.menuBar)

################################################################################################
########                               Menu Project                                     ########
################################################################################################

    # Fluxo que carrega os rótulos (labels) com seus componentes
    def loadProjectLabels(self):
        self.btn_rmLb.configure(state="disabled")

        # Removendo todos os labels carregados
        for i in range(len(self.label) ):
            self.label[-1][0].destroy() # Removendo o componente do id
            self.label[-1][1].destroy() # Removendo o componente do comentário
            self.label[-1][2].destroy() # Removendo o componente da cor
            del self.label[-1] # Os componentes de rótulos da aplicação

        del self.lb_comment[:]

        # Adicionando os novos rótulos
        for i in range( self.projects.getQtdLabel() ):
            self.addLb( self.projects.getLabel(i) )

        idx_selectedLb = self.projects.getSelectedLb()
        self.label[ idx_selectedLb ][0].configure(relief='solid') # index
        self.label[ idx_selectedLb ][1].configure(relief='solid') # comentário
        self.label[ idx_selectedLb ][2].configure(relief='solid') # cor

    # Ação quando o usuário seleciona um usuário
    def confirmUser(self, window):
        self.canvasWin = None
        del(self.canvasWin)
        window.destroy()
        tkinter.messagebox.showinfo(message="Welcome back %s" %(self.projects.getCurrUserName()) )
        self.loadUser()
        self.loadProjectLabels()
    
    # Evento para o funcionamento do scroll
    def onChooseWindowConfigure(self, event):
        self.canvasWin.configure(scrollregion=self.canvasWin.bbox("all"))
    
    # Evento de seleção do componente radio
    def radioSelected(self, param):    
        self.projects.setCurrUser(param.get())

    # Janela para escolher qual o usuário que está abrindo/carregando o projeto
    def createWin_choose(self):

        tkinter.messagebox.showinfo(message="Opening Project")
        topChooseWindow= tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge' )
        topChooseWindow.title("Who are you?")
        topChooseWindow.minsize(240,100)
        topChooseWindow.resizable(width=False, height=False)
        topChooseWindow.wait_visibility()
        topChooseWindow.focus_force()
        topChooseWindow.grab_set()
        topChooseWindow.protocol('WM_DELETE_WINDOW', self.sair)

        # Elemento canvas para a janela de seleção de qual usuário está realizando a ação
        self.canvasWin = tkinter.Canvas(topChooseWindow)

        # Definindo barra de scroll veritical e horizontal para o componente
        chooseWindow = tkinter.Frame(self.canvasWin)
        vsb = tkinter.Scrollbar(topChooseWindow, orient="vertical", command=self.canvasWin.yview)
        hsb = tkinter.Scrollbar(topChooseWindow, orient="horizontal", command=self.canvasWin.xview)
        self.canvasWin.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right", fill="y")
        self.canvasWin.pack(side="left", fill="both", expand=True)
        self.canvasWin.create_window((0, 0), window=chooseWindow, anchor="nw", tags="chooseWindow")

        chooseWindow.bind("<Configure>", self.onChooseWindowConfigure)

        chWin_lb = tkinter.Label(chooseWindow, text="What's your name?", anchor="center")
        chWin_lb.grid(row = 0, column = 0, padx = 52)

        chWin_radio = []
        index_var = tkinter.IntVar()
        # Criando um componente de radio para cada usuário do projeto
        for i in range(self.projects.getQtdUser()):
            chWin_radio.append(tkinter.Radiobutton(chooseWindow, text=self.projects.getUserName(i), variable = index_var, value=i) )
            chWin_radio[i]['command'] = lambda radio = index_var : self.radioSelected(radio)
            chWin_radio[i].grid(row = i+1, column = 0, padx = 52)

        chWin_radio[ self.projects.getCurrUserID() ].select()
        
        chWin_btnConfirm = tkinter.Button(chooseWindow, text="Confirm", padx=10)
        chWin_btnConfirm['command'] = lambda btn = topChooseWindow: self.confirmUser(btn)
        chWin_btnConfirm.grid(row = len(chWin_radio)+2, column = 0, padx = 52, pady = 10)

        screen_width = self.parent.winfo_screenwidth() / 2
        screen_height = self.parent.winfo_screenheight() / 2
        size = [topChooseWindow.winfo_reqwidth(), topChooseWindow.winfo_reqheight()]
        x = screen_width - (size[0] / 2)
        y = screen_height - (size[1] / 2)

        if( (size[0] + x) < 824):
            size[0] = size[0] + 824 - (size[0] + x)

        if( i < 4):
            size[1] = size[1] - (50 - ((i-1) * 22))
        topChooseWindow.geometry("%dx%d+%d+%d" % (size[0], size[1], x, y))

    # Ação escolhida pelo usuário (criar ou abrir um projeto)
    def choooseActionEvent(self, param):
        if(param[1]):
            self.createProj(True, param[0])
        else:
            self.openProj(param[0])

    # Janela que exibe para o usuário dois botões: Criar um novo projeto ou abrir um projeto já existente
    def chooseAction(self):
        createWin = tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge')
        createWin.title("")
        centralized = [(self.parent.winfo_screenwidth() // 2) - 175, (self.parent.winfo_screenheight() // 2) - 55]
        createWin.geometry('+%d+%d' % (centralized[0], centralized[1]))
        createWin.minsize(100,100)
        createWin.resizable(width=False, height=False)
        createWin.focus_force()
        createWin.wait_visibility()
        createWin.grab_set()
        createWin.protocol('WM_DELETE_WINDOW', self.sair)

        createWin.grid_columnconfigure(0, minsize=50)
        createWin.grid_columnconfigure(3, minsize=50)

        btnNewProject = tkinter.Button(createWin, text="Create a new project")
        btnNewProject['command'] = lambda btn=[createWin, True]: self.choooseActionEvent(btn)
        btnNewProject.grid(row=2, column=1)
        createWin.grid_rowconfigure(btnNewProject, minsize=50)
        
        btnOpenProject = tkinter.Button(createWin, text="Open a project")
        btnOpenProject['command'] = lambda btn=[createWin, False]: self.choooseActionEvent(btn)
        btnOpenProject.grid(row=4, column=1)
        createWin.grid_rowconfigure(btnOpenProject, minsize=50)

    # Fluxo para carregar os componentes com os dados do projeto
    def loadProject(self, new = False):
        if ( not self.projects.isRecentProjectExist() ):
            tkinter.messagebox.showwarning("Warning", "Recent project not found.\nPlease, click in OK and create a new project or open an existing project.")
            self.chooseAction()
            return

        self.projects.loadProject() # Carrega os dados de um arquivo de projeto do Neuronote

        if( self.projects.getQtdUser() > 1): # Se o projeto tiver mais de um usuário abrir uma seleção de escolha
            self.createWin_choose()
        else: # Se o projeto tem apenas um usuário ja carrega os dados do projeto
            self.loadUser()
            self.loadProjectLabels()
            self.selectLb(0)
            if( new ):
                msg = "Welcome "
            else:
                msg = "Welcome back "
            tkinter.messagebox.showinfo(message=msg + self.projects.getCurrUserName() )

    # Ação para o botão Confirm da janela de criar projeto
    #info [ project input, project user, project frame, parent frame ]
    def newWinConfirm(self, info):
        if( (len(info[0].get().replace(" ", "") ) == 0) or (len(info[1].get().replace(" ", "") ) == 0) ):
            tkinter.messagebox.showwarning("Warning", "A field name has been left blank.\nEnter a name in the field before proceeding.")
            if(info[3] != None):
                info[3].focus_force()
                info[3].wait_visibility()
                info[3].grab_set()
                info[2].focus_force()
                info[2].wait_visibility()
                info[2].grab_set()
            return

        self.projects.newProject(info[0].get(), info[1].get())

        info[2].destroy()

        if(info[3] != None):
            info[3].destroy()

        self.loadProject(True)

    # Ação para o botão Cancel da janela de criar projeto
    # info [ project frame, flag se a ação veio do menu, parent frame ]
    def newWinCancel(self, info):

        if(info[1]):
            info[0].destroy()
            if(info[2] != None):
                info[2].focus_force()
                info[2].wait_visibility()
                info[2].grab_set()
        else:
            self.sair()

    # Fluxo para criar um novo projeto
    def createProj(self, menu = True, win_parent = None):
        createWin= tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge' )
        createWin.title("New Project")
        centralized = [ (self.parent.winfo_screenwidth() // 2) - 175, (self.parent.winfo_screenheight() // 2) - 55 ]
        createWin.geometry('+%d+%d' %(centralized[0], centralized[1]) )
        createWin.resizable(width=False, height=False)
        createWin.focus_force()
        createWin.wait_visibility()
        createWin.grab_set()

        newWin_lbProj = tkinter.Label(createWin, text="Project Name: ")
        newWin_lbProj.grid(row = 0, column = 0)
        newWin_lbUser = tkinter.Label(createWin, text="Your Username: ")
        newWin_lbUser.grid(row = 1, column = 0)

        newWin_entProj = tkinter.Entry(createWin)
        newWin_entProj.grid(row = 0, column = 1)
        newWin_entUser = tkinter.Entry(createWin)
        newWin_entUser.grid(row = 1, column = 1)

        newWin_btnOK = tkinter.Button(createWin, text="Confirm", padx=3)
        newWin_btnOK['command'] = lambda btn = [newWin_entProj, newWin_entUser, createWin, win_parent]: self.newWinConfirm(btn)
        newWin_btnOK.grid(row = 3, column = 0)

        if(not menu): # Se a ação de criar não foi pelo menu então o botão de fechar irá sair da aplicação
            createWin.protocol('WM_DELETE_WINDOW', self.sair)
        if(win_parent != None):
            createWin.protocol('WM_DELETE_WINDOW', lambda prot = [createWin, menu, win_parent]: self.newWinCancel(prot))

        newWin_btnCancel = tkinter.Button(createWin, text="Cancel", padx=3)
        newWin_btnCancel['command'] = lambda btn = [createWin, menu, win_parent]: self.newWinCancel(btn)
        newWin_btnCancel.grid(row = 3, column = 1)

    # Fluxo para abrir um projeto já criado
    def openProj(self, win_parent = None):
        initial_dir = self.projects.getAppPath() + self.projects.getDefaultPath()
        file_types = [ ("NeuroNote Project", "*" + self.projects.getDefaultExtension()) ]

        filedir = filedialog.askopenfilename(initialdir = initial_dir, filetypes = file_types )

        if( len(filedir) > 0):
            self.projects.setProjectPath(filedir)

            if(win_parent != None):
                win_parent.destroy()

            self.loadProject()

    # Fluxo para salvar um projeto no mesmo arquivo criado/carregado
    def saveProject(self):
        self.projects.saveProject()
        tkinter.messagebox.showwarning("Warning", "Project saved.")

    # Fluxo para salvar um projeto em um arquivo diferente
    def saveProjectAs(self):
        # Diálogo para selecionar diretório e nome do novo arquivo a ser salvo
        dir = filedialog.asksaveasfilename(defaultextension=".neuronote", filetypes = ( ("Neuronote Files","*.neuronote"), ("All Files", "*.*") ) )

        if(not dir):
            return

        self.projects.saveProject(dir)
        tkinter.messagebox.showwarning("Warning", "Project saved.")

    # Fluxo para confirmar e atualizar os dados de configuração
    def confirmConfigure(self, createWin):
        newWin_entX, newWin_entY, newWin_entZ, newWin_btnColor, newWin_op = [createWin.newWin_entX, createWin.newWin_entY, createWin.newWin_entZ, createWin.newWin_btnColor, createWin.newWin_op]

        # Verificando se os valores estão vazios
        if( (len(newWin_entX.get().replace(" ", "") ) == 0) or (len(newWin_entY.get().replace(" ", "") ) == 0) or (len(newWin_entZ.get().replace(" ", "") ) == 0) or (len(newWin_op.get().replace(" ", "") ) == 0)):
            tkinter.messagebox.showwarning(parent=createWin,title="Warning", message="A field name has been left blank.\nEnter a number in the field before proceeding.")
            return

        # Verificando se os valores são numéricos
        if( (not newWin_entX.get().isdigit()) or (not newWin_entY.get().isdigit()) or (not newWin_entZ.get().isdigit()) ):
            tkinter.messagebox.showwarning(parent=createWin,title="Warning", message="Please, enter a valid number.")
            return

        # Se existir o campo de peso (se for gradiente Sobel 3D)
        if(hasattr(createWin, 'newWin_entPeso')):
            newWin_entPeso = createWin.newWin_entPeso
            if(len(newWin_entPeso.get().replace(" ", "") ) == 0):
                tkinter.messagebox.showwarning(parent=createWin,title="Warning", message="A field name has been left blank.\nEnter a number in the field before proceeding.")
                return
            else:
                campoPeso = newWin_entPeso.get().replace(",", ".")
                try:
                    float(campoPeso)
                except ValueError:
                    tkinter.messagebox.showwarning(parent=createWin,title="Warning", message="Please, enter a valid number.")
                    return
        else:
            campoPeso = None

        flag = self.projects.configure(int(newWin_entX.get()), int(newWin_entY.get()), int(newWin_entZ.get()), newWin_btnColor.cget('bg'), newWin_op.get(), campoPeso)

        # Se o gradiente ou o peso do sobel 3D foi atualizado e alguma imagem já estiver carregada é atualizado o gradiente
        if(flag and (self.projects.getQtdImage() > 0) ):
            progressBar = pb.ProgressBar(self.parent) # Criando um objeto de barra de progresso para ir atualizando conforme processa as imagens
            self.projects.changeGradient(progressBar) # Reprocessa as imagens gradiente
            progressBar.close()

            if( self.projects.getGradShow() ): # Se estiver sendo exibido a imagem gradiente então é necessário atualiza a exibição
                self.refresh()

        createWin.destroy()

    # Evento ao selecionar a opção Sobel 3D para exibir outro componente de texto para inserir o valor de peso
    def comboEvent(self, createWin):
        if(createWin.newWin_op.get() == "Sobel 3D"):
            createWin.newWin_lbPeso = tkinter.Label(createWin, text="Peso Sobel 3D: ")
            createWin.newWin_lbPeso.grid(row = 5, column = 0, padx=(15,0))
            createWin.newWin_entPeso = tkinter.Entry(createWin)
            createWin.newWin_entPeso.insert(0, self.projects.getSobel3Peso())
            createWin.newWin_entPeso.grid(row = 5, column = 1, padx=(15,0))
        elif(hasattr(createWin, 'newWin_lbPeso')): # Se não for Sobel 3D, verificar se o peso está na memória para limpar o valor
            createWin.newWin_lbPeso.destroy()
            del(createWin.newWin_lbPeso)
            createWin.newWin_entPeso.destroy()
            del(createWin.newWin_entPeso)

    # Abre uma caixa para selecionar uma cor e seta no componente passado como parâmetro
    def changeColorRoi(self, btn):
        color = colorchooser.askcolor()
        if(color[1] == None):
            return
            
        btn.configure(bg=color[1])

    # Fluxo para criar a janela de configuração da aplicação
    def configure(self):
        createWin= tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge' )
        createWin.title("Insert new Values")
        centralized = [ (self.parent.winfo_screenwidth() // 2) - 175, (self.parent.winfo_screenheight() // 2) - 55 ]
        createWin.geometry('+%d+%d' %(centralized[0], centralized[1]) )
        createWin.minsize(width=270, height=150)
        createWin.resizable(width=False, height=False)
        createWin.focus_force()
        createWin.wait_visibility()
        createWin.grab_set()

        value_padx = (15,0)
        value_pady = (15,0)

        # Campos para definir o tamanho da caixa de processamento (RoI)
        createWin.newWin_lbX = tkinter.Label(createWin, text="X: ") # Tamanho horizontal
        createWin.newWin_lbX.grid(row = 0, column = 0, padx=value_padx)
        createWin.newWin_lbY = tkinter.Label(createWin, text="Y: ") # Tamanho vertical
        createWin.newWin_lbY.grid(row = 1, column = 0, padx=value_padx)
        createWin.newWin_lbZ = tkinter.Label(createWin, text="Z: ") # Profundidada (quantidade de imagens)
        createWin.newWin_lbZ.grid(row = 2, column = 0, padx=value_padx)
        createWin.newWin_lbZ = tkinter.Label(createWin, text="Color: ") # Cor da caixa
        createWin.newWin_lbZ.grid(row = 3, column = 0, padx=value_padx)
        
        # Criando os componentes para colocar os valores
        createWin.newWin_entX = tkinter.Entry(createWin)
        createWin.newWin_entX.insert(0, self.projects.getWradius(0))
        createWin.newWin_entX.grid(row = 0, column = 1, padx=value_padx)

        createWin.newWin_entY = tkinter.Entry(createWin)
        createWin.newWin_entY.insert(0, self.projects.getWradius(1))
        createWin.newWin_entY.grid(row = 1, column = 1, padx=value_padx)

        createWin.newWin_entZ = tkinter.Entry(createWin)
        createWin.newWin_entZ.insert(0, self.projects.getWradius(2))
        createWin.newWin_entZ.grid(row = 2, column = 1, padx=value_padx)

        createWin.newWin_btnColor = tkinter.Button(createWin, width = 5, bg=self.projects.getWradius(3))
        createWin.newWin_btnColor['command'] = lambda : self.changeColorRoi(createWin.newWin_btnColor)
        createWin.newWin_btnColor.grid(row = 3, column = 1, padx=value_padx)

        # Criando componente caixa de seleção para escolher o tipo de gradiente utilizado no watershed
        createWin.newWin_lbX = tkinter.Label(createWin, text="Gradient: ")
        createWin.newWin_lbX.grid(row = 4, column = 0, padx=value_padx, pady=value_pady)

        options = self.projects.getGradientOptions()
        createWin.newWin_op = ttk.Combobox(createWin, values=options, state='readonly')
        createWin.newWin_op.current(options.index(self.projects.grad))
        createWin.newWin_op.grid(row = 4, column = 1, padx=value_padx, pady=value_pady)

        createWin.newWin_op.bind("<<ComboboxSelected>>", lambda event: self.comboEvent(createWin))
        self.comboEvent(createWin)

        # Botões de Confirmar e Cancelar
        createWin.newWin_btnOK = tkinter.Button(createWin, text="Confirm", padx=3)
        createWin.newWin_btnOK['command'] = lambda btn = createWin: self.confirmConfigure(btn)
        createWin.newWin_btnOK.grid(row = 6, column = 0, padx=value_padx, pady=value_pady)
        
        createWin.newWin_btnCancel = tkinter.Button(createWin, text="Cancel", padx=3, command = createWin.destroy)
        createWin.newWin_btnCancel.grid(row = 6, column = 1, padx=value_padx, pady=value_pady)

    # Fluxo para encerrar a aplicação
    def sair(self):
        ans = tkinter.messagebox.askquestion("Quit", "Are you sure?", icon='warning')

        if ans == 'yes':
            self.parent.destroy()
            exit()

################################################################################################
########                               Menu Image                                       ########
################################################################################################

    # Fluxo para abrir apenas uma única imagem
    def openImage(self, menu = True):
        if(menu):
            filedir = filedialog.askopenfilename(initialdir= self.projects.getLastImagePath() ,filetypes = ( ("Jpeg Images", "*.jpg"), ("Gif Images","*.gif"), ("Png Images","*.png"), ("Tiff Images",".*tiff") ) )
            if(not filedir):
                return

            progressBar = pb.ProgressBar(self.parent) # Barra de progresso
            self.projects.setImagePaths(filedir)
            self.projects.openImage(progressBar, filedir)
            tkinter.messagebox.showwarning("Warning", "Image loaded.")
        else:
            progressBar = pb.ProgressBar(self.parent) # Barra de progresso
            self.projects.setImagePaths()
            self.projects.openImage(progressBar)

        progressBar.close()
        self.projects.loadAnnotation()
        self.refresh()

    # Fluxo para abrir um conjunto de imagens
    def openImageStack(self, menu = True):
        if(menu):
            dirname = filedialog.askdirectory(initialdir= self.projects.getLastImagePath())
            if(not dirname):
                return
            
            progressBar = pb.ProgressBar(self.parent) # Barra de progresso
            flag_load = self.projects.openStack(progressBar, dirname)
            tkinter.messagebox.showwarning("Warning", "All images loaded.")
        else:
            progressBar = pb.ProgressBar(self.parent) # Barra de progresso
            flag_load = self.projects.openStack(progressBar) # Flag Load indica se alguma imagem foi carregada

        progressBar.close()
        if (self.projects.getQtdImage() > 0) and flag_load:
            self.projects.loadAnnotation()
            self.refresh()

################################################################################################
########                               Menu Annotations                                 ########
################################################################################################

    # Ação do menu para limpar as marcações realizadas pelo usuário
    def reset(self):
        self.projects.clearImage()
        tkinter.messagebox.showwarning("Warning", "Image(s) cleaned.")
        self.refresh()

    # Ação do menu que irá chamar o fluxo que salva as marcações em um arquivo
    def saveAnnotation(self):
        self.projects.saveAnnotation()
        tkinter.messagebox.showwarning("Warning", "Annotation saved.")

    # Ação do menu que irá chamar o fluxo que realiza e salva a contagem das marcações em um arquivo
    def exportCount(self):
        path = self.projects.getExportPath()
        dir = filedialog.asksaveasfilename(title="Export as ", initialfile="count_" + self.projects.getCurrUserName(), initialdir=path, defaultextension=".txt", filetypes = ( ("Text Files","*.txt"), ("All Files", "*.*") ) )

        if(isinstance(dir, str) and dir != ""):
            progressBar = pb.ProgressBar(self.parent) # Barra de progresso
            self.projects.exportCount(progressBar, dir)
            progressBar.close()
            tkinter.messagebox.showwarning("Warning", "Count exported.")

################################################################################################
########                             Menu Help                                          ########
################################################################################################
        
    # Ação que exibe informações sobre a aplicação
    def sobre(self):
        pass

    # Ação que exibe para o usuário uma janela contendo os atalhos que a aplicação possui
    def shortcuts(self):
        createWin= tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge' )
        createWin.title("List of keyboard shortcuts")
        centralized = [ (self.parent.winfo_screenwidth() // 2) - 175, (self.parent.winfo_screenheight() // 2) - 55 ]
        createWin.geometry('+%d+%d' %(centralized[0], centralized[1]) )
        createWin.minsize(width=270, height=150)
        createWin.resizable(width=False, height=False)
        createWin.focus_force()
        createWin.wait_visibility()
        createWin.grab_set()

        text = "Left Click -> marks a region \n Mouse Scroll Wheel or Page Up / Down -> switch to the next or previous image \n F2 -> show or hide image markings \n F3 -> show or hide image gradient \n Numeric Keys -> select a label \n Plus and Minus Key -> zoom in / zoom out \n Shift + Holding Right Click + Drag -> drag the image"
        createWin.lb = tkinter.Label(createWin, text=text)
        createWin.lb.grid(row = 0)

        createWin.btn = tkinter.Button(createWin, text="Confirm", command = createWin.destroy)
        createWin.btn.grid(row = 1)
        
################################################################################################
########                       Create Image Frame                                       ########
################################################################################################

    # Fluxo que cria o espaço reservado para a exibição da imagem para o usuário
    def imageFrame(self):
        self.fImage = tkinter.Frame(self.parent)
        self.fImage.grid(row=0, column = 0)

        self.parent.columnconfigure(0, weight=1, minsize=450)

        self.imgScrollVertical = tkinter.Scrollbar(self.fImage, orient="vertical")
        self.imgScrollHorizontal = tkinter.Scrollbar(self.fImage, orient="horizontal")
        self.canvas = tkinter.Canvas(self.fImage, highlightthickness=10, scrollregion=(0,0,100,100), xscrollcommand=self.imgScrollHorizontal.set, yscrollcommand=self.imgScrollVertical.set)

        self.imgScrollVertical.config(command=self.canvas.yview)
        self.imgScrollVertical.pack(side="right", fill="y")

        self.imgScrollHorizontal.config(command=self.canvas.xview)
        self.imgScrollHorizontal.pack(side="bottom", fill="x")

        self.canvas.pack(fill='both', expand=True)

################################################################################################
########                        Create Status Frame                                     ########
################################################################################################

    # Fluxo que cria na parte inferior da aplicação um espaço reservado para a exibição das coordenadas (x,y,z) e o número de imagens
    def statusFrame(self):
        self.fStatus = tkinter.Frame(self.parent)
        self.fStatus.grid(row = 1, column = 0, stick='nswe', columnspan=2)

        self.status = tkinter.Label(self.fStatus, text="", bd=1,relief='sunken', anchor='w')
        self.status.pack(side='bottom', fill='x')

        self.status.x = -1
        self.status.y = -1

################################################################################################
########                        Create Right Frame                                      ########
################################################################################################

    # Fluxo que cria o espaço do lado direito da aplicação reservado para a exibição dos rótulos (labels) e usuários
    def rightFrame(self):
        self.frameRight = tkinter.Frame(self.parent)
        self.frameRight.grid(row = 0, column = 1, stick='nswe', ipadx=5)

        self.parent.columnconfigure(1, weight=1, minsize=300)
        self.frameRight.rowconfigure(0, weight=1, minsize=170)
        self.frameRight.columnconfigure(0, weight=1)
        self.frameRight.rowconfigure(1, weight=1, minsize=130)

################################################################################################
########                               Label Frame                                      ########
################################################################################################

    # Ação de mudar a cor de um botão de rótulo (label)
    def changeColor(self, btn, index = None):
        color = colorchooser.askcolor()
        if(color[1] == None):
            return
            
        btn.configure(bg=color[1])
        if(index != None):
            self.projects.setLabelColor(index, color[1])

    # Janela que permite editar o comentário de um rótulo (label)
    def commentLb(self, index):
        comment = tkinter.simpledialog.askstring("Editing Comment", "Comment:", initialvalue = self.lb_comment[index].get(), parent=self.parent)
        if(comment == None):
            return

        if (len(comment.replace(" ", "")) == 0):
            tkinter.messagebox.showwarning("Warning", "Comments can't be empty.\n")
            return

        self.lb_comment[index].set(comment)
        self.projects.setLabelComment(index, comment)

    # Evento que seleciona o rótulo "key" passado como parâmetro
    def selectLb(self, key = 9):
        if(key >= self.projects.getQtdLabel()):
            return
        
        # Modifica os botões para destacar o rótulo selecionado
        index_selectedLb = self.projects.getSelectedLb()
        if( (index_selectedLb > -1) and (index_selectedLb != key) ):
            self.label[index_selectedLb][0].configure(relief='flat')
            self.label[index_selectedLb][1].configure(relief='flat')
            self.label[index_selectedLb][2].configure(relief='flat')
            
        self.label[key][0].configure(relief='solid')
        self.label[key][1].configure(relief='solid')
        self.label[key][2].configure(relief='solid')

        self.projects.setSelectedLb(key)

    # Ação do botão Insert Label
    def addLb(self, load = None):
        qtd_label = len(self.label)
        self.label.append( [ [],[],[] ] )

        if(qtd_label == 1): #Se já tiver ao menos um rótulo então deixa habilitado o botão de remover
            self.btn_rmLb.configure(state="normal")

        # Cria as variáves com valores iniciais padrões e adiciona o novo rótulo como o último da lista
        self.lb_comment.append(tkinter.StringVar())
        if(load == None):
            self.lb_comment[-1].set("Comment_%d" %(qtd_label+1) )
            color = self.projects.getNextColor(qtd_label)

            if(self.projects.getQtdLabel() > 0):
                self.projects.addLabel(self.lb_comment[-1].get(), color)
        else:
            self.lb_comment[-1].set(load[0])
            color = load[1]

        # Cria os três botões dos rótulos (0 -> index, 1 -> comentário, 2 -> cor)
        self.label[-1][0] = tkinter.Button(self.fLabel, text="%d" %(qtd_label+1), relief="flat", padx=3)
        self.label[-1][0]['command'] = lambda : self.selectLb(qtd_label)
        self.label[-1][0].grid(row=qtd_label+1, column = 0, ipady=5)

        self.label[-1][1] = tkinter.Button(self.fLabel, textvariable=self.lb_comment[-1], relief="flat", padx=3, command=lambda:self.commentLb(qtd_label))
        self.label[-1][1].grid(row=qtd_label+1, column = 1, ipady=5)

        self.label[-1][2] = tkinter.Button(self.fLabel, text="Color", relief="flat", padx=3, bg=color)
        self.label[-1][2]['command'] = lambda : self.changeColor(self.label[-1][2], qtd_label)
        self.label[-1][2].grid(row=qtd_label+1, column = 2, ipady=5)
        
        self.btn_addLb.grid(row=qtd_label+2, column = 0, ipady=5)
        self.btn_rmLb.grid(row=qtd_label+2, column = 2, ipady=5)

    # Ação para remover um rótulo
    def rmLb(self, flag = None):
        if( (flag == None) and (len(self.label) == (self.projects.getSelectedLb()+1) ) ):
            tkinter.messagebox.showwarning("Warning", "You cannot remove a selected label!!\n")
            return

        if( len(self.label) == 2) and (flag == None): # Se ao remover o rótulo atual sobrar apenas um, então o botão de remover é desabilitado
            self.btn_rmLb.configure(state="disabled")

        # Removendo os componentes
        self.label[-1][0].destroy()
        self.label[-1][1].destroy()
        self.label[-1][2].destroy()

        # Limpando as variáveis
        del self.lb_comment[-1]
        del self.label[-1]

        if(flag == None):
            self.projects.removeLabel()

    # Fluxo que cria o espaço reservado para os rótulos e organiza os componentes
    def labelFrame(self):
        self.frameLb = tkinter.Frame(self.frameRight)
        self.frameLb.grid(row = 0, stick='nswe', ipadx=5)

        # Cria o scroll e o canvas dos componentes
        self.lbScrollVertical = tkinter.Scrollbar(self.frameLb, orient="vertical")
        self.lbScrollHorizontal = tkinter.Scrollbar(self.frameLb, orient="horizontal")
        self.lbCanvas = tkinter.Canvas(self.frameLb, xscrollcommand=self.lbScrollHorizontal.set, yscrollcommand=self.lbScrollVertical.set, height=self.parent.winfo_screenheight()/2)#, width= 250)
        self.lbScrollVertical.config(command=self.lbCanvas.yview)
        self.lbScrollHorizontal.config(command=self.lbCanvas.xview)

        self.fLabel = tkinter.Frame(self.lbCanvas)
        self.fLabel.pack(fill="both", expand=False)

        self.lbCanvas.create_window( 0,0, window=self.fLabel, anchor="nw")
        
        self.lbScrollVertical.pack(side="right", fill="y")
        self.lbScrollHorizontal.pack(side="bottom", fill="x")
        self.lbCanvas.pack(side="left", fill="both", expand=True)

        self.lb_comment = []
        self.label = []
        self.labelTitle = []

        # Cria as colunas
        self.labelTitle.append(tkinter.Label(self.fLabel, text="Label", relief='flat', padx=3, border=0))
        self.labelTitle[0].grid(row=0, column = 0, ipady=10)
        self.labelTitle.append(tkinter.Label(self.fLabel, text="Comments", relief='flat', padx=3, border=0))
        self.labelTitle[1].grid(row=0, column = 1, ipady=10)
        self.labelTitle.append(tkinter.Label(self.fLabel, text="Mark Color", relief='flat', padx=3,border=0))
        self.labelTitle[2].grid(row=0, column = 2, ipady=10)

        # Cria os botões de ações
        self.btn_addLb = tkinter.Button(self.fLabel, text="Insert Label", padx=3, command= self.addLb)
        self.btn_rmLb = tkinter.Button(self.fLabel, text="Remove Last Label", padx=3, state = "disabled", command= self.rmLb)

        # Adicionando como padrão dois rótulos caso não tenha dados de rótulos salvos para um determinado projeto
        self.addLb()
        self.addLb()

################################################################################################
########                               User Frame                                       ########
################################################################################################

    # Ação quando seleciona um usuário
    def userSelected(self, idx_user):
        if( self.projects.isCurrUser(idx_user.get()) ):
            return
        ans = tkinter.messagebox.askquestion("Warning", "Are you sure about changing user?\nAll alterations not saved will be lost!", icon = "warning")
        if(ans == "yes"):
            self.projects.setCurrUser(idx_user.get())
            self.loadUser()
            
        self.User_radio[ self.projects.getCurrUserID() ].select()

    # Fluxo que remove todos os usuários e readiciona os componentes (a lista estará ordenada pelo username)
    def addUserBtn(self):
        for i in range(0, self.projects.getQtdUser() ):
            self.User_radio[i].destroy()
            self.User_btnRm[i].destroy()

        idx_user = tkinter.IntVar()
        self.User_btnAdd.grid_remove()
        self.User_radio = []
        self.User_btnRm = []

        # Criação dos radios e botões
        for index in range(0, self.projects.getQtdUser() ):
            self.User_radio.append(tkinter.Radiobutton(self.fUser, text=self.projects.getUserName(index), variable = idx_user, value=index) )
            self.User_radio[index]['command'] = lambda radio = idx_user : self.userSelected(radio)
            self.User_radio[index].grid(row = index+1, column = 0)

            self.User_btnRm.append(tkinter.Button(self.fUser, text="Remove", padx=3) )
            self.User_btnRm[index]['command'] = lambda btn = index: self.rmUser(btn)
            self.User_btnRm[index].grid(row = index+1, column = 1)

        self.User_radio[ self.projects.getCurrUserID() ].select()
        self.User_btnAdd.grid(row = len(self.User_radio)+2, column = 0, ipady=5)

    # Fluxo que carrega um usuário do projeto
    def loadUser(self):
        self.projects.setImagePaths()
        self.projects.updateCurrImg("user")
        
        if( self.projects.getImagePaths() ): # Se o usuário já tem carregado alguma imagem no projeto
            if( self.projects.isStackImg() ):
                self.openImageStack(False)
            else:
                self.openImage(False)
        else: # Se o usuário não carregou imagem ainda, então os componentes de imagens são apagados
            self.parent.title(self.projects.getProjectName())
            self.status.configure(text=(""))
            self.canvas.delete("imgTag")
            self.canvas.delete("maskTag")
            self.canvas.delete("rect")

        self.addUserBtn()

    # Ação do botão Remove que irá remover um usuário do projeto
    def rmUser(self, idx_user):
        if( self.projects.isCurrUser(idx_user) ):
            tkinter.messagebox.showwarning("Warning", "You can't remove an active user.\nPlease, change the user and try again.")
            return

        ans = tkinter.messagebox.askquestion("Warning", "Are you sure about deleting this specialist?", icon = "warning")
        if(ans == "no"):
            return

        self.projects.removeUser(idx_user)
        self.addUserBtn()
        tkinter.messagebox.showwarning("Warning", "Specialist " + self.projects.getUserName(idx_user) + " has been deleted.")

    # Ação do botão Insert User que permite adicionar um novo usuário ao projeto
    def addUser(self):
        username = tkinter.simpledialog.askstring("New user", "Insert new user name:", parent = self.parent)

        if(username == None):
            return

        if (len(username.replace(" ", "")) == 0):
            tkinter.messagebox.showwarning("Warning", "The user name can't be empty.\n")
            return
        
        self.projects.addUser(username)
        self.addUserBtn()

    # Fluxo que cria o espaço reservado para os usuários e organiza os componentes
    def userFrame(self):
        self.frameUser = tkinter.Frame(self.frameRight)
        self.frameUser.grid(row = 1, stick='nswe', ipadx=5)

        self.userScrollVertical = tkinter.Scrollbar(self.frameUser, orient="vertical")
        self.userScrollHorizontal = tkinter.Scrollbar(self.frameUser, orient="horizontal")
        self.userCanvas = tkinter.Canvas(self.frameUser, xscrollcommand=self.userScrollHorizontal.set, yscrollcommand=self.userScrollVertical.set)
        self.userScrollVertical.config(command=self.userCanvas.yview)
        self.userScrollHorizontal.config(command=self.userCanvas.xview)

        self.fUser = tkinter.Frame(self.userCanvas)
        self.fUser.pack(fill="both", expand=False)

        self.userCanvas.create_window( 0, 0, window=self.fUser, anchor="nw")
        
        self.userScrollVertical.pack(side="right", fill="y")
        self.userScrollHorizontal.pack(side="bottom", fill="x")
        self.userCanvas.pack(side="left", fill="both", expand=True)

        self.User_radio = []
        self.User_btnRm = []

        self.userTitle = tkinter.Label(self.fUser, text="Users:", padx=3)
        self.userTitle.grid(row=0, ipady = 10)
        self.User_btnAdd = tkinter.Button(self.fUser, text="Insert user", padx=3, command = self.addUser)

################################################################################################
########                             Binding Events                                     ########
################################################################################################

    # Evento que ocorre ao clicar com o botão esquerdo do mouse
    # Evento realiza a marcação no ponto clicado
    def onClick(self, event):
        # Realizando validações
        if( (self.projects.getSelectedLb() < 0) or (event.x < 10) or (event.y < 10) ):
            return

        if( (event.x > (self.canvas.winfo_width() - 10)) or (event.y > (self.canvas.winfo_height() - 10)) ):
            return

        imgScale = self.projects.getImgScale()
        x = int(self.canvas.canvasx(event.x) / imgScale)
        y = int(self.canvas.canvasy(event.y) / imgScale)
        limite = [(self.canvas.bbox("imgTag")[2] / imgScale) - 1, (self.canvas.bbox("imgTag")[3] / imgScale) - 1]

        if( (x < 0) or (y < 0) or (x > limite[0]) or (y > limite[1]) ):
            return

        # Pegando a cor em hexadecimal do rótulo selecionado e convertendo para RGB
        colorHex = self.projects.getLabel(self.projects.getSelectedLb())[1]
        colorRGB = tuple(int(colorHex.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))

        progressBar = pb.ProgressBar(self.parent, "watershed") # Barra de progresso para a execução do watershed
        coord = self.projects.applyWatershed([x,y], progressBar) # Execução do watershed

        # Encontrando coordenada "0" da subimagem criada pelo RoI
        tam = self.projects.getWradius()
        limite_x = max(0, x-tam[0])
        limite_y = max(0, y-tam[1])

        # Pegando o index das imagens que foram processadas
        z_start = max(0, self.projects.getCurrImgID() - tam[2])
        z_end = min(self.projects.getQtdImage()-1, self.projects.getCurrImgID() + tam[2]) + 1

        # Para cada imagem e coordenada que foi marcada...
        for index in range(z_start,z_end):
            if(len(coord[0]) > 0):
                image_mask = self.projects.getMask(index)
                image_annotation = self.projects.getAnnotation(index)
                for c in coord[0]:
                    # Realiza a marcação no pixel tanto na imagem de máscara como na de anotação
                    image_mask.putpixel( (limite_x + c[0], limite_y + c[1]), colorRGB )
                    image_annotation.putpixel( (limite_x + c[0], limite_y + c[1]), self.projects.getSelectedLb() + 1)
                # Atualiza as imagens de máscara e anotação
                self.projects.setMask(index, image_mask)
                self.projects.setAnnotation(index, image_annotation)
            del(coord[0])
                
        progressBar.close()
        self.paint()

    # Evento que ocorre ao mover o mouse pela janela
    # Evento realiza a atualização das coordenadas na barra de status e move o retângulo RoI para acompanhar o mouse
    def motion(self, event):
        # Validações
        if( (event.x < 10) or (event.y < 10)):
            return

        if( (event.x > (self.canvas.winfo_width() - 10)) or (event.y > (self.canvas.winfo_height() - 10)) ):
            return

        self.eventX = event.x
        self.eventY = event.y

        imgScale = self.projects.getImgScale()
        x = self.canvas.canvasx(event.x) / imgScale
        y = self.canvas.canvasy(event.y) / imgScale

        if( (x < 0) or (y < 0) ):
            return

        limite = [ (self.canvas.bbox("imgTag")[2] / imgScale) - 1, (self.canvas.bbox("imgTag")[3] / imgScale) - 1]

        if( (x > limite[0]) or (y > limite[1]) ):
            return

        self.status.x = x
        self.status.y = y

        # Atualização do RoI e do status
        tam = [ self.projects.getWradius()[0] * imgScale, self.projects.getWradius()[1] * imgScale ]
        self.canvas.coords(self.canvas.rect, self.canvas.canvasx(event.x)-tam[0], self.canvas.canvasy(event.y)-tam[1], self.canvas.canvasx(event.x)+tam[0], self.canvas.canvasy(event.y)+tam[1])
        self.canvas.itemconfigure(self.canvas.rect, outline = self.projects.getWradius()[3])
        self.updateStatus()

    # Evento que ocorre ao mover o scroll do mouse ou botão Page Up e Down
    # Evento permite passar para uma imagem posterior ou anterior de acordo com o comando dado
    def moveImg(self, event):
        flag_change = False 
        # Próxima imagem
        if (event.keysym == "Next") or (event.delta < 0) or (event.num == 5):
            if( self.projects.getCurrImgID()  > 0):
                self.projects.updateCurrImg("sub")
                flag_change = True
        # Imagem anterior
        if (event.keysym == "Prior") or (event.delta > 0) or (event.num == 4):
            if self.projects.getCurrImgID() < self.projects.getQtdImage()-1:
                self.projects.updateCurrImg("add")
                flag_change = True
        # Caso tenha mudado a imagem é atualizado sua exibição
        if flag_change == True: 
            self.refresh()

    # Evento que ocorre ao apertar F2
    # Evento modifica a máscara utilizada na exibição entre uma imagem limpa e com marcações
    def showHideMask(self, event):
        self.projects.changeMaskClean() # Muda o tipo de exibição
        self.paint() # Atualiza exibição para o usuário

    # Evento que ocorre ao apertar F3
    # Evento modifica a imagem utilizada na exibição entre a imagem original e a gradiente
    def showHideGrad(self, event):
        self.projects.changeGradImg() # Muda o tipo de exibição
        self.paint() # Atualiza exibição para o usuário

    # Evento que ocorre ao apertar clicar com o botão esquerdo no index do rótulo ou apertar o valor numérico correspondente
    # Evento seleciona o rótulo com o valor clicado/apertado
    def selectLbEvent(self, event):
        if(event.keysym[0] == 'K'):
            key = int(event.keysym.split('_')[1]) - 1
        else:
            key = int(event.keysym) - 1
        
        self.selectLb(key)

    # Eventos do canvas para permitir o funcionamento do scroll
    def OnFrameConfigureImg(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def OnFrameConfigureLabel(self, event):
        self.lbCanvas.configure(scrollregion=self.lbCanvas.bbox("all"))

    def OnFrameConfigureUser(self, event):
        self.userCanvas.configure(scrollregion=self.userCanvas.bbox("all"))

    # Evento que ocorre ao apertar + ou -
    # Evento permite dar zoom in (ampliar) ou zoom out (reduzir) a imagem
    def zoom(self,event):
        if( (event.keysym == "plus") or (event.keysym == "KP_Add") ): # KP_ para linux
            res = self.projects.increaseImgScale()
        else:
            res = self.projects.decreaseImgScale()

        if(res):
            self.redraw(True) # Atualiza a exibição

    # Evento que ocorre ao clicar com o botão direito do mouse segurando o SHIFT
    # Evento realiza procedimentos iniciais de drag_to (arrastar)
    def buttonPress(self, event):
        self.canvas.scan_mark(event.x, event.y)
        self.canvas.shiftPress = True

    # Evento que ocorre ao mover o mouse com o botão direito e o SHIFT apertado
    # Evento movimenta a imagem no campo de visão do usuário respeitando os limites das barras de scroll
    def buttonMove(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    # Evento que ocorre ao soltar o botão direito do mouse
    # Evento permite apagar marcações já realizadas
    def buttonRelease(self, event):
        if(self.canvas.shiftPress):
            self.canvas.shiftPress = False
            return
        tam = self.projects.getWradius()
        coord_x = [max(0, int(self.canvas.canvasx(event.x) / self.projects.getImgScale()) - tam[0]), min(self.projects.getDimensionCurrImg()[0], int(self.canvas.canvasx(event.x) / self.projects.getImgScale()) + tam[0]) ]
        coord_y = [max(0, int(self.canvas.canvasy(event.y) / self.projects.getImgScale()) - tam[1]), min(self.projects.getDimensionCurrImg()[1], int(self.canvas.canvasy(event.y) / self.projects.getImgScale()) + tam[1]) ]
        coord_z = [max(0, self.projects.getCurrImgID() - tam[2]), min(self.projects.getQtdImage(), self.projects.getCurrImgID() + tam[2] + 1) ]

        colorHex = self.projects.getLabel(self.projects.getSelectedLb())[1]
        colorRGB = tuple(int(colorHex.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))

        for index in range(coord_z[0], coord_z[1]):
            for x in range(coord_x[0], coord_x[1]):
                for y in range (coord_y[0], coord_y[1]):
                    image_mask = self.projects.getMask(index)
                    image_annotation = self.projects.getAnnotation(index)
                    if(image_mask.getpixel((x, y))[:-1] == colorRGB):
                        image_mask.putpixel( (x, y), (0,0,0,0) )
                        image_annotation.putpixel( (x, y), 0 )
            self.projects.setMask(index, image_mask)
            self.projects.setAnnotation(index, image_annotation)
        self.paint()

    # Fluxo que adiciona os atalhos (key binds) nos componentes
    def addBind(self):
        self.canvas.shiftPress = False
        
        #Image Bind
        self.canvas.tag_bind("maskTag", "<Button-1>", self.onClick)
        self.canvas.tag_bind("maskTag", "<Motion>", self.motion)

        self.parent.bind("<Next>", self.moveImg)
        self.parent.bind("<Prior>", self.moveImg)

        self.parent.bind("<MouseWheel>", self.moveImg) #Windows
        self.parent.bind("<Button-4>", self.moveImg) #Linux
        self.parent.bind("<Button-5>", self.moveImg) #Linux

        self.parent.bind("<F2>", self.showHideMask)
        self.parent.bind("<F3>", self.showHideGrad)

        #Label Bind
        for i in range(10):
            self.parent.bind(str(i), self.selectLbEvent)
            self.parent.bind("<KP_" + str(i) + ">", self.selectLbEvent) #Linux - Numpad

        self.fImage.bind("<Configure>", self.OnFrameConfigureImg)
        self.fLabel.bind("<Configure>", self.OnFrameConfigureLabel)
        self.fUser.bind("<Configure>", self.OnFrameConfigureUser)

        self.parent.bind("<plus>", self.zoom)
        self.parent.bind("<minus>", self.zoom)
        self.parent.bind("<KP_Add>", self.zoom) #Linux - Numpad
        self.parent.bind("<KP_Subtract>", self.zoom) #Linux - Numpad

        self.canvas.tag_bind("maskTag", "<Shift-ButtonPress-3>", self.buttonPress)
        self.canvas.tag_bind("maskTag", "<Shift-B3-Motion>", self.buttonMove)
        self.canvas.tag_bind("maskTag", "<ButtonRelease-3>", self.buttonRelease)


################################################################################################
########                             Binding Functions                                  ########
################################################################################################

    # Função que atualiza os valores de status do componente
    def updateStatus(self):
        if (self.projects.isStackImg()):
            self.status.configure(text=("X: %d \t Y: %d \t Z: %d / %d \t\t Scale: %d%%" % (self.status.x, self.status.y, self.projects.getCurrImgID() + 1, self.projects.getQtdImage(), self.projects.getImgScale() * 100)))
        else:
            self.status.configure(text=("X: %d \t Y: %d \t\t Scale: %d%%" % (self.status.x, self.status.y, self.projects.getImgScale() * 100)))

    # Função que atualiza uma nova imagem exibida para o usuário de forma redimensionada de acordo com sua escala
    def redraw(self, zoom = False):
        self.canvas.delete("all")

        dimensionImg = self.projects.getDimensionCurrImg()
        size = int(self.projects.getImgScale() * dimensionImg[0]), int(self.projects.getImgScale() * dimensionImg[1])
        
        self.canvas.image = self.projects.getCurrImgResize(size)
        self.canvas.mask = self.projects.getCurrMaskResize(size)
        self.canvas.config(width=size[0], height=size[1])

        tam = [ int(size[0] / 2), int(size[1] / 2)]
        self.canvas.imgID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.image, tags="imgTag")
        self.canvas.maskID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.mask, tags="maskTag")

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.config(xscrollcommand=self.imgScrollHorizontal.set, yscrollcommand=self.imgScrollVertical.set)
        self.canvas.pack(fill='both', expand=True)

        if(zoom):
            coord = [(self.status.x * self.projects.getImgScale() + 1) / size[0], (self.status.y * self.projects.getImgScale() + 1) / size[1]]

            self.canvas.xview_moveto(coord[0])
            self.canvas.yview_moveto(coord[1])

            self.imgScrollHorizontal.update()
            self.imgScrollVertical.update()

            tamScroll = [self.imgScrollHorizontal.get()[1] - self.imgScrollHorizontal.get()[0], self.imgScrollVertical.get()[1] - self.imgScrollVertical.get()[0] ]
            valor = [10,10]

            if ((tamScroll[0] + coord[0]) > 1.0):
                valor[0] = int((tamScroll[0] + coord[0] - 1.0) * size[0])
                valor[0] = int(valor[0])

            if( (tamScroll[1] + coord[1]) > 1.0):
                valor[1] = int((tamScroll[1] + coord[1] - 1.0) * size[1])
                valor[1] = int(valor[1])

            self.canvas.scan_mark(valor[0], valor[1])
            self.canvas.scan_dragto(self.eventX, self.eventY, 1)

        self.updateStatus()
        tam = [ self.projects.getWradius()[0] * self.projects.getImgScale(), self.projects.getWradius()[1] * self.projects.getImgScale() ]
        rec_x = self.status.x * self.projects.getImgScale()
        rec_y = self.status.y * self.projects.getImgScale()
        self.canvas.rect = self.canvas.create_rectangle(rec_x-tam[0],  rec_y-tam[1], rec_x+tam[0],  rec_y+tam[1], outline = self.projects.getWradius()[3], tags="rect")

    # Função que atualiza a exibição de uma nova imagem para o usuário
    def refresh(self):
        self.canvas.delete("all")

        if(self.projects.getImgScale() != 1):
            self.redraw()
            return

        dimensionImg = self.projects.getDimensionCurrImg()
        self.canvas.config(width=dimensionImg[0], height=dimensionImg[1] )

        self.canvas.image = self.projects.getCurrImg()
        self.canvas.mask = self.projects.getCurrMask()

        tam = [ int(dimensionImg[0] / 2), int(dimensionImg[1] / 2) ]
        self.canvas.imgID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.image, tags="imgTag")
        self.canvas.maskID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.mask, tags="maskTag")
        self.canvas.pack(fill='both', expand=True)

        if( self.projects.isStackImg() ):
            self.projects.updateUserImg()

        self.updateStatus()
        self.parent.title("(%s)" %self.projects.getPathCurrImg() )
        tam = [ self.projects.getWradius()[0] * self.projects.getImgScale(), self.projects.getWradius()[1] * self.projects.getImgScale() ]
        self.canvas.rect = self.canvas.create_rectangle(self.status.x-tam[0], self.status.y-tam[1], self.status.x+tam[0], self.status.y+tam[1], outline = self.projects.getWradius()[3], tags="rect")
        self.menuBar.entryconfig("Annotation", state="normal")

    # Função que atualiza a exibição da imagem para o usuário
    def paint(self):
        dimensionImg = self.projects.getDimensionCurrImg()

        size = int(self.projects.getImgScale() * dimensionImg[0]), int(self.projects.getImgScale() * dimensionImg[1])
        self.canvas.image = self.projects.getCurrImgResize(size)
        self.canvas.mask = self.projects.getCurrMaskResize(size)

        self.canvas.itemconfigure(self.canvas.imgID, image=self.canvas.image)
        self.canvas.itemconfigure(self.canvas.maskID, image=self.canvas.mask)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.canvas.config(xscrollcommand=self.imgScrollHorizontal.set, yscrollcommand=self.imgScrollVertical.set)
        self.canvas.pack(fill='both', expand=True)

################################################################################################
########                               Open Settings                                    ########
################################################################################################

    # Fluxo que verifica no arquivo Settings da aplicação o último projeto aberto
    def openSettings(self):
        self.projects.loadProject()
        
        if( not self.projects.isProjectExist() ):
            tkinter.messagebox.showwarning("Warning", "There is no project yet.\nPlease, click in OK and create a new project.")
            self.createProj(False)
            return
        self.loadProject()


#########################################################################
#########################################################################

# Criação do objeto da aplicação Neuronote e execução do mesmo
if __name__ == "__main__":
    root = tkinter.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.title('Neuronote')

    root.minsize(750,340)
    
    app = win_main(root)
    app.mainloop()
