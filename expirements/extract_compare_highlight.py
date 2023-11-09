from html.parser import HTMLParser
import json
parser = HTMLParser()
from bs4 import BeautifulSoup
import difflib
from pathlib import Path
from PyPDF2 import PdfFileWriter, PdfFileReader
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLineHorizontal, LTAnno
import pandas as pd
import os
from py_pdf_highlight import createHighlight, addHighlightToPage
import logging
logger = logging.getLogger()
logging.getLogger().setLevel(logging.INFO)

class CharComponent:
    char_index: int
    character: str
    font: str
    size: int
    colour: str
    style: str
    x1:int
    x2:int
    y1:int
    y2:int
    def __init__(self,
                 char_index: int,
                 character: str,
                 font: str,
                 size: float,
                 colour: str,
                 x1: float,
                 x2: float,
                 y1: float,
                 y2: float):
        self.char_index = char_index
        self.character = character
        self.font = font
        self.size = size
        self.colour = colour
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

charComp = CharComponent(char_index=0,character='t', font='Roman times', colour='FF23FB', 
    size=13.345, x1=0.0, y1=0.0, x2=0.0, y2=0.0)

src_char_components = [charComp]
dest_char_components = [charComp]

def get_diff_soups(compare_text_html):
    try:
        html_file_obj = open(compare_text_html, "r")
        html_str = html_file_obj.read()
        soup = BeautifulSoup(html_str, 'html.parser')
        tbody = soup.find('tbody')
        all_tr_soup = tbody.find_all('tr')
        source_td_soups = [BeautifulSoup(features="lxml")]
        dest_td_soups = [BeautifulSoup(features="lxml")]
        for tr_soup in all_tr_soup:
            if tr_soup.find_all('td')[2] is not None and tr_soup.find_all('td')[2].get_text() != '':
                source_td_soups.append(tr_soup.find_all('td')[2])
            if tr_soup.find_all('td')[5] is not None and tr_soup.find_all('td')[5].get_text() != '':
                dest_td_soups.append(tr_soup.find_all('td')[5])
        source_td_soups.pop(0)
        dest_td_soups.pop(0)
        return source_td_soups, dest_td_soups
    except Exception as error:
        logging.error(str(error)+' Error while parsing HTML Contents!!.')

