#!/bin/sh

#################
#Author:Willy Xi
#20200325
##################


downloadtt(){
  #$1:dsn $2tablename $3location
  ##############################
  #Format the unl file timesten download text file contain table structure ,need delete
  ##############################
    ttBulkCp -o  -s \| -Q 1  -tsformat "YYYY-MM-DD HH24:MI:SS"  -nullFormat "empty"  DSN=$1 $1.$2 $3/$2.unl.tmp
    delete_line=`sed -n '3p' $3/$2.unl.tmp|cut -d , -f 2|tr -d [:blank:][:alpha:]`
    delete_line=`expr $delete_line + 7`
    sed -i  "1,${delete_line}d" $3/$2.unl.tmp
    sed -i '$d' $3/$2.unl.tmp
    awk -F \| '{print $0"|"}'  $3/$2.unl.tmp> $3/$2.unl
    rm $3/$2.unl.tmp
}
workpath=`pwd`
#ttisql "uid=ocs;pwd=ocs;dsn=ocs"
cfg=$workpath'/../config/tt.cfg'
user_name_row=`sed -n '/Username/=' $cfg`
((user_name_row++))
user_name=`sed -n ''$user_name_row'p' $cfg`
passwd_row=`sed -n '/Password/=' $cfg`
((passwd_row++))
passwd=`sed -n ''$passwd_row'p' $cfg`
dsn_row=`sed -n '/Dsn/=' $cfg`
((dsn_row++))
dsn=`sed -n ''$dsn_row'p' $cfg`
start_row=`sed -n '/Tablename/=' $cfg`
((start_row++))
end_row=`sed -n '/End/=' $cfg`
((end_row--))


for i in `sed -n ""$start_row","$end_row"p" $cfg` 
    do
        table_name=`echo $i|awk -F "|" '{print $1}'`
        file_name=`echo $i|awk -F "|" '{print $2}'`
        file=$workpath'/../data/'$file_name
        echo 'Begin to dowload '$table_name
        downloadtt $dsn $table_name $workpath'/../data/'
        echo 'Finish to dowload '$table_name
    done

