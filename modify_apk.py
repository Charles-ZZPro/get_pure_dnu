#-*-coding:utf-8-*-
from __future__ import print_function
from __future__ import unicode_literals
import gzip 
import tarfile
import os
import sys
import datetime
import random
import shutil
import socket
import time
import os, tempfile, zipfile  
from wsgiref.util import FileWrapper
import struct
import md5
import binascii
from os.path import join, getsize

reload(sys)
sys.setdefaultencoding('utf-8')

## get md5 from a string
def GetStringMD5(str):  
    m = md5.new()  
    m.update(str)  
    return m.hexdigest()  

## get md5 of a input bigfile  
def GetBigFileMD5(file):  
    m = md5.new()  
    f = open(file,'rb')  
    maxbuf = 8192  
  
    while 1:  
        buf = f.read(maxbuf)  
        if not buf:  
            break  
        m.update(buf)   
  
    f.close()  
    return m.hexdigest() 

now = datetime.datetime.now()
date_str = now.strftime('%Y_%m_%d-%H_%M_%S') 

# file_src_dir = "c:/apk_src/apk_src.apk"
# file_goal_dir = "c:/apk_goal/"+date_str+".data"
# jpg_src_dir = "c:/apk_src/jpg_src.jpg"

file_src_dir = "/home/charles/Downloads/apk_src/apk_src.apk"
file_goal_dir = "/home/charles/Downloads/apk_goal/"+date_str+".data"
jpg_src_dir = "/home/charles/Downloads/apk_src/jpg_src.jpg"
# file_check_dir = "/home/charles/Downloads/apk_goal/apk_check.apk"

## get md5 of apk file
md5_got = GetBigFileMD5(file_src_dir)
md5_length = len(md5_got)
md5_bin = binascii.hexlify(md5_got)

## get apk file
file_src_obj = open(file_src_dir , "rb")
file_src = file_src_obj.read()
src_length = sys.getsizeof(file_src)
file_src_obj.close()

## get jpg file
jpg_src_obj = open(jpg_src_dir , "rb")
jpg_src = jpg_src_obj.read()
# jpg_length = sys.getsizeof(jpg_src)
jpg_length = getsize(jpg_src_dir)
jpg_src_obj.close()
jpg_length_bin = bin(jpg_length)

if len(sys.argv) == 1:
    print("!!! Enter apk version !!!")
    exit(1)

ver = int(sys.argv[1])
# print(ver)
ver_length = sys.getsizeof(ver)
# ver_bin = binascii.hexlify(ver)

## mix them to goal file(.data)
try:
	## pack by struck
    # str_stru = str(md5_length) + "s" + str(ver_length) + "si" + str(jpg_length) + "s" + str(src_length) + "s"
    # s = struct.Struct(str_stru)
    # values = (md5_got,ver,jpg_length,jpg_src,file_src)
    # package = s.pack(*values)
    # bi_values = binascii.hexlify(package)
    ##

    ## check apk error    
    # unpacked = s.unpack(binascii.unhexlify(bi_values))
    # file_check = open(file_check_dir , "wb")
    # file_check.write(unpacked[4])
    # file_check.close()
    ##

    ## packing
    ver_c = struct.pack('<LL',ver,jpg_length)
    # print(sys.getsizeof((ver_c)))
    # print(ver_c)
    # print(sys.getsizeof((jpg_length)))
    # float_value = 1.5
    # float_bytes = struct.pack('f', float_value)
    # print(float_bytes)
    # int_value = struct.unpack('L', float_bytes)[0]
    # print(int_value)
    # int_bytes = struct.pack('L', int_value)
    # print(int_bytes)

    bin_col = (md5_got, ver_c, jpg_src, file_src)
    for each in bin_col:
	    file_goal = open(file_goal_dir , "ab+")
	    file_goal.write(each)
	    file_goal.close()
	##

    print("OK")
except Exception,e:
	print("!!! Something went wrong !!! :::")
	print(e.message)






