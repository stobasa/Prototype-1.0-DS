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
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import os

filename = 'Baronsmead-copy.pdf'

# This function converts the pdf into a list of texts
def extractText(file):
    doc = fitz.open(file)
    text = []
    for page in doc:
        t = page.getText() 
        text.append(t)
    return text

def extractHtml(file):
    doc = fitz.open(file)
    text = []
    for page in doc:
        t = page.getText('html') #.split('\n')
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
    
    pdf_title = file.split('.')[0]
    images_dir = pdf_title + '/images'
    
    if os.path.isdir(pdf_title) == False:
        os.mkdir(pdf_title)
                
    if os.path.isdir(images_dir) == False:
        os.mkdir(images_dir)
           
            
    doc = fitz.open(file)
    temp = file.split('/')
    for i in range(len(doc)):
        count = 0
        for img in doc.getPageImageList(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:       # this is GRAY or RGB
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.writePNG(images_dir + "/%s-Pg%s-Img%s.png" % (temp[-1], i+1, count+1))
            else:               # CMYK: convert to RGB first
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.writePNG(images_dir + "/%s-%s-%s.png" % (temp[-1], i, count))
                pix1 = None
            pix = None
            count += 1


text_list = extractText(filename) # the pdf document is returned as a list of texts
dict_list = extractDict(filename) # the pdf document is returned as a list of dictionary objects (this is a better output format for creating structure)
extractImages(filename) # this extracts the image files from the pdf and saves it to the same directory as where the PDF was located
html_list = extractHtml(filename)

# Extract the key terms from each section of the text
temp = dict_list[0]['blocks']
print(temp[0].keys())

class Bbox(object):
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __repr__(self):
        return self.left, self.top, self.right, self.bottom

    def __str__(self):
        return str(self.__repr__())

    def __eq__(self, bbox):
        if isinstance(bbox, Bbox):
            return (
                self.left == bbox.left and \
                self.top == bbox.top and \
                self.right == bbox.right and \
                self.bottom == bbox.bottom
            )

        return NotImplemented

    def __sub__(self, bbox):
        if isinstance(bbox, Bbox):
           return Bbox(
                self.left - bbox.left,
                self.top - bbox.top,
                self.right - bbox.right,
                self.bottom - bbox.bottom
            )

        return NotImplemented

    def __add__(self, bbox):
        if isinstance(bbox, Bbox):
            return Bbox(
                self.left + bbox.left,
                self.top + bbox.top,
                self.right + bbox.right,
                self.bottom + bbox.bottom
            )

        return NotImplemented

    def sum(self):
        return self.left + self.top + self.right + self.bottom


def get_segments(dict_list):
    line_details = []
    block_texts = []
    distances = []
    segments = []
    
    for doc_dict in dict_list:
        blocks = doc_dict.get('blocks', [])
    
        for block in blocks:
            lines = block.get('lines', [])
            block_text = ''
    
            for line in lines:
                bbox = line.get('bbox')
                spans = line.get('spans', [])
    
                current_bbox = Bbox(bbox[0], bbox[1], bbox[2], bbox[3])
    
                try:
                    last_bbox = line_details[-1].get('bbox')
                    top_distance = current_bbox.top - last_bbox.top
                except IndexError:
                    top_distance = None
    
    #            s = distance_bbox #distance_bbox.sum() if distance_bbox is not None else None
    
                if top_distance is not None:
                    distances.append(abs(top_distance))
    
                line_detail = {
                    'bbox': current_bbox,
                    'top_distance': top_distance
                }
    
                for span in spans:
                    text = span.get('text')
                    
                    try: 
                        line_detail['text'] += text
                    except KeyError:
                        line_detail['text'] = text
                        
                    block_text += text
    
                line_details.append(line_detail)
                    
            block_texts.append(block_text)
            
    
    segment_text = ''
    for line_detail in line_details:
        top_distance = abs(line_detail.get('top_distance')) if line_detail.get('top_distance') is not None else None
        text = line_detail.get('text')
        
        if top_distance is not None and top_distance < 25:
            segment_text += text + '\n'
        elif top_distance is not None: 
            segments.append(segment_text)
            segment_text = text + '\n'
    
    return segments

def process_table(table_rows):
    columns = 0
    row_length = 0
    csv_string = ''
    table_visible_items = []
    
    for row in table_rows:
        splitted_row = [item.strip() for item in re.split(r'(\s\s)+', row)]
        visible_items = list(filter(None, splitted_row))
        table_visible_items.append(visible_items)
        
        if len(visible_items) > columns:
            columns = len(visible_items)
        
        if len(row) > row_length:
            row_length = len(row)
    
    
    
    if columns > 0: 
        for index, row in enumerate(table_rows):
            positioned_row = [""] * columns
            average_column_character_length = row_length / columns
            
            visible_items = table_visible_items[index]
            
            for visible_item in visible_items:
                if visible_item in positioned_row:
                    start = int(row.index(visible_item)) + len(visible_item)
                    item_index = row.index(str(visible_item), start)
                else:
                    item_index = row.index(str(visible_item))
                    
                column_ranges = [average_column_character_length * i for i in range(1, columns + 1)]
    
                estimated_position = 0
                
                for index, column_range in enumerate(column_ranges):
                    if item_index < column_range:
                        estimated_position = index
                        break
                
                positioned_row[estimated_position] = visible_item
            
            cleaned_positioned_row = [item.replace(',','') for item in positioned_row]
            csv_string += ','.join(cleaned_positioned_row) + '\n'
            
        
            
    return { 
        'column_count': columns,
        'csv_string': csv_string
    }

def process_segments(segments):
    processed_segments = []
    
    for segment in segments:
        processed_segment = {}
        processed_segment['type'] = 'text'
        processed_segment['text'] = segment
            
        lines = segment.split('\n')
        for line in lines:
            spaces = re.findall(r'\s+', line)
            for space in spaces:
                if len(space) > 3:
                    processed_segment['type'] = 'table'
                    
                    try:
                        processed_segment['table_rows']
                    except KeyError:
                        processed_segment['table_rows'] = []
                        
            if processed_segment['type'] == 'table':
                processed_segment['table_rows'].append(line)
                
        if processed_segment['type'] == 'table':
            processed_table = process_table(processed_segment['table_rows'])
            processed_segment['column_count'] = processed_table.get('column_count')
            processed_segment['csv_string'] = processed_table.get('csv_string')
        
        
        processed_segments.append(processed_segment)
    
    return processed_segments
        
def save_tables_to_csv(processed_segments, pdf_filename):
    for segment in processed_segments:
        if segment['type'] == 'table' and segment['column_count'] > 1:
            first_line_text = segment['text'].split('\n')[0]
            title = " ".join(first_line_text.split())
            csv_filename = title.strip() + '.csv'
            
            pdf_title = pdf_filename.split('.')[0]
            tables_path = pdf_title + '/tables'
            
            if os.path.isdir(pdf_title) == False:
                os.mkdir(pdf_title)
                
            if os.path.isdir(tables_path) == False:
                os.mkdir(tables_path)
            
            with open(tables_path + '/' + csv_filename, 'w') as csv_file:
                csv_file.write(segment['csv_string'])
                


segments = get_segments(dict_list)
processed_segments = process_segments(segments)
save_tables_to_csv(processed_segments, filename)

def process_pdf(filepath):
    pdf_dict = extractDict(filepath)
    pdf_segments = get_segments(pdf_dict)
    processed_pdf_segments = process_segments(pdf_segments)
    save_tables_to_csv(processed_pdf_segments, filepath)
    
    return processed_pdf_segments
    
princess_segments = process_pdf('princess.pdf')
princess_text = extractText('princess.pdf')

icg_segments = process_pdf('icg.pdf')
icg_text = extractText('icg.pdf')



#import tabula
#df = tabula.read_pdf(filename, pages='all')
#print(df)
#            
            
    
        





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







