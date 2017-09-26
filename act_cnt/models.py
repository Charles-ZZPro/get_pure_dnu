#-*-coding:utf-8-*-
from __future__ import print_function
from __future__ import unicode_literals
import gzip 
import tarfile
import os
from django.db import models
import psycopg2
import sys
import datetime
import random
import shutil
import socket
import time
import oss2
from django.http import StreamingHttpResponse
import os, tempfile, zipfile  
from django.http import HttpResponse  
# from django.core.servers.basehttp import FileWrapper  
from wsgiref.util import FileWrapper
import urllib2
from django.http import HttpResponseRedirect  

from leancloud import Object
from leancloud import Query
from leancloud.errors import LeanCloudError
import leancloud
# import time
# import datetime
import hashlib
# from random import Random
# import sys

#from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY

reload(sys)
sys.setdefaultencoding('utf-8')

# Create your models here.
def get_pgconn():
    # Connect to an existing database
    conn = psycopg2.connect("dbname=myTestDB user=postgres password=postgres")
    #conn = psycopg2.connect("dbname=myTestDB user=littleAdmin password=postgres")
    # Open a cursor to perform database operations
    cur = conn.cursor()
    return cur,conn

def close_pgconn(cur,conn):
    cur.close()    
    conn.close()

def commit_conn(conn):
	conn.commit()

def get_active_totalnums():
    cur,conn= get_pgconn()
    sql_get_act = "select proj_name, proj_id, sum(act_num) cnt_num from table_activate_num_fake group by proj_id, proj_name order by proj_id limit 1"
    cur.execute(sql_get_act)
    results = cur.fetchall()
    close_pgconn(cur,conn)
    result_item = []
    result_str = ""
    
    for item in results:
    	each_result = {}
    	each_result['title'] = item[0]
    	each_result['title'] = each_result['title'].encode('utf-8')
    	##print type(each_result['title'])    	
    	##print each_result['title']
    	each_result['number'] = str(item[2])
        #result_str_each = each_result['title'] + "," + each_result['number']
        result_item.append(each_result)
        result_str = result_str+'{"title":"' + each_result['title'] +'",'+'"number":"' + each_result['number'] + '","id":"'+str(item[1])+'"},'
    ##print result_item
    #return HttpResponse("<p>"+str(result_item)+"</p>")
    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"tuple":[' + result_str +']}'
    ##print result_str
    #result_str = result_str.replace("\","")
    ##print result_str
    json_total = {}
    json_total['tuple'] = result_item

    #return json_total
    return result_str

def get_active_dailynums(proj_id):

    cur,conn= get_pgconn()
    sql_get_act = "select date_s,sum(act_num),avg(rate) from table_activate_num_fake where proj_id=" + str(proj_id)+" group by date_s order by date_s desc"
    cur.execute(sql_get_act)
    results = cur.fetchall()
    close_pgconn(cur,conn)

    cur,conn= get_pgconn()
    sql_get_act = "select sum(act_num) from table_activate_num_fake where proj_id=" + str(proj_id)
    cur.execute(sql_get_act)
    results_all = cur.fetchall()
    close_pgconn(cur,conn)

    result_item = []
    result_str = ""
    join_user = ""

    add_num = results_all[0][0]+results[0][1]

    for index ,item in enumerate(results):
        each_result = {}
        each_result['date'] = item[0].encode('utf-8')
        each_result['act_num'] = item[1]
        #each_result['rate'] = '%.4f' %(item[2])
        each_result['rate'] = item[2]
        if index==0:
            add_num = add_num - results[0][1]
        else:
            add_num = add_num-results[index-1][1]

        each_result['lively_num'] = int(add_num*each_result['rate'])
        result_str = result_str+'{date:"' + each_result['date'] +'",'+'activated_num:' + str(each_result['act_num']) + ',addup_num:' + str(add_num) + ',lively_num:' + str(each_result['lively_num']) +'},'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}'        

    return result_str    

def get_active_dailynums_filter(proj_id,date_range):
    
    # #print date_range

    date_range_array = date_range.split(",")
    date_range_box = []
    date_from = ""
    date_to = ""

    for j in date_range_array:
        date_array = j.split(' ')
        month = date_array[1]
        day = date_array[2]
        year = date_array[3]
        if month == 'Jan':
            month = '1'
        elif month == 'Feb':
            month = '2' 
        elif month == 'Mar':
            month = '3' 
        elif month == 'Apr':
            month = '4'             
        elif month == 'May':
            month = '5'     
        elif month == 'Jun':
            month = '6' 
        elif month == 'Jul':
            month = '7' 
        elif month == 'Aug':
            month = '8'             
        elif month == 'Sep':
            month = '9'   
        elif month == 'Oct':
            month = '10' 
        elif month == 'Nov':
            month = '11'             
        elif month == 'Dec':
            month = '12' 
        formatted_date = year +"-"+ month +"-"+ day
        date_range_box.append(formatted_date)

    date_from = date_range_box[0]
    date_to = date_range_box[1]

    cur,conn = get_pgconn()
    sql_get_act = "select date_s,sum(act_num),avg(rate) from table_activate_num_fake where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+"' group by date_s order by date_s desc"
    cur.execute(sql_get_act)
    results = cur.fetchall()
    close_pgconn(cur,conn)    
    result_item = []
    result_str = ""
    
    if results!=[]:
        for item in results:
            each_result = {}
            each_result['date'] = item[0]
            each_result['date'] = each_result['date'].encode('utf-8')     
            each_result['number'] = int(item[1])   
            each_result['rate'] = item[2] 

            result_item.append(each_result)

            cur,conn = get_pgconn()
            sql_get_act_each_total = "select sum(act_num) from table_activate_num_fake where proj_id=" + str(proj_id)+" and date_s<='" + each_result['date'] +"'"
            cur.execute(sql_get_act_each_total)
            results = cur.fetchall()       
            close_pgconn(cur,conn)  
            each_result['lively_num'] = int(results[0][0]*each_result['rate'])      

            result_str = result_str+'{"date":"' + each_result['date'] +'",'+'"activated_num":"' + str(each_result['number']) + '","addup_num":"' + str(results[0][0]) +'"'+ ',"lively_num":"' + str(each_result['lively_num']) + '"},'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}'        

    return result_str  

def insert_daily_fake_data():
    now = datetime.datetime.now()
    rand1 = str(random.randint(1000, 1000000))
    rand2 = str(random.randint(1000, 1000000))
    rand3 = str(random.randint(1000, 1000000))
    rand4 = str(random.randint(1000, 1000000))
    date_str = now.strftime('%Y-%m-%d')  

    cur,conn = get_pgconn()
      
    sql_insert_act = "insert into table_activate_num(proj_name,date_s,act_num,proj_id) values('第一个项目','"+date_str+"',"+rand1+",1);"+\
    "insert into table_activate_num(proj_name,date_s,act_num,proj_id) values('第二个项目','"+date_str+"',"+rand2+",2);"+\
    "insert into table_activate_num(proj_name,date_s,act_num,proj_id) values('第三个项目','"+date_str+"',"+rand3+",3);"+\
    "insert into table_activate_num(proj_name,date_s,act_num,proj_id) values('第四个test项目','"+date_str+"',"+rand4+",4);"

    ##print sql_insert_act                    
    cur.execute(sql_insert_act)
    commit_conn(conn)   
    close_pgconn(cur,conn)
    #results = cur.fetchall()
    # #print " that is enough"
    return "OK"

def insert_daily_fake_data_fortesting():

    now = datetime.datetime.now()
    delta=datetime.timedelta(days=1)
    t_str = '2016-12-29'
    now_fake = datetime.datetime.strptime(t_str,'%Y-%m-%d')
    rand1 = random.randint(5000,5300)
    t_str_end = '2017-01-08'
    t_str_end_fake = datetime.datetime.strptime(t_str_end,'%Y-%m-%d')

    while now_fake.strftime('%Y-%m-%d') < t_str_end_fake.strftime('%Y-%m-%d'):
        now_fake=now_fake+delta
        date_str = now_fake.strftime('%Y-%m-%d')
        rand1 = rand1 + random.randint(200, 600)
        rand1_uni = random.uniform(0.88,0.92)
        date_str = now_fake.strftime('%Y-%m-%d')  
        sql_insert_act = "insert into table_activate_num_fake(proj_name,date_s,act_num,proj_id,country,rate) values('project_1','"+date_str+"',"+str(rand1)+",1,'China',"+str(rand1_uni)+");"

    # #print " that is enough"
    return "OK"

def insert_daily_fake_data_fortesting_rate():

    now = datetime.datetime.now()
    delta=datetime.timedelta(days=1)
    t_str = '2016-10-21'
    now_fake = datetime.datetime.strptime(t_str,'%Y-%m-%d')
    rand1 = random.randint(200,400)

    for id_got in range(1105,2500): 
        cur,conn = get_pgconn()        
        rand1 = random.uniform(0.20,0.99)      
        #sql_insert_act = "update table_activate_num_fake set rate="+str(rand1)+" where country='bra' and id="+str(id_got)
        sql_insert_act = "update table_activate_num_fake set rate="+str(rand1)+" where id="+str(id_got)
        # #print sql_insert_act
        id_got=id_got+1
        cur.execute(sql_insert_act)
        commit_conn(conn)   
        close_pgconn(cur,conn)        

    # #print " that is enough"
    return "OK"

def insert_daily_fake_data_fortesting_daily():
    now = datetime.datetime.now()
    rand1 = random.randint(200,400)

    date_str = now.strftime('%Y-%m-%d')  

    # #print " that is enough"
    return "OK"

def get_list_by_date():
    cur,conn= get_pgconn()
    sql_get_act = "select date_s,sum(act_num),avg(rate) from table_activate_num_fake group by date_s order by date_s desc"
    cur.execute(sql_get_act)
    results = cur.fetchall()
    close_pgconn(cur,conn)

    cur,conn= get_pgconn()
    sql_get_act = "select sum(act_num) from table_activate_num_fake"
    cur.execute(sql_get_act)
    results_all = cur.fetchall()
    close_pgconn(cur,conn)

    result_item = []
    result_str = ""
    join_user = ""

    add_num = results_all[0][0]+results[0][1]

    for index ,item in enumerate(results):
        each_result = {}
        each_result['date'] = item[0].encode('utf-8')
        each_result['act_num'] = item[1]
        #each_result['rate'] = '%.4f' %(item[2])
        each_result['rate'] = item[2]
        if index==0:
            add_num = add_num - results[0][1]
        else:
            add_num = add_num-results[index-1][1]

        each_result['lively_num'] = int(add_num*each_result['rate'])
        result_str = result_str+'{date:"' + each_result['date'] +'",'+'activated_num:' + str(each_result['act_num']) + ',addup_num:' + str(add_num) + ',lively_num:' + str(each_result['lively_num']) +'},'
   
    #result_str = join_user 
    result_str = result_str[0:int(len(result_str))-1]  
    result_str = '{tuple:[' + result_str +']}'   

    ##print result_str
    return result_str

def get_list_by_country():
    cur,conn= get_pgconn()
    sql_get_act = "select country,sum(act_num) s,avg(rate) from table_activate_num_fake group by country order by s desc"
    cur.execute(sql_get_act)
    results = cur.fetchall()
    close_pgconn(cur,conn)
    result_item = []
    result_str = ""
    join_user = ""

    add_num = 2645225+75170

    for index ,item in enumerate(results):
        each_result = {}        

        each_result['country'] = item[0]
        if each_result['country']=='india':
            each_result['country'] = '印度'
        elif each_result['country']=='indonisia':
            each_result['country'] = '印度尼西亚'
        elif each_result['country']=='viet':      
             each_result['country'] = '越南'
        elif each_result['country']=='spain':
            each_result['country'] = '西班牙'
        elif each_result['country']=='italy':  
            each_result['country'] = '意大利'
        elif each_result['country']=='malay':
            each_result['country'] = '马来西亚'
        elif each_result['country']=='bra':  
            each_result['country'] = '巴西'
        elif each_result['country']=='eng':
            each_result['country'] = '英国'
        elif each_result['country']=='taiwan': 
             each_result['country'] = '台湾'
        elif each_result['country']=='us':
            each_result['country'] = '美国'
        elif each_result['country']=='cn':  
            each_result['country'] = '中国'
        elif each_result['country']=='thai':
            each_result['country'] = '泰国'

        each_result['country'] = each_result['country'].encode('utf-8')
        each_result['act_num'] = item[1]
        each_result['rate'] = item[2]
        if index==0:
            add_num = add_num - 75170
        else:
            add_num = add_num-results[index-1][1]
        rate_country = str('%.2f'%((each_result['act_num']/2645225.0)*100.0))+"%"

        each_result['lively_num'] = int(add_num*each_result['rate'])
        result_str = result_str+'{name:"' + each_result['country'] +'",'+'value:' + str(each_result['act_num'])+',percent:"'+str(rate_country)+'"},'
   
    result_str = result_str[0:int(len(result_str))-1]  
    result_str = '{tuple:[' + result_str +']}'   

    ##print result_str
    return result_str

def get_user_info():
    cur,conn= get_pgconn()
    sql_get_act = "select user_name, passwd ,status from table_user"
    cur.execute(sql_get_act)
    results = cur.fetchall()
    close_pgconn(cur,conn)
    result_item = []
    result_str = ""
    join_user = ""

    for item in results:
        each_result = {}
        each_result['user_name'] = item[0].encode('utf-8')
        each_result['passwd'] = item[1].encode('utf-8')
        each_result['status'] = item[2].encode('utf-8')
        join_user = join_user + each_result['user_name'] + each_result['passwd'] +each_result['status']+ "Mypassinstringhere"
 
    result_str = join_user 
    result_str = '{"tuple":"' + result_str +'"}'
    # #print result_str

    return result_str

def get_top5_lively_country(proj_id):
    ##print "wocacca"
    cur,conn= get_pgconn()
    sql_get_all = "select sum(act_num) from table_activate_num_fake  where proj_id=" + str(proj_id)
    cur.execute(sql_get_all)
    results_all = cur.fetchall()
    close_pgconn(cur,conn)

    count_all = results_all[0][0]

    cur,conn= get_pgconn()
    sql_get_top5 = "select country,sum(act_num) sum from table_activate_num_fake where proj_id=" + str(proj_id)+" group by country order by sum desc limit 5 "
    cur.execute(sql_get_top5)
    results_top5 = cur.fetchall()
    close_pgconn(cur,conn)

    result_str = ""

    for item in results_top5:
        each_result = {}
        each_result['country'] = item[0].encode('utf-8')
        each_result['sum'] = item[1]

        each_result['rate'] = str('%.2f'%((float(each_result['sum'])/count_all)*100.0))+"%"
        result_str = result_str + '{name:"' + each_result['country'] +'",'+'value:' + str(each_result['sum'])+',percent:"'+str(each_result['rate'])+'"},'
 
    result_str = result_str[0:int(len(result_str))-1]  
    result_str = '{allData:[' + result_str +']}'   
    ##print result_str

    return result_str    

def get_map_data(proj_id):
    cur,conn= get_pgconn()
    sql_get_all = "select sum(act_num) from table_activate_num_fake where proj_id=" + str(proj_id)
    cur.execute(sql_get_all)
    results_all = cur.fetchall()
    close_pgconn(cur,conn)

    count_all = results_all[0][0]

    cur,conn= get_pgconn()
    sql_get_top5 = "select country,sum(act_num) sum from table_activate_num_fake where proj_id=" + str(proj_id) +" group by country order by sum desc"
    cur.execute(sql_get_top5)
    results_top5 = cur.fetchall()
    close_pgconn(cur,conn)

    result_str = ""

    for item in results_top5:
        each_result = {}
        each_result['country'] = item[0].encode('utf-8')
        each_result['sum'] = item[1]

        each_result['rate'] = str('%.2f'%((float(each_result['sum'])/count_all)*100.0))+"%"
        result_str = result_str + '{name:"' + each_result['country'] +'",'+'value:' + str(each_result['sum'])+',percent:"'+str(each_result['rate'])+'"},'
 
    result_str = result_str[0:int(len(result_str))-1]  
    result_str = '{allData:[' + result_str +']}'
    ##print result_str

    return result_str

def putting_data():
    cur,conn = get_pgconn()        
    #rand1 = random.uniform(0.20,0.99)      
    #sql_insert_act = "update table_activate_num_fake set rate="+str(rand1)+" where country='bra' and id="+str(id_got)
    sql_insert_act = "update table_activate_num_fake set proj_id=1 where date_s>'2017-01-05'"
    ##print sql_insert_act
    #id_got=id_got+1
    cur.execute(sql_insert_act)
    commit_conn(conn)   
    close_pgconn(cur,conn)     

    return "OK"

#create table for daily active
def create_new_table_for_daily_active():

    now_t = datetime.datetime.now()
    now_str_t = now_t.strftime('%Y_%m_%d')
    daily_table = "table_daily_active_"+now_str_t

    cur,conn = get_pgconn()  
    sql_create_seq = 'CREATE SEQUENCE public.'+daily_table+'_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 99999999 START 1 CACHE 1;'+'ALTER TABLE public.'+daily_table+'_id_seq OWNER TO "postgres";'    
    cur.execute(sql_create_seq)
    commit_conn(conn)   
    close_pgconn(cur,conn) 

    cur,conn = get_pgconn() 
    sql_create= 'CREATE TABLE public.'+daily_table+"(id integer NOT NULL DEFAULT nextval('"+daily_table+"_id_seq'::regclass),"+'imsi text,'\
      'imei text,'\
      'android_id text,'\
      'wifi_mac text,'\
      'date_s text,'\
      'proj_name text,'\
      'sub_channel_name text,'\
      'sub_channel_id text,'\
      'CONSTRAINT '+daily_table+'_pkey PRIMARY KEY (id))'\
      'WITH (OIDS=FALSE);'\
      'ALTER TABLE public.'+daily_table+' OWNER TO "postgres";'
    cur.execute(sql_create)
    commit_conn(conn)   
    close_pgconn(cur,conn) 

    return "OK"

