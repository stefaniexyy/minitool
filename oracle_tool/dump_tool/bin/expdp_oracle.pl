#!/usr/bin/perl
use strict;
use warnings;
use 5.010;
use JSON;
use DBI;

die "Parameter lost, please input 1 or 2,1=imp,2=exp" unless defined($ARGV[0]);
$ARGV[0]==1?(say "imp mode on."):(say "exp mode on");

#如果第二个参数没有传递，那么就采用默认的配置文件

my $conf_file=defined($ARGV[1])?$ARGV[1]:'../../config/oracle_expimpdp.json';
die "Can not find configure file." unless -f $conf_file;
say 'Current working congfigure file is:'.$conf_file;

sub collect_exp_parameter{
    my $cfg=shift;
    my @exp_statement_arr;
    foreach (@{$cfg->{'exp'}->{'tables'}}){
        my $exp_statement='expdp '.$cfg->{'exp'}->{'username'}.'/'.$cfg->{'exp'}->{'password'}.'@'.$cfg->{'exp'}->{'connect_str'}.' tables='.$_.' Directory='.$cfg->{'exp'}->{'Directory'}.' CONTENT='.$cfg->{'exp'}->{'Content'}.' dumpfile='.$_.'.dump logfile=exp_'.$_.'.log';
        push(@exp_statement_arr,$exp_statement);
    }
    return \@exp_statement_arr;
}

sub collect_imp_parameter{
    my $cfg=shift;
    my @imp_statement_arr;
    my $statement_part=$cfg->{'imp'}->{'Remap_Schema'} eq 'Y'?(' REMAP_SCHEMA="'.$cfg->{'imp'}->{'Source_username'}.':'.$cfg->{'imp'}->{'username'}.'" '):("");
    $statement_part.='Table_exists_action='.$cfg->{'imp'}->{'Table_exists_action'}.' ';
    my $full_statement="";
    foreach (@{$cfg->{'imp'}->{'Table_Name'}}){
        if($cfg->{'imp'}->{'Remap_Tables'} eq 'Y'){
            $full_statement='impdp '.$cfg->{'imp'}->{'username'}.'/'.$cfg->{'imp'}->{'password'}.'@'.$cfg->{'imp'}->{'connect_str'}.' directory='.$cfg->{'imp'}->{'Directory'}.'  dumpfile='.$_->[2].' remap_table="'.$_->[1].':'.$_->[0].'" '.$statement_part.' logfile=imp_'.$_->[0].'.log';
        }else{
            $full_statement='impdp '.$cfg->{'imp'}->{'username'}.'/'.$cfg->{'imp'}->{'password'}.'@'.$cfg->{'imp'}->{'connect_str'}.' directory='.$cfg->{'imp'}->{'Directory'}.'  dumpfile='.$_[2].$statement_part.' logfile=imp_'.$_[0].'.log';
        }
        push(@imp_statement_arr,$full_statement);
    }
    return \@imp_statement_arr;
}
open(JSON_FILE,$conf_file)||die "error can not open $conf_file,$!\n";
my $json_text;
while(<JSON_FILE>){
    chomp();
    $json_text.=$_;
}
close(JSON_FILE);
my $json_instance=new JSON;
my $cfg=$json_instance->decode($json_text);
#@my $exp_command=collect_exp_parameter($cfg);
my @execute=$ARGV[0]==1?(@{collect_imp_parameter($cfg)}):(@{collect_exp_parameter($cfg)});
my $cycle0=scalar(@execute)-scalar(@execute)%$cfg->{'exec_proc_num'};
$cycle0=$cycle0/$cfg->{'exec_proc_num'}+1;
my($zombies,$collect,$process_num)=(0,0,0);
for(my $i=0;$i<$cfg->{'exec_proc_num'};$i++){
    my $pid=fork();
    $zombies++;
    if(!defined($pid)){
        say "Fata error, can not fork chile process,pls check system!";
        exit 0;
    }
    if($pid==0){
        #This is child process
        foreach(1..$cycle0){
            my $cycle=$_;
            my $arr_location= $zombies+($cycle-1)*$cfg->{'exec_proc_num'}-1;
            if($ARGV[0]==2){#如果是exp模式要删除文件
                last unless defined($cfg->{'exp'}->{'tables'}->[$arr_location]);
                if(-f $cfg->{'exp'}->{'Directory_Path'}.'/'.$cfg->{'exp'}->{'tables'}->[$arr_location].'.dump'){
                  unlink $cfg->{'exp'}->{'Directory_Path'}.'/'.$cfg->{'exp'}->{'tables'}->[$arr_location].'.dump'|| warn "$!\n";
                }
            }                           
            next unless defined($execute[$arr_location]);
            `$execute[$arr_location]`;
        }
    exit;
    }else{
    }
    sleep(1);
}
if($zombies>0){
    while(($collect=waitpid(-1,0))>0){
        $zombies --;
    }
}

if($ARGV[0] ==1){
    my($ip,$port,$sid)=$cfg->{'imp'}->{'connect_str'}=~/^(\d+\.\d+\.\d+\.\d+):(\d+)\/(.+)$/;
    my $oracle=DBI->connect("dbi:Oracle:host=".$ip.";sid=".$sid.";port=".$port,$cfg->{'imp'}->{'username'},$cfg->{'imp'}->{'password'}); 
    say "Check number of loaded table recored"
    foreach(@{$cfg->{'imp'}->{'Table_Name'}}){
        my $sql='select/*+parallel 8*/ count(1) from '.$_->[0];
        my $sth=$oracle->prepare($sql);
        $sth->execute()||die $sth->errstr;
        my @arr=$sth->fetchrow_array;
        printf "%-30s:%-20s\n",$_->[0],$arr[0];
        $sth->finish();
    }
    $oracle->disconnect();
}

__END__
=head1 Author

        Willy Xi

=cut