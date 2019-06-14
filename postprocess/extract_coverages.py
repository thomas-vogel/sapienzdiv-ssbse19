# Copyright (c) 2016-present, Ke Mao. All rights reserved.


import os

from lxml import html
from bs4 import UnicodeDammit

import settings


def extract_coverage(path):
    with open(path, 'rb') as file:
        content = file.read()
        doc = UnicodeDammit(content, is_html=True)

    parser = html.HTMLParser(encoding=doc.original_encoding)
    root = html.document_fromstring(content, parser=parser)
    return root.xpath('/html/body/table[2]/tr[2]/td[5]/text()')[0].strip()


if __name__ == "__main__":

    PROJECT_FOLDER = "com.brocktice.JustSit_17_src"

    coverages = []

    for coverage_folder in os.listdir(settings.EMMA_ED + PROJECT_FOLDER + "/coverages/"):
        try:
            html_file = settings.EMMA_ED + settings.PROJECT_FOLDER + "/coverages/" + coverage_folder + "/coverage/index.html"
            coverage_str = extract_coverage(html_file)
            coverages.append(int(coverage_str.split("%")[0]))
        except:
            pass

    print max(coverages)
    print "len", len(coverages)
