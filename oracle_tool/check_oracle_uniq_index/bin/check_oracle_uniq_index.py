#!/usr//bin/python
import cx_Oracle
import re
import json
import sys
import os
"""
    AUthor:Willy Xi
    Check data in staging enviroment's data is correspond to production/test enviroment
    Only for Oracle
    Test in CentOS 7 X64 Virtual Machine
"""

class Check_Oracle_uniq_ind:
    def __init__(self,staging_connect_str,production_connect_str):
        self.staging_connect_str=staging_connect_str
        self.production_connect_str=production_connect_str
        self.stag=cx_Oracle.connect(self.staging_connect_str)
        self.prod=cx_Oracle.connect(self.production_connect_str)

    def get_check_sql(self,v_name,r_name):#r_name=real table name in stag env, v_name= virtual_table in mig db
        #ex_sql='select b.COLUMN_NAME from USER_INDEXES a,USER_IND_COLUMNS b where a.INDEX_NAME=b.INDEX_NAME and a.UNIQUENESS=\'UNIQUE\' and a.TABLE_NAME=upper(\''+r_name+'\')'
        sql_get_index='select INDEX_NAME from USER_INDEXES a where   a.UNIQUENESS=\'UNIQUE\' and a.TABLE_NAME=upper(\''+r_name+'\')'
        sql_get_index_count='select count(1) from USER_INDEXES a where   a.UNIQUENESS=\'UNIQUE\' and a.TABLE_NAME=upper(\''+r_name+'\')'
        return_sql_head='select count(1) from (select ' 
        renturn_sql_mid=' from '+v_name+' group by '
        cursor_r=self.prod.cursor()
        cursor_r2=self.prod.cursor()
        cursor_r.execute(sql_get_index_count)
        count_reslut=cursor_r.fetchone()[0]
        cursor_r.execute(sql_get_index)
        hash_execute_sql={}
        hash_execute_sql=[]
        if count_reslut >0:
            cursor_r.execute(sql_get_index)
            for index_name in cursor_r:
                return_sql_content=""
                sql_get_index_column='select COLUMN_NAME from USER_IND_COLUMNS where INDEX_NAME=\''+index_name[0]+'\''
                sql_get_index_column_count='select count(1) from USER_IND_COLUMNS where INDEX_NAME=\''+index_name[0]+'\''
                cursor_r2.execute(sql_get_index_column_count)
                if cursor_r2.fetchone()[0]>0:
                    cursor_r2.execute(sql_get_index_column)
                    for colunm_name in cursor_r2:
                        return_sql_content=return_sql_content+colunm_name[0]+','               
                    return_sql_content=return_sql_content[:-1]
                    hash_execute_sql.append([index_name[0],return_sql_head+return_sql_content+renturn_sql_mid+return_sql_content+' having count(1)>1)'])
        cursor_r.close()
        cursor_r2.close()
        return hash_execute_sql

    def check_stg_table(self,get_check_sql,table_list):#parameter=get_check_sql 
        result_set=[]
        for i in table_list:
            sql=get_check_sql(i[0],i[1])
            if len(sql)=="":
                result_set.append([i[0],'No unique index,skip'])
            else:
                for exec_sql in sql:
                    cursor=self.stag.cursor()
                    try:
                        cursor.execute(exec_sql[1])
                        result= 'Ok' if cursor.fetchone()[0]==0 else 'Fail'
                        result_set.append([i[0],exec_sql[0],result])
                    except cx_Oracle.DatabaseError:
                        print(exec_sql[1]+' execute fail')
                        continue
                    cursor.close()
        return result_set

        
    def disconnet(self):
        self.stag.close()
        self.prod.close()
        return 1

###################################
print('#####################################################################')
print('#                                                                   #')
print('#  Chek migration table adapt uniqe index in production database   #')
print('#  Python3 check_oracle_uniq_index.py ../../../example.json         #')
print('#                                                                   #')
print('#####################################################################')

if len(sys.argv) <=1:
    file=input('Please input table list file\n')
else:
    file=sys.argv[1]

while not os.path.exists(file):
    print('File not exits,please input again')
    file=input('Please input table list file\n')

with open(file) as table_list:
    tables=json.load(table_list)

a=Check_Oracle_uniq_ind('mig/Zsmart*2018@10.120.244.99:11521/cc','cc/Zsmart*2018@10.120.243.4:11521/cc')


#a=Check_Oracle_uniq_ind('mig/Zsmart*2018@10.120.244.99:11521/cc','cc/Zsmart*2018@10.120.243.4:11521/cc')
#for i in a.get_check_sql('MIG_WOM_RUT','WOM_RUT'):
#    print(i[1])

for i in a.check_stg_table(a.get_check_sql,tables['mig_tales']):
    print('Check Table:%30s %30s %s'%(i[0],i[1],i[2]))
a.disconnet()
#