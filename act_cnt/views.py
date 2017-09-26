# -*- coding: utf-8 -*-
from __future__ import print_function
from django.shortcuts import render
from django.http import HttpResponse
import psycopg2
import json
from act_cnt import models
from django.shortcuts import render_to_response
# Create your views here.

import datetime
import random
import shutil
import socket
import time
import oss2
from django.http import StreamingHttpResponse

import os, tempfile, zipfile  
# from django.http import HttpResponse  
# from django.core.servers.basehttp import FileWrapper  
from wsgiref.util import FileWrapper
import urllib2
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseServerError
from django import http
import sys
from django.shortcuts import render

from leancloud import Object
from leancloud import Query
from leancloud.errors import LeanCloudError
import leancloud
# import time
# import datetime
import hashlib
# from random import Random
# import sys

def first_page(request):
    return HttpResponse("<p>Gotcha!!!!</p>")

def get_active_totalnums(request):
    cb_mine = request.GET.get('_cb_mine')
    result_item = cb_mine+"("+models.get_active_totalnums()+")"
    #result_item = models.get_active_totalnums()
    #print result_item
    #print HttpResponse(json.dumps(result_item), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")  
    #return result_item

def get_active_dailynums(request):
    proj_id = request.GET.get('proj_id')
    cb_mine = request.GET.get('_cb_mine')
    result_item = cb_mine+"("+models.get_active_dailynums(proj_id)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")  
    #return result_item	

def get_active_dailynums_filter(request):
    proj_id = request.GET.get('proj_id')
    cb_mine = request.GET.get('_cb_mine')
    date_range = request.GET.get('value')
    result_item = cb_mine+"("+models.get_active_dailynums_filter(proj_id,date_range)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")  
    #return result_item 

def insert_daily_fake_data(request):
    #print "fffffffff"
    return HttpResponse(models.insert_daily_fake_data())

def insert_daily_fake_data_fortesting_rate(request):
    #print "fffffffff"
    return HttpResponse(models.insert_daily_fake_data_fortesting_rate())    
    

def insert_daily_fake_data_fortesting(request):
    # print "fffffffff"
    return HttpResponse(models.insert_daily_fake_data_fortesting())

def get_list_by_date(request):
    proj_id = request.GET.get('proj_id')
    cb_mine = request.GET.get('_cb_mine')
    result_item = models.get_list_by_date()
    #result_item = cb_mine+"("+models.get_list_by_date()+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")  
    #return result_item 

def get_list_by_country(request):
    proj_id = request.GET.get('proj_id')
    cb_mine = request.GET.get('_cb_mine')
    result_item = models.get_list_by_country()
    #result_item = cb_mine+"("+models.get_list_by_date()+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")  
    #return result_item     

def get_user_info(request):
    cb_mine = request.GET.get('_cb_mine')
    result_item = cb_mine+"("+models.get_user_info()+")"
    #result_item = models.get_active_totalnums()
    #print result_item
    #print HttpResponse(json.dumps(result_item), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")      


def get_top5_lively_country(request):
    proj_id = request.GET.get('proj_id')
    cb_mine = request.GET.get('_cb_mine')
    result_item = cb_mine+"("+models.get_top5_lively_country(proj_id)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")  

def get_map_data(request):
    proj_id = request.GET.get('proj_id')
    cb_mine = request.GET.get('_cb_mine')
    result_item = cb_mine+"("+models.get_map_data(proj_id)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")  

####################
def get_tongji_to_frontpage(request):
    user_name = request.GET.get('user_name')
    cb_mine = request.GET.get('_cb_mine')
    #cb_mine="fff"
    date_1 = request.GET.get('value1')
    date_2 = request.GET.get('value2')
    proj = request.GET.get('proj')
    result_item = cb_mine+"("+models.get_tongji_to_frontpage(user_name,date_1,date_2,proj)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain") 

def get_tongji_to_frontpage_proj(request):
    user_name = request.GET.get('user_name')
    cb_mine = request.GET.get('_cb_mine')
    #cb_mine="fff"
    date_1 = request.GET.get('value1')
    date_2 = request.GET.get('value2')
    proj = request.GET.get('proj')
    result_item = cb_mine+"("+models.get_tongji_to_frontpage_proj(user_name,date_1,date_2,proj)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain") 


def get_sum_to_frontpage(request):
    user_name = request.GET.get('user_name')
    cb_mine = request.GET.get('_cb_mine')
    # cb_mine = "ffff"
    date_1 = request.GET.get('date_1')
    date_2 = request.GET.get('date_2')
    proj = request.GET.get('proj')
    result_item = cb_mine+"("+models.get_sum_to_frontpage(user_name,date_1,date_2,proj)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain") 

