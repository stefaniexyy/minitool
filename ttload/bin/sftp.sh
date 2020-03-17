#!/bin/ksh
###################################################################################
# Function: ftp files from remote network sites according to 
#           corresponding configuration in cfg file.
# Note: 1. cfg file formate as followings:
#          -------------------------------       
#          [FTP1]
#          10.137.150.198
#          oracle
#          oracle
#          /opt/oracle/wuyande/rechargelog_mig/data
#          /home/liyu/liyu/sftp/data
#          bin
#          *.gz *.tar *.Z
#          [END]
#          -------------------------------
#       2. filename may be entire(basetab.unl) or some patterns(* means all files).
# Usage: ./scriptname configfile
#
####################################################################################

# global variable meaning maximum processes
pronum=5

#[20120514]global variable(0-no 1-yes) whether to gunzip files with gz format
ifgunzip=1

ftp_files ()
{
    ftptmp="${TMPDIR}ftp_${idx}.tmp"
    logtmp="${TMPDIR}ftp_${idx}.log"
    gzlisttmp="${TMPDIR}gzlist_${idx}.tmp"

    echo "" | tee -a ${logtmp}
	  echo "------------ [`date +'%Y-%m-%d %H:%M:%S`]Now,Begin to run FTP${idx} ------------" | tee -a ${logtmp}
		echo "${FILETYPE}"
		
	  echo "#!/usr/bin/expect" > transfile.sh
	  echo "" >>transfile.sh
	  echo "set timeout -1" >> transfile.sh
	  echo "spawn sftp "${USER}"@"${DESTIP} >> transfile.sh
	  
	  echo "expect {" >> transfile.sh
    echo "\"(yes/no)?\" {" >> transfile.sh
    echo "	   send \"yes\\r\"" >> transfile.sh
    echo "	   expect \"assword\"" >> transfile.sh
    echo "	   send \"${PASSWORD}\\r\" " >> transfile.sh
    echo "           }" >> transfile.sh
    echo "\"password:\" {" >> transfile.sh
    echo "	    send \"${PASSWORD}\\r\" " >> transfile.sh
    echo "	    }" >> transfile.sh
    echo "\"sftp> \" {" >> transfile.sh
    echo "	     send \"cd .\\r\"" >> transfile.sh
    echo "	    }" >> transfile.sh
    echo "}" >> transfile.sh
	  
	  #echo "expect \"Password:\"">> transfile.sh
	  #echo "send ""\""${PASSWORD}"\\\n""\"" >> transfile.sh
	  echo "expect \"sftp> \"" >> transfile.sh
	  echo "send \"lcd "$LOCALDIR"\\r\"" >> transfile.sh
	  echo "expect \"sftp> \"" >> transfile.sh
	  echo "send \"cd "$DESTDIR"\\r\"" >> transfile.sh	  
	  
		a=1
		ftypeno=`echo "$FILETYPE"|awk '{printf NF}'`
		while [ $a -le $ftypeno ]
		do
		va=`echo "$FILETYPE" | cut -d " " -f$a`
		((a += 1))
		     echo "expect \"sftp> \"" >> transfile.sh
		     echo "send \"mget $va\\r\"" >> transfile.sh
		done
	  #if [ "x${FILETYPE}" = "x*" ];then
		#		echo "expect \"sftp> \"" >> transfile.sh
    #  	echo "send \"mget "*"\\r\"" >> transfile.sh
		#else
		#		for va in ${FILETYPE[@]}
    #  		do
    #  		    echo "${FILETYPE[1]}"
    #  		    echo "expect \"sftp> \"" >> transfile.sh
    #  		    echo "send \"mget $va\\\n\"" >> transfile.sh
    #  		done
		#fi
	  echo "expect \"sftp> \"" >> transfile.sh
	  echo "send \"bye \\r\"" >> transfile.sh
	  echo "expect eof" >> transfile.sh
	  chmod 777 transfile.sh
	  expect $HOME/ttload/bin/transfile.sh
	  sleep 3
	  rm -rf $HOME/mig/bin/transfile.sh
	  echo "------------ [`date +'%Y-%m-%d %H:%M:%S`]FTP${idx} Complete ---------------------" | tee -a ${logtmp}
	  echo "" | tee -a ${logtmp}
		#20190694 xiyangyang:这一段阉割掉，并不需要自动压缩和解压的功能
	  #[20120514]add to output files with gz format for gunzip
	  #if [ "x${ifgunzip}" = "x1" ];then
		#		cd ${LOCALDIR}
		#		ls ${FILETYPE}|grep '.\.gz$' |awk '{print DIR "/" $0}' DIR=$LOCALDIR > ${gzlisttmp} 2>/dev/null
		#		cd ${WORKDIR}
		#fi
}