#create table for daily active(2016 passed)
def create_new_table_for_daily_active_pass(date):

    daily_table = "table_daily_active_"+date
    cur,conn = get_pgconn()  
    sql_create_seq = 'CREATE SEQUENCE public.'+daily_table+'_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 99999999 START 1 CACHE 1;'+'ALTER TABLE public.'+daily_table+'_id_seq OWNER TO "postgres";'    
    cur.execute(sql_create_seq)
    commit_conn(conn)   
    close_pgconn(cur,conn) 

    cur,conn = get_pgconn() 
    sql_create= 'CREATE TABLE public.'+daily_table+"(id integer NOT NULL DEFAULT nextval('"+daily_table+"_id_seq'::regclass),"+'imsi text,'\
      'imei text,'\
      'android_id text,'\
      'wifi_mac text,'\
      'date_s text,'\
      'proj_name text,'\
      'sub_channel_name text,'\
      'sub_channel_id text,'\
      'CONSTRAINT '+daily_table+'_pkey PRIMARY KEY (id))'\
      'WITH (OIDS=FALSE);'\
      'ALTER TABLE public.'+daily_table+' OWNER TO "postgres";'      
    cur.execute(sql_create)
    commit_conn(conn)   
    close_pgconn(cur,conn) 

    return "OK"


#从rawdata压缩文件中提取有效新增独立用户，插入数据库
def insert_formatted_data_to_db(file_name,time,proj_name):

    time = time[0:10]
    file_name = '/home/charles/log/'+file_name

    """ungz zip file"""  
    f_name_tar = file_name.replace(".gz", "")  
    #获取文件的名称，去掉  
    g_file = gzip.GzipFile(file_name)  
    #创建gzip对象  
    open(f_name_tar, "w+").write(g_file.read())  
    #gzip对象用read()打开后，写入open()建立的文件中。  
    g_file.close()  
    #关闭gzip对象


    """untar zip file"""  
    tar = tarfile.open(f_name_tar)  
    names = tar.getnames()  
    if os.path.isdir(f_name_tar + "_files"):  
        pass  
    else:  
        os.mkdir(f_name_tar + "_files")  
    #由于解压后是许多文件，预先建立同名文件夹  
    for name in names:  
        tar.extract(name, f_name_tar + "_files/")  
    tar.close()  

    for file in os.listdir(f_name_tar + "_files/"):
        f = open(f_name_tar + "_files/"+file)
        #f = open(file)
        for i in f:
            if i.count('android_id')==0:
                continue
            else:
                ind_imsi = i.index('imsi')
                ind_imei = i.index('imei')
                ind_androidid = i.index('android_id')
                ind_mac = i.index('wifi_mac')

                imsi = i[ind_imsi+7:ind_imsi+22]
                imei = i[ind_imei+7:ind_imei+22]
                android_id = i[ind_androidid+13:ind_androidid+28]
                wifi_mac = i[ind_mac+11:ind_mac+28]

                ### calculating independent users
                cur,conn= get_pgconn()
                sql_get_all = "select count(id) from table_activate_num_ids  where imsi='" + imsi + "' or android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                cur.execute(sql_get_all)
                results_all = cur.fetchall()
                close_pgconn(cur,conn)

                if results_all[0][0]==0:
                    cur,conn = get_pgconn()  
                    sql_insert_act = "insert into table_activate_num_ids(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                    cur.execute(sql_insert_act)
                    commit_conn(conn)   
                    close_pgconn(cur,conn)         

                if imsi.count("UNKNOWN")>0 or imei.count("UNKNOWN")>0:
                    cur,conn= get_pgconn()
                    sql_get_all_unk = "select count(id) from table_activate_num_ids  where android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                    cur.execute(sql_get_all_unk)
                    results_all_unk = cur.fetchall()
                    close_pgconn(cur,conn)   

                    if results_all_unk[0][0]==0: 
                        cur,conn = get_pgconn()  
                        sql_insert_act = "insert into table_activate_num_ids(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                        cur.execute(sql_insert_act)
                        commit_conn(conn)   
                        close_pgconn(cur,conn) 

                ### calculating daily active users
                now_t = datetime.datetime.now()
                now_str_t = now_t.strftime('%Y_%m_%d')
                daily_table = "table_daily_active_"+now_str_t

                cur,conn= get_pgconn()
                sql_get_all = "select count(id) from "+daily_table+"  where imsi='" + imsi + "' or android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                cur.execute(sql_get_all)
                results_all = cur.fetchall()
                close_pgconn(cur,conn)

                if results_all[0][0]==0:
                    cur,conn = get_pgconn()  
                    sql_insert_act = "insert into "+daily_table+"(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                    cur.execute(sql_insert_act)
                    commit_conn(conn)   
                    close_pgconn(cur,conn)         

                if imsi.count("UNKNOWN")>0 or imei.count("UNKNOWN")>0:
                    cur,conn= get_pgconn()
                    sql_get_all_unk = "select count(id) from "+daily_table+"  where android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                    cur.execute(sql_get_all_unk)
                    results_all_unk = cur.fetchall()
                    close_pgconn(cur,conn)   

                    if results_all_unk[0][0]==0: 
                        cur,conn = get_pgconn()  
                        sql_insert_act = "insert into "+daily_table+"(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                        cur.execute(sql_insert_act)
                        commit_conn(conn)   
                        close_pgconn(cur,conn)            

    #os.remove(file_name)
    # os.remove(f_name_tar)
    shutil.rmtree(f_name_tar + "_files/")

    return "OK"

#从rawdata压缩文件中提取有效新增独立用户，插入数据库
def insert_formatted_data_to_db_pass(file_name,time,proj_name):

    time = time[0:10]

    file_name = '/home/charles/log/'+file_name

    """ungz zip file"""  
    f_name_tar = file_name.replace(".gz", "")  
    #获取文件的名称，去掉  
    g_file = gzip.GzipFile(file_name)  
    #创建gzip对象  
    open(f_name_tar, "w+").write(g_file.read())  
    #gzip对象用read()打开后，写入open()建立的文件中。  
    g_file.close()  
    #关闭gzip对象


    """untar zip file"""  
    tar = tarfile.open(f_name_tar)  
    names = tar.getnames()  
    if os.path.isdir(f_name_tar + "_files"):  
        pass  
    else:  
        os.mkdir(f_name_tar + "_files")  
    #由于解压后是许多文件，预先建立同名文件夹  
    ############ 2016 passed start
    ##print "extracting begin !!!!!!!!!!!!!!!!!!!!!!!!!!!!!1"
    ############ 2016 passed end     
    for name in names:  
        tar.extract(name, f_name_tar + "_files/")  
    tar.close()  
    ############ 2016 passed start
    ##print "extracting over !!!!!!!!!!!!!!!!!!!!!!!!!!!!!1"
    ############ 2016 passed end  
    ############ 2016 passed start
    time = ""
    time_p = ""
    daily_table_last = ""
    daily_table_list = []
    ############ 2016 passed end 
    for file in os.listdir(f_name_tar + "_files/"):
        f = open(f_name_tar + "_files/"+file)
        ############ 2016 passed start
        ##print file
        ############ 2016 passed end       

        #f = open(file)

        for i in f: 
            if i.count('android_id')==0:
                ############ 2016 passed start
                if i.count(']  INFO -- : [')!=0:
                    time = i[4:14]
                    time_p = time.replace("-","_")
                ############ 2016 passed end                
                continue
            else:
                ind_imsi = i.index('imsi')
                ind_imei = i.index('imei')
                ind_androidid = i.index('android_id')
                ind_mac = i.index('wifi_mac')

                imsi = i[ind_imsi+7:ind_imsi+22]
                imei = i[ind_imei+7:ind_imei+22]
                android_id = i[ind_androidid+13:ind_androidid+28]
                wifi_mac = i[ind_mac+11:ind_mac+28]

                #info_join = imsi+"$&&&#####"+imei+"$&&&#####"+android_id+"$&&&#####"+wifi_mac

                ### calculating independent users
                cur,conn= get_pgconn()
                #sql_get_all = "select count(id) from table_activate_num_ids  where imsi='" + imsi + "' or imei='" + imei +"' or android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                sql_get_all = "select count(id) from table_activate_num_ids  where imsi='" + imsi + "' or android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                cur.execute(sql_get_all)
                results_all = cur.fetchall()
                close_pgconn(cur,conn)

                if results_all[0][0]==0:
                    cur,conn = get_pgconn()  
                    sql_insert_act = "insert into table_activate_num_ids(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                    cur.execute(sql_insert_act)
                    commit_conn(conn)   
                    close_pgconn(cur,conn)         

                if imsi.count("UNKNOWN")>0 or imei.count("UNKNOWN")>0:
                    cur,conn= get_pgconn()
                    sql_get_all_unk = "select count(id) from table_activate_num_ids  where android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                    cur.execute(sql_get_all_unk)
                    results_all_unk = cur.fetchall()
                    close_pgconn(cur,conn)   

                    if results_all_unk[0][0]==0: 
                        cur,conn = get_pgconn()  
                        sql_insert_act = "insert into table_activate_num_ids(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                        cur.execute(sql_insert_act)
                        commit_conn(conn)   
                        close_pgconn(cur,conn) 

                ### calculating daily active users

                now_t = datetime.datetime.now()
                now_str_t = now_t.strftime('%Y_%m_%d')
                daily_table = "table_daily_active_"+now_str_t
           
                ############ 2016 passed start
                daily_table = "table_daily_active_"+time_p
                #daily_table_last = daily_table     
                if daily_table not in daily_table_list:
                    ##print "daily table existed !!!!!"   
                    #else:
                    create_new_table_for_daily_active_pass(time_p)
                    daily_table_last = daily_table
                    daily_table_list.append(daily_table)
                ############ 2016 passed end                


                cur,conn= get_pgconn()
                #sql_get_all = "select count(id) from "+daily_table+"  where imsi='" + imsi + "' or imei='" + imei +"' or android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                sql_get_all = "select count(id) from "+daily_table+"  where imsi='" + imsi + "' or android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                cur.execute(sql_get_all)
                results_all = cur.fetchall()
                close_pgconn(cur,conn)

                if results_all[0][0]==0:
                    cur,conn = get_pgconn()  
                    sql_insert_act = "insert into "+daily_table+"(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                    cur.execute(sql_insert_act)
                    commit_conn(conn)   
                    close_pgconn(cur,conn)         

                if imsi.count("UNKNOWN")>0 or imei.count("UNKNOWN")>0:
                    cur,conn= get_pgconn()
                    sql_get_all_unk = "select count(id) from "+daily_table+"  where android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                    cur.execute(sql_get_all_unk)
                    results_all_unk = cur.fetchall()
                    close_pgconn(cur,conn)   

                    if results_all_unk[0][0]==0: 
                        cur,conn = get_pgconn()  
                        sql_insert_act = "insert into "+daily_table+"(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                        cur.execute(sql_insert_act)
                        commit_conn(conn)   
                        close_pgconn(cur,conn)            

    #os.remove(file_name)
    # os.remove(f_name_tar)
    shutil.rmtree(f_name_tar + "_files/")

    ##print daily_table_list

    return "OK"


def compare(x, y):

    DIR = "/home/charles/log/kkk_files"

    stat_x = os.stat(DIR + "/" + x)

    stat_y = os.stat(DIR + "/" + y)

    if stat_x.st_ctime < stat_y.st_ctime:
        return -1
    elif stat_x.st_ctime > stat_y.st_ctime:
        return 1
    else:
        return 0


#从rawdata压缩文件中提取有效新增独立用户，插入数据库
def insert_formatted_data_to_db_pass_new_2017():

    proj_name = "Tripics"

    time = ""
    time_p = ""
    daily_table_last = ""

    sql_get_tables = "select pg_tables.tablename from pg_tables  where pg_tables.tablename LIKE 'table_daily_active_%' order by pg_tables.tablename"
    cur,conn= get_pgconn()
    cur.execute(sql_get_tables)
    results_get_tables = cur.fetchall()
    close_pgconn(cur,conn)    

    daily_table_list = []
    for item_tables in results_get_tables:
        daily_table_list.append(item_tables[0])

    f_name_tar = "/home/charles/log/kkk"

    ############ 2016 passed end 

    count_loop = 0

    for file in os.listdir(f_name_tar + "_files/"):
        f = open(f_name_tar + "_files/"+file)
        ############ 2016 passed start
        ##print ("file_name : "+str(file))
        ############ 2016 passed end       
        if file.count('production_')==0:
            ##print "Not log file !!!!!"
            # os.remove(f_name_tar + "_files/"+file)
            continue

        now_t = datetime.datetime.now()
        now_str_t = now_t.strftime('%Y-%m-%d')

        for i in f: 
            if i.count('android_id')!=0:
                ind_imsi = i.index('imsi')
                ind_imei = i.index('imei')
                ind_androidid = i.index('android_id')
                ind_mac = i.index('wifi_mac')

                imsi = i[ind_imsi+7:ind_imsi+22]
                imei = i[ind_imei+7:ind_imei+22]
                android_id = i[ind_androidid+13:ind_androidid+28]
                wifi_mac = i[ind_mac+11:ind_mac+28]

                ### calculating independent users
                cur,conn= get_pgconn()
                sql_get_all = "select count(id) from table_activate_num_ids  where imsi='" + imsi + "' or android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                cur.execute(sql_get_all)
                results_all = cur.fetchall()
                close_pgconn(cur,conn)

                if results_all[0][0]==0:
                    cur,conn = get_pgconn()  
                    sql_insert_act = "insert into table_activate_num_ids(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                    cur.execute(sql_insert_act)
                    commit_conn(conn)   
                    close_pgconn(cur,conn)         

                if imsi.count("UNKNOWN")>0 or imei.count("UNKNOWN")>0:
                    cur,conn= get_pgconn()
                    sql_get_all_unk = "select count(id) from table_activate_num_ids  where android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                    cur.execute(sql_get_all_unk)
                    results_all_unk = cur.fetchall()
                    close_pgconn(cur,conn)   

                    if results_all_unk[0][0]==0: 
                        cur,conn = get_pgconn()  
                        sql_insert_act = "insert into table_activate_num_ids(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                        cur.execute(sql_insert_act)
                        commit_conn(conn)   
                        close_pgconn(cur,conn) 

                ### calculating daily active users

                now_t = datetime.datetime.now()
                now_str_t = now_t.strftime('%Y_%m_%d')
                daily_table = "table_daily_active_"+now_str_t
           
                ############ 2016 passed start
                daily_table = "table_daily_active_"+time_p
                #daily_table_last = daily_table     
                if daily_table not in daily_table_list:
                    ##print "daily table existed !!!!!"   
                    #else:
                    if time_p=="":
                        return "first line userstat!!!"
                    create_new_table_for_daily_active_pass(time_p)
                    daily_table_last = daily_table
                    daily_table_list.append(daily_table)
                ############ 2016 passed end                


                cur,conn= get_pgconn()
                sql_get_all = "select count(id) from "+daily_table+"  where imsi='" + imsi + "' or android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                cur.execute(sql_get_all)
                results_all = cur.fetchall()
                close_pgconn(cur,conn)

                if results_all[0][0]==0:
                    cur,conn = get_pgconn()  
                    sql_insert_act = "insert into "+daily_table+"(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                    cur.execute(sql_insert_act)
                    commit_conn(conn)   
                    close_pgconn(cur,conn)         

                if imsi.count("UNKNOWN")>0 or imei.count("UNKNOWN")>0:
                    cur,conn= get_pgconn()
                    sql_get_all_unk = "select count(id) from "+daily_table+"  where android_id='"+android_id+"' or wifi_mac='"+wifi_mac+"' and proj_name='"+proj_name+"'"
                    cur.execute(sql_get_all_unk)
                    results_all_unk = cur.fetchall()
                    close_pgconn(cur,conn)   

                    if results_all_unk[0][0]==0: 
                        cur,conn = get_pgconn()  
                        sql_insert_act = "insert into "+daily_table+"(imsi,imei,android_id,wifi_mac,date_s,proj_name) values('"+ imsi + "','" + imei + "','" + android_id + "','" + wifi_mac +"','"+time+"','"+proj_name+"')"             
                        cur.execute(sql_insert_act)
                        commit_conn(conn)   
                        close_pgconn(cur,conn) 
            else:
                ############ 2016 passed start
                if i.count(']  INFO -- : [')!=0:
                    time = i[4:14]
                    time_p = time.replace("-","_")
                ############ 2016 passed end      
                continue       

        f.close()
        #os.remove(f_name_tar + "_files/"+file)      
        count_loop = count_loop + 1

    #os.remove(file_name)
    #os.remove(f_name_tar)
    #shutil.rmtree(f_name_tar + "_files/")

    ##print daily_table_list

    return "OK"    

def get_all_table_name():
    sql = "select pg_tables.tablename from pg_tables order by pg_tables.tablename"
    cur,conn = get_pgconn()
    cur.execute(sql)
    results = cur.fetchall()
    close_pgconn(cur,conn)   
    
    result_str = []
    for items in results:
        result_str.append(items[0])

    ##print result_str
    return "OK"

