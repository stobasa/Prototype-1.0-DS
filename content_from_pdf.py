#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 21:43:18 2019

@author: Gadcet
"""

"""
For this to work you will first need to make sure that you have installed the libraries below... I use a mac but it shouldnt be difficult doing this on windows
pip3 install PyMuPDF -> import as fitz
pip3 install git+https://github.com/StevenMapes/textract
pip3 install nltk - you should already have this
"""

import fitz
import textract
import camelot
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# This function converts the pdf into a list of texts
def extractText(file):
    doc = fitz.open(file)
    text = []
    for page in doc:
        t = page.getText().split('\n')
        text.append(t)
    return text

# This function converts the pdf into a list of dictionary objects that you can then parse as you see fit
def extractDict(file):
    doc = fitz.open(file)
    dict_list = []
    for page in doc:
        t = page.getText('dict')
        dict_list.append(t)
    return dict_list

def extractImages(file):
    """
    The images seem to be inverted in some funny way,
    but i'm sure there must be a way of dealing with it and converting
    back to the proper format.
    """
    doc = fitz.open(file)
    temp = file.split('/')
    for i in range(len(doc)):
        count = 0
        for img in doc.getPageImageList(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:       # this is GRAY or RGB
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.writePNG("%s-Pg%s-Img%s.png" % (temp[-1], i+1, count+1))
            else:               # CMYK: convert to RGB first
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.writePNG("%s-%s-%s.png" % (temp[-1], i, count))
                pix1 = None
            pix = None
            count += 1


# Example Run
filename = './Baronsmead-copy.pdf' # the path of the example PDF

tables = camelot.read_pdf(filename, flavor='stream')
print(tables[0].df)
tables[0].to_html('table.html') # to_json, to_excel

text_list = extractText(filename) # the pdf document is returned as a list of texts
dict_list = extractDict(filename) # the pdf document is returned as a list of dictionary objects (this is a better output format for creating structure)
extractImages(filename) # this extracts the image files from the pdf and saves it to the same directory as where the PDF was located


# Extract the key terms from each section of the text
temp = dict_list[0]['blocks']
print(temp[0].keys())

count = 0
#for tt in temp: # build in something that groups in all the text in a block together
#    try:
#        lines = tt['lines']
#        print('--------------------------subsection %s----------------------' % count)
#        for ttt in lines:
#            temp = ttt['spans']
#            for lines in temp:
#                text = lines['text'] # the first line should be the desciprtion of the feature/information there
#                if len(text.split()) > 0:
#                    text = text.split()
#                    for t in text:
#                        print(t.strip())
#        print()
#        count += 1
#    except:
#        count += 1
#        continue


class Bbox(object):
    def __init__(self, cord1, cord2, cord3, cord4):
        self.cord1 = cord1
        self.cord2 = cord2
        self.cord3 = cord3
        self.cord4 = cord4

    def __repr__(self):
        return self.cord1, self.cord2, self.cord3, self.cord4

    def __str__(self):
        return str(self.__repr__())

    def __eq__(self, bbox):
        if isinstance(bbox, Bbox):
            return (
                self.cord1 == bbox.cord1 and \
                self.cord2 == bbox.cord2 and \
                self.cord3 == bbox.cord3 and \
                self.cord4 == bbox.cord4
            )

        return NotImplemented

    def __sub__(self, bbox):
        if isinstance(bbox, Bbox):
           return Bbox(
                self.cord1 - bbox.cord1,
                self.cord2 - bbox.cord2,
                self.cord3 - bbox.cord3,
                self.cord4 - bbox.cord4
            )

        return NotImplemented

    def __add__(self, bbox):
        if isinstance(bbox, Bbox):
            return Bbox(
                self.cord1 + bbox.cord1,
                self.cord2 + bbox.cord2,
                self.cord3 + bbox.cord3,
                self.cord4 + bbox.cord4
            )

        return NotImplemented
    
    def sum(self):
        return self.cord1 + self.cord2 + self.cord3 + self.cord4


line_details = []

for doc_dict in dict_list:
    blocks = doc_dict.get('blocks', [])
    
    for block in blocks:
        lines = block.get('lines', [])
        
        for line in lines:
            bbox = line.get('bbox')
            spans = line.get('spans', [])
            
            current_bbox = Bbox(bbox[0], bbox[1], bbox[2], bbox[3])
            
            try:
                last_bbox = line_details[-1].get('bbox')
                distance_bbox = current_bbox - last_bbox
            except IndexError:
                distance_bbox = None
                
           
            line_detail = {
                'bbox': current_bbox,
                'distance_bbox': distance_bbox
            }
            
            for span in spans:
                text = span.get('text')
                
                line_detail['text'] = text
                
                line_details.append(line_detail)
            

    


#### Further Development - the script here is initial development of a functionality that can take a table within a pdf and then
#### create key-value pairs. With this format you can create a searchable format and be able to achieve something where you search
#### for a term in the document and recover keys from any table where the information is found.
## note - to detect paragraphs in text, look for lines of text that are short and also contain a fullstop '.'.
#
## You can run the code snippet below as an example and you would see an idea of what the output format looks like.
#
#filename = '/Users/Gadcet/Documents/Example.pdf' # the path of the example PDF
#
#text_list = extractText(filename)
#dict_list = extractDict(filename)
#temp1 = dict_list[6]
#temp = dict_list[6]['blocks']
##print(temp.key)
#
#for tt in temp:
#    lines = tt['lines']
#    print('a new key from the table')
#    for ttt in lines:
#        #print(ttt)
#        text = ttt['spans'][0]['text'] # the first line should be the desciprtion of the feature/information there
#        if len(text.split()) > 0:
#            print(text)
#    print()







