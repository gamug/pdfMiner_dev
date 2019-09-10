import sys, os, psutil, time, threading, re
import pandas as pd
import numpy as np
from exploreText import exploreText, textClassifier
from toolBox.collections import structureEnglish, structureSpanish
from toolBox.collections import filter1, filter2
from toolBox._classes import resultSearched
from toolBox.codeUpgrader import upgradeCode
import PyQt5
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from tkinter.simpledialog import askstring
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter import messagebox
from win32api import GetSystemMetrics


class textMiner():
    def __init__(self):
        self.width = int(GetSystemMetrics(0) * 0.7)
        self.height = int(GetSystemMetrics(1) * 0.7)
        self.root = Tk()
        self.root.resizable(0, 0)
        self.root.title('textMiner V 0.0 pre-alpha - state: developing pdfMiner post-processing')
        self.root.geometry(f'{self.width}x{self.height}')
        self.root.iconbitmap(os.path.join(os.path.dirname(sys.executable)),'textMiner.ico')
        self.personalized = 'Create your filter!!'
        self.placeWidgets()
        descr_en = []
        descr_es = []
        for filter_en, filter_es in zip(structureEnglish, structureSpanish):
            for filter in filter_en:
                descr_en.append(filter.symbol)
            for filter in filter_es:
                descr_es.append(filter.symbol)
        self.describe_filter = {
            'Default': f"This filter was designed to search in english and spanish papers.\n\n"
                       f"Describers: {str(descr_en).replace('[','').replace(']','')}\n\n"
                       f"Words: About {len(descr_en)*2}",
            'Complex': f"Search complexity in documents\n\n"
                       f"Descibers: {filter1[0][0].symbol}\n\n"
                       f"Words: {str(filter1[0][0].words).replace('[','').replace(']','')}",
            'Proj Issues': f"Search project issues in documents\n\n"
                       f"Descibers: {filter2[0][0].symbol}\n\n"
                       f"Words: {str(filter2[0][0].words).replace('[','').replace(']','')}"
        }
        # let's upgrade code
        upgradeCode(self.state)

    def placeWidgets(self):
        self.frame1 = Frame(self.root, bg='black', height=self.height, width=int(self.width / 4))
        self.frame1.pack_propagate(False)
        self.FpdfMiner = LabelFrame(self.frame1, text=r'pdfMiner', bg='black', relief=RIDGE,
                                    height=int(self.height / 3), width=int(self.width / 4), fg='white',
                                    font=("comic sans ms", 13, "bold"))
        self.FpdfMiner.pack_propagate(False)
        self.BpdfMiner1 = Button(self.FpdfMiner, command=self.auxFunc,
                                bg='Black', fg='white', font=("comic sans ms", 10), text='filterApply')
        self.BpdfMiner2 = Button(self.FpdfMiner, command=self.structureAnalysis,
                                bg='Black', fg='white', font=("comic sans ms", 10), text='sintaxStructure')
        self.frame2 = Frame(self.root, bg='black', height=self.height, width=int(3 * self.width / 4))
        self.frame2.pack_propagate(False)
        self.state = scrolledtext.ScrolledText(
            self.frame2, undo=True, relief=RIDGE, bg='black', fg='white', padx=20, pady=20, height=self.height,
            width=int(3 * self.width / 4), font=("comic sans ms", 10)
        )
        self.state['font'] = ("comic sans ms", 12)
        self.state.pack(expand=True, fill='both')
        #         self.state.insert(END, text)
        #         self.state.config(state=DISABLED)
        # Packing all
        self.FpdfMiner.pack(side=TOP)
        self.BpdfMiner1.pack(side=TOP)
        self.BpdfMiner2.pack(side=TOP)
        self.frame1.pack(side=LEFT)
        self.frame2.pack(side=LEFT)
        self.state.pack(side=LEFT)

    def pdfMiner(self):
        # and here we run pdfExplorer
        database = exploreText(self.workPath, self.state, self.filter)  # creating explorePDF object
        database.main()
        self.setState('********************************************')
        self.setState('database analized')
        self.setState('********************************************')

    def bindFilter(self, event=None):
        if self.comb_filter.get()!='Personalized':
            self.label_filter.grid(row=0, column=1, rowspan=4)
            self.but_addFilt.grid_forget()
            self.but_editFilt.grid_forget()
            for widget in self.words_collect:
                widget.grid_forget()
            self.cond1.grid_forget(), self.cond2.grid_forget(), self.cond3.grid_forget(), self.cond4.grid_forget()
            self.cond5.grid_forget(), self.cond6.grid_forget(), self.cond7.grid_forget(), self.cond8.grid_forget()
            self.words.grid_forget()
            self.label_filter['text'] = self.describe_filter[self.comb_filter.get()]
        else:
            self.label_filter.grid_forget()
            self.words.grid(column = 0, row = 0, columnspan = 6, pady=10)
            self.words.configure(state = NORMAL)
            self.words.insert(END, self.personalized)
            self.words.configure(state = DISABLED)
            self.var1.grid(column = 0, row = 1)
            self.cond1.grid(column = 1, row = 1)
            self.var2.grid(column = 2, row = 1)
            self.cond2.grid(column = 3, row=1)
            self.var3.grid(column = 4, row = 1)
            self.cond3.grid(column = 5, row = 1)
            self.var4.grid(column = 0, row = 2)
            self.cond4.grid(column = 1, row = 2)
            self.var5.grid(column = 2, row = 2)
            self.cond5.grid(column = 3, row = 2)
            self.var6.grid(column = 4, row = 2)
            self.cond6.grid(column = 5, row = 2)
            self.var7.grid(column = 0, row = 3)
            self.cond7.grid(column = 1, row = 3)
            self.var8.grid(column = 2, row = 3)
            self.cond8.grid(column = 3, row = 3)
            self.var9.grid(column = 4, row = 3)
            self.but_addFilt.grid(column = 0, row = 4, columnspan = 2, pady = 10)
            self.but_editFilt.grid(column = 2, row = 4, columnspan = 2, pady = 10)
            self.but_clearBoxes.grid(column = 4, row = 4, columnspan = 2, pady = 10)

    def aceptFilter(self):
        if self.comb_filter.get() != 'Personalized':
            self.filter = self.comb_filter.get()
            self.emerg_filter.destroy()
            return
        else:
            aux = self.words.get('1.0', END).replace('\n', '')
            aux = aux.split(' and '); aux = [vec.split(' or ') for vec in aux]
            for i in range(len(aux)):
                aux[i] = [re.sub('^ {1,}', '', re.sub(r' {1,}$', '', word)) for word in aux[i]]
            self.filter = [[resultSearched(words, words[0])] for words in aux]
            self.emerg_filter.destroy()
            return

    def addFilter(self):
        words_aux = np.array([widget.get().replace('\n', '') for widget in self.words_collect],dtype=np.str)
        words_aux = np.delete(words_aux,np.where(words_aux==''))
        words_aux = ' or '.join(words_aux)
        if len(words_aux)>0:
            if self.words.get(1.0, END).replace('\n','')=='Create your filter!!':
                aux = ''
            else:
                aux = self.words.get(1.0, END).replace('\n', ' and ')
            self.words.configure(state = NORMAL)
            self.words.delete(1.0, END)
            self.words.insert(END, aux+words_aux)
            self.words.configure(state = DISABLED)
            self.personalized = self.words.get(1.0, END).replace('\n', '')

    def clearBoxes(self):
        for widget in self.words_collect:
            widget.delete(0, END)
        self.words_collect[0].focus_set()

    def selectAll(self):
        if self.vari0.get() == True:
            for widget in self.checkbut:
                widget.select()
        else:
            for widget in self.checkbut:
                widget.deselect()

    def delFilter(self):
        aux = np.array([var.get() for var in self.vari])
        words = np.array(self.words.get(1.0, END).replace('\n', '').split(' and '), dtype = np.str)
        words = np.delete(words, np.where(aux == True))
        self.personalized = ' and '.join(words)
        self.words.configure(state=NORMAL)
        self.words.delete(1.0, END)
        self.words.insert(END, self.personalized)
        self.words.configure(state=DISABLED)
        self.emerg_editfilter.destroy()
        self.emerg_filter.deiconify()

    def deleteEditFilter(self):
        self.emerg_editfilter.destroy()
        self.emerg_filter.deiconify()

    def editFilter(self):
        self.emerg_filter.withdraw()
        aux = self.words.get(1.0, END).replace('\n', '').split(' and ')
        self.emerg_editfilter = Toplevel(self.root, bg = 'black')
        self.emerg_editfilter.resizable(0, 0)
        self.emerg_editfilter.title('Select filter to remove')
        self.emerg_editfilter.iconbitmap(os.path.join(os.path.dirname(sys.executable)), 'textMiner.ico')
        self.emerg_editfilter.geometry(f'{int(self.width/2)}x{int(self.height/1.9)}')
        self.emerg_editfilter.protocol("WM_DELETE_WINDOW", self.deleteEditFilter)
        self.emerg_editfilter.attributes("-topmost", True)
        self.frame_editfil = Frame(self.emerg_editfilter, bg='black', width=int(self.width * 1 / 8),
                                  height=int(self.height / 1.9), padx=20, pady=20)
        self.frame_editfil.grid_propagate(False)
        self.frame_wordsfil = Frame(self.emerg_editfilter, bg='black', width=int(self.width * 3 / 8),
                                   height=int(self.height / 1.9), padx=20, pady=20)
        self.frame_wordsfil.grid_propagate(False)
        self.but_delfilt = Button(self.frame_editfil, command=self.delFilter, bg='Black', fg='white',
                                   font=("comic sans ms", 10), text='delFilter')
        self.but_delfilt.grid(row = 0, column = 0)
        self.vari0 = BooleanVar()
        checkbut0 = Checkbutton(self.frame_wordsfil, text = 'Select all', variable = self.vari0, bg = 'black', fg = 'gray',
                                font=("comic sans ms", 10, 'bold'), command = self.selectAll, relief=RIDGE,)
        self.vari, self.checkbut = [], []
        if len(aux)==1:
            vari1 = BooleanVar()
            checkbut1 = Checkbutton(self.frame_wordsfil, text = aux[0], variable = vari1, bg = 'black', fg = 'gray',
                                    relief = RIDGE,)
            self.checkbut.append(checkbut1)
            self.vari.append(vari1)
            checkbut0.grid(row=0, column=1, sticky = NW)
            checkbut1.grid(row=1, column=1, sticky = NW)
        else:
            checkbut0.grid(row=0, column=1, sticky = NW)
            for i in range(len(aux)):
                vari = BooleanVar()
                if len(aux[i])>35:
                    text = f'{aux[i][0:35]}...'
                else:
                    text = aux[i]
                checkbutt = Checkbutton(self.frame_wordsfil, text = text, variable = vari, bg = 'black',
                                        fg = 'gray', relief=RIDGE)
                self.checkbut.append(checkbutt)
                self.vari.append(vari)
                checkbutt.grid(row=i+1, column=1, sticky = NW)

        self.frame_editfil.grid(row = 0, column = 0, padx = 20)
        self.frame_wordsfil.grid(row = 0, column = 1, padx = 20)


        self.emerg_editfilter.wait_window()

    def selectFilter(self):
        self.emerg_filter = Toplevel(self.root)
        self.filter = None
        self.emerg_filter.attributes("-topmost", True)
        self.emerg_filter.resizable(0, 0)
        self.emerg_filter.title('Select filter')
        self.emerg_filter.iconbitmap(os.path.join(os.path.dirname(sys.executable)), 'textMiner.ico')
        self.emerg_filter.geometry(f'{int(self.width/2)}x{int(self.height/1.9)}')

        self.frame_filter = Frame(self.emerg_filter, bg='black', width = int(self.width * 3 / 16),
                                  height = int(self.height/1.9), padx = 20, pady = 20)
        self.frame_filter.grid_propagate(False)

        self.frame_display = Frame(self.emerg_filter, bg='black', width = int(self.width * 5 / 16),
                                  height = int(self.height/1.9), padx = 20, pady = 20)
        self.frame_display.grid_propagate(False)

        self.comb_filter = ttk.Combobox(self.frame_filter, state="readonly")
        self.comb_filter['values'] = ['Default', 'Complex', 'Proj Issues', 'Personalized']
        self.comb_filter.set('Default')
        self.comb_filter.bind('<<ComboboxSelected>>', self.bindFilter)

        self.but_filter =  Button(self.frame_filter, command = self.aceptFilter, bg = 'Black', fg = 'white',
                                  font = ("comic sans ms", 10), text = 'selectFilter')

        describe_filter = self.describe_filter['Default']
        self.label_filter = Label(
            self.frame_display, bg = 'black', fg = 'white', font = ("comic sans ms", 10),
            text = describe_filter, justify = LEFT, anchor = NW, relief=RIDGE, padx = 10, pady = 10,
            wraplength = int(0.25*self.width), width = int(self.width/30), height = int(self.height/44)
        )

        self.but_addFilt = Button(self.frame_display, command = self.addFilter, bg = 'Black', fg = 'white',
                                  font = ("comic sans ms", 10), text = 'addFilter')
        self.but_editFilt = Button(self.frame_display, command=self.editFilter, bg='Black', fg='white',
                                  font=("comic sans ms", 10), text='editFilter')
        self.but_clearBoxes = Button(self.frame_display, command=self.clearBoxes, bg='Black', fg='white',
                                   font=("comic sans ms", 10), text='clearBoxes')
        self.words = scrolledtext.ScrolledText(
            self.frame_display, undo=True, relief=RIDGE, bg='black', fg='white', padx=10, pady=5,
            height=int(self.height/100), width=int(3 * self.width / 110), font=("comic sans ms", 10)
        )

        width = width=int(3 * self.width / 380)
        self.var1 = ttk.Entry(self.frame_display, font=("comic sans ms", 10), width = width)
        self.cond1 = ttk.Entry(self.frame_display, font=("comic sans ms", 10, 'bold'), width = 2)
        self.cond1.insert(0, 'or')
        self.cond1.configure(state = "readonly")
        self.var2 = ttk.Entry(self.frame_display, font=("comic sans ms", 10), width = width)
        self.cond2 = ttk.Entry(self.frame_display, font=("comic sans ms", 10, 'bold'), width=2)
        self.cond2.insert(0, 'or')
        self.cond2.configure(state="readonly")
        self.var3 = ttk.Entry(self.frame_display, font=("comic sans ms", 10), width = width)
        self.cond3 = ttk.Entry(self.frame_display, font=("comic sans ms", 10, 'bold'), width=2)
        self.cond3.insert(0, 'or')
        self.cond3.configure(state="readonly")
        self.var4 = ttk.Entry(self.frame_display, font=("comic sans ms", 10), width = width)
        self.cond4 = ttk.Entry(self.frame_display, font=("comic sans ms", 10, 'bold'), width=2)
        self.cond4.insert(0, 'or')
        self.cond4.configure(state="readonly")
        self.var5 = ttk.Entry(self.frame_display, font=("comic sans ms", 10), width = width)
        self.cond5 = ttk.Entry(self.frame_display, font=("comic sans ms", 10, 'bold'), width=2)
        self.cond5.insert(0, 'or')
        self.cond5.configure(state="readonly")
        self.var6 = ttk.Entry(self.frame_display, font=("comic sans ms", 10), width = width)
        self.cond6 = ttk.Entry(self.frame_display, font=("comic sans ms", 10, 'bold'), width=2)
        self.cond6.insert(0, 'or')
        self.cond6.configure(state="readonly")
        self.var7 = ttk.Entry(self.frame_display, font=("comic sans ms", 10), width = width)
        self.cond7 = ttk.Entry(self.frame_display, font=("comic sans ms", 10, 'bold'), width=2)
        self.cond7.insert(0, 'or')
        self.cond7.configure(state="readonly")
        self.var8 = ttk.Entry(self.frame_display, font=("comic sans ms", 10), width = width)
        self.cond8 = ttk.Entry(self.frame_display, font=("comic sans ms", 10, 'bold'), width=2)
        self.cond8.insert(0, 'or')
        self.cond8.configure(state="readonly")
        self.var9 = ttk.Entry(self.frame_display, font=("comic sans ms", 10), width = width)
        self.words_collect = [self.var1, self.var2, self.var3, self.var4, self.var5, self.var6, self.var7,
                              self.var8, self.var9]

        self.frame_filter.grid(row = 0, column = 0)
        self.frame_display.grid(row=0, column=1)
        self.comb_filter.grid(row=0, column=0)
        self.frame_filter.grid_columnconfigure(1, pad = 40)
        self.frame_filter.grid_rowconfigure(1, pad = 40)
        self.but_filter.grid(row = 1, column = 0)
        self.label_filter.grid(row = 0, column = 1)
        self.emerg_filter.wait_window()
        return


    def auxFunc(self):
        self.proceed = askstring(r'Confirm transaction', r'Reports will be erase, do you want proceed? (y/n):')
        process = threading.Thread(name='pdfMiner', target=self.pdfMiner, daemon=True)
        if len(re.findall(r'y.*', self.proceed, re.IGNORECASE)) > 0:
            self.selectFilter()
            if self.filter == None:
                self.setState('process rejected')
                return
            else:
                self.workPath = askdirectory(initialdir="/", title="Select directory where database is located")
                try:
                    os.makedirs(os.path.join(self.workPath, r'reports'))
                except:
                    try:
                        os.remove(os.path.join(self.workPath, r'reports\consolidate.csv'))
                        os.remove(os.path.join(self.workPath, r'reports\rejected.txt'))
                    except:
                        pass
        else:
            self.setState('process rejected')
            return
        process.start()

    def textClassify(self):
        self.setState('Charging csv')
        df=pd.read_csv(self.dir,header=0,index_col=0)
        self.setState('done')
        if not 'TEXT' in df.axes[1]:
            self.setState("Wrong database structure, data wasn't analyzed")
            return
        aux = textClassifier(self.state)
        i = -1
        for text in df['TEXT']:
            i += 1
            self.setState(f"\n\n\n{i+1} progress {round((i)*100/len(df['TEXT']),2)}%")
            self.setState(f"Analizing paragraph '{text[0:int(len(text)*0.5)]}...':")
            aux.proccessText(text)
            if i == 0:
                aux.result.to_csv(os.path.join(os.path.dirname(self.dir),'textClassified.csv'))
            else:
                aux.result.to_csv(os.path.join(os.path.dirname(self.dir),'textClassified.csv'),mode='a',header=False)
        self.setState('********************************************')
        self.setState('database analized')
        self.setState('********************************************')

    def structureAnalysis(self):
        self.proceed = askstring(r'Confirm transaction', r'Reports will be erase, do you want proceed? (y/n):')
        process = threading.Thread(name='textClassify', target=self.textClassify, daemon=True)
        # charging text database
        if len(re.findall(r'y.*', self.proceed, re.IGNORECASE)) > 0:
            self.dir = askopenfilename(filetypes=[("csv files", ".csv")],
                                  title="Choose a file.")
            try:
                os.makedirs(os.path.join(dir, r'reports'))
            except:
                try:
                    os.remove(os.path.join(os.path.dirname(self.dir), 'textClassified.csv'))
                except:
                    pass
        else:
            self.setState('process rejected')
            return
        process.start()

    def setState(self, text):
        self.state.config(state=NORMAL)
        self.state.insert(END, '\n' + text)
        self.state.config(state=DISABLED)

    def _mainloop_(self):
        self.root.mainloop()