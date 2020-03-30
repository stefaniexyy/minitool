#!/bin/sh


#$1 inputfile
cat $1|tr -d 'NULL'>$1'.tmp'
rm $1
delete_line=`sed -n '3p'  $1.tmp|cut -d , -f 2|tr -d [:blank:][:alpha:]`
delete_line=`expr $delete_line + 7`
sed -i  "1,${delete_line}d"  $1'.tmp'
sed -i '$d'  $1'.tmp'
awk -F \| '{print $0"|"}'   $1'.tmp'>$1
rm $1'.tmp'