def get_sum_to_frontpage_proj(request):
    user_name = request.GET.get('user_name')
    cb_mine = request.GET.get('_cb_mine')
    date_1 = request.GET.get('value1')
    date_2 = request.GET.get('value2')
    # cb_mine = "ffff"
    proj = request.GET.get('proj')
    result_item = cb_mine+"("+models.get_sum_to_frontpage_proj(user_name,date_1,date_2,proj)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain") 


def get_user_info_list(request):
    user_name = request.GET.get('user_name')
    cb_mine = request.GET.get('_cb_mine')
    name_filter = request.GET.get('value')
    result_item = cb_mine+"("+models.get_user_info_list(user_name,name_filter)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")     

def put_logintime(request):
    #print "fffffffff"
    user_name = request.GET.get('user_name')    
    cb_mine = request.GET.get('_cb_mine')
    # name_filter = request.GET.get('value')
    result_item = cb_mine+"("+models.put_logintime(user_name)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")  

def get_user_logintime_list(request):
    #print "fffffffff"
    user_name = request.GET.get('user_name')    
    cb_mine = request.GET.get('_cb_mine')
    # name_filter = request.GET.get('value')
    result_item = cb_mine+"("+models.get_user_logintime_list(user_name)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain") 

def change_passwd(request):
    #print "fffffffff"
    user_name = request.GET.get('user_name')    
    passwd = request.GET.get('passwd')      
    cb_mine = request.GET.get('_cb_mine')
    # name_filter = request.GET.get('value')
    result_item = cb_mine+"("+models.change_passwd(user_name, passwd)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")

def froze_accout(request):
    #print "fffffffff"
    user_name = request.GET.get('user_name')    
    passwd = request.GET.get('passwd')      
    cb_mine = request.GET.get('_cb_mine')
    # name_filter = request.GET.get('value')
    result_item = cb_mine+"("+models.froze_accout(user_name)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")

def change_role(request):
    #print "fffffffff"
    user_name = request.GET.get('user_name')    
    role = request.GET.get('role')      
    cb_mine = request.GET.get('_cb_mine')
    # name_filter = request.GET.get('value')
    result_item = cb_mine+"("+models.change_role(user_name, role)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")

def get_rolemenues_info(request):
    #print "fffffffff"
    # user_name = request.GET.get('user_name')    
    cb_mine = request.GET.get('_cb_mine')
    # name_filter = request.GET.get('value')
    result_item = cb_mine+"("+models.get_rolemenues_info()+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")     

def get_projs(request):
    #print "fffffffff"
    # user_name = request.GET.get('user_name')    
    cb_mine = request.GET.get('_cb_mine')
    # name_filter = request.GET.get('value')
    result_item = cb_mine+"("+models.get_projs()+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain") 

def change_related_project(request):
    #print "fffffffff"
    user_name = request.GET.get('user_name')    
    cb_mine = request.GET.get('_cb_mine')
    arr_projs = request.GET.get('arr_projs')
    result_item = cb_mine+"("+models.change_related_project(user_name,arr_projs)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain") 

################################################## 2017-04-17
def get_active_totalnums_by_proj(request):    
    #print "fffffffff"
    user_name = request.GET.get('user_name')    
    # cb_mine = request.GET.get('_cb_mine')
    # cb_mine = "fffff"
    # name_filter = request.GET.get('value')
    result_item = cb_mine+"("+models.get_active_totalnums_by_proj(user_name)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")

def get_project_info(request):    
    #print "fffffffff"
    user_name = request.GET.get('user_name')    
    # cb_mine = request.GET.get('_cb_mine')
    # cb_mine = "fffff"
    # name_filter = request.GET.get('value')
    result_item = cb_mine+"("+models.get_active_totalnums_by_proj(user_name)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")

def save_project_info(request):
    #print "fffffffff"
    former_user_name = request.GET.get('former_user_name')    
    new_user_name = request.GET.get('new_user_name')
    # cb_mine = request.GET.get('_cb_mine')
    url = request.GET.get('url')
    manual_sum = request.GET.get('manual_sum')
    api_id = request.GET.get('api_id')
    result_item = cb_mine+"("+models.save_project_info(former_user_name,new_user_name,url,manual_sum,api_id)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain")  

def get_sum_each_proj(request):       
    proj_name = request.GET.get('proj_name')
    # cb_mine = request.GET.get('_cb_mine')
    date_1 = request.GET.get('date_1')
    date_2 = request.GET.get('date_2')    
    result_item = models.get_sum_each_proj(proj_name,date_1,date_2)

    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain") 
