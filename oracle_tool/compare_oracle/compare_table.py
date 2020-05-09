#!usr/bin/python
import cx_Oracle
import re

src_db="cc/Zsmart*2018@10.120.244.34:11521/cc"
tag_db='mig/Zsmart*2018@10.120.244.99:11521/cc'


class compare_table:
    def __init__(self,segment,src_db,tag_db,tables,field_name):
        self.segment=segment
        self.src_db=src_db
        self.tag_db=tag_db
        self.table_name=tables
        self.field_name=field_name

    def return_table_count(self,table,connect_str,field):
        oracle_conn=cx_Oracle.connect(connect_str)
        curs = oracle_conn.cursor()
        curs.execute('select/*+aprallel 8*/ max('+field+') from '+table)
        table_count=curs.fetchone()[0]
        curs.close()
        oracle_conn.close()
        return table_count

    def get_value(self,conn_str,table,field,star_value,seg,noclob_sql):
        oracle_conn=cx_Oracle.connect(conn_str)
        curs = oracle_conn.cursor()
        sql='select a.'+field+noclob_sql+' from '+table+' a where a.'+field+' between '+str(star_value)+' and '+str(seg)
        curs.execute(sql)
        hash_result={}
        for result in curs: 
            hash_result[result[0]]=result[1:]
        curs.close()
        oracle_conn.close()
        return hash_result

    def check_lob(self,conn_str,table_name):#lob field will set null
        oracle_conn=cx_Oracle.connect(conn_str)
        curs = oracle_conn.cursor()
        curs.execute('select * from '+table_name)
        head='insert into '+table_name+' values('
        seq=0
        sql=''
        for i in curs.description:
            if i[1]== cx_Oracle.CLOB or i[1]== cx_Oracle.BLOB or i[1]== cx_Oracle.NCLOB:
                sql+=', null'
            else:
                sql+=','+i[0]
        head=re.sub(',$','',head)
        curs.close()
        oracle_conn.close()
        head+=')'
        return sql

    def get_insert_sql(self,conn_str,table_name):
        oracle_conn=cx_Oracle.connect(conn_str)
        curs = oracle_conn.cursor()
        curs.execute('select * from '+table_name)
        head='insert into '+table_name+' values('
        seq=1
        for i in curs.description:
            head+=':'+str(seq)+','
            seq+=1
        head=re.sub(',$','',head)
        curs.close()
        oracle_conn.close()
        head+=')'
        return head

    def get_difference(self,start_value):#return value is a arrary
        noclob_sql=self.check_lob(self.src_db,self.table_name)
        count_src=self.return_table_count(self.table_name,self.src_db,self.field_name)
        count_tag=self.return_table_count(self.table_name,self.tag_db,self.field_name)
        hash1=self.get_value(self.src_db,self.table_name,self.field_name,start_value,self.segment,noclob_sql)
        hash2=self.get_value(self.tag_db,self.table_name,self.field_name,start_value,self.segment,noclob_sql)
        diff_add=set(hash1)-set(hash2)
        diff_del=set(hash2)-set(hash1)
        diff_upd=[]
        sam_compare=set(hash1)&set(hash2)
        arr_diff=[]
        for i in diff_add:
            arr_diff.append(hash1[i])
        for i in sam_compare:
            if not hash1[i]==hash2[i]:
                diff_upd.append([i,hash1[i]])
        return [arr_diff,diff_del,diff_upd]

    def get_hash_diff(self,src_hash,tag_hash):
        diff_add=set(tag_hash)-set(src_hash)
        diff_del=set(src_hash)-set(tag_hash)
        sam_compare=set(src_hash)&set(tag_hash)
        diff_upd=[]
        for i in sam_compare:
            if not tag_hash[i]==src_hash[i]:
                diff_upd.append(i)
        return (diff_add,diff_del,diff_upd)

    def batch_insert(self):
        table_count=self.return_table_count(self.table_name,self.src_db,self.field_name)
        cycle_num=(table_count-table_count%self.segment)/self.segment+1
        insert_sql=self.get_insert_sql(self.src_db,self.table_name)
        connect_db=cx_Oracle.connect(self.tag_db)
        curs = connect_db.cursor()
        tot_inset_num=0
        tot_delete_num=0
        tot_update_num=0
        for i in range(1,int(cycle_num)+1):
            difference=self.get_difference(self.segment*(i-1)+1)
            tot_inset_num+=len(difference[0])
            tot_delete_num+=len(difference[1])
            tot_update_num+=len(difference[2])
            for i in difference[0]:
                curs.execute(insert_sql,i)
            for i in difference[1]:
                curs.execute('delete from '+self.table_name+' where '+self.field_name+'='+i)
            for i in difference[2]:
                curs.execute('delete from '+self.table_name+' where '+self.field_name+'='+str(i[0]))
                curs.execute(insert_sql,i[1])
        connect_db.commit()
        curs.close()
        connect_db.close()
        return (tot_inset_num,tot_delete_num,tot_update_num)

a=compare_table(10000,src_db,tag_db,'advice_type','advice_type')
b=a.batch_insert()
print('Total insert record is:'+str(b[0])+"\nTotal delete record is:"+str(b[1])+"\n"+"Total update record is:"+str(b[2]))
