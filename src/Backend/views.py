from django.shortcuts import render_to_response, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from time import time
import re

from utils import *

def homepage(request):
    return render_to_response('homepage.html')

def search(request):
    if request.GET.get('wd', None) and request.GET["wd"]:
        inverted_index = load_obj("inverted_index")
        query = request.GET["wd"].lower()

        start = time()
        res_vec = parse_query(inverted_index, query, use_skip=True)
        stop = time()
        search_time = stop - start

        res = []
        len_res = len(res_vec)
        for node in res_vec.nodes:
            num = node.data
            html = f'.\cacm\CACM-{str(num).zfill(4)}.html'

            with open(html,'r',encoding="utf-8") as f:
                html = f.readlines()
            tmp = []
            for line in html:
                if '<' in line or '\t' in line or line == '\n':
                    pass
                else:
                    tmp.append(line[:-1])

            title = ""
            for line in tmp:
                if "CACM" in line:
                    break
                title += " " + line
            title = re.sub(' +', ' ', title)

            res.append({'name': f"CACM-{str(num).zfill(4)}.html", 'title':title})

        gap = 15
        pages = Paginator(res, gap)
        num_page = int(request.GET.get('page', 1))
        len_page = len(res) // gap + 1

        try:
           res = pages.page(num_page)
        except EmptyPage:
           res = pages.page(1)
           num_page = 1

        args = {'wd':request.GET["wd"], 'res':res, 'search_time':search_time, 'len_res':len_res, 'len_page':len_page, 'num_page':num_page, 'range_page':range(1, len_page+1)}
        return render_to_response('result.html', args)
    else:
        return render_to_response('homepage.html')