################################################### 2017-04-17
def change_comment(request):
    #print "fffffffff"
    user_name = request.GET.get('user_name')    
    cb_mine = request.GET.get('_cb_mine')
    comment = request.GET.get('comment')
    result_item = cb_mine+"("+models.change_comment(user_name,comment)+")"
    #print result_item
    #return HttpResponse(json.dumps(result_item,ensure_ascii=False), content_type="application/json") 
    return HttpResponse(result_item, content_type="text/plain") 
    
def insert_formatted_data_to_db_pass(request):
    #print "fffffffff"
    file_name = request.GET.get('file_name')
    time = request.GET.get('time')    
    proj_name = request.GET.get('proj_name')      
    return HttpResponse(models.insert_formatted_data_to_db_pass(file_name,time,proj_name)) 

def put_active_datelist_into_db(request):
    #print "fffffffff"
    # arr = request.GET.get('arr')
    # time = request.GET.get('time')    
    # proj_name = request.GET.get('proj_name')      
    return HttpResponse(models.put_active_datelist_into_db()) 

def put_daily_active_total_2016(request):
    #print "fffffffff"
    # file_name = request.GET.get('file_name')
    # time = request.GET.get('time')    
    # proj_name = request.GET.get('proj_name')      
    return HttpResponse(models.put_daily_active_total_2016())  

def insert_formatted_data_to_db_pass_new_2017(request):
    #print "fffffffff"
    # file_name = request.GET.get('file_name')
    # time = request.GET.get('time')    
    # proj_name = request.GET.get('proj_name') 
    return HttpResponse(models.insert_formatted_data_to_db_pass_new_2017())      
  
def get_all_table_name(request):
    #print "fffffffff"
    # file_name = request.GET.get('file_name')
    # time = request.GET.get('time')    
    # proj_name = request.GET.get('proj_name')      
    return HttpResponse(models.get_all_table_name()) 
    
def get_a(request):
    #print "fffffffff"
    # file_name = request.GET.get('file_name')
    # time = request.GET.get('time')    
    # proj_name = request.GET.get('proj_name')      
    return render_to_response('a.html')    

def get_b(request):
    #print "fffffffff"
    # file_name = request.GET.get('file_name')
    # time = request.GET.get('time')    
    # proj_name = request.GET.get('proj_name')      
    return render_to_response('b.html')   

def insert_subchannel_into_db(request):
    #print "fffffffff"
    # file_name = request.GET.get('file_name')
    # time = request.GET.get('time')    
    # proj_name = request.GET.get('proj_name') 
    return HttpResponse(models.insert_subchannel_into_db()) 

def add_columns_to_dailyactive_tables(request):
    #print "fffffffff"
    # file_name = request.GET.get('file_name')
    # time = request.GET.get('time')    
    # proj_name = request.GET.get('proj_name') 
    return HttpResponse(models.add_columns_to_dailyactive_tables())   

def add_columns_to_duli_tables(request):
    #print "fffffffff"
    # file_name = request.GET.get('file_name')
    # time = request.GET.get('time')    
    # proj_name = request.GET.get('proj_name') 
    return HttpResponse(models.add_columns_to_duli_tables())   

def add_columns_to_total_tables(request):
    #print "fffffffff"
    # file_name = request.GET.get('file_name')
    # time = request.GET.get('time')    
    # proj_name = request.GET.get('proj_name') 
    return HttpResponse(models.add_columns_to_total_tables())       
    

def put_total_active_II(request):
    #print "fffffffff"
    # file_name = request.GET.get('file_name')
    # time = request.GET.get('time')    
    # proj_name = request.GET.get('proj_name') 
    return HttpResponse(models.put_total_active_II())     
           
####################
def putting_data(request):
    #print "fffffffff"
    return HttpResponse(models.putting_data())   
    
def insert_formatted_data_to_db(request):
    #print "fffffffff"
    file_name = request.GET.get('file_name')
    time = request.GET.get('time')    
    proj_name = request.GET.get('proj_name')      
    return HttpResponse(models.insert_formatted_data_to_db(file_name,time,proj_name))   

def create_new_table_for_daily_active(request):
    #print "fffffffff"    
    return HttpResponse(models.create_new_table_for_daily_active()) 

def insert_all_daily_data(request):
    #print "fffffffff"    
    return HttpResponse(models.insert_all_daily_data())                 

def insert_formatted_data_to_db_imsi(request):
    #print "fffffffff"
    return HttpResponse(models.insert_formatted_data_to_db_imsi())   
     
    
def check_files_for_updated(request):
    #print "fffffffff"
    return HttpResponse(models.check_files_for_updated())      