#insert date list into table that holds activated dates
def put_active_datelist_into_db():

    sql_get_tables = "select pg_tables.tablename from pg_tables order by pg_tables.tablename"
    cur,conn= get_pgconn()
    cur.execute(sql_get_tables)
    results_get_tables = cur.fetchall()
    close_pgconn(cur,conn)    

    arr = []
    for item_tables in results_get_tables:
        arr.append(item_tables[0])    

    # arr = ['auth_group', 'auth_group_permissions', 'auth_permission', 'auth_user', 'auth_user_groups', 'auth_user_user_permissions', 'django_admin_log', 'django_content_type', 'django_migrations', 'django_session', 'pg_aggregate', 'pg_am', 'pg_amop', 'pg_amproc', 'pg_attrdef', 'pg_attribute', 'pg_auth_members', 'pg_authid', 'pg_cast', 'pg_class', 'pg_collation', 'pg_constraint', 'pg_conversion', 'pg_database', 'pg_db_role_setting', 'pg_default_acl', 'pg_depend', 'pg_description', 'pg_enum', 'pg_event_trigger', 'pg_extension', 'pg_foreign_data_wrapper', 'pg_foreign_server', 'pg_foreign_table', 'pg_index', 'pg_inherits', 'pg_language', 'pg_largeobject', 'pg_largeobject_metadata', 'pg_namespace', 'pg_opclass', 'pg_operator', 'pg_opfamily', 'pg_pltemplate', 'pg_policy', 'pg_proc', 'pg_range', 'pg_replication_origin', 'pg_rewrite', 'pg_seclabel', 'pg_shdepend', 'pg_shdescription', 'pg_shseclabel', 'pg_statistic', 'pg_tablespace', 'pg_transform', 'pg_trigger', 'pg_ts_config', 'pg_ts_config_map', 'pg_ts_dict', 'pg_ts_parser', 'pg_ts_template', 'pg_type', 'pg_user_mapping', 'sql_features', 'sql_implementation_info', 'sql_languages', 'sql_packages', 'sql_parts', 'sql_sizing', 'sql_sizing_profiles', 'table_activate_date_list', 'table_activate_num', 'table_activate_num_daily_total', 'table_activate_num_fake', 'table_activate_num_ids', 'table_country_list', 'table_daily_active_2016_05_29', 'table_daily_active_2016_05_30', 'table_daily_active_2016_05_31', 'table_daily_active_2016_06_10', 'table_daily_active_2016_06_11', 'table_daily_active_2016_06_12', 'table_daily_active_2016_06_13', 'table_daily_active_2016_06_14', 'table_daily_active_2016_06_15', 'table_daily_active_2016_06_16', 'table_daily_active_2016_06_17', 'table_daily_active_2016_06_18', 'table_daily_active_2016_06_19', 'table_daily_active_2016_06_20', 'table_daily_active_2016_06_21', 'table_daily_active_2016_06_22', 'table_daily_active_2016_06_23', 'table_daily_active_2016_06_24', 'table_daily_active_2016_06_25', 'table_daily_active_2016_06_26', 'table_daily_active_2016_06_27', 'table_daily_active_2016_06_28', 'table_daily_active_2016_06_29', 'table_daily_active_2016_06_30', 'table_daily_active_2016_07_01', 'table_daily_active_2016_07_02', 'table_daily_active_2016_07_03', 'table_daily_active_2016_07_04', 'table_daily_active_2016_07_05', 'table_daily_active_2016_07_06', 'table_daily_active_2016_07_07', 'table_daily_active_2016_07_08', 'table_daily_active_2016_07_09', 'table_daily_active_2016_08_29', 'table_daily_active_2016_08_30', 'table_daily_active_2016_09_03', 'table_daily_active_2016_09_04', 'table_daily_active_2016_09_05', 'table_daily_active_2016_09_06', 'table_daily_active_2016_09_13', 'table_daily_active_2016_09_14', 'table_daily_active_2016_11_22', 'table_daily_active_2016_11_23', 'table_daily_active_2016_11_28', 'table_daily_active_2016_12_05', 'table_daily_active_2016_12_06', 'table_daily_active_2016_12_14', 'table_daily_active_2016_12_18', 'table_daily_active_2016_12_19', 'table_daily_active_2016_12_27', 'table_daily_active_2016_12_28', 'table_daily_active_2016_12_29', 'table_daily_active_2016_12_30', 'table_daily_active_2017_01_07', 'table_daily_active_2017_01_08', 'table_daily_active_2017_01_12', 'table_daily_active_2017_01_13', 'table_daily_active_2017_01_21', 'table_daily_active_2017_01_22', 'table_daily_active_2017_01_23', 'table_daily_active_2017_01_24', 'table_daily_active_2017_01_25', 'table_daily_active_2017_02_13', 'table_daily_active_2017_02_14', 'table_login_time', 'table_menues', 'table_permission', 'table_proj', 'table_role', 'table_user']

    for item in arr:
        if item.count("table_daily_active_")!=0:
            sql_get_existance = "select id from table_activate_date_list where date_s='"+str(item[19:29])+"' and "
            cur,conn = get_pgconn()
            cur.execute(sql_get_existance)
            results_get_existance = cur.fetchall()
            close_pgconn(cur,conn)    
                
            if results_get_existance==[]:
                sql = "insert into table_activate_date_list(date_s) values('"+str(item[19:29])+"')"
                ##print sql
                cur,conn = get_pgconn()
                cur.execute(sql)
                commit_conn(conn)   
                close_pgconn(cur,conn)

    return "OK"   

#insert active daily num for 2016
def put_daily_active_total_2016():
    sql_get_date_list = "select date_s from table_activate_date_list"
    cur,conn = get_pgconn()
    cur.execute(sql_get_date_list)
    results_get_date_list = cur.fetchall()
    close_pgconn(cur,conn)  

    for item in results_get_date_list:
        table_name = "table_daily_active_"+item[0]
        date_replace = item[0].replace("_","-")

        sql_get_existance = "select id from table_activate_num_daily_total where date_s='"+date_replace+"' and sub_channel_name="
        cur,conn = get_pgconn()
        cur.execute(sql_get_existance)
        results_get_existance = cur.fetchall()
        close_pgconn(cur,conn) 

        if results_get_existance==[]:
            sql_get_num = "select count(id) from "+table_name

            cur,conn = get_pgconn()
            cur.execute(sql_get_num)
            results_sql_get_num = cur.fetchall()
            close_pgconn(cur,conn)  

            sql = "insert into table_activate_num_daily_total(date_s,proj_name,total_num,sub_channel_name) values('"+date_replace+"','Tripics',"+str(results_sql_get_num[0][0])+")"
            cur,conn = get_pgconn()
            cur.execute(sql)
            commit_conn(conn)   
            close_pgconn(cur,conn)

    return "OK"

#put total_active II
def put_total_active_II():    

    cur,conn= get_pgconn()
    sql = "select pg_tables.tablename from pg_tables  where pg_tables.tablename like 'table_daily_active_%' order by pg_tables.tablename"
    cur.execute(sql)
    results = cur.fetchall()
    close_pgconn(cur,conn) 

    for item in results:
        date = item[0][19:].replace("_","-")
        sql_get_total_by_subchannel = "select count(a.id),b.sub_channel_name from " + item[0] + "  a join table_activate_num_ids b on a.wifi_mac=b.wifi_mac where b.sub_channel_name!='' group by b.sub_channel_name"
        cur,conn= get_pgconn()
        cur.execute(sql_get_total_by_subchannel)
        results_get_total_by_subchannel = cur.fetchall()
        close_pgconn(cur,conn)
        ##print sql_get_total_by_subchannel

        for item_fff in results_get_total_by_subchannel:
            sql_get_total_by_subchannel_exe = "select id from table_activate_num_daily_total where date_s='"+date+"' and sub_channel_name='" +item_fff[1]+"'"
            cur,conn= get_pgconn()
            cur.execute(sql_get_total_by_subchannel_exe)
            results_get_total_by_subchannel_exe = cur.fetchall()
            close_pgconn(cur,conn) 

            if results_get_total_by_subchannel_exe==[]:
                cur,conn= get_pgconn()
                sql_in = "insert into table_activate_num_daily_total(date_s,proj_name,total_num,sub_channel_name) values('"+date+"','Tripics','"+str(item_fff[0])+"','"+item_fff[1]+"')"
                cur.execute(sql_in)
                commit_conn(conn)   
                close_pgconn(cur,conn)                           

    return "OK"

#insert daily active total count for every project to database ,and delete the table for today
def insert_all_daily_data():
    now_t = datetime.datetime.now()
    now_str_t = now_t.strftime('%Y-%m-%d')
    daily_table = "table_daily_active_"+now_str_t

    cur,conn= get_pgconn()
    sql = "select count(id) cnt,proj_name from "+daily_table+" group by proj_name"
    cur.execute(sql)
    results_total_daily = cur.fetchall()
    close_pgconn(cur,conn) 

    for i in results_total_daily:
        cur,conn= get_pgconn()
        sql_in = "insert into table_activate_num_daily_total(date_s,proj_name,total_num) values('"+now_str_t+"','"+i[1]+"',"+str(i[0])+")"
        cur.execute(sql_in)
        commit_conn(conn)   
        close_pgconn(cur,conn)           
    ###

    ### delete daily table 
    # cur,conn= get_pgconn()
    # sql_tun = "truncate "+daily_table
    # cur.execute(sql_tun)
    # commit_conn(conn)   
    # close_pgconn(cur,conn)

    return "OK"  

#get user type
def get_user_type(user_name):
    sql = "select user_type from table_user where user_name='"+user_name+"'"
    cur,conn = get_pgconn()
    cur.execute(sql)
    results = cur.fetchall()
    close_pgconn(cur,conn)

    ##print results[0][0]
    return results[0][0]

#get project info
def get_project_info(user_name):
    sql_get_projs = "select related_projs from table_user where user_name='"+str(user_name)+"'"
    cur,conn = get_pgconn()
    cur.execute(sql_get_projs)
    results_get_projs = cur.fetchall()
    close_pgconn(cur,conn)
    ##print sql_get_projs

    related_projs = str(results_get_projs[0][0])
    related_projs_ar = related_projs.split(',')

    result_str = ""

    sql_related_projs = "select pid,api_id,proj_name,url,active_sum_manual from table_proj where proj_id in ("+related_projs+")"
    cur,conn = get_pgconn()
    cur.execute(sql_related_projs)
    results_related_projs = cur.fetchall()
    close_pgconn(cur,conn)   

    for item in results_related_projs:
        each_result = {}
        each_result['pid'] = item[0].encode('utf-8')
        each_result['api_id'] = item[1].encode('utf-8')
        each_result['proj_name'] = item[2].encode('utf-8')
        each_result['url'] = item[3].encode('utf-8')
        each_result['active_sum_manual'] = item[4].encode('utf-8')                                

        result_str = result_str + '{pid:"' + each_result['pid'] +'",'+'api_id:' + str(each_result['api_id'])+',proj_name:"'+str(each_result['proj_name'])+',url:"'+str(each_result['url'])+',active_sum_manual:"'+str(each_result['active_sum_manual'])+'"},'
 
    result_str = result_str[0:int(len(result_str))-1]  
    result_str = '{allData:[' + result_str +']}'
    ##print result_str    

#save project info
def save_project_info(former_proj_name,new_proj_name,url,manual_sum,api_id):
    sql = "update table_proj set proj_name='"+str(new_proj_name)+"',url='" +str(url) +"',active_sum_manual='" +str(manual_sum) +"',api_id='" +str(api_id) + "' where proj_name='"+str(former_proj_name)+"'"   
    cur,conn= get_pgconn()
    # sql_in = "insert into table_activate_num_daily_total(date_s,proj_name,total_num) values('"+now_str_t+"','"+i[1]+"',"+str(i[0])+")"
    cur.execute(sql)
    commit_conn(conn)   
    close_pgconn(cur,conn) 

    return "OK"



#get user info
def get_user_info_list(user_name, name_filter):

    result_str = ""

    if name_filter=="":
        sql = "select id ,user_name,last_login_time, user_type , comment, status, related_projs from table_user"
    else:
        sql = "select id ,user_name,last_login_time, user_type , comment, status, related_projs from table_user where user_name like '%"+name_filter+"%'"

    sql_get_user_type = "select user_type from table_user where user_name='"+user_name+"'"

    cur,conn = get_pgconn()
    cur.execute(sql_get_user_type)
    results_get_user_type = cur.fetchall()
    close_pgconn(cur,conn)

    #print results_get_user_type[0][0]
    if results_get_user_type[0][0]!='超级管理员':
        sql = "select id ,user_name,last_login_time, user_type, comment, status, related_projs from table_user where user_name='"+user_name+"'"

    cur,conn = get_pgconn()
    cur.execute(sql)
    results = cur.fetchall()
    close_pgconn(cur,conn)

    if results!=[]:
        for item in results:
            each_result = {}
            each_result['id'] = item[0]
            each_result['user_name'] = item[1]
            ##print each_result['title']
            ##print type(each_result['title'])       
            each_result['last_login_time'] = item[2]  
            if item[3]=='super_admin':
                each_result['user_type'] = "超级管理员"
            elif item[3]=='admin':
                each_result['user_type'] = "管理员"
            elif item[3]=='commercial':
                each_result['user_type'] = "商务"
            elif item[3]=='client':
                each_result['user_type'] = "客户"

            each_result['user_type'] = item[3]  
            each_result['comment'] = item[4]
            each_result['state'] = item[5]
            #each_result['rate'] = item[2] 
            #result_str_each = each_result['title'] + "," + each_result['number']
            #result_item.append(each_result)

            #each_result['lively_num'] = int(results[0][0]*each_result['rate'])      
            if item[3]!='客户' and item[3]!='商务':   
                proj_col = "99999999"   
            else:
                proj_col = item[6]   
            if str(proj_col) != "None":
                #print str(proj_col)
                #proj_col = ""
                sql_get_projs = "select proj_name from table_proj where id in ("+proj_col+")"

                cur,conn = get_pgconn()
                cur.execute(sql_get_projs)
                results_get_projs = cur.fetchall()
                close_pgconn(cur,conn)

                projs_str = ""
                for i in results_get_projs:
                    projs_str = projs_str + i[0] + ","

                projs_str = projs_str[0:int(len(projs_str))-1]
            else:
                projs_str = " "
            
            if item[3] == "超级管理员" or item[3] == "管理员":
                projs_str = "所有"
            # #print "projs "
            # #print results_get_user_type[0][0]
            # #print sql_get_projs
            # #print projs_str
            sql_get_logintime = "select login_time from table_login_time where user_name='"+item[1]+"' order by id desc limit 1"

            cur,conn = get_pgconn()
            cur.execute(sql_get_logintime)
            results_get_logintime = cur.fetchall()
            close_pgconn(cur,conn)          
            #print sql_get_logintime
            if results_get_logintime!=[]:
                each_result['last_login_time'] = results_get_logintime[0][0]
            else:
                each_result['last_login_time'] = " "                

            result_str = result_str+'{"id":"' + str(each_result['id']) +'",'+'"user_name":"' + str(each_result['user_name']) + '","last_login_time":"' + str(each_result['last_login_time'])  + '",'+'"user_type":"' + item[3]+'","comment":"' + item[4]+'","state":"' + item[5]+'","projs":"'+projs_str+'"'+'},'      

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}'        
    ##print result_item
    #return HttpResponse("<p>"+str(result_item)+"</p>")
    #print result_str
    return result_str  

#put logintime into database
def put_logintime(user_name):
    now_t = datetime.datetime.now()
    now_str_t = now_t.strftime('%Y-%m-%d %H:%M:%S')

    #获取本机电脑名
    myname = socket.getfqdn(socket.gethostname(  ))
    #获取本机ip
    myaddr = socket.gethostbyname(myname) 
  
    sql = "insert into table_login_time(user_name,login_time,ip) values('"+user_name+"','"+now_str_t+"','"+myaddr+"')"
    cur,conn= get_pgconn()
    # sql_in = "insert into table_activate_num_daily_total(date_s,proj_name,total_num) values('"+now_str_t+"','"+i[1]+"',"+str(i[0])+")"
    cur.execute(sql)
    commit_conn(conn)   
    close_pgconn(cur,conn) 

    return "OK"
#get logintime list
def get_user_logintime_list(user_name):
    result_str = ""

    sql = "select login_time ,ip from table_login_time where user_name='"+ user_name +"' order by login_time desc"
    # if name_filter=="":
    #     sql = "select id ,user_name,last_login_time, user_type , comment, status, related_projs from table_user"
    # else:
    #     sql = "select id ,user_name,last_login_time, user_type , comment, status, related_projs from table_user where user_name like '%"+name_filter+"%'"

    # sql_get_user_type = "select user_type from table_user where user_name='"+user_name+"'"

    # cur,conn = get_pgconn()
    # cur.execute(sql_get_user_type)
    # results_get_user_type = cur.fetchall()
    # close_pgconn(cur,conn)

    # if results_get_user_type[0][0]!='超级管理员':
    #     sql = "select id ,user_name,last_login_time, user_type, comment, status, related_projs from table_user where user_name='"+user_name+"'"

    cur,conn = get_pgconn()
    cur.execute(sql)
    results = cur.fetchall()
    close_pgconn(cur,conn)

    if results!=[]:
        for item in results:
            each_result = {}
            each_result['id'] = item[0]
            each_result['user_name'] = item[1]
            ##print each_result['title']
            ##print type(each_result['title'])       
            # each_result['last_login_time'] = item[2]  
            # if item[3]=='super_admin':
            #     each_result['user_type'] = "超级管理员"
            # elif item[3]=='admin':
            #     each_result['user_type'] = "管理员"
            # elif item[3]=='commercial':
            #     each_result['user_type'] = "商务"
            # elif item[3]=='client':
            #     each_result['user_type'] = "客户"

            each_result['login_time'] = item[0]  
            each_result['ip'] = item[1]
            # each_result['state'] = item[5]
            #each_result['rate'] = item[2] 
            #result_str_each = each_result['title'] + "," + each_result['number']
            #result_item.append(each_result)

            #each_result['lively_num'] = int(results[0][0]*each_result['rate'])      
            # if item[3]!='客户' and item[3]!='商务':   
            #     proj_col = "99999999"   
            # else:
            #     proj_col = item[6]   
            # sql_get_projs = "select proj_name from table_proj where id in ("+proj_col+")"

            # cur,conn = get_pgconn()
            # cur.execute(sql_get_projs)
            # results_get_projs = cur.fetchall()
            # close_pgconn(cur,conn)

            # projs_str = ""
            # for i in results_get_projs:
            #     projs_str = projs_str + i[0] + ","

            # projs_str = projs_str[0:int(len(projs_str))-1]

            # # #print "projs "
            # # #print results_get_user_type[0][0]
            # # #print sql_get_projs
            # # #print projs_str
            # sql_get_logintime = "select login_time from table_login_time where user_name='"+item[1]+"' order by id desc limit 1"

            # cur,conn = get_pgconn()
            # cur.execute(sql_get_logintime)
            # results_get_logintime = cur.fetchall()
            # close_pgconn(cur,conn)          
            # #print sql_get_logintime
            # if results_get_logintime!=[]:
            #     each_result['last_login_time'] = results_get_logintime[0][0]
            # else:
            #     each_result['last_login_time'] = " "                

            if str(each_result['ip'])=="None":
               each_result['ip'] = " "

            result_str = result_str+'{"login_time":"' + str(each_result['login_time']) +'",'+'"ip":"' + str(each_result['ip']) + '"'+'},'      

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}'        
    ##print result_item
    #return HttpResponse("<p>"+str(result_item)+"</p>")
    #print result_str
    return result_str  

