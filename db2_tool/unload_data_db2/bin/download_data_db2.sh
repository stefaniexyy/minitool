#!/bin/sh
######################################################
###Author:Willy Xi                                   #
###Describer :Donwload data from DB2                 #
###Usage:./download_data ../config/download_db2.cfg  #
######################################################
export PATH=/usr/java/jdk1.6.0_45/bin:/home/bips/bin:/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/usr/X11R6/bin:/usr/games:/usr/lib/mit/bin:/usr/lib/mit/sbin:/home/irm/java/jdk1.6.0_45/bin:/home/db2inst1/sqllib/bin:/home/db2inst1/sqllib/adm:/home/db2inst1/sqllib/misc:/home/db2inst1/sqllib/db2tss/bin:/home/bips/ubin:/home/bips/tools:/home/bips/shl:/home/bips/vsrc:/home/bips/mak

cfg_file=$1

if [ -z $cfg_file ];then
    echo 'Please input cfg file location';
    exit;
fi
dbname=`sed -n '/\[dbname\]/=' $cfg_file`
((dbname++))

dbname=`sed -n ""$dbname"p" $cfg_file`
db_username=${dbname%%/*}
db_passwd=${dbname#*/}
db_passwd=${db_passwd%%@*}
db_passwd=${db_passwd%%@*}
db_ip0=${dbname#*@}
db_ip=${db_ip0%/*}
db_db=${db_ip0#*/}

row_begin=`sed -n '/\[tablelist\]/=' $cfg_file`
row_end=`sed -n '/\[end\]/=' $cfg_file`
((row_begin++))
((row_end--))
j=0
echo $row_begin
echo $row_end



for((i=$row_begin;i<=$row_end;i++));
    do
        row=`sed -n "$i"p $cfg_file`
        table=`echo $row|cut -d \| -f 1`
        save_file='../data/'`echo $row|cut -d \| -f 2`
        EXEC[$j]='db2 export to "'$save_file'" of del modified by nochardel codepage=1208 COLDEL\| "'$table'"'
        ((j++))
done
#db2 connect to $db_db user $db_username using $db_passwd
db2 connect to $db_db user $db_username using $db_passwd
trap "exec 1000>&-;exec 1000<&-;exit 0" 2
mkfifo testinfo
exec 1000<>testinfo
rm -rf testinfo
for((n=1;n<=4;n++))
do  
    echo>&1000
done
echo [ `date +%Y-%m-%d\ %H:%M:%S`]Process Begin.....
for((k=0;k<j;k++))
    do
    read -u 1000
    {
        eval ${EXEC[$k]}
        sleep 1
        echo >&1000

    }
done
wait
echo [ `date +%Y-%m-%d\ %H:%M:%S`]All complete!
exec 1000>&-
exec 1000<&-