def index_cnt_from_cdn(request):
    #print "fffffffff"
    url = request.GET.get('url')
    date_from = request.GET.get('date_from') 
    date_to = request.GET.get('date_to')    
    # proj_name = request.GET.get('proj_name')      
    return HttpResponse(models.index_cnt_from_cdn(url,date_from,date_to)) 

def apk_cnt_from_cdn(request):
    #print "fffffffff"
    url = request.GET.get('url')
    date_from = request.GET.get('date_from')   
    date_to = request.GET.get('date_to')  
    # proj_name = request.GET.get('proj_name')      
    return HttpResponse(models.apk_cnt_from_cdn(url,date_from,date_to)) 

def redirect_to_dl(url):
    print(url)
    return http.HttpResponseRedirect(url)

def percentage(consumed_bytes, total_bytes):
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        print('\r{0}% '.format(rate), end='')
        sys.stdout.flush()
    
def download_file(filename):  
    # do something  
    the_file_name = filename
    # the_file_name='11.png'             #显示在弹出对话框中的默认的下载文件名      
    # filename='media/uploads/11.png'    #要下载的文件路径  
    print(" download file !!!!! ")
    response=StreamingHttpResponse(readFile(filename))  
    response['Content-Type']='application/octet-stream'  
    response['Content-Disposition']='attachment;filename="{0}"'.format(the_file_name)  
    return response  
  
def readFile(filename,chunk_size=512):  
    with open(filename,'rb') as f:  
        while True:  
            c=f.read(chunk_size)  
            if c:  
                yield c  
            else:  
                break  

def download_multiapks(request):
    #print "fffffffff"
    apks = request.GET.get('apks')  

    apk_col = apks.split("$$$")

    AccesKeyID = 'AjHtBvujgTZo3JUw'
    AccessKeySecret = 'WsgWVEzBi0nHNwoC0mNEBJaMk5iWx7'
    auth = oss2.Auth(AccesKeyID, AccessKeySecret)
    EndPoint = 'oss-cn-hangzhou.aliyuncs.com'
    bucket_name_apk = 'apk-tripics'
    bucket_name_apk_cdn = "apk"
    bucket_name_apk_internal = 'apk-internal'
    bucket_name_apk_internal_cdn = "apk-internal"
    bucket_apk = oss2.Bucket(auth, EndPoint, bucket_name_apk)
    bucket_apk_internal = oss2.Bucket(auth, EndPoint, bucket_name_apk_internal)
    
    response_col = []
    url_col = []
    url_col_str = ""
    for every_apk in apk_col:
        if bucket_apk.object_exists(every_apk):
            cdn_url = "https://"+bucket_name_apk_cdn+".thetripics.com/"+every_apk
            url_col_str = url_col_str + cdn_url
            url_col.append(cdn_url)
            # bucket_apk.get_object_to_file(every_apk, every_apk,progress_callback=percentage)
            # print("going in ")
            # response_col.append(download_file(every_apk))
            # f = open(every_apk)
            # return HttpResponse(f)
            # urllib.urlretrieve(cdn_url, localPDF)
            # get_file_from_url(cdn_url)
            # print("apk !!")
            # return HttpResponseRedirect("baidu.com")
            # redirect_to_dl(cdn_url)
        elif bucket_apk_internal.object_exists(every_apk):
            # bucket_apk_internal.get_object_to_file(every_apk, every_apk,progress_callback=percentage)
            cdn_url = "https://"+bucket_name_apk_internal_cdn+".thetripics.com/"+every_apk
            url_col_str = url_col_str + cdn_url
            url_col.append(cdn_url)
            # response_col.append(download_file(every_apk))
            # redirect_to_dl(cdn_url)
    # url_col_str='"' + url_col_str + '"'
    # time_now_com = timezone.localtime(timezone.now()).strftime("'%Y-%m-%d_%H_%M_%S'")
    # cmd = "tar -cvf apks_"+time_now_com+".tar  *.apk"
    # os.system(cmd)
    # print('zip over')
    
    # wrapper = FileWrapper(file(filename))  
    # response = HttpResponse(wrapper, content_type='text/plain')  
    # response['Content-Length'] = os.path.getsize(filename)  
    # return response 

    # return HttpResponse("success")
    # return response_col
    context          = {}  
    context['List'] = json.dumps(url_col)
    return render(request, 'multi_dl.html', context,content_type='text/html')      
    # proj_name = request.GET.get('proj_name')      
    
    # return HttpResponse(models.download_multiapks(apks)) 

def get_pure_dnu(request):  
    argv = request.GET.get('proj_id')    
    # proj_name = request.GET.get('proj_name')      
    return HttpResponse(models.get_pure_dnu(argv), content_type="text/plain") 