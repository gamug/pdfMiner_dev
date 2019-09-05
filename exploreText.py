import fitz, os, sys, re, spacy
from tkinter import *
from langdetect import detect
# import filtering structures
from toolBox.collections import structureEnglish, structureSpanish, petroleum_companies, engineer_companies
from toolBox.collections import filter1, filter2
from toolBox.codeUpgrader import whatsNew
from toolBox._classes import entGetter
from appInterface._classes import HyperlinkManager
import numpy as np
import pandas as pd
from googletrans import Translator
from nltk.stem.snowball import SnowballStemmer
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
import xlwings as xw
import en_core_web_sm
import fr_core_news_sm
import es_core_news_sm
import pt_core_news_sm
import it_core_news_sm


# This is main class to search into PDF
class exploreText():
    def __init__(self, workPath, state, filter, consolidate=True):
        self.workPath = workPath
        self.state = state
        self.filter = filter
        self.consolidate = consolidate
        self.rejected=[]

    def main(self):
        '''''
        This function let user analize all PDF in database.
            Input:
                workPath: This path refers to a PDF database path
                consolidate: It determine export type. Default: True
                    True: Put all PDF analysis in the same excel file
                    False: Create a report by PDF file explored
            Output:
                None: save report in self.workPath\reports as excel file
        '''''
        self.state.config(state=NORMAL)
        self.state.delete(1.0,END)
        hyperlink = HyperlinkManager(self.state)
        self.setState('********************************************')
        whatsNew(self.state, hyperlink)
        self.setState('********************************************\n')
        self.state.config(state=DISABLED)
        self.n = -1
        self.pdfFiles=os.listdir(self.workPath)
        self.filesCount=0
        for file in self.pdfFiles:
            extention=file.split('.')[len(file.split('.'))-1]
            if extention=='pdf':
                self.filesCount=self.filesCount+1
        for fileName in self.pdfFiles:
            if fileName.split('.')[len(fileName.split('.')) - 1] == 'pdf':
                self.n = self.n + 1
                if self.n == 0:
                    header = True
                else:
                    header = False
                if self.consolidate == False:
                    self.readPDF(os.path.join(self.workPath, r'reports'), os.path.join(self.workPath, fileName))
                else:
                    summary = self.readPDF(os.path.join(self.workPath, r'reports'),
                                           os.path.join(self.workPath, fileName))
                    try:
                        summary.to_csv(os.path.join(self.workPath, 'reports', 'consolidate.csv'),
                                       mode='a', header=header)
                    except:
                        pass
        if len(self.rejected) > 0:
            with open(os.path.join(self.workPath, r'reports\rejected.txt'), 'w') as f:
                f.write(str(self.rejected))
                f.close()
        if self.consolidate == True:
            summary=pd.read_csv(os.path.join(self.workPath, 'reports', 'consolidate.csv'),sep=',')
            summary.rename({'Unnamed: 0':'pdfcount'},axis='columns',inplace=True)
            summary.to_csv(os.path.join(self.workPath, 'reports', 'consolidate.csv'), mode='w',sep=',')
        return False

    def readPDF(self, workPath, pdfName):
        '''''
        This function is base to open, process and export PDF database analysis
            Input:
                workPath: This path refers to a PDF database path
                pdfName: This is the PDF full path
                consolidate: It determine export type. Default: True
                    True: Put all PDF analysis in the same excel file
                    False: Create a report by PDF file explored
            Output:
                return summary as a pandas consolidate information
        '''''
        fileName = os.path.basename(pdfName)[0:len(os.path.basename(pdfName)) - 4]
        self.setState(f'Advance: {str(round(self.n*100/self.filesCount,2))} %')
        self.setState(fileName)
        try:
            self.setState(f'Opening: {pdfName}...')
            pdf_reader = fitz.open(pdfName)
            self.setState('Success\n')
        except:
            self.setState('Opening failed, adding to rejected...\n')
            self.rejected.append(f'{os.path.basename(pdfName)[0:len(os.path.basename(pdfName)) - 4]}: corrupted file')
            return 1
        summary = pd.DataFrame(columns=['PDFNAME', 'PAGE', 'PARAGRAPH', 'WORDS', 'TEXT'])
        structure = self.getStructure(pdf_reader, fileName)  # Defining filtering structure
        try:
            structure[0][0].symbol
        except:
            return 1
        for page in range(pdf_reader.pageCount):
            i = 0
            paragraphs = pdf_reader.loadPage(page).getText("text").split('\n')
            paragraphs = self.clarify(paragraphs)
            for paragraph in paragraphs:
                words = paragraph.split(' ')
                i = i + 1
                if len(words) > 5:
                    result, boolvalues = self.boolean(words, structure)
                    if result:
                        aux = pd.DataFrame.from_dict({'PDFNAME': [fileName], 'PAGE': [page + 1], 'PARAGRAPH': [i],
                                                      'WORDS': [self.countWords(boolvalues, structure)],
                                                      'TEXT': [paragraph]})
                        summary = summary.append(aux)
        summary = summary.reset_index(drop=True)
        if self.consolidate == False:
            summary.reset_index(drop=False, inplace=True)
            summary.to_csv(os.path.join(self.workPath, 'reports', fileName + '.csv'),sep=',')
        pdf_reader.close()
        return summary

    def clarify(self, array):
        '''''
        As split function in PDF page doesn't have expected results we define this function to 
        to try make some sense in page's text.
            Input:
                array: page text splited by "\n" wich result in row split
            Output:
                return: ordered page's text in paragraphs.
        '''''
        paragraphs = []
        aux = True;
        count = -1;
        i = 0;
        while count < len(array)-1:
            paragraphs.append(' ')
            aux = True
            while count < len(array)-1 and aux == True:
                count = count + 1
                if len(array[count]) > 4:
                    if paragraphs[i][len(paragraphs[i]) - 1] == r'-':
                        paragraphs[i] = paragraphs[i][0:len(paragraphs[i]) - 1] +str(array[count])
                    elif paragraphs[i][len(paragraphs[i]) - 2] == r'-':
                        paragraphs[i] = paragraphs[i][0:len(paragraphs[i]) - 2] + str(array[count])
                    else:
                        paragraphs[i] = paragraphs[i] + r' ' + array[count]
                    if r'.' in array[count][len(array[count]) - 3:len(array[count])] or\
                       r':' in array[count][len(array[count]) - 3:len(array[count])]:
                        paragraphs[i]=paragraphs[i].replace(';',',')
                        i = i + 1
                        aux = False
        return paragraphs

    def boolean(self, words, structure):
        '''''
        this function check words and process criterion to acept a paragraph
            input:
                words: words from a paragraph
                structure: filtering structure
            output:
                tuple: 
                    result: boolean result
                    boolean: list with boolean criterion
        '''''
        boolean = [[obj.function(words) for obj in objlist] for objlist in structure]
        boolean
        aux = []
        result = True
        for boolist in boolean:
            if True in boolist:
                aux = True
            else:
                aux = False
            result = result and aux
        return result, boolean

    # this is the function encharged to load filter structure
    def getStructure(self, pdf_reader, fileName):
        '''''
        Charge filter into class explorePDF
            input
                pdf_reader: opened pdf object
                fileName: name from pdf opened
            output:
                list of resultSearched class: charge model in explorePDF class
        '''''
        if self.filter=='Default':
            aux1 = True; n = 0; m=-1;
            while aux1 and n < 10:
                aux2 = True; m=-1;
                while aux2 and m<20:
                    paragraphs1 = pdf_reader.loadPage(np.random.randint(0, pdf_reader.pageCount)-1).getText("text")
                    self.paragraphs1 = self.clarify(paragraphs1)
                    paragraphs2 = pdf_reader.loadPage(np.random.randint(0, pdf_reader.pageCount)-1) .getText("text")
                    self.paragraphs2 = self.clarify(paragraphs2)
                    try:
                        if detect(paragraphs1) == detect(paragraphs2):
                            language = detect(paragraphs1)
                            aux2 = False
                    except:
                        m=m+1
                        pass
                #set default language in case we have anormal behaviour
                if m==20:
                    try:
                        language=detect(fileName)
                    except:
                        language='en'
                if language == 'en':
                    return structureEnglish
                elif language == 'es':
                    return structureSpanish
                else:
                    n = n + 1
            if n == 10:
                pdf_reader.close()
                self.setState(f'Language not supported in pdf file {fileName}\n')
                self.rejected.append(f'{fileName}: language not supported')
                return 1
        elif self.filter=='Complex':
            return filter1
        elif self.filter=='Proy Issues':
            return filter2

    def countWords(self, boolvalues, structure):
        '''''
        This function is designed to obtain word ocurrence count in paragraph
            Input:
                array: paragraph splited as words
                numb: numbers mode in main function
                structure: filter structure
            Output:
                All finded words
        '''''
        aux = []
        b1 = -1
        for boolist in boolvalues:
            b2 = -1
            b1 = b1 + 1
            for boolean in boolist:
                b2 = b2 + 1
                if boolean == True:
                    aux.append(structure[b1][b2].symbol)
        return aux

    def setState(self, text):
        self.state.config(state=NORMAL)
        self.state.insert(END, '\n'+text)
        self.state.config(state=DISABLED)