#change passwd
def change_passwd(user_name, passwd):
    sql = "update table_user set passwd='"+passwd+"' where user_name='"+user_name+"'"
    cur,conn= get_pgconn()
    ##sql_in = "insert into table_activate_num_daily_total(date_s,proj_name,total_num) values('"+now_str_t+"','"+i[1]+"',"+str(i[0])+")"
    cur.execute(sql)
    commit_conn(conn)   
    close_pgconn(cur,conn)    

    return "OK"

#change role
def change_role(user_name, role):
    sql = "update table_user set user_type='"+role+"' where user_name='"+user_name+"'"
    cur,conn= get_pgconn()
    ##sql_in = "insert into table_activate_num_daily_total(date_s,proj_name,total_num) values('"+now_str_t+"','"+i[1]+"',"+str(i[0])+")"
    cur.execute(sql)
    commit_conn(conn)   
    close_pgconn(cur,conn)    

    return "OK"

#change comment for user
def change_comment(user_name, comment):
    sql = "update table_user set comment='"+comment+"' where user_name='"+user_name+"'"
    cur,conn= get_pgconn()
    ##sql_in = "insert into table_activate_num_daily_total(date_s,proj_name,total_num) values('"+now_str_t+"','"+i[1]+"',"+str(i[0])+")"
    cur.execute(sql)
    commit_conn(conn)   
    close_pgconn(cur,conn)    

    return "OK"    

#get role info
def get_role_info():
    sql = "select id, role from table_role"
    cur,conn = get_pgconn()
    cur.execute(sql)
    results = cur.fetchall()
    close_pgconn(cur,conn)

    result_str = ""
    if results!=[]:
        result_str = result_str+'{"role":"' + results[0][0] + '"},'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}'    

    #print result_str
    return result_str    

#froze account
def froze_accout(user_name):
    sql = "update table_user set status='冻结' where user_name='"+user_name+"'"    
    cur,conn= get_pgconn()
    ##sql_in = "insert into table_activate_num_daily_total(date_s,proj_name,total_num) values('"+now_str_t+"','"+i[1]+"',"+str(i[0])+")"
    cur.execute(sql)
    commit_conn(conn)   
    close_pgconn(cur,conn)    

    return "OK"    

# def get_projs():
#     sql = "select proj_id,proj_name from table_proj order by proj_id"
#     cur,conn = get_pgconn()
#     cur.execute(sql)
#     results = cur.fetchall()
#     close_pgconn(cur,conn)

#     result_str = ""
#     if results!=[]:
#         for item  in results:
#             # result_str = result_str+'{"proj_id":"' + str(item[0]) + '","proj_name":"'+ str(item[1]) +'"},'
#             result_str = result_str + '"'+str(item[1]) +'",'

#     result_str = result_str[0:int(len(result_str))-1]    
#     result_str = '{"allData":[' + result_str +']}' 

#     #print result_str
#     return result_str   

def get_projs():
    sql = "select distinct sub_channel_name from table_activate_num_ids where  sub_channel_name!=''"
    cur,conn = get_pgconn()
    cur.execute(sql)
    results = cur.fetchall()
    close_pgconn(cur,conn)

    result_str = ""
    if results!=[]:
        for item  in results:
            # result_str = result_str+'{"proj_id":"' + str(item[0]) + '","proj_name":"'+ str(item[1]) +'"},'
            result_str = result_str + '"'+str(item[0]) +'",'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}' 

    #print result_str
    return result_str  

#change related project
def change_related_project(user_name, arr_projs):
    #print "changing!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    #print arr_projs
    sql_get_user_former_info = "select user_type, passwd, last_login_time, status ,comment  from table_user where user_name='"+user_name+"' limit 1"
    cur,conn = get_pgconn()
    #sql_get_type = "select user_type from table_user where user_name='"+user_name+"'"
    cur.execute(sql_get_user_former_info)
    results_get_user_former_info = cur.fetchall()
    close_pgconn(cur,conn)

    sql_delete_former = "delete from table_user where user_name='"+user_name+"'"
    cur,conn= get_pgconn()
    ##sql_in = "insert into table_activate_num_daily_total(date_s,proj_name,total_num) values('"+now_str_t+"','"+i[1]+"',"+str(i[0])+")"
    cur.execute(sql_delete_former)
    commit_conn(conn)   
    close_pgconn(cur,conn)      

    arr_projs_str = ""
    arr_str_sp = arr_projs.split(",")
    for i in arr_str_sp:
        
        
        #print "dfddfdfdfdfdfdfd"
        #print i
        sql_get_proj_id = "select proj_id  from table_proj where proj_name='"+str(i)+"' limit 1"
        cur,conn = get_pgconn()
        #sql_get_type = "select user_type from table_user where user_name='"+user_name+"'"
        cur.execute(sql_get_proj_id)
        results_get_proj_id = cur.fetchall()
        close_pgconn(cur,conn)

        arr_projs_str = arr_projs_str + str(results_get_proj_id[0][0])+","
        results_get_proj_id


    arr_projs_str = arr_projs_str[0:int(len(arr_projs_str))-1]  

    # arr_projs_str

    la_l = results_get_user_former_info[0][2]
    if str(results_get_user_former_info[0][2])=="None":
        la_l = ""
    
    status = results_get_user_former_info[0][3]
    comment = results_get_user_former_info[0][4]
    #print user_name
    #print results_get_user_former_info[0][0]
    #print results_get_user_former_info[0][1]
    #print arr_projs_str
    #print results_get_user_former_info[0][2]
    #print status

    sql_insert_new = "insert into table_user(user_name,user_type,passwd, related_projs, last_login_time,status,comment) values('"+user_name+"','"+results_get_user_former_info[0][0]+"','"+results_get_user_former_info[0][1]+"','"+arr_projs_str+"','"+la_l+"','"+status+"','"+comment+"')"
    cur,conn= get_pgconn()
    cur.execute(sql_insert_new)
    commit_conn(conn)   
    close_pgconn(cur,conn)

    return "OK"          

def get_active_totalnums_by_proj(user_name):

    sql_get_projs = "select related_projs from table_user where user_name='"+str(user_name)+"'"
    cur,conn = get_pgconn()
    cur.execute(sql_get_projs)
    results_get_projs = cur.fetchall()
    close_pgconn(cur,conn)
    #print sql_get_projs

    related_projs = str(results_get_projs[0][0])
    related_projs_ar = related_projs.split(',')

    result_str = ""

    sql_related_projs = "select proj_name from table_proj where proj_id in ("+related_projs+")"
    cur,conn = get_pgconn()
    cur.execute(sql_related_projs)
    results_related_projs = cur.fetchall()
    close_pgconn(cur,conn)   

    for item in  results_related_projs:
        proj_name = str(item[0])
        tot = ""
        sql_get_manuel_sum = "select active_sum_manuel from table_proj where proj_name='"+proj_name+"'"
        cur,conn = get_pgconn()
        cur.execute(sql_get_manuel_sum)
        results_get_manuel_sum = cur.fetchall()
        close_pgconn(cur,conn)

        sql_get_totalnums = "select count(id) from table_activate_num_ids where proj_name='"+proj_name+"'"
        cur,conn = get_pgconn()
        cur.execute(sql_get_totalnums)
        results_get_totalnums = cur.fetchall()
        close_pgconn(cur,conn)     

        if str(results_get_manuel_sum[0][0])!="None":
            tot = results_get_manuel_sum[0][0]
        else:
            tot = str(results_get_totalnums[0][0])
        result_str = result_str+'{"proj_name":"' + proj_name + '","num":"'+ tot + '"},'
    
    result_str = result_str[0:int(len(result_str))-1]           
    result_str = '{"allData":[' + result_str +']}' 
    #print result_str
    return result_str   

#get each project sum
def get_sum_each_proj(proj,date_1,date_2):
    
    user_name = "WX"
    # date_range_array=[]
    # date_range_array.append(date_1)
    # date_range_array.append(date_2)
    # date_range_box = []
    # date_from = ""
    # date_to = ""

    # fil = False

    # if date_1.count(' ')!=0 and date_2.count(' ')!=0 and date_1!="undefined" and date_1!="" and date_2!="undefined" and date_2!="" and date_1!="first" and date_2!="first":
    #     fil = True
    #     for j in date_range_array:
    #         date_array = j.split(' ')
    #         month = date_array[1]
    #         day = date_array[2]
    #         year = date_array[3]
    #         if month == 'Jan':
    #             month = '01'
    #         elif month == 'Feb':
    #             month = '02' 
    #         elif month == 'Mar':
    #             month = '03' 
    #         elif month == 'Apr':
    #             month = '04'             
    #         elif month == 'May':
    #             month = '05'     
    #         elif month == 'Jun':
    #             month = '06' 
    #         elif month == 'Jul':
    #             month = '07' 
    #         elif month == 'Aug':
    #             month = '08'             
    #         elif month == 'Sep':
    #             month = '09'   
    #         elif month == 'Oct':
    #             month = '10' 
    #         elif month == 'Nov':
    #             month = '11'             
    #         elif month == 'Dec':
    #             month = '12' 
    #         formatted_date = year +"-"+ month +"-"+ day
    #         date_range_box.append(formatted_date)

    #     date_from = date_range_box[0]
    #     date_to = date_range_box[1]
    # elif len(date_1)==10 and len(date_2)==10:
    #     date_from = str(date_1)
    #     date_to = str(date_2)        
    # else:
    #     now = datetime.datetime.now()
    #     one_week_ago = now - datetime.timedelta(days=7)
    #     date_str = now.strftime('%Y-%m-%d') 
    #     date_str_one_week_ago = one_week_ago.strftime('%Y-%m-%d')  
    #     date_from = date_str_one_week_ago
    #     date_to = date_str

    # #print date_from
    # #print date_to

    # sql_get_duli_ids = "select c.date_s,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_name='"+proj_name+"' and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "'  group by c.date_s order  by c.date_s desc"

    # cur,conn = get_pgconn()
    # cur.execute(sql_get_duli_ids)
    # results_get_duli_ids = cur.fetchall()
    # close_pgconn(cur,conn)        

    # result_item = []
    # result_str = ""
    
    # if results_get_duli_ids!=[]:
    #     for index,item in enumerate(results_get_duli_ids):             
    #         sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where c.date_s='"+item[0]+"' and b.proj_name='"+proj_name+"' and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"'  group by c.date_s order  by c.date_s desc"
    #         cur,conn = get_pgconn()
    #         cur.execute(sql_get_dailyactive)
    #         results_get_dailyactive = cur.fetchall()
    #         close_pgconn(cur,conn)    

    #         each_result = {}
    #         each_result['proj_name'] = proj_name
    #         if results_get_dailyactive!=[]:
    #             each_result['active'] = results_get_dailyactive[0][1]
    #         else:
    #             each_result['active'] = 0      
    #         each_result['duli'] = item[1]   
    #         result_item.append(each_result)     

    #         sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_name='"+proj_name+"'  group by c.date_s order  by c.date_s desc"
    #         cur,conn = get_pgconn()
    #         cur.execute(sql_get_totalactive)
    #         results_get_totalactive = cur.fetchall()
    #         close_pgconn(cur,conn)  

    #         each_result['total_active'] = results_get_totalactive[0][1]

    #         ######get total duli begin
                
    #         sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_name='"+proj_name+"' and c.date_s<='" +str(item[0])+"'"
                
    #         cur,conn = get_pgconn()
    #         cur.execute(sql_get_totalduli_ids)
    #         results_get_totalduli_ids = cur.fetchall()
    #         close_pgconn(cur,conn)  

    #         if results_get_totalduli_ids!=[]:
    #             each_result['total_duli_s'] = results_get_totalduli_ids[0][0]
    #         else:
    #             each_result['total_duli_s'] = 0

    #         ######get total duli over

    #         result_str = result_str+'{"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' +'"date":"'+str(item[0])+'"},'
    # else:           
    #     sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where   b.proj_name='"+proj_name+"' and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' group by c.date_s order  by c.date_s desc"                                                 
    #     cur,conn = get_pgconn()
    #     cur.execute(sql_get_dailyactive)
    #     results_get_dailyactive = cur.fetchall()
    #     close_pgconn(cur,conn)    

    #     if results_get_dailyactive!=[]:
    #         for item_daily in results_get_dailyactive:
    #             each_result = {}
    #             each_result['active'] = item_daily[1]
    #             each_result['duli'] = 0   
    #             each_result['proj_name'] = proj_name            
    #             each_result['total_duli_s'] = 0
    #             result_item.append(each_result)    

    #             sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_name='"+proj_name+"'  group by c.date_s order by c.date_s desc"                                        
    #             cur,conn = get_pgconn()
    #             cur.execute(sql_get_totalactive)
    #             results_get_totalactive = cur.fetchall()
    #             close_pgconn(cur,conn)  

    #             #print sql_get_totalactive

    #             if results_get_totalactive!=[]:
    #                 each_result['total_active'] = results_get_totalactive[1]
    #             else:
    #                 each_result['total_active'] = 0
                
    #             sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_name='"+proj_name+"' and c.date_s<='" +str(results_get_dailyactive[0][0])+"'"                       
    #             cur,conn = get_pgconn()
    #             cur.execute(sql_get_totalduli_ids)
    #             results_get_totalduli_ids = cur.fetchall()
    #             close_pgconn(cur,conn)  

    #             if results_get_totalduli_ids!=[]:
    #                 each_result['total_duli_s'] = results_get_totalduli_ids[0][0]
    #             else:
    #                 each_result['total_duli_s'] = 0
    #             ######get total duli over      

    #             result_str = result_str+'{"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' +'"date":"'+str(results_get_dailyactive[0][0])+'"},'            

    #     else:
    #         result_str = result_str+'{"daily_active":"' + str(0) + '","duli":"' + str(0) +'",' + '"date":"--"},'            

    # result_str = result_str[0:int(len(result_str))-1]    
    # result_str = '{"allData":[' + result_str +']}'        

    # return result_str  



    date_range_array=[]
    date_range_array.append(date_1)
    date_range_array.append(date_2)
    date_range_box = []
    date_from = ""
    date_to = ""

    fil = False

    date_range_array=[]
    date_range_array.append(date_1)
    date_range_array.append(date_2)
    date_range_box = []
    date_from = ""
    date_to = ""

    fil = False

    if date_1.count(' ')!=0 and date_2.count(' ')!=0 and date_1!="undefined" and date_1!="" and date_2!="undefined" and date_2!="" and date_1!="first" and date_2!="first":
        fil = True
        for j in date_range_array:
            date_array = j.split(' ')
            month = date_array[1]
            day = date_array[2]
            year = date_array[3]
            if month == 'Jan':
                month = '01'
            elif month == 'Feb':
                month = '02' 
            elif month == 'Mar':
                month = '03' 
            elif month == 'Apr':
                month = '04'             
            elif month == 'May':
                month = '05'     
            elif month == 'Jun':
                month = '06' 
            elif month == 'Jul':
                month = '07' 
            elif month == 'Aug':
                month = '08'             
            elif month == 'Sep':
                month = '09'   
            elif month == 'Oct':
                month = '10' 
            elif month == 'Nov':
                month = '11'             
            elif month == 'Dec':
                month = '12' 
            formatted_date = year +"-"+ month +"-"+ day
            date_range_box.append(formatted_date)

        date_from = date_range_box[0]
        date_to = date_range_box[1]
    elif len(date_1)==10 and len(date_2)==10:
        date_from = str(date_1)
        date_to = str(date_2)        
    else:
        now = datetime.datetime.now()
        one_week_ago = now - datetime.timedelta(days=7)
        date_str = now.strftime('%Y-%m-%d') 
        date_str_one_week_ago = one_week_ago.strftime('%Y-%m-%d')  
        date_from = date_str_one_week_ago
        date_to = date_str

    #print date_from
    #print date_to


    cur,conn = get_pgconn()
    sql_get_type = "select user_type ,related_projs from table_user where user_name='"+user_name+"'"
    cur.execute(sql_get_type)
    results_get_type = cur.fetchall()
    close_pgconn(cur,conn) 

    # #print "fdddd"
    # #print str(results_get_type[0][1])

    if str(results_get_type[0][1])!="None":
        proj_id_col = "("+results_get_type[0][1]+")"
    else:
        proj_id_col = "nothing"


    if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
        # group by date 
        # sql_get_duli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "' group by c.proj_name"
        sql_get_duli_ids = "select c.date_s,count(c.id)  from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "' "+"and c.sub_channel_name='"+proj+"' group by c.date_s order  by c.date_s desc"
 
    else:
        # group by date
        # sql_get_duli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "' group by c.proj_name"
        sql_get_duli_ids = "select c.date_s,count(c.id)   from table_activate_num_ids c  where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "'"+"  and c.sub_channel_name='"+proj+"' "+" group by c.date_s order by c.date_s desc"

    cur,conn = get_pgconn()
    #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
    cur.execute(sql_get_duli_ids)
    # #print sql_get_duli_ids
    results_get_duli_ids = cur.fetchall()
    close_pgconn(cur,conn)        

    result_item = []
    result_str = ""
    
    if results_get_duli_ids!=[]:
        for index,item in enumerate(results_get_duli_ids):

            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                # group by date
                # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+ "' group by c.proj_name"                
                sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where c.date_s='"+item[0]+"' and b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s order  by c.date_s desc"
            else:
                # group by date
                # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+"' group by c.proj_name "                
                sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where  c.date_s='"+item[0]+"' and  c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s  order  by c.date_s desc"

            cur,conn = get_pgconn()
            #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
            cur.execute(sql_get_dailyactive)
            ##print sql_get_dailyactive
            results_get_dailyactive = cur.fetchall()
            close_pgconn(cur,conn)    


            each_result = {}
            # group by date
            # each_result['proj_name'] = item[0]
            each_result['proj_name'] = "Tripics"
            if results_get_dailyactive!=[]:
                each_result['active'] = results_get_dailyactive[0][1]
            else:
                each_result['active'] = 0
            ##print each_result['title']
            ##print type(each_result['title'])       
            each_result['duli'] = item[1]   
            #each_result['rate'] = item[2] 
            #result_str_each = each_result['title'] + "," + each_result['number']
            result_item.append(each_result)

            #each_result['lively_num'] = int(results[0][0]*each_result['rate'])      
            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                # group by date
                # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+ "' group by c.proj_name"
                sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.sub_channel_name='"+proj+"'"+"  group by c.date_s order  by c.date_s desc"                
            else:
                # group by date
                # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.proj_name='"+item[0]+"' group by c.proj_name "                
                sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where c.sub_channel_name='"+proj+"'"+"group by c.date_s  order  by c.date_s desc"            

            cur,conn = get_pgconn()
            #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
            cur.execute(sql_get_totalactive)
            ##print sql_get_totalactive
            results_get_totalactive = cur.fetchall()
            close_pgconn(cur,conn)  

            each_result['total_active'] = results_get_totalactive[0][1]

            ######get total duli begin
            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                # group by date
                # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+"' group by c.proj_name"                 
                sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +str(item[0])+"'"+" and c.sub_channel_name='"+sub_channel_name+"'"
            else:
                # group by date
                # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.proj_name='"+item[0]+"' group by c.proj_name"  
                sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +str(item[0])+"'"+" and c.sub_channel_name='"+proj+"'"
                
            cur,conn = get_pgconn()
            cur.execute(sql_get_totalduli_ids)
            results_get_totalduli_ids = cur.fetchall()
            close_pgconn(cur,conn)  

            if results_get_totalduli_ids!=[]:
                total_duli_s = results_get_totalduli_ids[0][0]
            else:
                total_duli_s = 0

            ######get total duli over

            result_str = result_str+'{"proj_name":"' + each_result['proj_name'] +'",'+'"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' + '"total_active":"'+str(each_result['total_active']) + '","total_duli":"'+ str(total_duli_s) +'","date":"'+str(item[0])+'","sub_channel_name":"'+proj+'"},'
    else:
        if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
            sql_get_today_none = "select b.proj_name from table_proj b where b.proj_id in "+proj_id_col
        else:
            sql_get_today_none = "select b.proj_name from table_proj b"

        cur,conn = get_pgconn()
        cur.execute(sql_get_today_none)
        results_get_today_none = cur.fetchall()
        close_pgconn(cur,conn)        

        if results_get_today_none!=[]:
            for item in results_get_today_none:            
                if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                    # group by date
                    # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+ "' group by c.proj_name"
                    sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where  c.date_s='"+item[0]+"' and b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+" group by c.date_s order  by c.date_s desc"                    
                else:
                    # group by date
                    # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+"' group by c.proj_name "    
                    sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where c.date_s='"+item[0]+"' and  c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s  order  by c.date_s desc"                             

                cur,conn = get_pgconn()
                #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
                cur.execute(sql_get_dailyactive)
                ##print sql_get_dailyactive
                results_get_dailyactive = cur.fetchall()
                close_pgconn(cur,conn)    


                each_result = {}
                # group by date
                # each_result['proj_name'] = item[0]
                each_result['proj_name'] = "Tripics"
                if results_get_dailyactive!=[]:
                    each_result['active'] = results_get_dailyactive[0][1]
                else:
                    each_result['active'] = 0
                ##print each_result['title']
                ##print type(each_result['title'])       
                each_result['duli'] = 0   
                #each_result['rate'] = item[2] 
                #result_str_each = each_result['title'] + "," + each_result['number']
                result_item.append(each_result)

                #each_result['lively_num'] = int(results[0][0]*each_result['rate'])      

                if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                    # group by date
                    # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+ "' group by c.proj_name"
                    sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s order by c.date_s desc"                    
                else:
                    # group by date
                    # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.proj_name='"+item[0]+"' group by c.proj_name "       
                    sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where c.sub_channel_name='"+proj+"'"+"  group by c.date_s  order  by c.date_s desc"                          

                cur,conn = get_pgconn()
                #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
                cur.execute(sql_get_totalactive)
                ##print sql_get_totalactive
                results_get_totalactive = cur.fetchall()
                close_pgconn(cur,conn)  

                #print sql_get_totalactive

                if results_get_totalactive!=[]:
                    each_result['total_active'] = results_get_totalactive[0][1]
                else:
                    each_result['total_active'] = 0

                # ######get total duli begin
                # if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                #     # group by date
                #     # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+"' group by c.proj_name"        
                #     sql_get_totalduli_ids = "select c.date_s,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+"  group by c.date_s order by c.date_s desc"                    
                # else:
                #     # group by date
                #     # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.proj_name='"+item[0]+"' group by c.proj_name"       
                #     sql_get_totalduli_ids = "select c.date_s,count(c.id) from table_activate_num_ids c   group by c.date_s order by c.date_s desc"                          
                # cur,conn = get_pgconn()
                # cur.execute(sql_get_totalduli_ids)
                # results_get_totalduli_ids = cur.fetchall()
                # close_pgconn(cur,conn)  

                # if results_get_totalduli_ids!=[]:
                #     each_result['total_duli'] = results_get_totalduli_ids[0][1]
                # else:
                #     each_result['total_duli'] = 0

                # ######get total duli over

                ######get total duli begin
                if results_get_dailyactive!=[]:
                    if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                        # group by date
                        # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+"' group by c.proj_name"                 
                        sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +str(results_get_dailyactive[0][0])+"'"+" and c.sub_channel_name='"+proj+"'"
                    else:
                        # group by date
                        # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.proj_name='"+item[0]+"' group by c.proj_name"  
                        sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +str(results_get_dailyactive[0][0])+"'"+" and c.sub_channel_name='"+proj+"'"
                        
                    cur,conn = get_pgconn()
                    cur.execute(sql_get_totalduli_ids)
                    results_get_totalduli_ids = cur.fetchall()
                    close_pgconn(cur,conn)  

                    if results_get_totalduli_ids!=[]:
                        total_duli_s = results_get_totalduli_ids[0][0]
                    else:
                        total_duli_s = 0

                ######get total duli over                

                # now_total_duli = total_duli_s - item[1]

                if results_get_dailyactive!=[]:
                    result_str = result_str+'{"proj_name":"' + each_result['proj_name'] +'",'+'"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' + '"total_active":"'+str(each_result['total_active']) + '","total_duli":"'+ str(total_duli_s)+'","date":"'+str(results_get_dailyactive[0][0])+'","sub_channel_name":"'+proj+'"},'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}'        
    ##print result_item
    #return HttpResponse("<p>"+str(result_item)+"</p>")
    ##print result_str
    return result_str  

