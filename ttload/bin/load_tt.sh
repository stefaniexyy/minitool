#!/bin/sh

workpath=`pwd`
#ttisql "uid=ocs;pwd=ocs;dsn=ocs"
cfg=$workpath'/../config/tt.cfg'
user_name_row=`sed -n '/Username/=' $cfg`
((user_name_row++))
user_name=`sed -n ''$user_name_row'p' $cfg`
passwd_row=`sed -n '/Pawwsord/=' $cfg`
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
        ttBulkCp -i -xp 1000 -notblLock -s \| -Q 1 -tsformat "YYYY-MM-DD HH24:MI:SS" DSN=$dsn $dsn.$table_name $file
    done
