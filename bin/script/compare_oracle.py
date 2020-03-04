#!/usr/bin/python
import json
import cx_Oracle
import os,copy
import sys


"""
    Compare the dirrerence between two database
    Test under python 3.8 Oracle 12c and CentOS 7
    Author Willy Xi
    20200203
"""

try:
    config=sys.argv[1]
except IndexError as e:
    config='../../config/compare_db.json'

print("Current config file is:"+config)
conf=open(config,'r')
conf_log=json.load(conf)

#Change cx_Oracle type to normal string
hash_oracle_map={}
hash_oracle_map[cx_Oracle.BFILE]='BFILE'
hash_oracle_map[cx_Oracle.NATIVE_FLOAT]='BINARY_DOUBLE'
hash_oracle_map[cx_Oracle.NATIVE_FLOAT]='BINARY_FLOAT'
hash_oracle_map[cx_Oracle.BLOB]='BLOB'
hash_oracle_map[cx_Oracle.FIXED_CHAR]='CHAR'
hash_oracle_map[cx_Oracle.CLOB]='CLOB'
hash_oracle_map[cx_Oracle.CURSOR]='CURSOR'
hash_oracle_map[cx_Oracle.DATETIME]='DATE'
hash_oracle_map[cx_Oracle.INTERVAL]='INTERVAL DAY TO SECOND'
hash_oracle_map[cx_Oracle.LONG_STRING]='LONG'
hash_oracle_map[cx_Oracle.LONG_BINARY]='LONG RAW'
hash_oracle_map[cx_Oracle.FIXED_NCHAR]='NCHAR'
hash_oracle_map[cx_Oracle.NCLOB]='NCLOB'
hash_oracle_map[cx_Oracle.NUMBER]='NUMBER'
hash_oracle_map[cx_Oracle.NCHAR]='NVARCHAR2'
hash_oracle_map[cx_Oracle.OBJECT]='OBJECT'
hash_oracle_map[cx_Oracle.BINARY]='RAW'
hash_oracle_map[cx_Oracle.ROWID]='ROWID'
hash_oracle_map[cx_Oracle.TIMESTAMP]='TIMESTAMP'
hash_oracle_map[cx_Oracle.STRING]='VARCHAR2'


def get_oracle_obj(db_connect_str):
    print("current connet string is :"+db_connect_str)
    try:
        db_connect=cx_Oracle.connect(db_connect_str)
    except cx_Oracle.DatabaseError as ef:
        print("Fata:Database connect err, pls check connect"+db_src)
        exit
    db_cursor1=db_connect.cursor()
    db_cursor2=db_connect.cursor()
    hash_result={}
    db_cursor1.execute('select * from user_all_tables')
    for table in db_cursor1:
        hash_result[table[0]]=[]
        exce_sql='select * from '+table[0]+' where 1=2'
        try:
            db_cursor2.execute(exce_sql)
        except cx_Oracle.DatabaseError as e:
            print("Warning:cx_Oracle.Database Error!Please check onject "+'\''+table[0]+'\'.')
            continue
        for column in db_cursor2.description:
            hash_result[table[0]].append(column[0]+' '+hash_oracle_map[column[1]]+' '+str(column[2]))
    db_cursor1.close()
    db_cursor2.close()
    db_connect.close()
    return hash_result


def compare_array(arr1,arr2):
    min_len=len(arr1) if len(arr1)<=len(arr2) else len(arr2)
    arr=[]
    for i in range(0,min_len):
        if arr1[i] != arr2[i]:
            arr.append("%30s|%30s|" %(arr1[i],arr2[i]))
    if len(arr1)!=min_len:
        for j in range(min_len,len(arr1)):
            arr.append("%30s|%30s|" %(arr1[j],""))
    else:
        for j in range(min_len,len(arr2)):
            arr.append("%30s|%30s|" %("",arr2[j])) 
    return arr




db_src=conf_log['src_db']['username']+'/'+conf_log['src_db']['password']+'@'+conf_log['src_db']['Oracle_connect']
db_tag=conf_log['tag_db']['username']+'/'+conf_log['tag_db']['password']+'@'+conf_log['tag_db']['Oracle_connect']



try:
    connect_tag=cx_Oracle.connect(db_tag)
except cx_Oracle.DatabaseError as ef:
    print("Database connect err, pls check connect:"+db_tag)

arr_src_notexists=[]
arr_tag_notexists=[]
hash_tab_src=copy.deepcopy(get_oracle_obj(db_src))
hash_tab_tag=copy.deepcopy(get_oracle_obj(db_tag))


for i in hash_tab_src:
    if not i in hash_tab_tag:
        arr_src_notexists.append(i)
    else:
        result_arr=compare_array(hash_tab_src[i],hash_tab_tag[i])
        if len(result_arr)>0:
            print("Table "+i+'')
            for k in result_arr:
                print(k)
                print("------------------------------------------------------------")

for i in hash_tab_tag:
    if not i in hash_tab_src:
        arr_tag_notexists.append(i)

if len(arr_src_notexists)>0:
    print(str(len(arr_src_notexists))+" table in SRC but not in TAG:")
    for m in arr_src_notexists:
        print(m)
    print("------------------------------------------------------------")
if len(arr_tag_notexists)>0:
    print(str(len(arr_tag_notexists))+" table in TAG but not in SRC:")
    for n in arr_tag_notexists:
        print(n)
    print("------------------------------------------------------------")
