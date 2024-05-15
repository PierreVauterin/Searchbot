import os
import fitz
import re
import tkinter as tk
from tkinter.ttk import Progressbar
from tkinter import filedialog
import nltk
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer
import datetime
import tkinter.messagebox
import time

def colorText(canva,listKeywords:list[str])->None:
    for keyword in listKeywords:
        start_index = "1.0"
        while True:
            index = canva.search(keyword, start_index, stopindex="end")
            if not index:break
            canva.tag_add("color", index, f"{index}+{len(keyword)}c")
            start_index = f"{index}+{len(keyword)}c"
    canva.tag_config("color", foreground="red") # Maybe find a way to adapt this color to the current color scheme of the window

def displayText(toDisplay,canva,bot):
    canva.insert(str(bot.yToPrint),text=toDisplay.strip()+"\n")
    bot.yToPrint += 1.0

def findSynonyms(keyword):
    setKeyword={keyword}
    for syn in wordnet.synsets(keyword): 
        for l in syn.lemmas():setKeyword.add(re.sub("_"," ",l.name().upper()))
    listKeyword=list(setKeyword)
    for val in listKeyword:
        if(val[-1]!="S"):listKeyword.append(val+"S")# So that plurals are detected too
    return listKeyword

def findKeyword(keyword:list[str],text,search:str) -> list[str]:
    found_sentences = []
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\n)(?=\s|[A-Z])', text)
    for sentence in sentences:
        if(search=="root"):
            if(keyword[0] in PorterStemmer().stem(sentence).upper()):found_sentences.append(sentence)
        else:
            for val in keyword:
                pattern = re.compile(fr'\b{re.escape(val)}\b', re.IGNORECASE)
                if re.search(pattern, sentence):
                    found_sentences.append(sentence)
                    continue #We do not want the same sentence to be analyzed for each synonym, processing will be faster
    return found_sentences

def extract_text_from_pdf(pdf_file_path:str,listKeywords:list[str],filename:str,bot,date:str,search:str):
    doc = fitz.open(pdf_file_path)
    fontsize=30
    res,outputCreated,outputModified,firstModification,pagesKeyword= "",False,False,True,[]
    outputExists=os.path.isfile(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")
    if(outputExists):output=fitz.open(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")
    for page in doc:
        page_text = page.get_text()
        lines = page_text.split('\n')
        sanitized_lines = [line for line in lines if not line.strip().isdigit()]
        sanitized_text = '\n'.join(sanitized_lines)
        res += sanitized_text
        if(len(findKeyword(listKeywords,sanitized_text,search))!=0):
            if(not outputExists):
                output=fitz.open()
                outputCreated=True
                outputExists=True
            if(firstModification):
                newPage=output.new_page(len(output))
                textLength = fitz.get_text_length(filename[:30], fontname="helv", fontsize=fontsize)
                newPage.insert_text(fitz.Point((newPage.mediabox.width-textLength)/2,(newPage.mediabox.height-textLength)/2),filename[:30],fontsize=fontsize)
                firstModification=False
            if(page.number not in pagesKeyword):
                pagesKeyword.append(page.number)
                page.clean_contents()
                output.insert_pdf(doc, from_page=page.number, to_page=page.number)
                outputModified=True
                watermark="{filename}-page {pageNumber}".format(filename=filename[:30],pageNumber=page.number+1)
                output[len(output)-1].insert_text((fitz.get_text_length(watermark, fontname="helv", fontsize=5)/2, 10), watermark)
    if(outputCreated):
        output.save(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")
        output.close()
    elif(outputModified):
        output.save(bot.output+"/BOT_"+bot.query+"_"+date+".pdf",incremental=True,encryption=0)
        output.close()
    doc.close()
    return re.sub(r"\n(?![A-Z])", "", res)
        
def formatSentence(keyword:list[str],sentence,canva,bot) -> None:
    modified_sentence = sentence
    for val in keyword:modified_sentence = re.sub(r'\b{}\b'.format(re.escape(val)), f'{val}', modified_sentence, flags=re.IGNORECASE)
    displayText(modified_sentence + "\n",canva,bot)
    
def extract(bot,canva,search:str) -> int:
    displayText("Looking for {word} in the database, please wait...\n".format(word=bot.query),canva,bot)
    textList,fileList=[],[]
    date = str(datetime.datetime.today().replace(microsecond=0)).replace(" ","_").replace(":","_")
    if(search=="root"):
        question=[]
        question.append(PorterStemmer().stem(bot.query).upper())
    else:question=findSynonyms(bot.query)
    for pathSearch,subdirs,files in os.walk(bot.directory):
        for filename in files:
            if(filename[-4:]!=".pdf"):continue # We only read PDFs, then we do not take into account other formats
            path = os.path.join(pathSearch, filename)
            path=os.path.normpath(path)
            textList.append(extract_text_from_pdf(path,question,filename,bot,date,search))
            fileList.append(filename)
    if(os.path.isfile(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")):
        output=fitz.open(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")
        for page in output:
            for keyword in question:
                matches=page.search_for(keyword+" ")
                page.add_highlight_annot(matches) # A modifier
        output.save(bot.output+"/BOT_"+bot.query+"_"+date+".pdf",incremental=True,encryption=0)
        output.close()
        tkinter.messagebox.showinfo(title="File ready", message="Your file has been saved in "+bot.output+"/COWI_BOT_"+bot.query+"_"+date+".pdf")
    occurrences,usefulFiles=0,[]
    for i in range(len(textList)):
        sentence=findKeyword(question,textList[i],search)
        if(len(sentence)==0):continue
        else:
            usefulFiles.append(fileList[i])
            displayText("--------------------------------------------------"+fileList[i]+"--------------------------------------------------------------\n",canva,bot)
            occurrences+=len(sentence)
            for j in range(len(sentence)):
                formatSentence(question,sentence[j],canva,bot)
                displayText("\n\n",canva,bot)
    displayText("Total occurrences of the keyword found: {occurences}".format(occurences=occurrences),canva,bot)
    bot.yToPrint+=3.0
    if(occurrences!=0):
        colorText(canva,question)
        bot.yToPrint+=5.0
    return 1