#get role-menu info 
def get_rolemenues_info():
    sql = "select id,role_name,related_menues from table_role"
    cur,conn = get_pgconn()
    cur.execute(sql)
    results = cur.fetchall()
    close_pgconn(cur,conn)

    result_str = ""
    if results!=[]:
        for item in results:          
            sql_menu_names = "select id,menu_name from table_menues where id in (" + str(item[2]) +")"
            cur,conn = get_pgconn()
            cur.execute(sql_menu_names)
            results_menu_names = cur.fetchall()
            close_pgconn(cur,conn)

            menu_names_str = ""
            for itemtt in results_menu_names:
                menu_names_str = menu_names_str + itemtt[1]+","
            menu_names_str = menu_names_str[0:int(len(menu_names_str))-1]

            result_str = result_str+'{"role":"' + item[1] + '","menues":"'+ menu_names_str+ '"},'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}'    

    #print result_str
    return result_str      

#interface to get tongji data to frontpage
def get_sum_to_frontpage(user_name,date_1,date_2,proj):

    date_range_array=[]
    date_range_array.append(date_1)
    date_range_array.append(date_2)
    date_range_box = []
    date_from = ""
    date_to = ""

    fil = False

    if date_1.count(' ')!=0 and date_2.count(' ')!=0 and date_1!="undefined" and date_1!="" and date_2!="undefined" and date_2!="" and date_1!="first" and date_2!="first":
        fil = True
        for j in date_range_array:
            date_array = j.split(' ')
            month = date_array[1]
            day = date_array[2]
            year = date_array[3]
            if month == 'Jan':
                month = '01'
            elif month == 'Feb':
                month = '02' 
            elif month == 'Mar':
                month = '03' 
            elif month == 'Apr':
                month = '04'             
            elif month == 'May':
                month = '05'     
            elif month == 'Jun':
                month = '06' 
            elif month == 'Jul':
                month = '07' 
            elif month == 'Aug':
                month = '08'             
            elif month == 'Sep':
                month = '09'   
            elif month == 'Oct':
                month = '10' 
            elif month == 'Nov':
                month = '11'             
            elif month == 'Dec':
                month = '12' 
            formatted_date = year +"-"+ month +"-"+ day
            date_range_box.append(formatted_date)

        date_from = date_range_box[0]
        date_to = date_range_box[1]
    elif len(date_1)==10 and len(date_2)==10:
        date_from = str(date_1)
        date_to = str(date_2)        
    else:
        now = datetime.datetime.now()
        one_week_ago = now - datetime.timedelta(days=7)
        date_str = now.strftime('%Y-%m-%d') 
        date_str_one_week_ago = one_week_ago.strftime('%Y-%m-%d')  
        date_from = date_str_one_week_ago
        date_to = date_str

    #print date_from
    #print date_to

    cur,conn = get_pgconn()
    sql_get_type = "select user_type ,related_projs from table_user where user_name='"+user_name+"'"
    cur.execute(sql_get_type)
    results_get_type = cur.fetchall()
    close_pgconn(cur,conn) 

    # #print "fdddd"
    # #print str(results_get_type[0][1])

    if str(results_get_type[0][1])!="None":
        proj_id_col = "("+results_get_type[0][1]+")"
    else:
        proj_id_col = "nothing"


    if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
        sql_get_duli_ids = "select c.date_s,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "'  group by c.date_s order  by c.date_s desc"
    else:
        sql_get_duli_ids = "select c.date_s,count(c.id) fro table_activate_num_ids c  where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "' group by c.date_s order by c.date_s desc"

    cur,conn = get_pgconn()
    cur.execute(sql_get_duli_ids)
    results_get_duli_ids = cur.fetchall()
    close_pgconn(cur,conn)        

    result_item = []
    result_str = ""
    
    if results_get_duli_ids!=[]:
        for index,item in enumerate(results_get_duli_ids):

            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':               
                sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where c.date_s='"+item[0]+"' and b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"'  group by c.date_s order  by c.date_s desc"
            else:              
                sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where  c.date_s='"+item[0]+"' and  c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"'  group by c.date_s  order  by c.date_s desc"

            cur,conn = get_pgconn()
            cur.execute(sql_get_dailyactive)
            results_get_dailyactive = cur.fetchall()
            close_pgconn(cur,conn)    


            each_result = {}
            each_result['proj_name'] = "Tripics"
            if results_get_dailyactive!=[]:
                each_result['active'] = results_get_dailyactive[0][1]
            else:
                each_result['active'] = 0      
            each_result['duli'] = item[1]   
            result_item.append(each_result)    

            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+"  group by c.date_s order  by c.date_s desc"                
            else:
                sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c group by c.date_s  order  by c.date_s desc"            

            cur,conn = get_pgconn()
            cur.execute(sql_get_totalactive)
            results_get_totalactive = cur.fetchall()
            close_pgconn(cur,conn)  

            each_result['total_active'] = results_get_totalactive[0][1]

            ######get total duli begin
            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':               
                sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +str(item[0])+"'"
            else:
                sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +str(item[0])+"'"
                
            cur,conn = get_pgconn()
            cur.execute(sql_get_totalduli_ids)
            results_get_totalduli_ids = cur.fetchall()
            close_pgconn(cur,conn)  

            if results_get_totalduli_ids!=[]:
                total_duli_s = results_get_totalduli_ids[0][0]
            else:
                total_duli_s = 0
            ######get total duli over

            result_str = result_str+'{"proj_name":"' + each_result['proj_name'] +'",'+'"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' + '"total_active":"'+str(each_result['total_active']) + '","total_duli":"'+ str(total_duli_s) +'","date":"'+str(item[0])+'","sub_channel_name":"'+"Tripics"+'"},'
    else:
        if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
            sql_get_today_none = "select b.proj_name from table_proj b where b.proj_id in "+proj_id_col
        else:
            sql_get_today_none = "select b.proj_name from table_proj b"

        cur,conn = get_pgconn()
        cur.execute(sql_get_today_none)
        results_get_today_none = cur.fetchall()
        close_pgconn(cur,conn)        

        if results_get_today_none!=[]:
            for item in results_get_today_none:            
                if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                    sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where  c.date_s='"+item[0]+"' and b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' group by c.date_s order  by c.date_s desc"                    
                else:   
                    sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where c.date_s='"+item[0]+"' and  c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"'  group by c.date_s  order  by c.date_s desc"                             
                cur,conn = get_pgconn()
                cur.execute(sql_get_dailyactive)
                results_get_dailyactive = cur.fetchall()
                close_pgconn(cur,conn)    


                each_result = {}
                each_result['proj_name'] = "Tripics"
                if results_get_dailyactive!=[]:
                    each_result['active'] = results_get_dailyactive[0][1]
                else:
                    each_result['active'] = 0
       
                each_result['duli'] = 0   
                result_item.append(each_result)      

                if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                    sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+"  group by c.date_s order by c.date_s desc"                    
                else:
                    sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c  group by c.date_s  order  by c.date_s desc"                          

                cur,conn = get_pgconn()
                cur.execute(sql_get_totalactive)
                results_get_totalactive = cur.fetchall()
                close_pgconn(cur,conn)  

                #print sql_get_totalactive

                if results_get_totalactive!=[]:
                    each_result['total_active'] = results_get_totalactive[0][1]
                else:
                    each_result['total_active'] = 0

                ######get total duli begin
                if results_get_dailyactive!=[]:
                    if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':                
                        sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +str(results_get_dailyactive[0][0])+"'"
                    else:
                        sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +str(results_get_dailyactive[0][0])+"'"
                        
                    cur,conn = get_pgconn()
                    cur.execute(sql_get_totalduli_ids)
                    results_get_totalduli_ids = cur.fetchall()
                    close_pgconn(cur,conn)  

                    if results_get_totalduli_ids!=[]:
                        total_duli_s = results_get_totalduli_ids[0][0]
                    else:
                        total_duli_s = 0
                ######get total duli over                

                if results_get_dailyactive!=[]:
                    result_str = result_str+'{"proj_name":"' + each_result['proj_name'] +'",'+'"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' + '"total_active":"'+str(each_result['total_active']) + '","total_duli":"'+ str(total_duli_s)+'","date":"'+str(results_get_dailyactive[0][0])+'","sub_channel_name":"'+"Tripics"+'"},'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}'        

    return result_str  

