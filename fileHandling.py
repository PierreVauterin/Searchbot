import os
import fitz
import re
from nltk.stem import PorterStemmer

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
