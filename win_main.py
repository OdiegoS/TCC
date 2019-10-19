# -*- coding: utf-8 -*

import tkinter
from tkinter import messagebox
from tkinter import filedialog
from tkinter.colorchooser import *
from tkinter.simpledialog import SimpleDialog
from projects import Projects
from watershed_flooding import Watershed
import numpy as np
import matplotlib.pyplot as plt


class win_main(tkinter.Frame):

    def __init__(self,parent):
        tkinter.Frame.__init__(self,parent)
        
        self.parent = parent

        self.projects = Projects()
        
        self.initialize()

    def initialize(self):

        #criando menu
        self.createMenu()

        #Frame principal (onde aparece a imagem)
        self.frameMain()

        #Frame de status
        self.frameStatus()

        #Frame Label
        self.frameLabel()

        #Apenas Key Binds
        self.addBind()

        #carregando settings (se houver)
        self.openSettings()

    def openSettings(self):
        self.projects.openSettings()
        
        if( self.projects.notExistProject() ):
            tkinter.messagebox.showwarning("Warning", "There is no project yet.\nPlease, click in OK and create a new project.")
            self.createProj()
            return
        self.loadSettings()


    def chooseAction(self):
        createWin = tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge')
        createWin.title("")
        centralized = [(self.parent.winfo_screenwidth() // 2) - 175, (self.parent.winfo_screenheight() // 2) - 55]
        createWin.geometry('+%d+%d' % (centralized[0], centralized[1]))
        createWin.minsize(100,100)
        createWin.resizable(width=False, height=False)
        createWin.focus_force()
        createWin.grab_set()

        createWin.grid_columnconfigure(0, minsize=50)
        createWin.grid_columnconfigure(3, minsize=50)

        btnNewProject = tkinter.Button(createWin, text="Create a new project", bg="green")
        btnNewProject.grid(row=2, column=1)
        createWin.grid_rowconfigure(btnNewProject, minsize=50)

        btnOpenProject = tkinter.Button(createWin, text="Open a project", bg="red")
        btnOpenProject.grid(row=4, column=1)
        createWin.grid_rowconfigure(btnOpenProject, minsize=50)

        btnNewProject['command'] = lambda btn=[createWin, True]: self.choooseActionEvent(btn)
        btnOpenProject['command'] = lambda btn=[createWin, False]: self.choooseActionEvent(btn)

    def choooseActionEvent(self, param):

        if(param[1]):
            self.createProj()
        else:
            self.abrirProj()

        param[0].destroy()

    def loadSettings(self, new = False):

        if (not self.projects.isProjectExist()):
            tkinter.messagebox.showwarning("Warning", "Recent project not found.\nPlease, click in OK and create a new project or open an existing project.")
            self.chooseAction()
            return


        self.projects.loadSettings()

        #listUsers = project[0:-1]
        #listUsers.sort()
        
        '''
        for expert in listUsers:
            #self.users.append(expert.split("gt_")[1])
            self.users.append(expert)

            #if(recentProj[1] == self.users[-1]):
            if(project[0] == self.users[-1]):
                userSelection = len(self.users)-1
        '''
        if( self.projects.sizeUsers()  > 1):
            self.createWin_choose()
        else:
            self.loadUser()
            self.loadComments()
            if( new ):
                tkinter.messagebox.showinfo(message="Welcome %s" %(self.projects.getCurrUserName()) )
            else:
                tkinter.messagebox.showinfo(message="Welcome back %s" %(self.projects.getCurrUserName()) )
                    

    def createWin_choose(self):

        #tkinter.messagebox.showinfo(message="Opening Project: %s" %(self.dir.split(".neuronote")[0] ) )
        tkinter.messagebox.showinfo(message="Opening Project")

        topChooseWindow= tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge' )
        topChooseWindow.title("Who are you?")
        topChooseWindow.resizable(width=False, height=False)
        topChooseWindow.focus_force()
        topChooseWindow.grab_set()

        self.canvasWin = tkinter.Canvas(topChooseWindow)
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
        var = tkinter.IntVar()
        for i in range(self.projects.sizeUsers()):
                
            chWin_radio.append(tkinter.Radiobutton(chooseWindow, text=self.projects.getUserName(i), variable = var, value=i) )
            chWin_radio[i]['command'] = lambda radio = var: self.radioSelected(radio)
            chWin_radio[i].grid(row = i+1, column = 0, padx = 52)

        chWin_radio[ self.projects.currUserID ].select()
        #self.user = var.get()

        chWin_btnConfirm = tkinter.Button(chooseWindow, text="Confirm", padx=10, bg = "green")
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

    def onChooseWindowConfigure(self, event):
        self.canvasWin.configure(scrollregion=self.canvasWin.bbox("all"))

    def radioSelected(self, param):    
        self.projects.updateCurrUser(param.get())

    def confirmUser(self, window):
        self.canvasWin = None
        del(self.canvasWin)
        window.destroy()
        tkinter.messagebox.showinfo(message="Welcome back %s" %(self.projects.getCurrUserName()) )
        self.loadUser()
        self.loadComments()

    def loadUser(self):

        self.projects.updateImagePaths()
        self.projects.updateCurrImg("load")
        

        if( self.projects.existImagePaths() ):
            
            if( self.projects.isBatchImg() ):
                self.abrirBatch(False)
            else:
                self.abrir(False)
        else:
            self.parent.title("Teste")
            self.status.configure(text=(""))
            self.canvas.delete("imgTag")
            self.canvas.delete("maskTag")

        for i in range(0, len(self.User_radio) ):
            self.User_radio[i].destroy()
            self.User_btnRm[i].destroy()

        self.User_radio = []
        self.User_btnRm = []

        var = tkinter.IntVar()
        
        for i in range(0, self.projects.sizeUsers() ):
            
            self.User_radio.append(tkinter.Radiobutton(self.fUser, text=self.projects.getUserName(i), variable = var, value=i) )
            self.User_radio[i]['command'] = lambda radio = var : self.userSelected(radio)
            self.User_radio[i].grid(row = i+1, column = 0)

            self.User_btnRm.append(tkinter.Button(self.fUser, text="Remove", padx=3, bg = "red") )
            self.User_btnRm[i]['command'] = lambda btn = i: self.rmUser(btn)
            self.User_btnRm[i].grid(row = i+1, column = 1)

            #if(self.user == self.users[i]):
                #self.User_radio[i].select()
        self.User_radio[ self.projects.getCurrUserID() ].select()

        self.User_btnAdd.grid(row = len(self.User_radio)+2, column = 0, ipady=5)


    def rmUser(self,user):
        
        if( self.projects.isCurrUser(user) ):
            tkinter.messagebox.showwarning("Warning", "You can't remove an active user.\nPlease, change the user and try again.")
            return

        ans = tkinter.messagebox.askquestion("Warning", "Are you sure about deleting this specialist?", icon = "warning")
        if(ans == "no"):
            return

        for i in range(0, self.projects.sizeUsers() ):
            self.User_radio[i].destroy()
            self.User_btnRm[i].destroy()

        name = self.projects.getUserName(user)
        self.projects.removeUser(user)

        var = tkinter.IntVar()

        self.User_btnAdd.grid_remove()
        
        self.User_radio = []
        self.User_btnRm = []
        for i in range(0, self.projects.sizeUsers() ):
            self.User_radio.append(tkinter.Radiobutton(self.fUser, text=self.projects.getUserName(i), variable = var, value=i) )
            self.User_radio[i]['command'] = lambda radio = var : self.userSelected(radio)
            self.User_radio[i].grid(row = i+1, column = 0)

            self.User_btnRm.append(tkinter.Button(self.fUser, text="Remove", padx=3, bg = "red") )
            self.User_btnRm[i]['command'] = lambda btn = i: self.rmUser(btn)
            self.User_btnRm[i].grid(row = i+1, column = 1)

            '''
            if(self.user[0] == self.users[i][0]):
                #self.User_radio[i].select()
                self.userID = i
            '''

        self.User_radio[ self.projects.getCurrUserID() ].select()
                
        self.User_btnAdd.grid(row = len(self.User_radio)+2, column = 0)

        tkinter.messagebox.showwarning("Warning", "Specialist " + name + " has been deleted.")
        
    def addUser(self):
        new = tkinter.simpledialog.askstring("New user", "Insert new user name:", parent = self.parent)

        if(new == None):
            return

        if (len(new.replace(" ", "")) == 0):
            tkinter.messagebox.showwarning("Warning", "The user name can't be empty.\n")
            return
        
        for i in range(0, self.projects.sizeUsers() ):
            self.User_radio[i].destroy()
            self.User_btnRm[i].destroy()

        self.projects.addUser(new)

        #print(self.users)
        #self.users.sort(key=lambda name: name[0][0])
        #self.users.sort()
        #print("\n##########\n")
        #print(self.users)
        
        var = tkinter.IntVar()

        self.User_btnAdd.grid_remove()
        
        self.User_radio = []
        self.User_btnRm = []
        for i in range(0, self.projects.sizeUsers() ):
            self.User_radio.append(tkinter.Radiobutton(self.fUser, text=self.projects.getUserName(i), variable = var, value=i) )
            self.User_radio[i]['command'] = lambda radio = var : self.userSelected(radio)
            self.User_radio[i].grid(row = i+1, column = 0)

            self.User_btnRm.append(tkinter.Button(self.fUser, text="Remove", padx=3, bg = "red", command = self.rmUser) )
            self.User_btnRm[i]['command'] = lambda btn = i: self.rmUser(btn)
            self.User_btnRm[i].grid(row = i+1, column = 1)

            '''
            if( projects.isCurrUser ):
                #self.User_radio[i].select()
                projects.updateCurrUser(i)
            '''

        self.User_radio[ self.projects.getCurrUserID() ].select()
                
        self.User_btnAdd.grid(row = len(self.User_radio)+2, column = 0)

    def userSelected(self, var):

        if( self.projects.isCurrUser(var.get()) ):
            return
        ans = tkinter.messagebox.askquestion("Warning", "Are you sure about changing user?", icon = "warning")
        if(ans == "yes"):
            self.projects.updateCurrUser(var.get())
            self.loadUser()
            
        '''
        for i in range(0, len(self.users) ):
            if(self.user == self.users[i]):
                self.User_radio[i].select()
        '''
        self.User_radio[ self.projects.getCurrUserID() ].select()

    '''
    def saveSettings(self):
        return
        file = open("settings","w")

        file.write(self.dirImage + "\n")
        file.write(self.dirStack + "\n")
        file.write(self.dirLoadComments + "\n")
        file.write(self.dirSaveComments + "\n")
        file.write(self.dirLoadAnnotations + "\n")
        file.write(self.dirSaveAnnotations + "\n")
    '''

    def createMenu(self):
        self.top = self.winfo_toplevel()
        self.menuBar = tkinter.Menu(self.top)
         
        self.mnuProject = tkinter.Menu(self.menuBar, tearoff=0)
        self.mnuProject.add_command(label="Create new project", command=self.createProj)
        self.mnuProject.add_command(label="Open project file", command=self.abrirProj)
        self.mnuProject.add_command(label="Save Project",  command=self.projects.saveProject)
        self.mnuProject.add_command(label="Save Project As", command=self.saveProjectAs)
        self.mnuProject.add_command(label="Save Annotation", command=self.saveAnnotation)
        self.menuBar.add_cascade(label="Project", menu=self.mnuProject)

        self.mnuArquivo = tkinter.Menu(self.menuBar, tearoff=0)
        #self.mnuArquivo.add_command(label="Open Image", state = "disabled", command=self.abrir)
        self.mnuArquivo.add_command(label="Open Image", command=self.abrir)
        self.mnuArquivo.add_command(label="Open Stack", command=self.abrirBatch)
        #self.mnuArquivo.add_command(label="Save Annotation ", command=self.nada)
        #self.mnuArquivo.add_command(label="Save Comments", state = "disabled", command=self.saveComments)
        #self.mnuArquivo.add_command(label="Save Comments As", command=self.saveCommentsAs)
        #self.mnuArquivo.add_command(label="Load Comments", command=self.loadComments)
        self.mnuArquivo.add_separator()
        self.mnuArquivo.add_command(label="Quit", command=self.sair)
        self.menuBar.add_cascade(label="Image", menu=self.mnuArquivo)
 
        mnuTeste = tkinter.Menu(self.menuBar, tearoff=0)
        mnuTeste.add_command(label="Blabla", command=self.nada)
        mnuTeste.add_command(label="Bla", command=self.nada)
        self.menuBar.add_cascade(label="Teste", menu=mnuTeste)
 
        mnuAjuda = tkinter.Menu(self.menuBar, tearoff=0)
        mnuAjuda.add_command(label="About", command=self.sobre)
        self.menuBar.add_cascade(label="Help", menu=mnuAjuda)

        self.top.config(menu=self.menuBar)

    def frameMain(self):
        self.fMain = tkinter.Frame(self.parent)
        #self.fMain.grid(row=0, column = 0, stick='nw')
        self.fMain.grid(row=0, column = 0)


        self.parent.columnconfigure(0, weight=1, minsize=450)
        #self.fMain.rowconfigure(0, weight=1)
        #self.fMain.columnconfigure(0, weight=1)

        self.imgScrollVertical = tkinter.Scrollbar(self.fMain, orient="vertical")
        self.imgScrollHorizontal = tkinter.Scrollbar(self.fMain, orient="horizontal")
        self.canvas = tkinter.Canvas(self.fMain, highlightthickness=10, scrollregion=(0,0,100,100), xscrollcommand=self.imgScrollHorizontal.set, yscrollcommand=self.imgScrollVertical.set)
        self.canvas.config(bg="yellow")

        self.imgScrollVertical.config(command=self.canvas.yview)
        self.imgScrollHorizontal.config(command=self.canvas.xview)
        

        self.imgScrollVertical.pack(side="right", fill="y")
        self.imgScrollHorizontal.pack(side="bottom", fill="x")
        #998x665
        #Somar 2 se qt pixel for par e somar 1 se qt de pixel for impar?
        #self.canvas.create_image(self.photo.width()/2+2, self.photo.height()/2+1, image=self.photo, tags="imgTag")
        self.canvas.pack(fill='both', expand=True)
        
    def frameStatus(self):
        self.fStatus = tkinter.Frame(self.parent)
        self.fStatus.grid(row = 1, column = 0, stick='nswe', columnspan=2)

        #self.fStatus.rowconfigure(0, weight=1)
        #self.fStatus.columnconfigure(0, weight=1)
        
        #self.status = tkinter.Label(self.fStatus, text="X: -- \t Y: -- \t Z: -- / --", bd=1,relief='sunken', anchor='w', bg='red')
        self.status = tkinter.Label(self.fStatus, text="", bd=1,relief='sunken', anchor='w', bg='red')
        self.status.pack(side='bottom', fill='x')

        self.status.x = -1
        self.status.y = -1
        
    def frameLabel(self):
        self.frameRight = tkinter.Frame(self.parent, bg= "orange")
        self.frameRight.grid(row = 0, column = 1, stick='nswe', ipadx=5)


        self.parent.columnconfigure(1, weight=1, minsize=300)
        self.frameRight.rowconfigure(0, weight=1, minsize=170)
        self.frameRight.columnconfigure(0, weight=1)
        self.frameRight.rowconfigure(1, weight=1, minsize=130)
                
        self.frameLb = tkinter.Frame(self.frameRight, bg="pink")
        #self.fLabel = tkinter.Frame(self.lbCanvas, bg="green")
        self.frameLb.grid(row = 0, stick='nswe', ipadx=5)

        #self.frameLb.rowconfigure(0, weight=1)
        #self.frameLb.columnconfigure(0, weight=1)
        
        self.lbScrollVertical = tkinter.Scrollbar(self.frameLb, orient="vertical")
        self.lbScrollHorizontal = tkinter.Scrollbar(self.frameLb, orient="horizontal")
        self.lbCanvas = tkinter.Canvas(self.frameLb, bg ="green", xscrollcommand=self.lbScrollHorizontal.set, yscrollcommand=self.lbScrollVertical.set, height=self.parent.winfo_screenheight()/2)#, width= 250)
        self.lbScrollVertical.config(command=self.lbCanvas.yview)
        self.lbScrollHorizontal.config(command=self.lbCanvas.xview)

        self.fLabel = tkinter.Frame(self.lbCanvas, bg="blue")
        self.fLabel.pack(fill="both", expand=False)

        #self.fLabel.rowconfigure(0, weight=1)
        #self.fLabel.columnconfigure(0, weight=1)

        self.lbCanvas.create_window( 0,0, window=self.fLabel, anchor="nw")
        
        self.lbScrollVertical.pack(side="right", fill="y")
        self.lbScrollHorizontal.pack(side="bottom", fill="x")
        self.lbCanvas.pack(side="left", fill="both", expand=True)
                
        
        #self.lbCanvas.config(scrollregion=self.lbCanvas.bbox("all"))
        #self.lbCanvas.yview_moveto(0)

        self.lb_comment = []
        self.label = []
        self.labelTitle = []

        self.labelTitle.append(tkinter.Label(self.fLabel, text="Label", relief='raised', padx=3))
        self.labelTitle[0].grid(row=0, column = 0, ipady=10)
        self.labelTitle.append(tkinter.Label(self.fLabel, text="Comments", relief='raised', padx=3))
        self.labelTitle[1].grid(row=0, column = 1, ipady=10)
        self.labelTitle.append(tkinter.Label(self.fLabel, text="Mark Color", relief='raised', padx=3))
        self.labelTitle[2].grid(row=0, column = 2, ipady=10)

        self.btn_addLb = tkinter.Button(self.fLabel, text="Insert Label", padx=3, command= self.addLb)
        self.btn_rmLb = tkinter.Button(self.fLabel, text="Remove Last Label", padx=3, state = "disabled", command= self.rmLb)
        #self.btn_rmLb = tkinter.Button(self.fLabel, text="Remove Last Label", padx=3, command= self.rmLb)

        self.addLb()
        self.addLb()
        
        self.frameUser = tkinter.Frame(self.frameRight, bg="purple")
        self.frameUser.grid(row = 1, stick='nswe', ipadx=5)

        #self.frameUser.rowconfigure(0, weight=1)
        #self.frameUser.columnconfigure(0, weight=1)

        self.userScrollVertical = tkinter.Scrollbar(self.frameUser, orient="vertical")
        self.userScrollHorizontal = tkinter.Scrollbar(self.frameUser, orient="horizontal")
        self.userCanvas = tkinter.Canvas(self.frameUser, bg ="pink", xscrollcommand=self.userScrollHorizontal.set, yscrollcommand=self.userScrollVertical.set)#, width= 250)
        self.userScrollVertical.config(command=self.userCanvas.yview)
        self.userScrollHorizontal.config(command=self.userCanvas.xview)

        self.fUser = tkinter.Frame(self.userCanvas, bg="gray")
        self.fUser.pack(fill="both", expand=False)

        #self.fUser.rowconfigure(0, weight=1)
        #self.fUser.columnconfigure(0, weight=1)

        #120
        self.userCanvas.create_window( 0, 0, window=self.fUser, anchor="nw")
        
        self.userScrollVertical.pack(side="right", fill="y")
        self.userScrollHorizontal.pack(side="bottom", fill="x")
        self.userCanvas.pack(side="left", fill="both", expand=True)

        self.User_radio = []
        self.User_btnRm = []

        self.userTitle = tkinter.Label(self.fUser, text="Users:", padx=3)
        self.userTitle.grid(row=0, ipady = 10)

        self.User_btnAdd = tkinter.Button(self.fUser, text="Insert specialist", padx=3, bg = "green", command = self.addUser)

    def commentLb(self, i):

        comment = tkinter.simpledialog.askstring("Editing Comment", "Comment:", initialvalue = self.lb_comment[i].get(), parent=self.parent)

        if(comment == None):
            return

        if (len(comment.replace(" ", "")) == 0):
            tkinter.messagebox.showwarning("Warning", "Comments can't be empty.\n")
            return

        self.lb_comment[i].set(comment)
        self.projects.updateLabelComment(i, comment)

    def addLb(self, load = None):

        i = len(self.label)
        self.label.append( [ [],[],[] ] )

        if(i == 1):
            self.btn_rmLb.configure(state="normal")
            #self.btn_rmLb.grid()

        if(load == None):
            self.lb_comment.append(tkinter.StringVar())
            self.lb_comment[i].set("Comment_%d" %(i+1) )

            color = self.projects.colorDefault(i)

            if(self.projects.sizeLabels() > 0):
                self.projects.addLabel(self.lb_comment[i].get(), color)
        else:
            self.lb_comment.append(tkinter.StringVar())
            self.lb_comment[i].set(load[0])

            color = load[1]

        self.label[i][0] = tkinter.Label(self.fLabel, text="%d" %(i+1), padx=3)
        self.label[i][0].grid(row=i+1, column = 0, ipady=5)

        self.label[i][1] = tkinter.Button(self.fLabel, textvariable=self.lb_comment[i], padx=3, command=lambda:self.commentLb(i))
        #self.label[i][1].bind("<Return>", self.lostFocus)
        #self.label[i][1].bind("<Enter>", self.lostFocus)

        #self.label[i][1] = tkinter.Label(self.fLabel, text=est_label[i][0], padx=3)
        self.label[i][1].grid(row=i+1, column = 1, ipady=5)

        self.label[i][2] = tkinter.Button(self.fLabel, text="Cor", padx=3, bg=color)
        self.label[i][2]['command'] = lambda : self.changeColor(self.label[i][2], i)
        self.label[i][2].grid(row=i+1, column = 2, ipady=5)
        
        self.btn_addLb.grid(row=i+2, column = 0, ipady=5)
        self.btn_rmLb.grid(row=i+2, column = 2, ipady=5)
            

    def rmLb(self, flag = None):

        if( len(self.label) == 2) and (flag == None):
            #tkinter.messagebox.showwarning("Warning", "You can't delete all the labels. You need at least one to work!")
            #return
            self.btn_rmLb.configure(state="disabled")
            #self.btn_rmLb.grid_remove()

        for i in range(3):
            self.label[-1][i].destroy()

        del self.lb_comment[-1]
        del self.label[-1]

        if(flag == None):
            self.projects.removeLabel()

    def addBind(self):
        ##########
        #Image Bind
        #self.canvas.tag_bind("imgTag", "<Button-1>", self.onClick)

        #self.canvas.tag_bind("imgTag", "<Double-Button-1>", self.onClick)
        #self.canvas.tag_bind("imgTag", "<Motion>", self.motion)
        self.canvas.tag_bind("maskTag", "<Double-Button-1>", self.onClick)
        self.canvas.tag_bind("maskTag", "<Motion>", self.motion)

        self.parent.bind("<Next>", self.moveImg)
        self.parent.bind("<Prior>", self.moveImg)

        self.parent.bind("<MouseWheel>", self.moveImg) #Windows
        self.parent.bind("<Button-4>", self.moveImg) #Linux
        self.parent.bind("<Button-5>", self.moveImg) #Linux
        #print(self.canvas.bbox("imgTag"))
        ##########

        #Label Bind
        
        for i in range(10):
            self.parent.bind(str(i), self.selectLb)
            self.parent.bind("<KP_" + str(i) + ">", self.selectLb) #Linux - Numpad

        
        self.fMain.bind("<Configure>", self.OnFrameConfigureImg)
        self.fLabel.bind("<Configure>", self.OnFrameConfigureLabel)
        self.fUser.bind("<Configure>", self.OnFrameConfigureUser)

        self.parent.bind("<plus>", self.zoom)
        self.parent.bind("<minus>", self.zoom)
        self.parent.bind("<KP_Add>", self.zoom) #Linux - Numpad
        self.parent.bind("<KP_Subtract>", self.zoom) #Linux - Numpad

        #self.canvas.tag_bind("imgTag", "<ButtonPress-3>", self.buttonPress)
        #self.canvas.tag_bind("imgTag", "<B3-Motion>", self.buttonMove)
        #self.canvas.tag_bind("imgTag", "<ButtonRelease-3>", self.buttonRelease)
        self.canvas.tag_bind("maskTag", "<ButtonPress-3>", self.buttonPress)
        self.canvas.tag_bind("maskTag", "<B3-Motion>", self.buttonMove)
        self.canvas.tag_bind("maskTag", "<ButtonRelease-3>", self.buttonRelease)

    def buttonPress(self, event):
        self.canvas.scan_mark(event.x, event.y)

        # self.canvasAtualX = event.x
        # self.canvasAtualY = event.y
        #
        # self.imgAtualX = self.canvas.canvasx(event.x)
        # self.imgAtualY = self.canvas.canvasy(event.y)

        #self.sumDeltaMov = [0,0]
        
        #self.canvas.scan_mark(self.canvasX, self.canvasY)

    def buttonRelease(self, event):
        # self.canvasAtualX = 0
        # self.canvasAtualY = 0
        #
        # self.dragX = self.dragX + self.dX;
        # self.dragY = self.dragY + self.dY;

        '''
        self.canvas.deltaMov[0] = self.canvas.deltaMov[0] + self.sumDeltaMov[0]
        self.canvas.deltaMov[1] = self.canvas.deltaMov[1] + self.sumDeltaMov[1]
        #self.canvas.deltaMov[2] =  0
        '''

        #print(self.dragY, self.dragX)

        #self.atualX = 0;
        #self.atualY = 0;

    def buttonMove(self, event):
        # deltaX = event.x - self.canvasAtualX
        # deltaY = event.y - self.canvasAtualY

        # self.dX = self.canvas.canvasx(event.x) - self.imgAtualX
        # self.dY = self.canvas.canvasy(event.y) - self.imgAtualY

        # self.canvas.move("imgTag", deltaX, deltaY)
        # self.canvas.move("maskTag", deltaX, deltaY)
        #self.canvas.scan_dragto(event.x, event.y, gain=1);

        self.canvas.scan_dragto(event.x, event.y, gain=1)

        '''
        self.sumDeltaMov = [self.sumDeltaMov[0] + deltaX,
                            self.sumDeltaMov[1] + deltaY]
        self.canvas.isMov = True
        '''

        # self.canvasAtualX = event.x
        # self.canvasAtualY = event.y
        
    def changeColor(self, btn, i):
        color = askcolor()

        #print(color)

        if(color[1] == None):
            return
            
        btn.configure(bg=color[1])
        self.projects.updateLabelColor(i, color[1])

    def refresh(self):
        self.canvas.delete("all")

        # self.projects.resetImgScale()

        if(self.projects.getImgScale() != 1):
            self.redraw()
            return

        dimensionImg = self.projects.getDimensionCurrImg()

        self.canvas.config(width=dimensionImg[0], height=dimensionImg[1] )
        self.canvas.image = self.projects.getCurrImg()
        self.canvas.mask = self.projects.getCurrMask()

        tam = [ int(dimensionImg[0] / 2), int(dimensionImg[1] / 2) ]
        # tam = [ dimensionImg[0] / 2, dimensionImg[1] / 2]
        # if( (dimensionImg[0] % 2) > 0):
        #     tam[0] = tam[0] + 1;
        # if( (dimensionImg[1] % 2) > 0):
        #     tam[1] = tam[1] + 1;

        #self.canvas.mask = Image.new('RGBA', dimensionImg, (0,0,0,0))
        #self.canvas.mask = ImageTk.PhotoImage(self.canvas.mask)

        self.canvas.imgID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.image, tags="imgTag")
        self.canvas.maskID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.mask, tags="maskTag")
        self.canvas.pack(fill='both', expand=True)

        # self.dragX = self.canvas.bbox("imgTag")[0];
        # self.dragY = self.canvas.bbox("imgTag")[1];

        self.dX = 0
        self.dY = 0
        '''
        self.canvas.deltaMov = [0,0, 0]
        self.canvas.isMov = False
        '''

        #print(self.canvas.bbox("imgTag"))

        if( self.projects.isBatchImg() ):
            self.projects.updateUserImg()

        self.updateStatus()
        self.parent.title("Teste (%s)" %self.projects.getPathCurrImg() )
        tam = self.projects.TAM
        self.canvas.rect = self.canvas.create_rectangle(self.status.x-tam, self.status.y-tam, self.status.x+tam, self.status.y+tam, outline = "black")

    def redraw(self):
        self.canvas.delete("all")

        dimensionImg = self.projects.getDimensionCurrImg()

        size = int(self.projects.getImgScale() * dimensionImg[0]), int(self.projects.getImgScale() * dimensionImg[1])
        
        self.canvas.image = self.projects.getCurrImgResize(size)
        self.canvas.mask = self.projects.getCurrMaskResize(size)

        tam = [ int(size[0] / 2), int(size[1] / 2)]
        # if( (dimensionImg[0] % 2) > 0):
        #     tam[0] = tam[0] + 1;
        # if( (dimensionImg[1] % 2) > 0):
        #     tam[1] = tam[1] + 1;

        self.canvas.config(width=size[0], height=size[1])

        self.canvas.imgID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.image, tags="imgTag")
        self.canvas.maskID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.mask, tags="maskTag")

        #self.dragX = self.canvas.bbox("imgTag")[0];
        #self.dragY = self.canvas.bbox("imgTag")[1];

        #print(self.canvas.bbox("imgTag"))

        self.dX = 0
        self.dY = 0
        '''
        self.canvas.isMov = False
        self.canvas.deltaMov = [0,0, 0]
        '''

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        #self.imgScrollVertical.config(command=self.canvas.yview)
        #self.imgScrollHorizontal.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.imgScrollHorizontal.set, yscrollcommand=self.imgScrollVertical.set)

        #self.imgScrollVertical.pack(side="right", fill="y")
        #self.imgScrollHorizontal.pack(side="bottom", fill="x")
        self.canvas.pack(fill='both', expand=True)


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
        tam = self.projects.TAM * self.projects.getImgScale()
        rec_x = self.status.x * self.projects.getImgScale()
        rec_y = self.status.y * self.projects.getImgScale()
        self.canvas.rect = self.canvas.create_rectangle(rec_x-tam,  rec_y-tam, rec_x+tam,  rec_y+tam, outline = "black")

    def paint(self):

        dimensionImg = self.projects.getDimensionCurrImg()

        size = int(self.projects.getImgScale() * dimensionImg[0]), int(self.projects.getImgScale() * dimensionImg[1])
        self.canvas.image = self.projects.getCurrImgResize(size)
        self.canvas.mask = self.projects.getCurrMaskResize(size)

        self.canvas.itemconfigure(self.canvas.imgID, image=self.canvas.image)
        self.canvas.itemconfigure(self.canvas.maskID, image=self.canvas.mask)

        #self.canvas.move("imgTag", self.dragX, self.dragY)
        #self.canvas.move("maskTag", self.dragX, self.dragY)

        #self.dragX = self.canvas.bbox("imgTag")[0];
        #self.dragY = self.canvas.bbox("imgTag")[1];

        #self.dX = 0
        #self.dY = 0

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        #self.imgScrollVertical.config(command=self.canvas.yview)
        #self.imgScrollHorizontal.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.imgScrollHorizontal.set, yscrollcommand=self.imgScrollVertical.set)

        #self.imgScrollVertical.pack(side="right", fill="y")
        #self.imgScrollHorizontal.pack(side="bottom", fill="x")
        self.canvas.pack(fill='both', expand=True)


        '''
        if(self.canvas.isMov):
            self.canvas.move("imgTag", self.canvas.deltaMov[0], self.canvas.deltaMov[1])
            self.canvas.move("maskTag", self.canvas.deltaMov[0], self.canvas.deltaMov[1])
            #self.delta[2] = self.canvas.delta[2] + 1

            self.dragX = self.dragX + self.canvas.deltaMov[0];
            self.dragY = self.dragY + self.canvas.deltaMov[1];
            
            #print(self.delta[2])
        '''
        
        

        