#interface to get tongji data to frontpage
def get_sum_to_frontpage_proj(user_name,date_1,date_2,proj):

    date_range_array=[]
    date_range_array.append(date_1)
    date_range_array.append(date_2)
    date_range_box = []
    date_from = ""
    date_to = ""

    fil = False
    
    if date_1.count(' ')!=0 and date_2.count(' ')!=0 and date_1!="undefined" and date_1!="" and date_2!="undefined" and date_2!="" and date_1!="first" and date_2!="first":
        fil = True
        for j in date_range_array:
            date_array = j.split(' ')
            month = date_array[1]
            day = date_array[2]
            year = date_array[3]
            if month == 'Jan':
                month = '01'
            elif month == 'Feb':
                month = '02' 
            elif month == 'Mar':
                month = '03' 
            elif month == 'Apr':
                month = '04'             
            elif month == 'May':
                month = '05'     
            elif month == 'Jun':
                month = '06' 
            elif month == 'Jul':
                month = '07' 
            elif month == 'Aug':
                month = '08'             
            elif month == 'Sep':
                month = '09'   
            elif month == 'Oct':
                month = '10' 
            elif month == 'Nov':
                month = '11'             
            elif month == 'Dec':
                month = '12' 
            formatted_date = year +"-"+ month +"-"+ day
            date_range_box.append(formatted_date)

        date_from = date_range_box[0]
        date_to = date_range_box[1]
    elif len(date_1)==10 and len(date_2)==10:
        date_from = str(date_1)
        date_to = str(date_2)
    else:
        now = datetime.datetime.now()
        one_week_ago = now - datetime.timedelta(days=7)
        date_str = now.strftime('%Y-%m-%d') 
        date_str_one_week_ago = one_week_ago.strftime('%Y-%m-%d')  
        date_from = date_str_one_week_ago
        date_to = date_str

    #print date_from
    #print date_to

    cur,conn = get_pgconn()
    sql_get_type = "select user_type ,related_projs from table_user where user_name='"+user_name+"'"
    cur.execute(sql_get_type)
    results_get_type = cur.fetchall()
    close_pgconn(cur,conn) 

    if str(results_get_type[0][1])!="None":
        proj_id_col = "("+results_get_type[0][1]+")"
    else:
        proj_id_col = "nothing"

    if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
        sql_get_duli_ids = "select c.date_s,count(c.id)  from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "' "+"and c.sub_channel_name='"+proj+"' group by c.date_s order  by c.date_s desc"
 
    else:
        sql_get_duli_ids = "select c.date_s,count(c.id)   from table_activate_num_ids c  where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "'"+"  and c.sub_channel_name='"+proj+"' "+" group by c.date_s order by c.date_s desc"

    cur,conn = get_pgconn()
    cur.execute(sql_get_duli_ids)
    results_get_duli_ids = cur.fetchall()
    close_pgconn(cur,conn)        

    result_item = []
    result_str = ""
    
    if results_get_duli_ids!=[]:
        for index,item in enumerate(results_get_duli_ids):

            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':           
                sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where c.date_s='"+item[0]+"' and b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s order  by c.date_s desc"
            else:               
                sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where  c.date_s='"+item[0]+"' and  c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s  order  by c.date_s desc"

            cur,conn = get_pgconn()
            cur.execute(sql_get_dailyactive)
            results_get_dailyactive = cur.fetchall()
            close_pgconn(cur,conn)    


            each_result = {}
            each_result['proj_name'] = "Tripics"
            if results_get_dailyactive!=[]:
                each_result['active'] = results_get_dailyactive[0][1]
            else:
                each_result['active'] = 0    
            each_result['duli'] = item[1]   
            result_item.append(each_result)
      
            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.sub_channel_name='"+proj+"'"+"  group by c.date_s order  by c.date_s desc"                
            else:               
                sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where c.sub_channel_name='"+proj+"'"+"group by c.date_s  order  by c.date_s desc"            

            cur,conn = get_pgconn()
            cur.execute(sql_get_totalactive)
            results_get_totalactive = cur.fetchall()
            close_pgconn(cur,conn)  

            each_result['total_active'] = results_get_totalactive[0][1]

            ######get total duli begin
            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':             
                sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +str(item[0])+"'"+" and c.sub_channel_name='"+sub_channel_name+"'"
            else: 
                sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +str(item[0])+"'"+" and c.sub_channel_name='"+proj+"'"
                
            cur,conn = get_pgconn()
            cur.execute(sql_get_totalduli_ids)
            results_get_totalduli_ids = cur.fetchall()
            close_pgconn(cur,conn)  

            if results_get_totalduli_ids!=[]:
                total_duli_s = results_get_totalduli_ids[0][0]
            else:
                total_duli_s = 0
            ######get total duli over

            result_str = result_str+'{"proj_name":"' + each_result['proj_name'] +'",'+'"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' + '"total_active":"'+str(each_result['total_active']) + '","total_duli":"'+ str(total_duli_s) +'","date":"'+str(item[0])+'","sub_channel_name":"'+proj+'"},'
    else:
        if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
            sql_get_today_none = "select b.proj_name from table_proj b where b.proj_id in "+proj_id_col
        else:
            sql_get_today_none = "select b.proj_name from table_proj b"

        cur,conn = get_pgconn()
        cur.execute(sql_get_today_none)
        results_get_today_none = cur.fetchall()
        close_pgconn(cur,conn)        

        if results_get_today_none!=[]:
            for item in results_get_today_none:            
                if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                    sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where  c.date_s='"+item[0]+"' and b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+" group by c.date_s order  by c.date_s desc"                    
                else:  
                    sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where c.date_s='"+item[0]+"' and  c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s  order  by c.date_s desc"                             

                cur,conn = get_pgconn()
                cur.execute(sql_get_dailyactive)
                results_get_dailyactive = cur.fetchall()
                close_pgconn(cur,conn)    

                each_result = {}

                each_result['proj_name'] = "Tripics"
                if results_get_dailyactive!=[]:
                    each_result['active'] = results_get_dailyactive[0][1]
                else:
                    each_result['active'] = 0      
                each_result['duli'] = 0   

                result_item.append(each_result)     

                if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                    sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s order by c.date_s desc"                    
                else:    
                    sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where c.sub_channel_name='"+proj+"'"+"  group by c.date_s  order  by c.date_s desc"                          

                cur,conn = get_pgconn()
                cur.execute(sql_get_totalactive)
                results_get_totalactive = cur.fetchall()
                close_pgconn(cur,conn)  

                #print sql_get_totalactive

                if results_get_totalactive!=[]:
                    each_result['total_active'] = results_get_totalactive[0][1]
                else:
                    each_result['total_active'] = 0

                ######get total duli begin
                if results_get_dailyactive!=[]:
                    if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':                
                        sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +str(results_get_dailyactive[0][0])+"'"+" and c.sub_channel_name='"+proj+"'"
                    else:
                        sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +str(results_get_dailyactive[0][0])+"'"+" and c.sub_channel_name='"+proj+"'"
                        
                    cur,conn = get_pgconn()
                    cur.execute(sql_get_totalduli_ids)
                    results_get_totalduli_ids = cur.fetchall()
                    close_pgconn(cur,conn)  

                    if results_get_totalduli_ids!=[]:
                        total_duli_s = results_get_totalduli_ids[0][0]
                    else:
                        total_duli_s = 0
                ######get total duli over                

                if results_get_dailyactive!=[]:
                    result_str = result_str+'{"proj_name":"' + each_result['proj_name'] +'",'+'"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' + '"total_active":"'+str(each_result['total_active']) + '","total_duli":"'+ str(total_duli_s)+'","date":"'+str(results_get_dailyactive[0][0])+'","sub_channel_name":"'+proj+'"},'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}'        
    return result_str  

#interface to get tongji data to frontpage
def get_tongji_to_frontpage(user_name,date_1,date_2,proj):

    # #print date_1
    # #print date_2
    ##print date_range

    date_range_array=[]
    date_range_array.append(date_1)
    date_range_array.append(date_2)
    date_range_box = []
    date_from = ""
    date_to = ""

    fil = False

    if date_1!="undefined" and date_1!="" and date_2!="undefined" and date_2!="" and date_1!="first" and date_2!="first":
        fil = True
        for j in date_range_array:
            date_array = j.split(' ')
            month = date_array[1]
            day = date_array[2]
            year = date_array[3]
            if month == 'Jan':
                month = '01'
            elif month == 'Feb':
                month = '02' 
            elif month == 'Mar':
                month = '03' 
            elif month == 'Apr':
                month = '04'             
            elif month == 'May':
                month = '05'     
            elif month == 'Jun':
                month = '06' 
            elif month == 'Jul':
                month = '07' 
            elif month == 'Aug':
                month = '08'             
            elif month == 'Sep':
                month = '09'   
            elif month == 'Oct':
                month = '10' 
            elif month == 'Nov':
                month = '11'             
            elif month == 'Dec':
                month = '12' 
            formatted_date = year +"-"+ month +"-"+ day
            date_range_box.append(formatted_date)

        date_from = date_range_box[0]
        date_to = date_range_box[1]
    else:
        now = datetime.datetime.now()
        one_week_ago = now - datetime.timedelta(days=7)
        date_str = now.strftime('%Y-%m-%d') 
        date_str_one_week_ago = one_week_ago.strftime('%Y-%m-%d')  
        date_from = date_str_one_week_ago
        date_to = date_str

    # #print date_from
    # #print date_to

    cur,conn = get_pgconn()
    sql_get_type = "select user_type ,related_projs from table_user where user_name='"+user_name+"'"
    cur.execute(sql_get_type)
    results_get_type = cur.fetchall()
    close_pgconn(cur,conn) 

    # #print "fdddd"
    # #print str(results_get_type[0][1])

    if str(results_get_type[0][1])!="None":
        proj_id_col = "("+results_get_type[0][1]+")"
    else:
        proj_id_col = "nothing"

    # ######get total duli begin
    # if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
    #     # group by date
    #     # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+"' group by c.proj_name"                 
    #     sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +date_to+"'"
    # else:
    #     # group by date
    #     # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.proj_name='"+item[0]+"' group by c.proj_name"  
    #     sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +date_to+"'"
        
    # cur,conn = get_pgconn()
    # cur.execute(sql_get_totalduli_ids)
    # results_get_totalduli_ids = cur.fetchall()
    # close_pgconn(cur,conn)  

    # if results_get_totalduli_ids!=[]:
    #     total_duli_s = results_get_totalduli_ids[0][0]
    # else:
    #     total_duli_s = 0

    # ######get total duli over

    if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
        # group by date 
        # sql_get_duli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "' group by c.proj_name"
        sql_get_duli_ids = "select c.date_s,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "'  group by c.date_s order  by c.date_s desc"
 
    else:
        # group by date
        # sql_get_duli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "' group by c.proj_name"
        sql_get_duli_ids = "select c.date_s,count(c.id) from table_activate_num_ids c  where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "' group by c.date_s order by c.date_s desc"

    cur,conn = get_pgconn()
    #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
    cur.execute(sql_get_duli_ids)
    # #print sql_get_duli_ids
    results_get_duli_ids = cur.fetchall()
    close_pgconn(cur,conn)        

    result_item = []
    result_str = ""
    
    if results_get_duli_ids!=[]:
        for index,item in enumerate(results_get_duli_ids):

            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                # group by date
                # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+ "' group by c.proj_name"                
                sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where c.date_s='"+item[0]+"' and b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"'  group by c.date_s order  by c.date_s desc"
            else:
                # group by date
                # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+"' group by c.proj_name "                
                sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where  c.date_s='"+item[0]+"' and  c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"'  group by c.date_s  order  by c.date_s desc"

            cur,conn = get_pgconn()
            #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
            cur.execute(sql_get_dailyactive)
            ##print sql_get_dailyactive
            results_get_dailyactive = cur.fetchall()
            close_pgconn(cur,conn)    


            each_result = {}
            # group by date
            # each_result['proj_name'] = item[0]
            each_result['proj_name'] = "Tripics"
            if results_get_dailyactive!=[]:
                each_result['active'] = results_get_dailyactive[0][1]
            else:
                each_result['active'] = 0
            ##print each_result['title']
            ##print type(each_result['title'])       
            each_result['duli'] = item[1]   
            #each_result['rate'] = item[2] 
            #result_str_each = each_result['title'] + "," + each_result['number']
            result_item.append(each_result)

            #each_result['lively_num'] = int(results[0][0]*each_result['rate'])      
            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                # group by date
                # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+ "' group by c.proj_name"
                sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+"  group by c.date_s order  by c.date_s desc"                
            else:
                # group by date
                # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.proj_name='"+item[0]+"' group by c.proj_name "                
                sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c group by c.date_s  order  by c.date_s desc"            

            cur,conn = get_pgconn()
            #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
            cur.execute(sql_get_totalactive)
            ##print sql_get_totalactive
            results_get_totalactive = cur.fetchall()
            close_pgconn(cur,conn)  

            each_result['total_active'] = results_get_totalactive[0][1]

            ######get total duli begin
            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                # group by date
                # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+"' group by c.proj_name"                 
                sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +str(item[0])+"'"
            else:
                # group by date
                # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.proj_name='"+item[0]+"' group by c.proj_name"  
                sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +str(item[0])+"'"
                
            cur,conn = get_pgconn()
            cur.execute(sql_get_totalduli_ids)
            results_get_totalduli_ids = cur.fetchall()
            close_pgconn(cur,conn)  

            if results_get_totalduli_ids!=[]:
                total_duli_s = results_get_totalduli_ids[0][0]
            else:
                total_duli_s = 0

            ######get total duli over

            result_str = result_str+'{"proj_name":"' + each_result['proj_name'] +'",'+'"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' + '"total_active":"'+str(each_result['total_active']) + '","total_duli":"'+ str(total_duli_s) +'","date":"'+str(item[0])+'","sub_channel_name":"'+"Tripics"+'"},'
    else:
        if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
            sql_get_today_none = "select b.proj_name from table_proj b where b.proj_id in "+proj_id_col
        else:
            sql_get_today_none = "select b.proj_name from table_proj b"

        cur,conn = get_pgconn()
        cur.execute(sql_get_today_none)
        results_get_today_none = cur.fetchall()
        close_pgconn(cur,conn)        

        if results_get_today_none!=[]:
            for item in results_get_today_none:            
                if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                    # group by date
                    # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+ "' group by c.proj_name"
                    sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where  c.date_s='"+item[0]+"' and b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' group by c.date_s order  by c.date_s desc"                    
                else:
                    # group by date
                    # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+"' group by c.proj_name "    
                    sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where c.date_s='"+item[0]+"' and  c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"'  group by c.date_s  order  by c.date_s desc"                             

                cur,conn = get_pgconn()
                #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
                cur.execute(sql_get_dailyactive)
                ##print sql_get_dailyactive
                results_get_dailyactive = cur.fetchall()
                close_pgconn(cur,conn)    


                each_result = {}
                # group by date
                # each_result['proj_name'] = item[0]
                each_result['proj_name'] = "Tripics"
                if results_get_dailyactive!=[]:
                    each_result['active'] = results_get_dailyactive[0][1]
                else:
                    each_result['active'] = 0
                ##print each_result['title']
                ##print type(each_result['title'])       
                each_result['duli'] = 0   
                #each_result['rate'] = item[2] 
                #result_str_each = each_result['title'] + "," + each_result['number']
                result_item.append(each_result)

                #each_result['lively_num'] = int(results[0][0]*each_result['rate'])      

                if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                    # group by date
                    # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+ "' group by c.proj_name"
                    sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+"  group by c.date_s order by c.date_s desc"                    
                else:
                    # group by date
                    # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.proj_name='"+item[0]+"' group by c.proj_name "       
                    sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c  group by c.date_s  order  by c.date_s desc"                          

                cur,conn = get_pgconn()
                #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
                cur.execute(sql_get_totalactive)
                ##print sql_get_totalactive
                results_get_totalactive = cur.fetchall()
                close_pgconn(cur,conn)  

                #print sql_get_totalactive

                if results_get_totalactive!=[]:
                    each_result['total_active'] = results_get_totalactive[0][1]
                else:
                    each_result['total_active'] = 0

                # ######get total duli begin
                # if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                #     # group by date
                #     # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+"' group by c.proj_name"        
                #     sql_get_totalduli_ids = "select c.date_s,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+"  group by c.date_s order by c.date_s desc"                    
                # else:
                #     # group by date
                #     # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.proj_name='"+item[0]+"' group by c.proj_name"       
                #     sql_get_totalduli_ids = "select c.date_s,count(c.id) from table_activate_num_ids c   group by c.date_s order by c.date_s desc"                          
                # cur,conn = get_pgconn()
                # cur.execute(sql_get_totalduli_ids)
                # results_get_totalduli_ids = cur.fetchall()
                # close_pgconn(cur,conn)  

                # if results_get_totalduli_ids!=[]:
                #     each_result['total_duli'] = results_get_totalduli_ids[0][1]
                # else:
                #     each_result['total_duli'] = 0

                # ######get total duli over

                ######get total duli begin
                if results_get_dailyactive!=[]:
                    if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                        # group by date
                        # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+"' group by c.proj_name"                 
                        sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +str(results_get_dailyactive[0][0])+"'"
                    else:
                        # group by date
                        # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.proj_name='"+item[0]+"' group by c.proj_name"  
                        sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +str(results_get_dailyactive[0][0])+"'"
                        
                    cur,conn = get_pgconn()
                    cur.execute(sql_get_totalduli_ids)
                    results_get_totalduli_ids = cur.fetchall()
                    close_pgconn(cur,conn)  

                    if results_get_totalduli_ids!=[]:
                        total_duli_s = results_get_totalduli_ids[0][0]
                    else:
                        total_duli_s = 0

                ######get total duli over                

                # now_total_duli = total_duli_s - item[1]

                if results_get_dailyactive!=[]:
                    result_str = result_str+'{"proj_name":"' + each_result['proj_name'] +'",'+'"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' + '"total_active":"'+str(each_result['total_active']) + '","total_duli":"'+ str(total_duli_s)+'","date":"'+str(results_get_dailyactive[0][0])+'","sub_channel_name":"'+"Tripics"+'"},'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}'        
    ##print result_item
    #return HttpResponse("<p>"+str(result_item)+"</p>")
    ##print result_str
    return result_str  

