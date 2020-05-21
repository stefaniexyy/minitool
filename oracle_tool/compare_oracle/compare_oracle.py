#!/usr/bin/python3
import cx_Oracle
import os,copy
import sys


"""
    Compare the dirrerence between two database
    Test under python 3.8 Oracle 12c and CentOS 7
    Author Willy Xi
    20200203
"""


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
            if(column[1]==cx_Oracle.DATETIME or column[1]==cx_Oracle.BLOB):
                hash_result[table[0]].append([column[0],hash_oracle_map[column[1]]])
            elif(column[1]==cx_Oracle.NUMBER and column[2]==39):#number 39=int
                hash_result[table[0]].append([column[0],'INT'])
            else:
                hash_result[table[0]].append([column[0],hash_oracle_map[column[1]]+'('+str(column[2])+')'])
    db_cursor1.close()
    db_cursor2.close()
    db_connect.close()
    return hash_result


def compare_array(arr1,arr2):
    min_len=len(arr1) if len(arr1)<=len(arr2) else len(arr2)
    arr=[]
    for i in range(0,min_len):
        if arr1[i][0]!= arr2[i][0]:
            arr.append("%30s|%30s|" %(arr1[i][0],arr2[i][0]))
    if len(arr1)!=min_len:
        for j in range(min_len,len(arr1)):
            arr.append("%30s|%30s|" %(arr1[j][0],""))
    else:
        for j in range(min_len,len(arr2)):
            arr.append("%30s|%30s|" %("",arr2[j][0])) 
    return arr

def generate_compare_array(arr1,arr2):
    min_len=len(arr1) if len(arr1)<=len(arr2) else len(arr2)
    arr=[]
    for i in arr1:
        flag=0
        for j in arr2:
            if i[0]==j[0] and i[1]!=j[1]:
                flag=1
                arr.append([i,j])
                break
            elif i[0]==j[0] and i[1]==j[1]:
                flag=2
                break
        if flag==0:
             arr.append([i,""])
    for i in arr2:
        flag=0
        for j in arr1:
            if i[0]==j[0]:
                flag=2
                break
        if flag==0:
            arr.append(["",i])
    #for i in range(0,min_len):
    #    if arr1[i][0] == arr2[i][0] and arr1[i][1] != arr2[i][1]:
    #        arr.append([arr1[i],arr2[i]])
    #if len(arr1)!=min_len:
    #    for j in range(min_len,len(arr1)):
    #        arr.append([arr1[j],""])
    #else:
    #    for j in range(min_len,len(arr2)):
    #        arr.append(["",arr2[j]])
    return arr


print('*****************************************************************************************************')
print('*                                                                                                   *')
print('*             Compare databse table structure                                                       *')
print('*                          V1.1                                                                     *')
print('*              Src db= databse will be compared and update                                          *')
print('*              Tag db= databse will be referenced                                                   *')
print('*                                                                                                   *')
print('*****************************************************************************************************')

db_src=input("Please input src db connect string,example xx/xx@10.10.10.10:1521/xx\n")
try:
    connect_test=cx_Oracle.connect(db_src)
    connect_test.close()
except cx_Oracle.DatabaseError as ef:
    print("Database connect err, pls check connect:"+db_src)
    sys.exit()
else:
    print('Source database connect OK')

db_tag=input("Please input target db connect string,example xx/xx@10.10.10.10:1521/xx\n")
try:
    connect_test=cx_Oracle.connect(db_tag)
    connect_test.close()
except cx_Oracle.DatabaseError as ef:
    print("Database connect err, pls check connect:"+db_src) 
    sys.exit()
else:
    print('Target database connect OK')

out_sql=open('compare_result.sql','w')

arr_src_notexists=[]
arr_tag_notexists=[]
hash_tab_src=copy.deepcopy(get_oracle_obj(db_src))
hash_tab_tag=copy.deepcopy(get_oracle_obj(db_tag))


for i in hash_tab_src:
    if not i in hash_tab_tag:
        pass
    else:
        result_arr=generate_compare_array(hash_tab_src[i],hash_tab_tag[i])
        if len(result_arr)>0:
            out_sql.write("--Table "+i+'\n')
            for k in result_arr:
                if k[0]!="" and k[1]=="":
                    out_sql.write('Alter table '+i+' drop column '+k[0][0]+';\n')
                elif k[1]!="" and k[0]=="":
                    out_sql.write('Alter table '+i+' add '+k[1][0]+' '+k[1][1]+';\n')
                elif  k[0]!="" and k[1] !="":
                     out_sql.write('Alter table '+i+' modify( '+k[1][0]+' '+k[1][1]+');\n')
for i in hash_tab_tag:
    if not i in hash_tab_src:
        arr_tep=[]
        for content in hash_tab_tag[i]:
            arr_tep.append(' '.join(content))
        out_sql.write('create table '+i+'(')
        out_sql.write(',\n'.join(arr_tep)+');\n')
        out_sql.write('\n')

out_sql.close()
print('Result file is:compare_result.sql')