############################################
#[20120514]
# function:gunzip files ith gz format
############################################
gunzip_files()
{
		echo "------------ [`date +'%Y-%m-%d %H:%M:%S`]Now,Begin to gunzip files  ---------------------" | tee -a ${logfile}

		cat ${TMPDIR}/gzlist_*.tmp |sort -u |\
		while read gzfile
		do
				# more process
		    vproNow2=`ps -fu $LOGNAME |grep  "gunzip"|wc -l`
        while [ ${vproNow2} -ge ${pronum} ]
        do
            sleep $waittime
  	        vproNow2=`ps -fu $LOGNAME |grep "gunzip" |wc -l` 
	      done
	      
				echo "begin to gunzip $gzfile" | tee -a ${logfile}
				gunzip $gzfile &
		done

		wait
		rm -f ${TMPDIR}/gzlist_*.tmp
		echo "------------ [`date +'%Y-%m-%d %H:%M:%S`]gunzip Complete ---------------------" | tee -a ${logfile}
}

if [ "x$#" != "x1" ]; then
  echo "[USAGE] $0 CFGFILE"
  exit 1
fi

scriptname=`basename $0`
cd $HOME/ttload/bin
WORKDIR=`pwd`
LOGDIR="${WORKDIR}/../log/"
TMPDIR="${WORKDIR}/../temp/"

env_cfgfile="${WORKDIR}/$1"
logfile="${LOGDIR}sftp.log"
rm -f ${gzfilelist}
echo "" > ${logfile}

pronum=`expr ${pronum} + 1`
waittime=2

echo "------------ [`date +'%Y-%m-%d %H:%M:%S]`Begin to FTP --------------------------" | tee -a ${logfile}

####### get start no and end no from cfg file########
# minimum and maximum
i=`grep "^\[FTP[0-9]*\]" ${env_cfgfile} |sed 's/^\[FTP\([0-9]*\)\]/\1/'|sort -n |head -1`
ftpno=`grep "^\[FTP[0-9]*\]" ${env_cfgfile} |sed 's/^\[FTP\([0-9]*\)\]/\1/'|sort -n -r |head -1`

################### main #############################
while [ $i -le $ftpno ]
do
   	sed -n '/^\[FTP'${i}'\]/,/^\[END\]/p' ${env_cfgfile}|awk '$0!~/^\[FTP/&&$0!~/^\[END\]/{printf $0 " "}'|read DESTIP USER PASSWORD DESTDIR LOCALDIR FORMAT FILETYPE 
   	if [ "x$DESTIP" != "x" ]; then

		    # more process
		    vproNow=`ps -fu $LOGNAME |grep  "$scriptname"|grep -v grep |wc -l`
        while [ ${vproNow} -ge ${pronum} ]
        do
            sleep $waittime
  	        vproNow=`ps -fu $LOGNAME |grep "$scriptname" |grep -v grep |wc -l` 
	      done
	      idx=${i}
	      # ftp in backgroud
   	    ftp_files &
   	 
   	 #[20120511] not break because there are other ftp configurations in cfgfile
   	 #else
   	 #  break
   	 fi
   	 i=`expr $i + 1`
done
wait

ls ${TMPDIR}/ftp_*.log >/dev/null 2>&1
if [ "x$?" != "x0" ];then
    echo "[ERROR] some wrong have happened,please check"
else
    cat ${TMPDIR}/ftp_*.log >> ${logfile}
fi

rm -rf ${TMPDIR}/ftp_*.tmp ${TMPDIR}/ftp_*.log >/dev/null 2>&1
#20190694 xiyangyang:这一段阉割掉，并不需要自动压缩和解压的功能
#if [ "x${ifgunzip}" = "x1" ];then
#		gunzip_files
#fi

echo "------------ [`date +'%Y-%m-%d %H:%M:%S]`ALL Complete --------------------------" | tee -a ${logfile}

exit 0