class textClassifier():

    def __init__(self,state):
        self.workPath = os.path.dirname(sys.executable)
        self.state=state
        self.nlp = spacy.load(os.path.join(self.workPath,r'lib\\en_core_web_sm'))
        #         First we charge models to proccesss text
        self.chargeModels()
        #         Next we charge industry companies to make ents recognition
        self.companies = entGetter(petroleum_companies, engineer_companies, self.nlp)

    def chargeModels(self):
        '''''
        let charge analytical models trained to predict text classification
        '''''
        self.models = {}; aux = {};
        path = os.path.join(self.workPath, 'randomForestModel')
        for file in os.listdir(path):
            filename = file.split('.')[0]
            ext = file.split('.')[len(file.split('.')) - 1]
            if ext == 'csv':
                aux[filename] = pd.read_csv(os.path.join(path, file), index_col=0, header=0)
            elif ext == 'pkl':
                self.models[filename] = joblib.load(os.path.join(path, file))
        self.bases = {
            'scope': [aux['lemmas_scope'], aux['pos_scope'], aux['stem_scope']],
            'expected': [aux['lemmas_expect'], aux['pos_expect'], aux['stem_expect']],
            'timeline': [aux['lemmas_timeline'], aux['pos_timeline'], aux['stem_timeline']],
            'cost': [aux['lemmas_cost'], aux['pos_cost'], aux['stem_cost']]
        }

    def proccessText(self, text):
        self.companiesFound, self.gpe = np.empty(0), np.empty(0)
        doc = self.nlp(text)
        scope, expect, timeline, cost = '', '', '', ''
        for sent in doc.sents:
            self.setState(f"\nAnalizing sentence '{sent}'")
            self.preText(sent.text)
            self.getData(sent.text)
            mscope = self.models['scope'].predict(self.df.T.iloc[0:15].T)[0]
            mexpect = self.models['expect'].predict(self.df.T.iloc[0:15].T)[0]
            mtimeline = self.models['timeline'].predict(self.df.T.iloc[0:15].T)[0]
            mcost = self.models['cost'].predict(self.df.T.iloc[0:15].T)[0]
            if mscope == 1:
                scope += f' {sent.text}'
            if mexpect == 1:
                expect += f' {sent.text}'
            if mtimeline == 1:
                timeline += f' {sent.text}'
            if mcost == 1:
                cost += f' {sent.text}'
        self.companiesFound = np.array(self.companiesFound)
        self.gpe = np.array(self.gpe)
        self.result = pd.DataFrame([[text, self.gpe, self.companiesFound, scope, expect, timeline, cost]],
                                   columns=['TEXT', 'Places', 'Companies', 'Scope', 'Expectations', 'Timeline',
                                            'Economic'])

