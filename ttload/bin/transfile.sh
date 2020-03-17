#!/usr/bin/expect

set timeout -1
spawn sftp mig@10.120.243.4
expect {
"(yes/no)?" {
	   send "yes\r"
	   expect "assword"
	   send "Zsmart123%\r" 
           }
"password:" {
	    send "Zsmart123%\r" 
	    }
"sftp> " {
	     send "cd .\r"
	    }
}
expect "sftp> "
send "lcd /tt/ttload/data\r"
expect "sftp> "
send "cd /ccdata/mig/mig/data/output\r"
expect "sftp> "
send "mget *1.unl\r"
expect "sftp> "
send "bye \r"
expect eof
