from PyPDF2 import PdfFileWriter, PdfFileReader
from py_pdf_highlight import createHighlight, addHighlightToPage
import difflib
from pdfminer.layout import LTTextContainer, LTChar, LTTextLineHorizontal, LTAnno
from pdfminer.high_level import extract_pages
from bs4 import BeautifulSoup
import os
from pathlib import Path
report_template_path = Path(__file__).parent / "Comparision_Report_Template.html"

def extract_text_from_pdf(path) -> str:
    content = ""
    source_page_info = list(extract_pages(path))
    for source_page in source_page_info:
        for element in source_page:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if str(text_line.get_text()).split() != []:
                        for char in text_line:
                            content = content + char.get_text()
    write_path = str(os.path.dirname(path)) + '/text/' + \
        str(os.path.basename(path).split('.')[-2]) + '.txt'
    os.makedirs(os.path.dirname(write_path), exist_ok=True)
    with open(write_path, 'w') as outfile:
        outfile.write(content)
        outfile.close()
    return write_path


def compare_text_files(path1, path2) -> str:
    html_differ = difflib.HtmlDiff()
    file1 = open(path1, 'r').readlines()
    file2 = open(path2, 'r').readlines()
    htmldiffs = html_differ.make_file(file1, file2)
    comparision_path = os.path.dirname(path1) + '/text-comparision.html'
    with open(comparision_path, 'w') as outfile:
        outfile.write(htmldiffs)
    return comparision_path


def get_diff_soups(compare_text_html):
    html_file_obj = open(compare_text_html, "r")
    html_str = html_file_obj.read()
    soup = BeautifulSoup(html_str, 'html.parser')
    tbody = soup.find('tbody')
    all_tr_soup = tbody.find_all('tr')
    source_td_soups = [BeautifulSoup(features="lxml")]
    dest_td_soups = [BeautifulSoup(features="lxml")]
    for tr_soup in all_tr_soup:
        if tr_soup.find_all('td')[2] is not None:
            source_td_soups.append(tr_soup.find_all('td')[2])
        if tr_soup.find_all('td')[5] is not None:
            dest_td_soups.append(tr_soup.find_all('td')[5])
    source_td_soups.pop(0)
    dest_td_soups.pop(0)
    return source_td_soups, dest_td_soups


def highlight_text_in_pdf(diff_soups, pdf_path: str) -> str:
    page_info = list(extract_pages(pdf_path))
    page_obj = open(pdf_path, "rb")
    pdf_input = PdfFileReader(page_obj)
    page_count = 0
    pdf_test_output = PdfFileWriter()
    for source_page in page_info:
        content = [LTTextLineHorizontal]
        pdf_page = pdf_input.getPage(page_count)
        page_count = page_count+1
        for element in source_page:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    word = ""
                    is_new_word = True
                    if str(text_line.get_text()).split() != []:
                        content.append(text_line)
        content.pop(0)
        for line in content:
            soup = diff_soups[0]
            if soup.find('span') is not None:
                r = g = b = 0
                if soup.find('span', {'class': 'diff_chg'}) is not None:
                    r = 1
                    g = 1
                    b = 0.15
                if soup.find('span', {'class': 'diff_add'}) is not None:
                    r = 0.33
                    g = 1
                    b = 0.34
                if soup.find('span', {'class': 'diff_sub'}) is not None:
                    r = 1
                    g = 0.27
                    b = 0.38
                word = ""
                is_new_word = True
                x1 = x2 = y1 = y2 = 0
                if str(line.get_text()).split() != []:
                    for char in line:
                        if isinstance(char, LTAnno) or char.get_text() == ' ':
                            if not is_new_word:
                                highlight_test = createHighlight(x1, y1, x2, y2, {
                                    "author": "",
                                    "contents": ""
                                }, color=[r, g, b])
                                addHighlightToPage(
                                    highlight_test, pdf_page, pdf_test_output)
                                #print('Word is : ' + word)
                            is_new_word = True
                            word = ""
                        elif isinstance(char, LTChar):
                            if is_new_word:
                                x1, y1 = char.bbox[0], char.bbox[1]
                                x2, y2 = char.bbox[2], char.bbox[3]
                            else:
                                x2, y2 = char.bbox[2], char.bbox[3]
                            word += char.get_text()
                            is_new_word = False
            diff_soups.pop(0)
        pdf_test_output.addPage(pdf_page)
    os.makedirs(str(os.path.dirname(pdf_path)) + '/comparison', exist_ok=True)
    hightlighted_pdf_path = open(str(os.path.dirname(pdf_path)) + '/comparison/' + str(
        os.path.basename(pdf_path).split('.')[-2]) + '_highlighted.pdf', "wb")
    pdf_test_output.write(hightlighted_pdf_path)
    page_obj.close()
    return hightlighted_pdf_path.name


def create_final_report(source_highlighted, destination_highlighted) -> str:
    with open(report_template_path, 'r') as template_file:
        html_template = template_file.read()
        html_template = html_template.replace('Source_highlighted.pdf', str(os.path.basename(source_highlighted)))
        html_template = html_template.replace('Destination_highlighted.pdf', str(os.path.basename(destination_highlighted)))
    report_path = os.path.dirname(source_highlighted) + '/final_report.html'
    with open(report_path, 'w') as outfile:
        outfile.write(html_template)
    outfile.close()
    template_file.close()
    return report_path