def compare_and_highlight_pdf(src_path_pdf, target_path_pdf):
    try:
        logging.info('Source PDF Location : ' + src_path_pdf)
        logging.info('Target PDF Location : ' + target_path_pdf)
        source_page_info = list(extract_pages(src_path_pdf))
        dest_page_info = list(extract_pages(target_path_pdf))
        logging.info('Number of pages in Source PDF : ' + str(len(source_page_info)))
        logging.info('Number of pages in Target PDF : ' + str(len(dest_page_info)))
        src_pdf_test_output = PdfFileWriter()
        dest_pdf_test_output = PdfFileWriter()
        src_page_obj = open(src_path_pdf, "rb")
        dest_page_obj = open(target_path_pdf, "rb")
        src_pdf_input = PdfFileReader(src_page_obj)
        dest_pdf_input = PdfFileReader(dest_page_obj)
        page_count = 0
        for source_page, dest_page in zip(source_page_info, dest_page_info):
            i:int = 0
            j:int = 0
            src_pdf_page = src_pdf_input.getPage(page_count)
            dest_pdf_page = dest_pdf_input.getPage(page_count)
            page_count = page_count+1
            logging.info('Comparing page : ' + str(page_count))
            for source_element, dest_element in zip(source_page, dest_page):
                if isinstance(source_element, LTTextContainer) and isinstance(dest_element, LTTextContainer):
                    src_char_components = [charComp]
                    dest_char_components = [charComp]
                    src_char_components.pop(0)
                    dest_char_components.pop(0)
                    for source_text_line, dest_text_line in zip(source_element, dest_element):
                        prev_src_char = LTChar
                        #print(source_text_line)
                        if isinstance(source_text_line, LTChar):
                            src_char_components.append(CharComponent(character=source_text_line.get_text(),
                            font=str(source_text_line.fontname).split('+')[1] if len(str(source_text_line.fontname).split('+')) > 1 else str(source_text_line.fontname),
                            colour=str(source_text_line.graphicstate.ncolor),
                            char_index=i,
                            size=0.0,x1=0, y1=0,
                            x2=0, y2=0))
                        elif isinstance(source_text_line, LTAnno):
                            src_char_components.append(CharComponent(character=source_text_line.get_text(),
                            font='LTAnno',
                            colour='LTAnno', 
                            char_index=i,
                            size=0.0,x1=0, y1=0,
                            x2=0, y2=0))
                        else :
                            for source_char in source_text_line:
                                if isinstance(source_char, LTAnno):
                                    #print('It is LTAnno : ' + source_char.get_text())
                                    if source_char.get_text() == '\n':
                                        src_char_components.append(CharComponent(character=source_char.get_text(),
                                        font=str(prev_src_char.fontname).split('+')[1] if len(str(prev_src_char.fontname).split('+')) > 1 else str(prev_src_char.fontname),
                                        colour=str(prev_src_char.graphicstate.ncolor),
                                        char_index=i,
                                        size=0.0, x1=prev_src_char.bbox[2], y1=prev_src_char.bbox[1],
                                        x2=prev_src_char.bbox[2] + prev_src_char.bbox[2] - prev_src_char.bbox[0], y2=prev_src_char.bbox[3]))
                                    elif source_char.get_text() == ' ':
                                        src_char_components.append(CharComponent(character=source_char.get_text(),
                                        font=str(prev_src_char.fontname).split('+')[1] if len(str(prev_src_char.fontname).split('+')) > 1 else str(prev_src_char.fontname),
                                        colour=str(prev_src_char.graphicstate.ncolor),
                                        char_index=i,
                                        size=0.0,x1=prev_src_char.bbox[2], y1=prev_src_char.bbox[1],
                                        x2=prev_src_char.bbox[2] + prev_src_char.bbox[2] - prev_src_char.bbox[0], y2=prev_src_char.bbox[3]))
                                elif isinstance(source_char, LTChar) or source_char.get_text() == ' ':
                                    prev_src_char = source_char
                                    src_char_components.append(CharComponent(
                                    char_index=i, x1=source_char.bbox[0], y1=source_char.bbox[1],
                                    x2=source_char.bbox[2], y2=source_char.bbox[3],
                                    character=source_char.get_text(),
                                    font=str(source_char.fontname).split('+')[1] if len(str(source_char.fontname).split('+')) > 1 else str(source_char.fontname),
                                    colour=str(source_char.graphicstate.ncolor), 
                                    size=round(source_char.size, 1)))
                                i += 1
                        prev_dest_char = ''
                        if isinstance(dest_text_line, LTChar):
                            prev_dest_char = dest_text_line
                            dest_char_components.append(CharComponent(character=dest_text_line.get_text(),
                            font=str(prev_dest_char.fontname).split('+')[1] if len(str(prev_dest_char.fontname).split('+')) > 1 else str(prev_dest_char.fontname),
                            colour=str(prev_dest_char.graphicstate.ncolor), 
                            char_index=j,
                            size=0.0,x1=0, y1=0,
                            x2=0, y2=0))
                        elif isinstance(dest_text_line, LTAnno):
                            src_char_components.append(CharComponent(character=dest_text_line.get_text(),
                            font='LTAnno',
                            colour='LTAnno', 
                            char_index=j,
                            size=0.0,x1=0, y1=0,
                            x2=0, y2=0))
                        else:
                            for dest_char in dest_text_line:
                                if isinstance(dest_char, LTAnno):
                                    #print('It is LTAnno : ' + dest_char.get_text())
                                    if dest_char.get_text() == '\n':
                                        dest_char_components.append(CharComponent(character=dest_char.get_text(),
                                        font=str(prev_dest_char.fontname).split('+')[1] if len(str(prev_dest_char.fontname).split('+')) > 1 else str(prev_dest_char.fontname),
                                        colour=str(prev_dest_char.graphicstate.ncolor), 
                                        char_index=j,
                                        size=0.0, x1=prev_dest_char.bbox[2], y1=prev_dest_char.bbox[1],
                                        x2=prev_dest_char.bbox[2] + 10, y2=prev_dest_char.bbox[3]))
                                    elif dest_char.get_text() == ' ':
                                        dest_char_components.append(CharComponent(character=dest_char.get_text(),
                                        char_index=j,
                                        font=str(prev_dest_char.fontname).split('+')[1] if len(str(prev_dest_char.fontname).split('+')) > 1 else str(prev_dest_char.fontname),
                                        colour=str(prev_dest_char.graphicstate.ncolor),  
                                        size=0.0,x1=prev_dest_char.bbox[2], y1=prev_dest_char.bbox[1],
                                        x2=prev_dest_char.bbox[2] + 10, y2=prev_dest_char.bbox[3]))
                                elif isinstance(dest_char, LTChar) or dest_char.get_text() == ' ':
                                    prev_dest_char = dest_char
                                    dest_char_components.append(CharComponent(
                                    char_index=j, x1=dest_char.bbox[0], y1=dest_char.bbox[1],
                                    x2=dest_char.bbox[2], y2=dest_char.bbox[3],
                                    character=dest_char.get_text(),
                                    font=str(dest_char.fontname).split('+')[1] if len(
                                    str(dest_char.fontname).split('+')) > 1 else str(dest_char.fontname),
                                    colour=str(dest_char.graphicstate.ncolor), 
                                    size=round(dest_char.size, 1)))
                                j += 1
                    df_src = pd.DataFrame()
                    df_dest = pd.DataFrame()
                    df_src = pd.DataFrame([x.__dict__ for x in src_char_components])
                    df_dest = pd.DataFrame([x.__dict__ for x in dest_char_components])
                    df_comp_src = df_src.drop(['char_index', 'x1', 'x2', 'y1', 'y2'], axis=1)
                    df_comp_dest = df_dest.drop(['char_index', 'x1', 'x2', 'y1', 'y2'], axis=1)
                    df_comp_src = df_comp_src.reset_index(drop=True)
                    df_comp_dest = df_comp_dest.reset_index(drop=True)
                    json_src = json.loads(df_comp_src.to_json(orient ='records'))
                    json_dest = json.loads(df_comp_dest.to_json(orient ='records'))
                    with open('src.txt' , 'w') as file:
                        for c in json_src:
                            file.write("%s\n" % c)
                        file.close()
                    with open('dest.txt' , 'w') as file:
                        for c in json_dest:
                            file.write("%s\n" % c)
                        file.close()
                    file1 = open('src.txt', 'r').readlines()
                    file2 = open('dest.txt', 'r').readlines()
                    html_differ = difflib.HtmlDiff()
                    htmldiffs = html_differ.make_file(file1, file2)
                    with open('comparision.html', 'w') as outfile:
                        outfile.write(htmldiffs)
                    source_diff_soups, dest_diff_soups = get_diff_soups('comparision.html')
                    for char in src_char_components:
                        soup = source_diff_soups[0]
                        if soup.find('span') is not None:
                            r = g = b = 0
                            if soup.find('span', {'class': 'diff_add'}) is not None:
                                r = 0.33
                                g = 1
                                b = 0.34
                            if soup.find('span', {'class': 'diff_sub'}) is not None:
                                r = 1
                                g = 0.28
                                b = 0.28
                            if soup.find('span', {'class': 'diff_chg'}) is not None:
                                r = 1
                                g = 1
                                b = 0.15
                            highlight_test = createHighlight(char.x1, char.y1, char.x2, char.y2, {
                                        "author": "",
                                        "contents": ""
                                    }, color=[r, g, b])
                            addHighlightToPage(
                                        highlight_test, src_pdf_page, src_pdf_test_output)
                        source_diff_soups.pop(0)
                    for char in dest_char_components:
                        soup = dest_diff_soups[0]
                        if soup.find('span') is not None:
                            r = g = b = 0
                            if soup.find('span', {'class': 'diff_add'}) is not None:
                                r = 0.33
                                g = 1
                                b = 0.34
                            if soup.find('span', {'class': 'diff_sub'}) is not None:
                                r = 1
                                g = 0.27
                                b = 0.38
                            if soup.find('span', {'class': 'diff_chg'}) is not None:
                                r = 1
                                g = 1
                                b = 0.15
                            highlight_test = createHighlight(char.x1, char.y1, char.x2, char.y2, {
                                        "author": "",
                                        "contents": ""
                                    }, color=[r, g, b])
                            addHighlightToPage(
                                        highlight_test, dest_pdf_page, dest_pdf_test_output)
                        dest_diff_soups.pop(0)
            src_pdf_test_output.addPage(src_pdf_page)
            dest_pdf_test_output.add_page(dest_pdf_page)
        os.makedirs(str(os.path.dirname(src_path_pdf)) + '/comparison', exist_ok=True)
        src_hightlighted_pdf_path = open(str(os.path.dirname(src_path_pdf)) + '/comparison/' + str(
            os.path.basename(src_path_pdf).split('.')[-2]) + '_highlighted_src.pdf', "wb")
        src_pdf_test_output.write(src_hightlighted_pdf_path)
        dest_hightlighted_pdf_path = open(str(os.path.dirname(target_path_pdf)) + '/comparison/' + str(
            os.path.basename(target_path_pdf).split('.')[-2]) + '_highlighted_target.pdf', "wb")
        dest_pdf_test_output.write(dest_hightlighted_pdf_path)
        src_page_obj.close()
        dest_page_obj.close()
        src_hightlighted_pdf_path.close()
        dest_hightlighted_pdf_path.close()
        logging.info('Comparision Successful!!.')
        return src_hightlighted_pdf_path.name, dest_hightlighted_pdf_path.name
    except Exception as error:
        logging.error(str(error)+' Error PDF comparision!!.')