#interface to get tongji data to frontpage
def get_tongji_to_frontpage_proj(user_name,date_1,date_2,proj):

    # #print date_1
    # #print date_2
    ##print date_range
    #print "555555555555555555555"
    # cur,conn = get_pgconn()
    # sql_get_pid = "select proj_id from table_proj where proj_name='"+proj+"'"
    # cur.execute(sql_get_pid)
    # results_get_pid = cur.fetchall()
    # close_pgconn(cur,conn) 

    # proj_id_p = str(results_get_pid[0][0])

    date_range_array=[]
    date_range_array.append(date_1)
    date_range_array.append(date_2)
    date_range_box = []
    date_from = ""
    date_to = ""

    fil = False

    if date_1!="undefined" and date_1!="" and date_2!="undefined" and date_2!="" and date_1!="first" and date_2!="first":
        fil = True
        for j in date_range_array:
            date_array = j.split(' ')
            month = date_array[1]
            day = date_array[2]
            year = date_array[3]
            if month == 'Jan':
                month = '01'
            elif month == 'Feb':
                month = '02' 
            elif month == 'Mar':
                month = '03' 
            elif month == 'Apr':
                month = '04'             
            elif month == 'May':
                month = '05'     
            elif month == 'Jun':
                month = '06' 
            elif month == 'Jul':
                month = '07' 
            elif month == 'Aug':
                month = '08'             
            elif month == 'Sep':
                month = '09'   
            elif month == 'Oct':
                month = '10' 
            elif month == 'Nov':
                month = '11'             
            elif month == 'Dec':
                month = '12' 
            formatted_date = year +"-"+ month +"-"+ day
            date_range_box.append(formatted_date)

        date_from = date_range_box[0]
        date_to = date_range_box[1]
    else:
        now = datetime.datetime.now()
        one_week_ago = now - datetime.timedelta(days=7)
        date_str = now.strftime('%Y-%m-%d') 
        date_str_one_week_ago = one_week_ago.strftime('%Y-%m-%d')  
        date_from = date_str_one_week_ago
        date_to = date_str

    # #print date_from
    # #print date_to

    cur,conn = get_pgconn()
    sql_get_type = "select user_type ,related_projs from table_user where user_name='"+user_name+"'"
    cur.execute(sql_get_type)
    results_get_type = cur.fetchall()
    close_pgconn(cur,conn) 

    # #print "fdddd"
    # #print str(results_get_type[0][1])

    if str(results_get_type[0][1])!="None":
        proj_id_col = "("+results_get_type[0][1]+")"
    else:
        proj_id_col = "nothing"

    # ######get total duli begin
    # if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
    #     # group by date
    #     # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+"' group by c.proj_name"                 
    #     sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +date_to+"'"
    # else:
    #     # group by date
    #     # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.proj_name='"+item[0]+"' group by c.proj_name"  
    #     sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +date_to+"'"
        
    # cur,conn = get_pgconn()
    # cur.execute(sql_get_totalduli_ids)
    # results_get_totalduli_ids = cur.fetchall()
    # close_pgconn(cur,conn)  

    # if results_get_totalduli_ids!=[]:
    #     total_duli_s = results_get_totalduli_ids[0][0]
    # else:
    #     total_duli_s = 0

    # ######get total duli over

    if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
        # group by date 
        # sql_get_duli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "' group by c.proj_name"
        sql_get_duli_ids = "select c.date_s,count(c.id)  from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "' "+"and c.sub_channel_name='"+proj+"' group by c.date_s order  by c.date_s desc"
 
    else:
        # group by date
        # sql_get_duli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "' group by c.proj_name"
        sql_get_duli_ids = "select c.date_s,count(c.id)   from table_activate_num_ids c  where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+ "'"+"  and c.sub_channel_name='"+proj+"' "+" group by c.date_s order by c.date_s desc"

    cur,conn = get_pgconn()
    #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
    cur.execute(sql_get_duli_ids)
    # #print sql_get_duli_ids
    results_get_duli_ids = cur.fetchall()
    close_pgconn(cur,conn)        

    result_item = []
    result_str = ""
    
    if results_get_duli_ids!=[]:
        for index,item in enumerate(results_get_duli_ids):

            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                # group by date
                # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+ "' group by c.proj_name"                
                sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where c.date_s='"+item[0]+"' and b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s order  by c.date_s desc"
            else:
                # group by date
                # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+"' group by c.proj_name "                
                sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where  c.date_s='"+item[0]+"' and  c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s  order  by c.date_s desc"

            cur,conn = get_pgconn()
            #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
            cur.execute(sql_get_dailyactive)
            ##print sql_get_dailyactive
            results_get_dailyactive = cur.fetchall()
            close_pgconn(cur,conn)    


            each_result = {}
            # group by date
            # each_result['proj_name'] = item[0]
            each_result['proj_name'] = "Tripics"
            if results_get_dailyactive!=[]:
                each_result['active'] = results_get_dailyactive[0][1]
            else:
                each_result['active'] = 0
            ##print each_result['title']
            ##print type(each_result['title'])       
            each_result['duli'] = item[1]   
            #each_result['rate'] = item[2] 
            #result_str_each = each_result['title'] + "," + each_result['number']
            result_item.append(each_result)

            #each_result['lively_num'] = int(results[0][0]*each_result['rate'])      
            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                # group by date
                # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+ "' group by c.proj_name"
                sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.sub_channel_name='"+proj+"'"+"  group by c.date_s order  by c.date_s desc"                
            else:
                # group by date
                # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.proj_name='"+item[0]+"' group by c.proj_name "                
                sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where c.sub_channel_name='"+proj+"'"+"group by c.date_s  order  by c.date_s desc"            

            cur,conn = get_pgconn()
            #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
            cur.execute(sql_get_totalactive)
            ##print sql_get_totalactive
            results_get_totalactive = cur.fetchall()
            close_pgconn(cur,conn)  

            each_result['total_active'] = results_get_totalactive[0][1]

            ######get total duli begin
            if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                # group by date
                # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+"' group by c.proj_name"                 
                sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +str(item[0])+"'"+" and c.sub_channel_name='"+sub_channel_name+"'"
            else:
                # group by date
                # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.proj_name='"+item[0]+"' group by c.proj_name"  
                sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +str(item[0])+"'"+" and c.sub_channel_name='"+proj+"'"
                
            cur,conn = get_pgconn()
            cur.execute(sql_get_totalduli_ids)
            results_get_totalduli_ids = cur.fetchall()
            close_pgconn(cur,conn)  

            if results_get_totalduli_ids!=[]:
                total_duli_s = results_get_totalduli_ids[0][0]
            else:
                total_duli_s = 0

            ######get total duli over

            result_str = result_str+'{"proj_name":"' + each_result['proj_name'] +'",'+'"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' + '"total_active":"'+str(each_result['total_active']) + '","total_duli":"'+ str(total_duli_s) +'","date":"'+str(item[0])+'","sub_channel_name":"'+proj+'"},'
    else:
        if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
            sql_get_today_none = "select b.proj_name from table_proj b where b.proj_id in "+proj_id_col
        else:
            sql_get_today_none = "select b.proj_name from table_proj b"

        cur,conn = get_pgconn()
        cur.execute(sql_get_today_none)
        results_get_today_none = cur.fetchall()
        close_pgconn(cur,conn)        

        if results_get_today_none!=[]:
            for item in results_get_today_none:            
                if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                    # group by date
                    # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+ "' group by c.proj_name"
                    sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where  c.date_s='"+item[0]+"' and b.proj_id in "+proj_id_col+" and c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+" group by c.date_s order  by c.date_s desc"                    
                else:
                    # group by date
                    # sql_get_dailyactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.proj_name='"+item[0]+"' group by c.proj_name "    
                    sql_get_dailyactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where c.date_s='"+item[0]+"' and  c.date_s>='"+date_from+"' and c.date_s<='" +date_to+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s  order  by c.date_s desc"                             

                cur,conn = get_pgconn()
                #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
                cur.execute(sql_get_dailyactive)
                ##print sql_get_dailyactive
                results_get_dailyactive = cur.fetchall()
                close_pgconn(cur,conn)    


                each_result = {}
                # group by date
                # each_result['proj_name'] = item[0]
                each_result['proj_name'] = "Tripics"
                if results_get_dailyactive!=[]:
                    each_result['active'] = results_get_dailyactive[0][1]
                else:
                    each_result['active'] = 0
                ##print each_result['title']
                ##print type(each_result['title'])       
                each_result['duli'] = 0   
                #each_result['rate'] = item[2] 
                #result_str_each = each_result['title'] + "," + each_result['number']
                result_item.append(each_result)

                #each_result['lively_num'] = int(results[0][0]*each_result['rate'])      

                if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                    # group by date
                    # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+ "' group by c.proj_name"
                    sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_proj b  join table_activate_num_daily_total c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+"' and c.sub_channel_name='"+proj+"'"+"  group by c.date_s order by c.date_s desc"                    
                else:
                    # group by date
                    # sql_get_totalactive = "select c.proj_name,sum(c.total_num) from table_activate_num_daily_total c where c.proj_name='"+item[0]+"' group by c.proj_name "       
                    sql_get_totalactive = "select c.date_s,sum(c.total_num) from table_activate_num_daily_total c where c.sub_channel_name='"+proj+"'"+"  group by c.date_s  order  by c.date_s desc"                          

                cur,conn = get_pgconn()
                #sql_get_act = "select proj_name,date_s,act_num from table_activate_num where proj_id=" + str(proj_id)+" and date_s>='"+date_from+"' and date_s<='" +date_to+ "' order by date_s desc"
                cur.execute(sql_get_totalactive)
                ##print sql_get_totalactive
                results_get_totalactive = cur.fetchall()
                close_pgconn(cur,conn)  

                #print sql_get_totalactive

                if results_get_totalactive!=[]:
                    each_result['total_active'] = results_get_totalactive[0][1]
                else:
                    each_result['total_active'] = 0

                # ######get total duli begin
                # if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                #     # group by date
                #     # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+"' group by c.proj_name"        
                #     sql_get_totalduli_ids = "select c.date_s,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+"  group by c.date_s order by c.date_s desc"                    
                # else:
                #     # group by date
                #     # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.proj_name='"+item[0]+"' group by c.proj_name"       
                #     sql_get_totalduli_ids = "select c.date_s,count(c.id) from table_activate_num_ids c   group by c.date_s order by c.date_s desc"                          
                # cur,conn = get_pgconn()
                # cur.execute(sql_get_totalduli_ids)
                # results_get_totalduli_ids = cur.fetchall()
                # close_pgconn(cur,conn)  

                # if results_get_totalduli_ids!=[]:
                #     each_result['total_duli'] = results_get_totalduli_ids[0][1]
                # else:
                #     each_result['total_duli'] = 0

                # ######get total duli over

                ######get total duli begin
                if results_get_dailyactive!=[]:
                    if results_get_type[0][0]=='客户' or results_get_type[0][0]=='商务':
                        # group by date
                        # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where b.proj_id in "+proj_id_col+" and c.proj_name='"+item[0]+"' group by c.proj_name"                 
                        sql_get_totalduli_ids = "select count(c.id) from table_proj b  join table_activate_num_ids c on b.proj_name=c.proj_name  where c.date_s<='" +str(results_get_dailyactive[0][0])+"'"+" and c.sub_channel_name='"+proj+"'"
                    else:
                        # group by date
                        # sql_get_totalduli_ids = "select c.proj_name,count(c.id) from table_activate_num_ids c  where c.proj_name='"+item[0]+"' group by c.proj_name"  
                        sql_get_totalduli_ids = "select count(c.id) from table_activate_num_ids c  where c.date_s<='" +str(results_get_dailyactive[0][0])+"'"+" and c.sub_channel_name='"+proj+"'"
                        
                    cur,conn = get_pgconn()
                    cur.execute(sql_get_totalduli_ids)
                    results_get_totalduli_ids = cur.fetchall()
                    close_pgconn(cur,conn)  

                    if results_get_totalduli_ids!=[]:
                        total_duli_s = results_get_totalduli_ids[0][0]
                    else:
                        total_duli_s = 0

                ######get total duli over                

                # now_total_duli = total_duli_s - item[1]

                if results_get_dailyactive!=[]:
                    result_str = result_str+'{"proj_name":"' + each_result['proj_name'] +'",'+'"daily_active":"' + str(each_result['active']) + '","duli":"' + str(each_result['duli']) +'",' + '"total_active":"'+str(each_result['total_active']) + '","total_duli":"'+ str(total_duli_s)+'","date":"'+str(results_get_dailyactive[0][0])+'","sub_channel_name":"'+proj+'"},'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}'        
    ##print result_item
    #return HttpResponse("<p>"+str(result_item)+"</p>")
    ##print result_str
    return result_str  

#insert subchannel into db
def insert_subchannel_into_db():

    time = ""
    time_p = ""
    daily_table_last = ""

    sql_get_tables = "select pg_tables.tablename from pg_tables order by pg_tables.tablename"
    cur,conn= get_pgconn()
    cur.execute(sql_get_tables)
    results_get_tables = cur.fetchall()
    close_pgconn(cur,conn)

    daily_table_list = []
    for item_tables in results_get_tables:
        daily_table_list.append(item_tables[0])

    f_name_tar = "/home/charles/log/kkk"

    ############ 2016 passed end
    for file in os.listdir(f_name_tar + "_files/"):
        f = open(f_name_tar + "_files/"+file)
        ############ 2016 passed start
        #print file

        if file.count('production_')==0:
            #print "Not log file !!!!!"
            # os.remove(f_name_tar + "_files/"+file)
            continue
        ############ 2016 passed end

        #f = open(file)

        inde_ad = 0

        for i in f:
            i = i.encode('utf-8')
            ##print i
            if i.count('sub_channel')==0:
                continue
            else:
                ind_imsi = i.find('imsi')
                ind_sub_channel = i.find('sub_channel')
                ind_sub_channel_id = i.find('sub_channel_id')
                ind_mac = i.find('mac_addr')

                if ind_imsi==-1 or ind_mac==-1:
                    continue
                else:
                    imsi = i[ind_imsi+7:ind_imsi+22]

                    sub_channel_clip = i[ind_sub_channel:-1]
                    ##print sub_channel_clip
                    first_get_yinhao = str(sub_channel_clip).find('"')
                    again_get_yinhao = sub_channel_clip.find('"',14)
                    ##print first_get_yinhao
                    ##print again_get_yinhao

                    sub_channel_name = sub_channel_clip[first_get_yinhao+1:again_get_yinhao]

                    sub_channel_id_clip = i[ind_sub_channel_id:-1]
                    # first_get_yinhao_id = sub_channel_id_clip.find['"']
                    again_get_yinhao_id = sub_channel_id_clip.find(',',17)
                    sub_channel_id = sub_channel_id_clip[16:again_get_yinhao_id]
                    wifi_mac = i[ind_mac+11:ind_mac+28]

                    sql_get_t = "select id from table_activate_num_ids  where wifi_mac='"+wifi_mac+"' and sub_channel_name is NULL" 
                    cur,conn= get_pgconn()
                    cur.execute(sql_get_t)
                    results_get_t = cur.fetchall()
                    close_pgconn(cur,conn)

                    if results_get_t==[]:
                       continue

                    ### calculating independent users
                    cur,conn= get_pgconn()
                    sql_update_sub_channel = "update table_activate_num_ids set sub_channel_name='"+sub_channel_name+"',sub_channel_id='" +sub_channel_id + "' where wifi_mac='"+wifi_mac+"'"
                    cur.execute(sql_update_sub_channel)
                    commit_conn(conn)
                    close_pgconn(cur,conn)

                    ### calculating daily active users

                    now_t = datetime.datetime.now()
                    now_str_t = now_t.strftime('%Y_%m_%d')
                    daily_table = "table_daily_active_"+now_str_t

                    ############ 2016 passed start
                    daily_table = "table_daily_active_"+time_p
                    #daily_table_last = daily_table
                    if daily_table not in daily_table_list:
                        #print "daily table existed !!!!!"
                        #else:
                        create_new_table_for_daily_active_pass(time_p)
                        daily_table_last = daily_table
                        daily_table_list.append(daily_table)
                    ############ 2016 passed end
                    cur,conn= get_pgconn()
                    sql_update_sub_channel = "update "+daily_table+" set sub_channel_name='"+sub_channel_name+"',sub_channel_id='" +sub_channel_id + "' where wifi_mac='"+wifi_mac+"'"
                    cur.execute(sql_update_sub_channel)
                    commit_conn(conn)
                    close_pgconn(cur,conn)

                    inde_ad = inde_ad + 1
                    print("duli id cals num : "+str(inde_ad))


        f.close()

    #print daily_table_list

    return "OK"

#adding columns to duli
def add_columns_to_duli_tables():
    
    sql_add_column ="alter table table_activate_num_ids add sub_channel_name text, add sub_channel_id text" 
    #print sql_add_column
    cur,conn= get_pgconn()
    cur.execute(sql_add_column)
    commit_conn(conn)   
    close_pgconn(cur,conn) 

    return "OK"

def add_columns_to_total_tables():
    
    sql_add_column ="alter table table_activate_num_daily_total add sub_channel_name text, add sub_channel_id text" 
    #print sql_add_column
    cur,conn= get_pgconn()
    cur.execute(sql_add_column)
    commit_conn(conn)   
    close_pgconn(cur,conn) 

    return "OK"    

#adding columns to daily active tables
def add_columns_to_dailyactive_tables():
    
    sql_get_tables = "select pg_tables.tablename from pg_tables  where pg_tables.tablename like 'table_daily_active_%' order by pg_tables.tablename"
    cur,conn= get_pgconn()
    cur.execute(sql_get_tables)
    results_get_tables = cur.fetchall()
    close_pgconn(cur,conn) 

    for item in results_get_tables:
        sql_add_column ="alter table " + item[0] + " add sub_channel_name text, add sub_channel_id text" 
        #print sql_add_column
        cur,conn= get_pgconn()
        cur.execute(sql_add_column)
        commit_conn(conn)   
        close_pgconn(cur,conn) 

    return "OK"

#insert daily active num for frontpage display
def insert_manual_daily_active(proj_id, num):
    return "OK"

#for testing logfile
def insert_formatted_data_to_db_imsi():
    f = open('/home/charles/production_2016-11-28.log.3', 'r')

    iii = 0
    for i in f:
        #print iii
        iii+=1
        if i.count('imei')==0:
            continue
        else:
            ind_imsi = i.index('imei')
            imsi = i[ind_imsi+7:ind_imsi+22]
            #print imsi
            if judge_imsi_exsit(imsi)==False:
                #print "not exsited!!!!!!!!!!!!!!!!!!!!!!!!!"
                f_w = open('/home/charles/myImei.txt','a')
                imsi_com = imsi+"\n"
                f_w.write(imsi_com)
                f_w.close()
            else:
                continue

    return "OK"    

#for testing logfile
def judge_imsi_exsit(imsi):
    #print "exsitance judging!!!!!!"
    #print imsi

    f = open('/home/charles/myImei.txt', 'r')

    for i in f:
        #print i
        if i.count(imsi)>0:
            #print "fffdfddfd"
            return True
        else:
            continue

    f.close()
    return False    

def check_files_for_updated():

    # f_name_tar = "/home/charles/log/kkk" 
    # for file in os.listdir(f_name_tar + "_files/"):
    #     f = open(f_name_tar + "_files/"+file)
    #     inde_ad = 0
    #     for index,i in enumerate(f):
    #         imsi_col = ['2300150073625550','2550142704699680','4660560025530690']

    #         for each in imsi_col:
    #             if i.count(each)>0:
    #                 #print "imsi "+str(each)+" found !!! file name : "+file+" line num : "+str(index+1)

    #     f.close()

    return "OK"

