import sys, os, zipfile, shutil, win32com.client
from appInterface._classes import HyperlinkManager
import github3 as git
from tkinter import *


def callBack():
    interp_path=os.path.dirname(sys.executable)
    workPath = os.path.join(interp_path, 'whatsNew.docx')
    word = win32com.client.Dispatch("Word.Application")
    word.visible = True
    wb = word.Documents.Open(workPath)


def setState(state,text):
    state.config(state=NORMAL)
    state.insert(END, '\n' + text)
    state.config(state=DISABLED)


def whatsNew(state, hyperlink):
    state.config(state=NORMAL)
    state.insert(INSERT, "\n"+r"To know what's new follow the ")
    state.insert(INSERT, r"link", hyperlink.add(callBack))
    state.config(state=DISABLED)


def copyInfo(a, interp_path):
    workPath=os.path.join(interp_path,'gitHub')
    filesbase = [name for name in os.listdir(interp_path)]
    filestoolbox = [name for name in os.listdir(os.path.join(interp_path,'toolBox'))]
    filesinterface = [name for name in os.listdir(os.path.join(interp_path, 'appInterface'))]
    a.extractall(path=workPath)
    for folder in os.listdir(workPath):
        if len(folder.split(r'.')) == 1:
            folderName=folder
            for file in os.listdir(os.path.join(workPath, folder)):
                if len(file.split('.')) > 1:
                    print(os.listdir(os.path.join(workPath, folder)))
                    extention = file.split('.')[len(file.split('.')) - 1]
                    if file in filesbase and extention == 'py':
                        shutil.copy2(os.path.join(workPath, folder, file), interp_path)
                    if extention=='docx':
                        try:
                            shutil.copy2(os.path.join(workPath, folder, file),
                                        os.path.join(interp_path))
                        except:
                            continue
                    if extention == 'pyc':
                        shutil.copy2(os.path.join(workPath, folder, file),
                                     os.path.join(interp_path,r'lib\tkinter'))
                else:
                    print(os.listdir(os.path.join(workPath, folder, file)))
                    for fileaux in os.listdir(os.path.join(workPath, folder, file)):
                        shutil.copy2(os.path.join(workPath, folder, file, fileaux),
                                    os.path.join(interp_path,file))
    shutil.rmtree(os.path.join(workPath, folderName))


def upgradeCode(state):
    interp_path = os.path.dirname(sys.executable)
    for folder in os.listdir(os.path.join(interp_path,r'gitHub')):
        if len(folder.split('.'))==1:
            shutil.rmtree(os.path.join(interp_path,r'gitHub',folder))
    hyperlink=HyperlinkManager(state)
    try:
        path = os.path.join(interp_path, 'GitHub', 'files.zip')
        path_upgrade = os.path.join(interp_path, 'GitHub', 'upgrated.txt')
        repo = git.GitHub().repository('gamug', 'pdfMiner')
        repo.archive('zipball', path=path)  # download repository content
        a = zipfile.ZipFile(path, 'r')  # This is the zip download Github content loaded
        # here we prepare download version information
        with open(path_upgrade, "r") as f:
            upgrated = f.read()
        f.close()
        if upgrated != str(repo.updated_at):
            print(upgrated)
            copyInfo(a, interp_path)  # we upload code if there is recent version in my repository
            setState(state, '********************************************')
            setState(state,
                     'The code was successfully upgraded, changes will be available next time you restar the program.')
            whatsNew(state, hyperlink)
            setState(state, '********************************************')
            with open(path_upgrade, "w") as f:
                f.write(str(repo.updated_at))
            f.close()
            return True
        else:
            setState(state,'********************************************')
            setState(state,"Seems you have code's latest version")
            whatsNew(state, hyperlink)
            setState(state,'********************************************')
            return False
    except:
        setState(state,'********************************************')
        setState(state,"The code wasn't upgraded")
        setState(state,'********************************************')
        return False