#   This is the class designed to classify text
    def preText(self, text):
        '''''
        This function let text information extraction
        Input:
            text: Text to analyze
        Output:
            lemmas: Lemmas from word's text
            pos: POS from word's text
            stem: Stemming from word's text
            num/i: Number frecuency on text 
            gpe/i: Places frecuency on text
            company/i: Companys frecuency on text
        '''''
        self.setState('Getting lemmas, stemmer, gpe, companies and other features from text...')
        #         Preparing variables, charging nlp model
        stemmer = SnowballStemmer(language='english')
        lemmas, pos, stem = [], [], []
        num = 0;
        i = 0;
        doc = self.nlp(text)
        #          Extracting companies and locations mentioned in text
        companiesFound, gpe, numgpe = self.companies.getEntities(text)
        self.companiesFound = np.append(self.companiesFound, companiesFound)
        self.gpe = np.append(self.gpe, gpe)
        #          Extracting lemmas, pos and stem
        for token in doc:
            isNum = False
            for char in token.text:
                try:
                    int(char)
                    isNum = True
                    break
                except:
                    pass
            if isNum:
                num += 1
            if not token.is_stop and not token.like_num and token.pos_ != 'PUNCT' and token.pos_ != 'SYM' \
                    and token.text != '\n' and token.text != ' ' and token.pos_ != 'SYM' and not isNum:
                lemmas.append(token.lemma_)
                pos.append(token.pos_)
                stem.append(stemmer.stem(token.text))
            i += 1
        self.textFeatures = np.array([np.unique(lemmas), np.unique(pos), np.unique(stem)])
        self.counts = [num / i, numgpe / i, len(companiesFound) / i]

    def getData(self, text):
        '''''
        Take data proccessed by preText and get lemmas, pos and stem cumulative frecuency
        Input:
            lemmas, pos, stem: Returned by preText function
            bases: DataFrames defined with getTextFeatures function
        output:
            proccessed dataframe with fifteen added columns:
                   [0]: lemas_score cumulative frecuency
                   [1]: pos_score cumulative frecuency
                   [2]: stem_score cumulative frecuency
                   [3]: lemas_expect cumulative frecuency
                   [4]: pos_expect cumulative frecuency
                   [5]: stem_expect cumulative frecuency 
                   [6]: lemas_timeline cumulative frecuency
                   [7]: pos_timeline cumulative frecuency
                   [8]: stem_timeline cumulative frecuency 
                   [9]: lemas_cost cumulative frecuency
                   [10]: pos_cost cumulative frecuency
                   [11]: stem_cost cumulative frecuency 
                   [12]: number frecuency in sentence.
                   [13]: places frecuency in sentence.
                   [14]: companies frecuency in sentence.
        '''''
        self.setState('Getting relative frecuencies and constructing database...')
        #          Defining structural variables for algorithm
        keys = ['words', 'pos', 'stem']
        self.master = [[0, 0, 0, 0],
                       [0, 0, 0, 0],
                       [0, 0, 0, 0]]
        j = -1
        #          Iterating and using structures we have
        for feature in self.textFeatures:
            j += 1
            df1 = self.bases['scope'][j]
            df2 = self.bases['expected'][j]
            df3 = self.bases['timeline'][j]
            df4 = self.bases['cost'][j]
            for i in range(len(feature)):
                try:
                    self.master[j][0] += df1[df1[keys[j]] == feature[i]]['frecuency'].iloc[0]
                except:
                    pass
                try:
                    self.master[j][1] += df2[df2[keys[j]] == feature[i]]['frecuency'].iloc[0]
                except:
                    pass
                try:
                    self.master[j][2] += df3[df3[keys[j]] == feature[i]]['frecuency'].iloc[0]
                except:
                    pass
                try:
                    self.master[j][3] += df4[df4[keys[j]] == feature[i]]['frecuency'].iloc[0]
                except:
                    pass
        self.df = {}
        self.df['number'] = self.counts[0]
        self.df['places'] = self.counts[1]
        self.df['companies'] = self.counts[2]
        self.df['lemmas_scope'] = self.master[0][0];
        self.df['lemmas_expect'] = self.master[0][1];
        self.df['lemmas_timeline'] = self.master[0][2];
        self.df['lemmas_cost'] = self.master[0][3];
        self.df['pos_scope'] = self.master[1][0];
        self.df['pos_expect'] = self.master[1][1];
        self.df['pos_timeline'] = self.master[1][2];
        self.df['pos_cost'] = self.master[1][3];
        self.df['stem_scope'] = self.master[2][0];
        self.df['stem_expect'] = self.master[2][1];
        self.df['stem_timeline'] = self.master[2][2];
        self.df['stem_cost'] = self.master[2][3]
        self.df = pd.DataFrame.from_dict(self.df, orient='index').T
        self.setState('Done')

    def setState(self, text):
        self.state.config(state=NORMAL)
        self.state.insert(END, '\n'+text)
        self.state.config(state=DISABLED)