def create_final_highlighted_report(source_highlighted, destination_highlighted,
        testcase_name, testcase_description, aut_version, app_version,
        generated_at, generated_by) -> str:
    try:
        logging.info('Generating Comparison Report!!.')
        report_template_path = Path(__file__).parent / "Comparision_Report_Template.html"
        with open(report_template_path, 'r') as template_file:
            html_template = template_file.read()
            html_template = html_template.replace('''{{SOURCE_HIGHTLIGHTED.PDF}}''', str(os.path.basename(source_highlighted)))
            html_template = html_template.replace('''{{TARGET_HIGHTLIGHTED.PDF}}''', str(os.path.basename(destination_highlighted)))
            html_template = html_template.replace('''{{GENERATED_AT}}''', generated_at)
            html_template = html_template.replace('''{{GENERATED_BY}}''', generated_by)
            html_template = html_template.replace('''{{TESTCASE_NAME}}''', testcase_name)
            html_template = html_template.replace('''{{TESTCASE_DESCRIPTION}}''', testcase_description)
            html_template = html_template.replace('''{{AUT}}''', aut_version)
            html_template = html_template.replace('''{{APP_VERSION}}''', app_version)
        report_path = os.path.dirname(source_highlighted) + '/final_report.html'
        with open(report_path, 'w') as outfile:
            outfile.write(html_template)
        outfile.close()
        template_file.close()
        return report_path
    except Exception as error:
        logging.error(str(error)+' Error while generating PDF comparision report!!.')

#mapPdfToCharComp('Source.pdf', 'Destination.pdf')