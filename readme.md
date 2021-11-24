
# Oracle tool
目录结构
>>-oracle_tool  
>>>|--check_oracle_unidex   
>>>|--compare_oracle  
>>>|--dump_tool  
>>>|--load_data
>>>|--unload_date 
## check_oracle_unidex  检查表数据是否违反oracle唯一索引约束
检查入库前的表是否存在违反oracle唯一约束索引的情况
    
运行环境：  
Python 3.X  
cx_Oracle  
  
    执行命令：python3 check_oracle_uniq_index_py ../config/example.json

  
  配置文件：  
```json
    {
    "mig_tables":[
        ["MIG_CUST","CUST"],
        ["MIG_CUST_IDENTIFY","CUST_IDENTIFY"],
        ["MIG_CUST_ATTR_VALUE","CUST_ATTR_VALUE"]
    ]
    }
```

配置文件需要放在config目录下  
其中[]数组里面第一个表名是需要检查是否违反唯一索引的表，第二个表名是参考的表  
脚本回去数据库根据第二个参数表面去获取索引信息然后根据索引信息检查第一个表中的数据是否违反了唯一索引约束

## dump_tool 自动化的按表导出导入dump
运行环境
perl

    导出执行: perl expdp_oracle.pl 2 ../config/oracle_expimpdp.json
    导入执行：perl expdp_oracle.pl 1 ../config/oracle_expimpdp.json

配置文件：  
```json
    {
        "exp":{
            "username":"mig",
            "password":"Zsmart*2018",
            "connect_str":"10.120.244.99:11521/cc",
            "tables":[
                "MIG_CUST",
                "MIG_CUST_IDENTIFY",
                "MIG_CUST_ATTR_VALUE"
            ],
        "Directory":"MIG",
        "Directory_Path":"/ccdata/migdump",
        "Compression":"ALL",
        "Content":"DATA_ONLY"
        },
        "imp":{
            "uername":"cc",
            "password":"Zsmart*2018",
            "connect_str":"10.120.243.4:11521/cc",
            "Directory":"MIGDUMP",
            "Table_exists_action":"truncate",
            "Remap_Schema":"Y",
            "Source_username":"mig",
            "Remap_Tables":"Y",
            "Table_Name":{
                [
                    ["CUST","MIG_CUST","MIG_CUST.dump"]
                    ["CUST_IDENTIFY","MIG_CUST_IDENTIFY","MIG_CUST_IDENTIFY.dump"]
                ]
            }
        },
        "exec_proc_num":8
    }
```
执行导入导出命令之前需要在oracle中配置好directory目录  
导出中的数组配置需要导出的表
导入中的数组，元素1：被导入的表，元素2：dump数据中的表名，元素3：dump文件名  

# load_data 把unl数据导入Oracle
    执行 chmod +x load.sh
         ./load.sh
    
配置文件
```cfg
#the file for load.

[dbtype]
oracle

[dbname]
mig/Zsmart*2018@10.120.244.99:11521/cc

[max_process_count]
5

[cpuno]
5

[datapath]
/ccdata/mig/data/output

[data only mode]
N

[tablelist]
MIG_EVENT_USAGE_C_71023|MIG_EVENT_USAGE_C_71023.unl|
MIG_EVENT_USAGE_71023|MIG_EVENT_USAGE_71023.unl|
[END]
````
数据文件需要放在[datapath]下  
[tablelist]下的参数第一个是表名，第二个是入库的文件名字
[tablelist]和[END]之间不要有空行

# unload_data 从oracle下载文本数据
    执行 chmod+x unload.sh
        ./unload.sh xxx.cfg

xxxx.cfg是配置文件名字，配置文件必须放在config目录下
```
[dbtype]
oracle

[dbname]
mig/Zsmart*2018@10.120.244.99:11521/cc

[max_process_count]
5

[cpuno]
5

[datapath]
/ccdata/mig/mig/data/input

[data only mode]
N

[tablelist]
FIX_cust_contact2|select *from FIX_cust_contact|
[END]
```

[datapath]下的路径是文件的下载路径  
[tablelist]下配置文件下载信息，第一个是文件名，脚本会自动加上后缀unl,第二个是下载的sql 如果只下载部分字段可以select col1,col2,col3 from table1 这样子，如果下载全表 ✳和from连在一起

需要sqluldr2_linux64_10204.bin

# sql2excel 从Oracle的sql文件中提取表结构并生成对应的Excel文件
需要python2.x  
需要安装openpyxl

    python sql2excel_py2.py xxxx.sql

xxx.sql需要是utf-8格式的，放在input文件夹下  
会生成对应的xxx.xlsx在output目录下

# timesten_tool
## ttload 导入和导出timesten数据
导入导出共用一个配置文件tt.cfg,位于config目录下
```
[username]
ocs
[Password]
ocs
[Dsn]
ocs
[Tablename]
BAL|BAL_1.unl|
SUBS_ACM|SUBS_ACM_1.unl|
SUBS_ACM_DAILY|SUBS_ACM_DAILY_1.unl|
[End]
```

下载数据：  

    ./download_tt.sh

把下载的数据转换为unl格式:

    ./tt2unl.sh

清理tt数据库的表的数据：  

    ./clean_tt.sh

把unl文件导入timesten

    ./load_tt.sh

# db2_tool
## unload_data_db2 下载db2的数据为文本格式

执行：

    ./download_data_db2.sh ../config/download.cfg

配置文件：  
```
#the file for load.

[dbtype]
db2

[dbname]
bips/pass@66.93.97.38/bipdb

[max_process_count]
4

[cpuno]
4

[tablelist]
select *from CMIS.BUSINESS_DUEBILL|CMIS.BUSINESS.unl|
select *from CMIS.business_contract|CMIS.BUSINESS_CONTRACT.unl|
select *from CMIS.classify_result|CMIS.CLASSIFY_RESULT.unl|
select FK_SAACN_KEY,SA_CURR_COD,SA_CURR_IDEN,SA_LTM_TX_DT,SA_NGO_DEP_FL_TOTL,SA_ACCT_BAL,SA_INTR_COD,SA_INTR,SA_FLTR_FVR_SIGN,SA_FLTR_FVR,SA_ASES_INSTN_COD,SA_FRZ_STS,SA_BELONG_INSTN_COD,SA_PDP_CODE from CBOD.SAACNAMT|CBOD.SAACNAMT.unl|
select SA_ACCT_NO,SA_OPAC_DT,SA_CUST_NO,SA_CUST_NAME,SA_CACCT_DT,SA_ACCT_CHAR,SA_OPAC_TLR_NO,SA_CACCT_TLR_NO,SA_QPSWD,SA_CARD_NO,SA_PDP_CODE,SA_CERT_TYP,SA_CERT_ID,SA_BELONG_INSTN_COD,SA_ASES_INSTN_COD,SA_DEP_TYP from CBOD.SAACNACN where sa_dep_typ in ('01','02','05','06','54','53','98','3J')|CBOD.SAACNACN.unl|
[end]
```

[tablelist]下第一个参数是需要下载表的sql，*和from要连在一起，第二个为下载的文件名

