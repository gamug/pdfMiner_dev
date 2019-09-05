import sys, os, psutil, time, threading
import pandas as pd
from exploreText import exploreText, textClassifier
from toolBox.collections import structureEnglish, structureSpanish
from toolBox.collections import filter1, filter2
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
        self.state = scrolledtext.ScrolledText(self.frame2, undo=True, relief=RIDGE, bg='black', fg='white',
                                               height=self.height, width=int(3 * self.width / 4))
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
            self.label_filter['text'] = self.describe_filter[self.comb_filter.get()]
        else:
            self.label_filter['text'] = 'This feature is still under development phase'

    def aceptFilter(self):
        self.filter = self.comb_filter.get()
        self.emerg_filter.destroy()
        return

    def selectFilter(self):
        self.emerg_filter = Toplevel(self.root)
        self.filter = None

        self.emerg_filter.resizable(0, 0)
        self.emerg_filter.title('Select filter')
        self.emerg_filter.iconbitmap(os.path.join(os.path.dirname(sys.executable)), 'textMiner.ico')
        self.emerg_filter.geometry(f'{int(self.width/2)}x{int(self.height/1.9)}')

        self.frame_filter = Frame(self.emerg_filter, bg='black', width = int(self.width/2),
                                  height = int(self.height/1.9), padx = 20, pady = 20)
        self.frame_filter.grid_propagate(False)

        self.comb_filter = ttk.Combobox(self.frame_filter, state="readonly")
        self.comb_filter['values'] = ['Default', 'Complex', 'Proj Issues', 'Personalized']
        self.comb_filter.set('Default')
        self.comb_filter.bind('<<ComboboxSelected>>', self.bindFilter)

        self.but_filter =  Button(self.frame_filter, command = self.aceptFilter, bg = 'Black', fg = 'white',
                                  font = ("comic sans ms", 10), text = 'selectFilter')

        describe_filter = self.describe_filter['Default']
        self.label_filter = Label(
            self.frame_filter, bg = 'black', fg = 'white', font = ("comic sans ms", 10),
            text = describe_filter, justify = LEFT, anchor = NW, relief=RIDGE, padx = 10, pady = 10,
            wraplength = int(0.25*self.width), width = int(self.width/30), height = int(self.height/44)
        )

        self.frame_filter.grid(row = 0, column = 0)
        self.comb_filter.grid(row=0, column=0)
        self.frame_filter.grid_columnconfigure(1, pad = 40)
        self.frame_filter.grid_rowconfigure(1, pad = 40)
        self.but_filter.grid(row = 1, column = 0)
        self.label_filter.grid(row = 0, column = 1, rowspan=2)
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
        self.state.insert(END, '\n'+text)
        self.state.config(state=DISABLED)

    def _mainloop_(self):
        self.root.mainloop()