def index_cnt_from_cdn(url, date_from, date_to):
    # AccesKeyID = 'AjHtBvujgTZo3JUw'
    # AccessKeySecret = 'WsgWVEzBi0nHNwoC0mNEBJaMk5iWx7'
    # auth = oss2.Auth(AccesKeyID, AccessKeySecret)
    # EndPoint = 'oss-cn-hangzhou.aliyuncs.com'
    # bucket_name = 'apk-tripics'
    # bucket = oss2.Bucket(auth, EndPoint, bucket_name)
    # # for b in islice(oss2.ObjectIterator(bucket), 10):
    # #     print(b.key)

    timeArray_from = time.strptime(date_from, "%Y-%m-%d")
    #转换为时间戳:
    timeStamp_from = int(time.mktime(timeArray_from))

    timeArray_to = time.strptime(date_to, "%Y-%m-%d")
    #转换为时间戳:
    timeStamp_to = int(time.mktime(timeArray_to))    
    # timeStamp == 1381419600

    # now = datetime.datetime.now()
    # # d_t = now + datetime.timedelta(days=1)
    # day = now.strftime('%Y-%m-%d')
    # prefix_l = 'log/apk-tripics-logapk-tripics' + day

    root = "/home/charles/Downloads/LOG_DL/"
    os.chdir(root)

    cmd_dl = './cdnlogdownloader.sh -domain="wallpaper.thetripics.com" -id="AjHtBvujgTZo3JUw" -secret="WsgWVEzBi0nHNwoC0mNEBJaMk5iWx7"  -date="'
    timestamp_mid = timeStamp_from
    while timeStamp_from <= timestamp_mid and timeStamp_to >= timestamp_mid:
        time_tuple = time.gmtime(timestamp_mid)
        time_over = time.strftime('%Y-%m-%d',time_tuple)
        cmd_dl = cmd_dl + time_over + '  '
        timestamp_mid+=86400

    cmd_dl += '"'
    #print cmd_dl
    os.system(cmd_dl)

    url = url.replace("$$$","/")
    print(url)
    prefix_f = url[0:url.find('/')]

    result_str = ""

    for file in os.listdir(root):
        # #print file
        num = 0
        if file.count(prefix_f) == 0:
            continue
        
        date_file = file[-10:].replace("_","-")
        timeArray_file = time.strptime(date_file, "%Y-%m-%d")
        #转换为时间戳:
        timeStamp_file = int(time.mktime(timeArray_file))

        # #print timeStamp_file
        # #print timeStamp_from
        # #print timeStamp_to
        if timeStamp_file<timeStamp_from or timeStamp_file>timeStamp_to:
            continue
        # #print "what!!!!!!!!!!!!!!!!!!1"
        f = open(root+file)
        for i in f:
            index_apk1 = i.find(url)
            # #print url
            ##print i[-11:-2]
            ##print index_apk1
            if index_apk1 != -1 and i[-11:-2] =='text/html':
                num+=1

        #print date_file+" INDEX : "+str(num)
        result_str = result_str+'{"date":"' + date_file +'",'+'"num":"' + str(num) + '"},'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}' 

    return result_str
    # prefix_l = 'log/apk-tripics-logapk-tripics' + "2017-07-05"
    # os.mknod("/home/apk-download-log/" + day) 

def apk_cnt_from_cdn(url,date_from,date_to):
    # AccesKeyID = 'AjHtBvujgTZo3JUw'
    # AccessKeySecret = 'WsgWVEzBi0nHNwoC0mNEBJaMk5iWx7'
    # auth = oss2.Auth(AccesKeyID, AccessKeySecret)
    # EndPoint = 'oss-cn-hangzhou.aliyuncs.com'
    # bucket_name = 'apk-tripics'
    # bucket = oss2.Bucket(auth, EndPoint, bucket_name)
    # # for b in islice(oss2.ObjectIterator(bucket), 10):
    # #     print(b.key)

    #将其转换为时间数组
    
    timeArray_from = time.strptime(date_from, "%Y-%m-%d")
    #转换为时间戳:
    timeStamp_from = int(time.mktime(timeArray_from))

    timeArray_to = time.strptime(date_to, "%Y-%m-%d")
    #转换为时间戳:
    timeStamp_to = int(time.mktime(timeArray_to))    
    # timeStamp == 1381419600

    # now = datetime.datetime.now()
    # # d_t = now + datetime.timedelta(days=1)
    # day = now.strftime('%Y-%m-%d')
    # prefix_l = 'log/apk-tripics-logapk-tripics' + day
    result_str = ""
    root = "/home/charles/Downloads/LOG_DL/"

    os.chdir(root)

    cmd_dl = './cdnlogdownloader.sh -domain="apk-internal.thetripics.com" -id="AjHtBvujgTZo3JUw" -secret="WsgWVEzBi0nHNwoC0mNEBJaMk5iWx7"  -date="'
    timestamp_mid = timeStamp_from
    while timeStamp_from <= timestamp_mid and timeStamp_to >= timestamp_mid:
        time_tuple = time.gmtime(timestamp_mid)
        time_over = time.strftime('%Y-%m-%d',time_tuple)
        cmd_dl = cmd_dl + time_over + '  '
        timestamp_mid+=86400

    cmd_dl += '"'
    #print cmd_dl
    os.system(cmd_dl)

    # prefix_f = "apk.thetripics.com"
    url = url.replace("$$$","/")
    prefix_f = url[0:url.find('/')]

    for file in os.listdir(root):
        num = 0
        num_click = 0

        if file.count(prefix_f) == 0:
            continue

        date_file = file[-10:].replace("_","-")
        timeArray_file = time.strptime(date_file, "%Y-%m-%d")
        #转换为时间戳:
        timeStamp_file = int(time.mktime(timeArray_file))

        if timeStamp_file<timeStamp_from or timeStamp_file>timeStamp_to:
            continue

        f = open(root+file)
        for i in f:
            index_apk1 = i.find(url)
            if index_apk1==-1:
                continue
            num_click+=1
            # index_apk2 = i.find('lls-zt_pc6-v5.2.1-721-20170607-135050',index_apk1+1)
            index_apk2 = i.find(' ',index_apk1+1)
            index_apk3 = i.find(' ',index_apk2+1)
            index_apk4 = i.find(' ',index_apk3+1)
            index_apk5 = i.find(' ',index_apk4+1)
            index_apk6 = i.find(' ',index_apk5+1)
            hit_length = i[index_apk4+1:index_apk5]
            hit_miss = i[index_apk5+1:index_apk6]
            # if int(hit_length)>=43616468 and hit_miss == "HIT":
            print(hit_miss)
            if int(hit_length)>=8486 and hit_miss == "HIT":
                # #print int(hit_length)
                num+=1
        #print date_file+" APK : "+str(num)
        result_str = result_str+'{"date":"' + date_file +'",'+'"num_dl":"' + str(num) +'",'+'"num_click":"' + str(num_click) + '"},'

    result_str = result_str[0:int(len(result_str))-1]    
    result_str = '{"allData":[' + result_str +']}' 

    return  result_str       
    # prefix_l = 'log/apk-tripics-logapk-tripics' + "2017-07-05"
    # os.mknod("/home/apk-download-log/" + day)     

def percentage(consumed_bytes, total_bytes):
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        print('\r{0}% '.format(rate), end='')
        sys.stdout.flush()


def big_file_download(request):
    # do something...

    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    the_file_name = file_name
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)

    return response

def send_file(filename):  
    """                                                                          
    Send a file through Django without loading the whole file into               
    memory at once. The FileWrapper will turn the file object into an            
    iterator for chunks of 8KB.                                                  
    """ 
    # filename = __file__ # Select your file here.                                  
    wrapper = FileWrapper(file(filename))  
    response = HttpResponse(wrapper, content_type='text/plain')  
    response['Content-Length'] = os.path.getsize(filename)  
    return response     

def get_file_from_url(url):

    req = urllib2.Request(url)

    return req

def redirect_to_dl(url):
    print(url)
    return HttpResponseRedirect(url) 

def download_multiapks(apks):
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
    
    for every_apk in apk_col:
        
        if bucket_apk.object_exists(every_apk):
            cdn_url = "https://"+bucket_name_apk_cdn+".thetripics.com/"+every_apk
            # bucket_apk.get_object_to_file(every_apk, every_apk,progress_callback=percentage)

            # urllib.urlretrieve(everyURL, localPDF)
            # get_file_from_url(cdn_url)
            print("apk !!")
            return HttpResponseRedirect("baidu.com")
        elif bucket_apk_internal.object_exists(every_apk):
            # bucket_apk_internal.get_object_to_file(every_apk, every_apk,progress_callback=percentage)
            cdn_url = "https://"+bucket_name_apk_internal_cdn+".thetripics.com/"+every_apk

            redirect_to_dl(cdn_url)

    # time_now_com = timezone.localtime(timezone.now()).strftime("'%Y-%m-%d_%H_%M_%S'")
    # cmd = "tar -cvf apks_"+time_now_com+".tar  *.apk"
    # os.system(cmd)
    # print('zip over')
    
    # wrapper = FileWrapper(file(filename))  
    # response = HttpResponse(wrapper, content_type='text/plain')  
    # response['Content-Length'] = os.path.getsize(filename)  
    # return response 

    return "Request apks are downloaded successfully !"

#####
def find_all_index(arr,item):
    return [i for i,a in enumerate(arr) if a==item]

##### get pure dnu/dau
def get_pure_dnu(argv):
    # print(datetime.datetime.now())
    result_str = ""
    proj_id_all = []
    proj_id_argv = argv

    leancloud.init("Fhdcn0x7iznoVTkg6kzthl6w-gzGzoHsz", master_key="usMoq9bILw9Yp39lL2K89sjq")

    if proj_id_argv == 'all-recal':
        queryAll = True
        cql_get_all_proj = "select * from Project order by name limit 99999999"
        todo_query_all_proj = leancloud.Query.do_cloud_query(cql_get_all_proj)
        todo_list_all_proj = todo_query_all_proj.results # 返回符合条件的 todo list 
        for each_proj in todo_list_all_proj:
            proj_id_all.append(each_proj.get('name'))
    elif proj_id_argv == 'all':
        queryAll = True
        # proj_id_all = ['Game01', 'OPPO', 'Titan01', 'Tripics测试通', 'aa', 'ad_dev_002', 'ad_ota_001', 'ad_ota_001_1', 'ad_ota_002', 'ad_ota_003', 'ad_ota_004', 'ad_ota_005', 'atcomm', 'dev_001', 'dev_002', 'divert testing', 'ecommerce01', 'fanzhuo-s004', 'fanzhuo_S003', 'fanzhuo_S004', 'google_play', 'ota_001', 'ota_001_1', 'ota_002', 'ota_003', 'ota_004', 'ota_005', 'sub_dev_001', 'sub_dev_002', 'sub_ota_S001', 'sub_ota_S002', 'sub_ota_S003', 'sub_ota_S004', 'unknown', 'wechat01', 'yeh-nigger32', '特别行动X', '金立壁纸广告5', '金立壁纸广告_01', '金立壁纸广告_02', '金立壁纸管广告']
        proj_id_all = ['ota_001_1', 'ad_ota_001_1', 'ad_ota_005', 'ad_ota_004', 'ad_ota_001', 'ota_004', 'ota_003', 'google_play', 'ota_001', 'ad_ota_003', 'fanzhuo_S004', 'ota_005']
    else:
        proj_id_all.append(proj_id_argv)

    res_col = []

    aday_for_st = datetime.timedelta(days=-1)
    ahour_for_st = datetime.timedelta(hours=-8)
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    date_from = (datetime.datetime.strptime(date_str+" 00:00:00", "%Y-%m-%d %H:%M:%S")+aday_for_st+ahour_for_st).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    date_to = (datetime.datetime.strptime(date_str+" 23:59:59", "%Y-%m-%d %H:%M:%S")+aday_for_st+ahour_for_st).strftime('%Y-%m-%dT%H:%M:%S.999Z')

    ########all dnu query
    cql_get_all_user = "select objectId, androidId, projectId, createdAt ,verified from StatUser where createdAt<date(?) order by createdAt limit 99999999"
    todo_query_all_user = leancloud.Query.do_cloud_query(cql_get_all_user, date_to)
    todo_list_all_user = todo_query_all_user.results # 返回符合条件的 todo list 
    ########all dau query
    cql_get_dau = "select objectId, userId, projectId, createdAt, verified from StatDAU  where createdAt>=date(?) and createdAt<=date(?) order by createdAt limit 99999999"
    todo_query_dau = leancloud.Query.do_cloud_query(cql_get_dau, date_from, date_to)
    todo_list_dau = todo_query_dau.results # 返回符合条件的 todo list 
    # print(datetime.datetime.now())

    for proj_id in proj_id_all:
        # print(datetime.datetime.now())
        dnu_cnt = 0
        dau_cnt = 0
        dnu_gross_cnt = 0
        dau_gross_cnt = 0

        user_obj_former = []
        aid_former = []
        oid_former = []
        proj_former = []

        user_obj_today = []

        user_obj_all = []
        aid_all = []
        oid_all = []
        proj_all = []
        time_all = []

        dau_obj_all = []
        dau_oid_all = []
        dau_aid_all = []
        dau_uid_all = []
        dau_proj_all = []

        dau_obj_today = []

        user_obj_thisproj = []  

        ########dnu calculation
        for each_user in todo_list_all_user:
            aid = each_user.get('androidId')
            oid = each_user.get('objectId')
            pid = each_user.get('projectId')
            if pid is None:
                pid = "ng"
            time = each_user.get('createdAt')

            user_obj_all.append(each_user)
            aid_all.append(aid)
            oid_all.append(oid)
            time_all.append(time)
            proj_all.append(pid)
            
            if pid == proj_id:
                user_obj_thisproj.append(each_user)

            if time.strftime('%Y-%m-%dT%H:%M:%S.000Z')<date_from:
                user_obj_former.append(each_user)
                aid_former.append(aid)
                proj_former.append(pid)
            elif pid == proj_id:
                user_obj_today.append(each_user)

        for each_user_today in user_obj_today:
            aid_today = each_user_today.get('androidId')
            oid_today = each_user_today.get('objectId')
            pid_today = each_user_today.get('projectId')
            time_today = each_user_today.get('createdAt')
            cflag=True
            if (aid_today in aid_former):
                index_f = find_all_index(aid_former,aid_today)
                for every_index in index_f:
                    if ('ad_'+pid_today) == str(proj_former[every_index]):
                        cflag=False
                if cflag==True:
                    if each_user_today.get('verified')==True:
                        dnu_cnt+=1
                        dnu_gross_cnt+=1
                    else:
                        dnu_gross_cnt+=1
            else:
                if each_user_today.get('verified')==True:
                    dnu_cnt+=1
                    dnu_gross_cnt+=1
                else:
                    dnu_gross_cnt+=1
        # print(datetime.datetime.now())

        ########dau calculation
        print(datetime.datetime.now())
        for each_dau in todo_list_dau:
            oid_dau = each_dau.get('objectId')
            pid_dau = each_dau.get('projectId')
            time_dau = each_dau.get('createdAt')
            uid_dau = each_dau.get('userId')

            aid_dau = aid_all[oid_all.index(uid_dau)]

            dau_obj_all.append(each_dau)
            dau_oid_all.append(oid_dau)
            dau_aid_all.append(aid_dau)
            dau_uid_all.append(uid_dau)    
            dau_proj_all.append(pid_dau)

        print(datetime.datetime.now())
        for index_dau,each_dau_obj in enumerate(dau_obj_all):
            each_aid_dau = dau_aid_all[index_dau] 
            each_pid_dau = dau_proj_all[index_dau] 
            each_uid_dau = dau_uid_all[index_dau]
            dau_user_index = oid_all.index(each_uid_dau)

            plus_confirm = False
            proj_col_dau = []
            if aid_all.count(each_aid_dau)>=2:
                index_dcheck = find_all_index(aid_all,each_aid_dau)
                cflag_dau = True
                for each_index_dcheck in index_dcheck:
                    proj_col_dau.append(proj_all[each_index_dcheck])
                    if each_index_dcheck == dau_user_index:
                        continue
                    
                    if ("ad_"+proj_id)==proj_all[each_index_dcheck]:
                        cflag_dau = False
                        break
                    if each_index_dcheck<dau_user_index and proj_id!=("ad_"+proj_all[each_index_dcheck]) and ("ad_"+proj_id)!=proj_all[each_index_dcheck]:
                        cflag_dau = False
                        break

                if cflag_dau == True and (proj_id in proj_col_dau):
                    if each_dau_obj.get('verified')==True:
                        dau_cnt+=1
                        dau_gross_cnt+=1
                        plus_confirm = True
                    else:
                        dau_gross_cnt+=1
                        
            elif proj_id == each_pid_dau:
                if each_dau_obj.get('verified')==True:
                    dau_cnt+=1
                    dau_gross_cnt+=1
                    plus_confirm = True
                else:
                    dau_gross_cnt+=1
        print(datetime.datetime.now())
        
        dic = {}
        dic['proj_id'] = proj_id
        dic['dnu'] = dnu_cnt
        dic['dau'] = dau_cnt
        dic['dnu_gross'] = dnu_gross_cnt
        dic['dau_gross'] = dau_gross_cnt
        print(dic)
        result_str = result_str+'{"proj_id":"' + proj_id +'",'+'"dnu":"' + str(dnu_cnt) +'",'+'"dau":"' + str(dau_cnt) +'",'+'"dnu_gross":"' + str(dnu_gross_cnt) +'",'+'",'+'"dau_gross":"' + str(dau_gross_cnt) +'"},'

    result_str = "["+result_str[0:int(len(result_str))-1]+"]"
    return  result_str