#########################################################################
#            Menu Bar Functions
#########################################################################

    def createProj(self):
        createWin= tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge' )
        createWin.title("New Project")
        centralized = [ (self.parent.winfo_screenwidth() // 2) - 175, (self.parent.winfo_screenheight() // 2) - 55 ]
        createWin.geometry('+%d+%d' %(centralized[0], centralized[1]) )
        createWin.resizable(width=False, height=False)
        createWin.focus_force()
        createWin.grab_set()

        newWin_lbProj = tkinter.Label(createWin, text="Project Name: ")
        newWin_lbProj.grid(row = 0, column = 0)
        newWin_lbUser = tkinter.Label(createWin, text="Your Username: ")
        newWin_lbUser.grid(row = 1, column = 0)

        newWin_entProj = tkinter.Entry(createWin)
        newWin_entProj.grid(row = 0, column = 1)
        newWin_entUser = tkinter.Entry(createWin)
        newWin_entUser.grid(row = 1, column = 1)

        newWin_btnOK = tkinter.Button(createWin, text="Confirm", padx=3, bg = "green")
        newWin_btnOK['command'] = lambda btn = [newWin_entProj, newWin_entUser, createWin]: self.newWinConfirm(btn)
        newWin_btnOK.grid(row = 3, column = 0)
        
        newWin_btnCancel = tkinter.Button(createWin, text="Cancel", padx=3, bg = "red", command = createWin.destroy)
        newWin_btnCancel.grid(row = 3, column = 1)
        
    def newWinConfirm(self, info):
        if( (len(info[0].get().replace(" ", "") ) == 0) or (len(info[1].get().replace(" ", "") ) == 0) ):
            tkinter.messagebox.showwarning("Warning", "A field name has been left blank.\nEnter a name in the field before proceeding.")
            return

        self.projects.newProject(info[0].get(), info[1].get())

        info[2].destroy()

        self.loadSettings(True)


    def abrirProj(self):
        filedir = filedialog.askopenfilename(initialdir= self.projects.getAppPath() + "/Projects/",filetypes = [("NeuroNote Project", "*.neuronote")] )
        #filedir = filedialog.askopenfilename(initialdir = "/Projects",filetypes = [("NeuroNote Project", "*.neuronote")] )

        if(len(filedir) > 0):
            #self.dir = os.path.split(filedir)
            self.projects.updateProjectPath(filedir)
            
            self.loadSettings()
        return
    
    def abrir(self, menu = True):

        #testa se foi chamado pelo menu
        if(menu):
            filedir = filedialog.askopenfilename(initialdir= self.projects.lastImagePath ,filetypes = ( ("Jpeg Images", "*.jpg"),
                                                            ("Gif Images","*.gif"),
                                                            ("Png Images","*.png"),
                                                            ("Tiff Images",".*tiff") ) )
                                                            #("All Files", "*.*") ) )
            #testa se o diretório do arquivo está vazio
            if(not filedir):
                return
            
            self.projects.updateImagePaths(filedir)
            self.projects.openImage(filedir)
        else:
            self.projects.updateImagePaths()
            self.projects.openImage()

        self.refresh()
        #self.saveSettings()
        
    def abrirBatch(self, menu = True):

        if(menu):
            dirname = filedialog.askdirectory(initialdir= self.projects.lastImagePath)
            #print(dirname)

            if(not dirname):
                return

        #images_ext = [".jpg",".gif",".png",".tiff"]

            limpar = self.projects.openBatch(dirname)
        else:
            limpar = self.projects.openBatch()

        if ( self.projects.sizeImages() > 0) and (limpar == 0):
            self.refresh()

        #self.saveSettings()

    def saveProjectAs(self):

        res = filedialog.asksaveasfilename(defaultextension=".neuronote", filetypes = ( ("Neuronote Files","*.neuronote"),
                                                         ("All Files", "*.*") ) )
        self.projects.saveProject(res)

    def saveAnnotation(self):
        self.projects.saveAnnotation()

    def loadComments(self):

        """
        if(flag == None):
            ini_dir = self.dirLoadComments.split("/")
            del ini_dir[-1]
            
            res = filedialog.askopenfilename(initialdir= "/".join(ini_dir) + "/" ,filetypes = [ ("Text Files","*.txt") ] )
        else:
            res = self.dirLoadComments

        file = open(res,"r")

        lines = file.read().splitlines()
        """
        
        self.btn_rmLb.configure(state="disabled")


        for i in range(len(self.label) ):
            self.rmLb(1)

        del self.lb_comment[:]
        self.lb_label = []

        for i in range( self.projects.sizeLabels() ):
            self.addLb( self.projects.getLabels(i) )

        #self.dirLoadComments = res

        #self.saveSettings()
        #file.close()

        #self.mnuArquivo.entryconfig("Save Comments", state="normal")

    def nada(self):
        pass
     
    def sobre(self):
        pass
         
    def sair(self):
        ans = tkinter.messagebox.askquestion("Quit", "Are you sure?", icon='warning')

        if ans == 'yes':
            #self.destroy()
            self.parent.destroy()

        
#########################################################################
#            Binds Functions
#########################################################################

    def OnFrameConfigureImg(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def OnFrameConfigureLabel(self, event):
        self.lbCanvas.configure(scrollregion=self.lbCanvas.bbox("all"))

    def OnFrameConfigureUser(self, event):
        self.userCanvas.configure(scrollregion=self.userCanvas.bbox("all"))

    def lostFocus(self, event):
        self.fLabel.focus()

    def lostFocus2(self, event):
        self.fUser.focus()

    def selectLb(self, event):
        if(event.keysym[0] == 'K'):
            key = int(event.keysym.split('_')[1]) - 1
        else:
            key = int(event.keysym) - 1

        if(key == -1):
            key = 9
        #print("Selecionado Label #%d" %(key) )

        if(key >= self.projects.sizeLabels()):
            return
        
        if( (self.projects.getSelectedLb() > -1) and (self.projects.getSelectedLb() != key) ):
            self.label[self.projects.getSelectedLb()][0].configure(relief='flat')
            self.label[self.projects.getSelectedLb()][1].configure(relief='flat')
            self.label[self.projects.getSelectedLb()][2].configure(relief='flat')
            
            
        self.label[key][0].configure(relief='solid')
        self.label[key][1].configure(relief='solid')
        self.label[key][2].configure(relief='solid')

        self.projects.setSelectedLb(key)
        
    def onClick(self, event):

        #print("######")

        # x = self.canvas.canvasx(event.x) - self.dragX;
        # y = self.canvas.canvasy(event.y) - self.dragY;

        if( (event.x < 10) or (event.y < 10)):
            return

        if( (event.x > (self.canvas.winfo_width() - 10)) or (event.y > (self.canvas.winfo_height() - 10)) ):
            return

        x = int(self.canvas.canvasx(event.x) / self.projects.getImgScale())
        y = int(self.canvas.canvasy(event.y) / self.projects.getImgScale())

        #print(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        #print(self.dragX, self.dragY)
        #print(self.canvas.coords("imgTag"))
        #print(self.canvas.deltaMov)
        #print(self.canvas.canvasx(self.delta[0]), self.canvas.canvasy(self.delta[1]))
        #print(self.canvas.canvasx(self.delta[0]) - (self.delta[0]*self.delta[2]), self.canvas.canvasy(self.delta[1]) - (self.delta[1]*self.delta[2]))

        '''
        #Para corrigir coordenadas quando refaz o movimento ao pintar a imagem
        if(self.mudanca):
            x = x - (self.dragX*self.delta[2])
            y = y - ( (self.dragY-2) * self.delta[2])
        '''

        if( (x < 0) or (y < 0) ):
            return

        #limite = [self.canvas.bbox("imgTag")[2] - self.canvas.bbox("imgTag")[0] - 1, self.canvas.bbox("imgTag")[3] - self.canvas.bbox("imgTag")[1] -1 ]
        limite = [(self.canvas.bbox("imgTag")[2] / self.projects.getImgScale()) - 1, (self.canvas.bbox("imgTag")[3] / self.projects.getImgScale()) - 1]
        if( (x > limite[0]) or (y > limite[1]) ):
            return

        if ( self.projects.getSelectedLb() < 0 ):
            print("não está selecionado")
            return

        colorHex = self.projects.getLabels(self.projects.getSelectedLb())[1]

        colorRGB = tuple(int(colorHex.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))

        #x = self.canvas.canvasx(event.x);
        #y = self.canvas.canvasy(event.y);
        
        print ("%d, %d" %(x, y) )

        mask = self.projects.getMask(self.projects.getCurrImgID())
        annotation = self.projects.getAnnotation(self.projects.getCurrImgID())

        tam = self.projects.TAM

        coord = self.projects.applyWatershed([x,y])

        limite_x = max(0, x-tam)
        limite_y = max(0, y-tam)

        for i in range(len(coord)):
            if(len(coord[i]) > 0):
                for c in coord[i]:
                    m = self.projects.getMask(i)
                    a = self.projects.getAnnotation(i)
                    m.putpixel( (limite_x + c[0], limite_y + c[1]), colorRGB )
                    a.putpixel( (limite_x + c[0], limite_y + c[1]), self.projects.getSelectedLb() + 1)
                self.projects.setMask(i, m)
                self.projects.setAnnotation(i, a)
                
        '''
        # self.projects.setImage(self.projects.getCurrImgID(),img)
        self.projects.setMask(self.projects.getCurrImgID(), mask)
        self.projects.setAnnotation(self.projects.getCurrImgID(), annotation)
        '''
        self.paint()

    def motion(self, event):

        # x = (self.canvas.canvasx(event.x) - self.dragX) / self.projects.getImgScale()
        # y = (self.canvas.canvasy(event.y) - self.dragY) / self.projects.getImgScale()

        if( (event.x < 10) or (event.y < 10)):
            return

        if( (event.x > (self.canvas.winfo_width() - 10)) or (event.y > (self.canvas.winfo_height() - 10)) ):
            return

        self.eventX = event.x
        self.eventY = event.y

        x = self.canvas.canvasx(event.x) / self.projects.getImgScale()
        y = self.canvas.canvasy(event.y) / self.projects.getImgScale()

        if( (x < 0) or (y < 0) ):
            return

        #limite = [self.canvas.bbox("imgTag")[2] - self.canvas.bbox("imgTag")[0] - 1, self.canvas.bbox("imgTag")[3] - self.canvas.bbox("imgTag")[1] -1 ]
        limite = [ (self.canvas.bbox("imgTag")[2] / self.projects.getImgScale()) - 1, (self.canvas.bbox("imgTag")[3] / self.projects.getImgScale()) - 1]

        if( (x > limite[0]) or (y > limite[1]) ):
            return

        self.status.x = x
        self.status.y = y

        #x = self.canvas.canvasx(event.x);
        #y = self.canvas.canvasy(event.y);

        #print(self.canvas.bbox("imgTag"));
        tam = self.projects.TAM * self.projects.getImgScale()
        self.canvas.coords(self.canvas.rect, self.canvas.canvasx(event.x)-tam, self.canvas.canvasy(event.y)-tam, self.canvas.canvasx(event.x)+tam, self.canvas.canvasy(event.y)+tam)
        
        self.updateStatus()
        #self.status.pack()

    def updateStatus(self):
        if (self.projects.isBatchImg()):
            self.status.configure(text=("X: %d \t Y: %d \t Z: %d / %d \t\t Scale: %d%%" % (self.status.x, self.status.y, self.projects.getCurrImgID() + 1, self.projects.sizeImages(), self.projects.getImgScale() * 100)))
        else:
            self.status.configure(text=("X: %d \t Y: %d \t\t Scale: %d%%" % (self.status.x, self.status.y, self.projects.getImgScale() * 100)))

    def moveImg(self, event):
        #print(self.currImg)
        #print(event)
        change = 0
        if (event.keysym == "Next") or (event.delta < 0) or (event.num == 5):
            if( self.projects.getCurrImgID()  > 0):
                self.projects.updateCurrImg("sub")
                change = 1
        if (event.keysym == "Prior") or (event.delta > 0) or (event.num == 4):
            if self.projects.getCurrImgID() < self.projects.sizeImages()-1:
                self.projects.updateCurrImg("add")
                change = 1
        #print(self.currImg)
        if change == 1:
            self.refresh()

    
    def zoom(self,event):
        if( (event.keysym == "plus") or (event.keysym == "KP_Add") ):
            res = self.projects.increaseImgScale()
        else:
            res = self.projects.decreaseImgScale()

        if(res):
            #self.dragX = 0;
            #self.dragY = 0;
            self.redraw()

#########################################################################
#########################################################################
if __name__ == "__main__":
    root = tkinter.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.title('Teste')

    root.minsize(750,340)
    
    #root.geometry('1000x700') #ativado para testes
    #root.resizable(width=False, height=False)
    
    app = win_main(root)
    app.mainloop()
