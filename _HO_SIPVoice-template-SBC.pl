#!/usr/bin/perl
#
# SBC Template generator for SIP Voice
# Supports single sites and clustered PBXs
# Standard configuration can be amended using Net-Net Central if needed
#
# Written by Marco Fais <mfais@eircom.ie>
# Modified on 07/11/2016
# Added Hosted Office provisioning
#

use strict;
use warnings;

use Term::ReadLine;
use Mail::Sender;
use Data::Dumper;

my $VIM;
my $VLANID;
my $ECID;
my $LWRCASE_ECID;
my $NAME;

sub print_CLD();
sub print_SRL();
sub ask_questions();
sub send_mail();
sub rollback_CLD();
sub rollback_SRL();
sub print_CLD_HO();
sub print_SRL_HO();
sub rollback_CLD_HO();
sub rollback_SRL_HO();

my $CLD_IP = "159.134.113.212";
my $CLD_IP_HO = "159.134.113.216";
my $CLD_PRIMARY_IP = "159.134.113.213";
my $CLD_SECONDARY_IP = "159.134.113.214";
my $CLD_GATEWAY = "159.134.113.211";
my $SRL_IP = "159.134.113.84";
my $SRL_IP_HO = "159.134.113.88";
my $SRL_PRIMARY_IP = "159.134.113.85";
my $SRL_SECONDARY_IP = "159.134.113.86";
my $SRL_GATEWAY = "159.134.113.83";
my $NETMASK = "255.255.255.240";

my $SMTP_SERVER = "10.144.130.196";
my $SMTP_FROM = 'acmetemplate@ngv.eircom.net';

my $LOGFILE = "$ENV{HOME}/.new-SBC-template-generator.log";

my @mail_addresses = (
'SODuibhginn@eircom.ie',
'LKelly@eircom.ie',
'greglawless@eircom.ie',
'Carrollm@eircom.ie',
'SMonaghan@eircom.ie',
'PFogarty@eircom.ie',
'mfais@eircom.ie'
);

my $answer;
my $cld_template;
my $srl_template;

my $cld_rollback;
my $srl_rollback;

my @sa_list;

my $full_provisioning;
my $ho_provisioning;
my $ptype;

open (my $LOGFH, ">>:crlf", $LOGFILE) or die "Cannot open $LOGFILE: $!";

print "======= SBC template generator =======\n";
do {
	ask_questions();
	print "\n==== VALUES ====\n";
	print << "EOF";
ECID: $ECID
VIM: $VIM
VLAN ID: $VLANID
ENTERPRISE NAME: $NAME
EOF
my $count = 0;
foreach (@sa_list) {
	print "SESSION AGENT ".($count + 1)." IP ADDRESS: ".$sa_list[$count]."\n";
	$count++;
}

print "================\n";
	do {
		print "Happy with the values? [y/n] ";
		$answer = <STDIN>;
		chomp $answer;
	} while ($answer ne 'y' and $answer ne 'n');
} while ($answer ne 'y');
	
if ($ho_provisioning) {
	$ptype="HO";
} elsif ($full_provisioning) {
	$ptype="FULL";
} else {
	$ptype="PARTIAL";
}

print "\n";
print "============= CLD config =============\n";
if (not $ho_provisioning) {
	print_CLD();
	rollback_CLD();
} else {
	print_CLD_HO();
	rollback_CLD_HO();
}
print "======================================\n\n\n";

print "============= SRL config =============\n";
if (not $ho_provisioning) {
	print_SRL();
	rollback_SRL();
} else {
	print_SRL_HO();
	rollback_SRL_HO();
}
print "======================================\n\n\n";

#my($currentday, $currentmonth, $currentyear)=(localtime)[3,4,5];
my @cdate = localtime;
#printf $LOGFH "\n%02d/%02d/%02d - %s", $currentday, $currentmonth+1, $currentyear+1900, "\nGenerated template for $ECID - $VIM - VLAN $VLANID";


printf $LOGFH "%02d/%02d/%02d %02d:%02d:%02d - %s(%s)\n", $cdate[3], $cdate[4]+1, $cdate[5]+1900, 
		$cdate[2], $cdate[1], $cdate[1], "Generated template for $ECID - $VIM - VLAN $VLANID - $NAME", $ptype;

do {
	print "Do you want to send the templates via e-mail? [y/n] ";
	$answer = <STDIN>;
	chomp $answer;
} while ($answer ne 'y' and $answer ne 'n');

send_mail() if $answer eq 'y';

unlink "$ECID-$VIM-CLD-$ptype.txt" or print "Error deleting $ECID-$VIM-CLD-$ptype.txt: $!\n";
unlink "$ECID-$VIM-SRL-$ptype.txt" or print "Error deleting $ECID-$VIM-SRL-$ptype.txt: $!\n";
unlink "$ECID-$VIM-CLD-rollback-$ptype.txt" or print "Error deleting $ECID-$VIM-CLD-rollback-$ptype.txt: $!\n";
unlink "$ECID-$VIM-SRL-rollback-$ptype.txt" or print "Error deleting $ECID-$VIM-SRL-rollback-$ptype.txt: $!\n";

close $LOGFH;


sub print_CLD () {

$cld_template = << "EOF";
conf ter
system 
network-interface 
name M00
sub-port-id $VLANID
description "$NAME $ECID.ngv.eircom.net"
ip-address $CLD_IP
pri-utility-addr $CLD_PRIMARY_IP
sec-utility-addr $CLD_SECONDARY_IP
netmask $NETMASK
gateway $CLD_GATEWAY
done
exit
exit

media-manager 
realm-config 
identifier $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net"
network-interfaces M00:$VLANID.4
mm-in-realm enabled
media-policy rtpsiptoscodes
out-manipulationid enterprise-fixup
manipulation-string ngv.eircom.net
class-profile sipqosmarking
access-control-trust-level high
trunk-context $LWRCASE_ECID.ngv.eircom.net
codec-policy g722_g711_g729_amrwb
invalid-signal-threshold 5
maximum-signal-threshold 100
untrusted-signal-threshold 10
deny-period 60
done
exit
exit

session-router 
sip-interface 
realm-id $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net"
state enabled
sip-ports 
address $CLD_IP
port 5060
transport-protocol UDP
allow-anonymous agents-only
done
address $CLD_IP
port 5060
transport-protocol TCP
allow-anonymous agents-only
done
exit
proxy-mode Proxy
redirect-action Proxy
nat-traversal always
nat-interval 60
tcp-nat-interval 60
registration-caching enabled
min-reg-expire 1800
registration-interval 1800
route-to-registrar enabled
options +preserve-user-info
options +strip-route-headers
options +via-header-transparency
trust-mode agents-only
max-nat-interval 3600
sip-ims-feature enabled
network-id ngv.eircom.net
done
exit
exit

media-manager 
steering-pool 
ip-address $CLD_IP
start-port 30000
end-port 49999
realm-id $ECID.ngv.eircom.net
network-interface M00:$VLANID.4
done
exit
exit

session-router 
local-policy 
from-address *
to-address *
source-realm $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net"
state enabled
next-hop sag:core-ICSCF
realm Core_Realm_Non_Reg
terminate-recursion disabled
app-protocol SIP
done
exit
exit
exit

EOF

if (@sa_list > 0) {
	my $count = 0;
	my $sa_cld_template;
	$sa_cld_template = << "EOF";
conf ter
session-router
EOF
	if ($full_provisioning) {
		$cld_template = $cld_template.$sa_cld_template;
	} else {
		$cld_template = $sa_cld_template;
	}

	foreach (@sa_list) {
		$count++;
		$sa_cld_template = << "EOF";
session-agent
hostname $ECID-$VIM-SA$count
ip-address $_
port 5060
state enabled
app-protocol SIP
transport-method UDP
realm-id $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net SA$count"
proxy-mode Proxy
redirect-action Proxy
trust-me enabled
in-manipulationid $ECID\_$VIM\_SM$count
trunk-group $VIM-TG$count
stop-recurse 401,407
max-register-sustain-rate 60
register-burst-window 1
sustain-rate-window 10
done
exit
sip-manipulation 
name $ECID\_$VIM\_SM$count
description "$NAME $ECID.ngv.eircom.net"
header-rules 
name enterprise_fixup
header-name to
action sip-manip
msg-type any
new-value TGRP_Enterprise_Common
done
name pai_fixup
header-name to
action sip-manip 
msg-type request
new-value PAI_Fixup
done
name add_psi_prefix
header-name to 
action sip-manip
msg-type request
new-value add_psi_prefix_Retail
done
exit
done
exit
EOF

	$cld_template = $cld_template.$sa_cld_template;

	}

	$sa_cld_template = << "EOF";
exit
exit
EOF

	$cld_template = $cld_template.$sa_cld_template;
}


#print $cld_template;
open (my $fh, ">:crlf", "$ECID-$VIM-CLD-$ptype.txt") or die "Cannot open $ECID-$VIM-CLD-$ptype.txt: $!";
print $fh $cld_template;
close $fh;
}

sub print_SRL () {

$srl_template = << "EOF";
conf ter
system 
network-interface 
name M00
sub-port-id $VLANID
description "$NAME $ECID.ngv.eircom.net"
ip-address $SRL_IP
pri-utility-addr $SRL_PRIMARY_IP
sec-utility-addr $SRL_SECONDARY_IP
netmask $NETMASK
gateway $SRL_GATEWAY
done
exit
exit

media-manager 
realm-config 
identifier $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net"
network-interfaces M00:$VLANID.4
mm-in-realm enabled
media-policy rtpsiptoscodes
out-manipulationid enterprise-fixup
manipulation-string ngv.eircom.net
class-profile sipqosmarking
access-control-trust-level high
trunk-context $LWRCASE_ECID.ngv.eircom.net
codec-policy g722_g711_g729_amrwb
invalid-signal-threshold 5
maximum-signal-threshold 100
untrusted-signal-threshold 10
deny-period 60
done
exit
exit

session-router 
sip-interface 
realm-id $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net"
state enabled
sip-ports 
address $SRL_IP
port 5060
transport-protocol UDP
allow-anonymous agents-only
done
address $SRL_IP
port 5060
transport-protocol TCP
allow-anonymous agents-only
done
exit
proxy-mode Proxy
redirect-action Proxy
nat-traversal always
nat-interval 60
tcp-nat-interval 60
registration-caching enabled
min-reg-expire 1800
registration-interval 1800
route-to-registrar enabled
options +preserve-user-info
options +strip-route-headers
options +via-header-transparency
trust-mode agents-only
max-nat-interval 3600
sip-ims-feature enabled
network-id ngv.eircom.net
done
exit
exit

media-manager 
steering-pool 
ip-address $SRL_IP
start-port 30000
end-port 49999
realm-id $ECID.ngv.eircom.net
network-interface M00:$VLANID.4
done
exit
exit

session-router 
local-policy 
from-address *
to-address *
source-realm $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net"
state enabled
next-hop sag:core-ICSCF
realm Core_Realm_Non_Reg
terminate-recursion disabled
app-protocol SIP
done
exit
exit
exit

EOF

if (@sa_list > 0) {
	my $count = 0;
	my $sa_srl_template;
	$sa_srl_template = << "EOF";
conf ter
session-router
EOF
	if ($full_provisioning) {
		$srl_template = $srl_template.$sa_srl_template;
	} else {
		$srl_template = $sa_srl_template;
	}

	foreach (@sa_list) {
		$count++;
		$sa_srl_template = << "EOF";
session-agent
hostname $ECID-$VIM-SA$count
ip-address $_
port 5060
state enabled
app-protocol SIP
transport-method UDP
realm-id $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net SA$count"
proxy-mode Proxy
redirect-action Proxy
trust-me enabled
in-manipulationid $ECID\_$VIM\_SM$count
trunk-group $VIM-TG$count
stop-recurse 401,407
max-register-sustain-rate 60
register-burst-window 1
sustain-rate-window 10
done
exit
sip-manipulation 
name $ECID\_$VIM\_SM$count
description "$NAME $ECID.ngv.eircom.net"
header-rules 
name enterprise_fixup
header-name to
action sip-manip
msg-type any
new-value TGRP_Enterprise_Common
done
name pai_fixup
header-name to
action sip-manip 
msg-type request
new-value PAI_Fixup
done
name add_psi_prefix
header-name to 
action sip-manip
msg-type request
new-value add_psi_prefix_Retail
done
exit
done
exit
EOF

	$srl_template = $srl_template.$sa_srl_template;

	}

	$sa_srl_template = << "EOF";
exit
exit
EOF

	$srl_template = $srl_template.$sa_srl_template;
}


#print $srl_template;
open (my $fh, ">:crlf", "$ECID-$VIM-SRL-$ptype.txt") or die "Cannot open $ECID-$VIM-SRL-$ptype.txt: $!";
print $fh $srl_template;
close $fh;
}


sub ask_questions () {
	my $term = Term::ReadLine->new('SBC Template generator');
	my $OUT = $term-> OUT || \*STDOUT;
	my $res;
	do {
		$res = $term->readline("\nEnter ICID (example: X1234): ");
		warn $@ if $@;
		$ECID = $res;
		$LWRCASE_ECID = lc $res;
		print "WARNING: ICID ($ECID) not in correct format (should be Xnnnn)!\n" if (not $ECID =~ /^X\d+$/);
	} while ($ECID =~ /^\d/);
	do {
		$res = $term->readline("Enter VLAN ID [500-1499] (example: 600): ");
		warn $@ if $@;
		$VLANID = $res;
	} while ($VLANID !~ /^\d+$/ or $VLANID < 500 or $VLANID >= 1500);
	do {
		$res = $term->readline("Enter VIM (example: VIM8812345): ");
		warn $@ if $@;
		$VIM = $res;
	} while ($VIM !~ /^VIM\d+$/);
	$res = $term->readline("Enteprise NAME (example: Irish Distillers):" );
	warn $@ if $@;
	$NAME = $res;

	do {
                print "\n\nHosted Office provisioning (select n for SIP Trunking)? [y/n] ";
                $answer = <STDIN>;
                chomp $answer;
        } while ($answer ne 'y' and $answer ne 'n');

	if ($answer eq 'y') {
		print "Hosted Office provisioning selected...\n";
		$ho_provisioning = 1;
	} else {
		print "SIP Trunking provisioning selected...\n";
		$ho_provisioning = 0;
	}

	if ($ho_provisioning) {
#		my $SFCOREIPLO;
#		do {
#			$res = $term->readline("Select the IP address to be used for the static flows [101-126]: ");
#			warn $@ if $@;
#			$SFCOREIPLO = $res;
#		} while ($SFCOREIPLO !~ /^\d+$/ or $SFCOREIPLO < 101 or $SFCOREIPLO >= 126);
	}

	if (not $ho_provisioning) {
		do {
			print "\n\nDo you want to configure the session-agents? [y/n] ";
			$answer = <STDIN>;
			chomp $answer;
		} while ($answer ne 'y' and $answer ne 'n');

		if ($answer eq 'y') {

			do {
				print "Is it a clustered PBX? (more than one session agent) [y/n] ";
				$answer = <STDIN>;
				chomp $answer;
			} while ($answer ne 'y' and $answer ne 'n');

			my $sa_address;
			if ($answer eq 'y') {

				my $sa_number;
				do {
					$res = $term->readline("How many session-agents do you want to configure? (max 10) ");
					warn $@ if $@;
					$sa_number = $res;
				} while ($sa_number < 1 or $sa_number > 10);

				for (my $sa_count = 0; $sa_count < $sa_number; $sa_count++) {

					do {
						my $prompt = "Insert IP address for SA number " . ($sa_count + 1) .": ";
						$res = $term->readline($prompt);
						warn $@ if $@;
						$sa_address = $res;
					} while (not $sa_address =~ /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/);
					$sa_list[$sa_count] = $sa_address;
#print "Assigning address $sa_address to sa_list[$sa_count]\n";
				}


			} else {

				do {
					my $prompt = "Insert IP address for SA: ";
					$res = $term->readline($prompt);
					warn $@ if $@;
					$sa_address = $res;
				} while (not $sa_address =~ /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/);
				$sa_list[0] = $sa_address;
			}
		}

		do {
			print "\n\nFull provisioning (select n for site only)? [y/n] ";
			$answer = <STDIN>;
			chomp $answer;
		} while ($answer ne 'y' and $answer ne 'n');

		if ($answer eq 'y') {
			print "Full provisioning selected...\n";
			$full_provisioning = 1;
		} else {
			print "Site only provisioning selected...\n";
			$full_provisioning = 0;
		}
	}
}


sub send_mail () {

print "Select the e-mail address from the list: \n";
my $count = 1;
my $address;
foreach (@mail_addresses) {
	$address = $_;
	printf "%d: %s\n",$count++, $address;
}

my $sel_addr;
my $mail_addresses_count = @mail_addresses;
do { 
	$sel_addr = -1;
	print "\nSelect the address: ";
	$sel_addr = <STDIN>;
	chomp $sel_addr;
} while ($sel_addr < 1 or $sel_addr > $mail_addresses_count);


my $mail_address = $mail_addresses[$sel_addr - 1];
print "Selected address: $mail_address -- Sending mail...\n";

my $sender = new Mail::Sender {smtp => $SMTP_SERVER, from => $SMTP_FROM};
die "Error in mailing : $Mail::Sender::Error\n" unless ref $sender;

$sender->OpenMultipart({to => $mail_address,
                         subject => "SBC Templates for $NAME - $VIM - $ptype provisioning"});
$sender->Body;
$sender->SendEnc(<<"*END*");
MAIL GENERATED FROM THE SBC TEMPLATE GENERATOR

This mail contains the template configurations for customer $NAME - $VIM - $ptype


Customer details:

NAME: $NAME
ICID: $ECID
VIM: $VIM
VLAN ID: $VLANID
IP addresses for session agents: @sa_list

TYPE OF PROVISIONING: $ptype

There are two files attached to this mail:

1) $ECID-$VIM-CLD-$ptype.txt --> template file for the CLD SBC
2) $ECID-$VIM-SRL-$ptype.txt --> template file for the SRL SBC

In order to implement the configuration in each SBC, please use the SBC-config-loader.pl script and then:

1) Copy and paste the template into the SBC CLI
2) Look at the output to determine if there have been any errors in the implementation

Please note the implementation might fail if the configuration for a specific customer has already been
implemented in the SBC.

For FULL PROVISIONING, make sure no configuration for the customer $NAME is currently implemented BEFORE
copying and pasting the one attached to this mail.

For PARTIAL PROVISIONING, make sure the configuration for the customer has already been completed AND the 
VIM circuit ID for this site is DIFFERENT from the ones used for previous sites. --> THIS IS VERY 
IMPORTANT AS OTHERWISE EXISTING CUSTOMER DATA WILL BE OVERWRITTEN <--


For any issues with the template, please contact Voice Services:
Liam O'Toole
Marco Fais
Gerry Flaherty


*END*
$sender->Attach(
 {description => 'CLD template',
   ctype => 'text/plain',
   encoding => 'Base64',
   disposition => "attachment; filename=\"$ECID-$VIM-CLD-$ptype.txt\"; type=\"Text file\"",
   file => "$ECID-$VIM-CLD-$ptype.txt"
  });
die "Error in mailing : $Mail::Sender::Error\n" unless ref $sender;

$sender->Attach(
 {description => 'SRL template',
   ctype => 'text/plain',
   encoding => 'Base64',
   disposition => "attachment; filename=\"$ECID-$VIM-SRL-$ptype.txt\"; type=\"Text file\"",
   file => "$ECID-$VIM-SRL-$ptype.txt"
  });
die "Error in mailing : $Mail::Sender::Error\n" unless ref $sender;

$sender->Attach(
 {description => 'CLD rollback',
   ctype => 'text/plain',
   encoding => 'Base64',
   disposition => "attachment; filename=\"$ECID-$VIM-CLD-rollback-$ptype.txt\"; type=\"Text file\"",
   file => "$ECID-$VIM-CLD-rollback-$ptype.txt"
  });
die "Error in mailing : $Mail::Sender::Error\n" unless ref $sender;

$sender->Attach(
 {description => 'SRL rollback',
   ctype => 'text/plain',
   encoding => 'Base64',
   disposition => "attachment; filename=\"$ECID-$VIM-SRL-rollback-$ptype.txt\"; type=\"Text file\"",
   file => "$ECID-$VIM-SRL-rollback-$ptype.txt"
  });
die "Error in mailing : $Mail::Sender::Error\n" unless ref $sender;

$sender->Close;
}

sub rollback_CLD () {
my $sa_cld_rollback;

$cld_rollback = << "EOF";
conf ter
session-router
local-policy
no
$ECID.ngv.eircom.net
*
*
1
exit

sip-interface
no
$ECID.ngv.eircom.net
1
exit

EOF


$cld_rollback = "conf ter\nsession-router\n" if not $full_provisioning;

if (@sa_list > 0) {
        my $count = 0;
        my $sa_cld_rollback;

       foreach (@sa_list) {
                $count++;
                $sa_cld_rollback = << "EOF";
session-agent
no
$ECID-$VIM-SA$count
1
exit

sip-manipulation
no
$ECID\_$VIM\_SM$count
1
exit
EOF

	$cld_rollback = $cld_rollback.$sa_cld_rollback;
	}
}

if ($full_provisioning) {
	my $pre_media_rollback = $cld_rollback;
	$cld_rollback = << "EOF";
exit

media-manager
realm-config
no
$ECID.ngv.eircom.net
1
exit
steering-pool
no
$CLD_IP
30000
$ECID.ngv.eircom.net
1
exit
exit

system
network-interface
no
M00:$VLANID
1
exit
exit
exit

EOF

	$cld_rollback = $pre_media_rollback.$cld_rollback;
}

open (my $fh, ">:crlf", "$ECID-$VIM-CLD-rollback-$ptype.txt") or die "Cannot open $ECID-$VIM-CLD-rollback-$ptype.txt: $!";
print $fh $cld_rollback;
close $fh;
}

sub rollback_SRL () {
my $sa_srl_rollback;

$srl_rollback = << "EOF";
conf ter
session-router
local-policy
no
$ECID.ngv.eircom.net
*
*
1
exit

sip-interface
no
$ECID.ngv.eircom.net
1
exit

EOF

$srl_rollback = "conf ter\nsession-router\n" if not $full_provisioning;

if (@sa_list > 0) {
        my $count = 0;
        my $sa_srl_rollback;


       foreach (@sa_list) {
                $count++;
                $sa_srl_rollback = << "EOF";
session-agent
no
$ECID-$VIM-SA$count
1
exit

sip-manipulation
no
$ECID\_$VIM\_SM$count
1
exit
EOF

	$srl_rollback = $srl_rollback.$sa_srl_rollback;
	}

}

if ($full_provisioning) {
	my $pre_media_rollback = $srl_rollback;
	$srl_rollback = << "EOF";
exit

media-manager
realm-config
no
$ECID.ngv.eircom.net
1
exit
steering-pool
no
$SRL_IP
30000
$ECID.ngv.eircom.net
1
exit
exit

system
network-interface
no
M00:$VLANID
1
exit
exit
exit

EOF

	$srl_rollback = $pre_media_rollback.$srl_rollback;
}

open (my $fh, ">:crlf", "$ECID-$VIM-SRL-rollback-$ptype.txt") or die "Cannot open $ECID-$VIM-SRL-rollback-$ptype.txt: $!";
print $fh $srl_rollback;
close $fh;
}

sub print_CLD_HO () {

$cld_template = << "EOF";
conf ter
system 
network-interface 
name M00
sub-port-id $VLANID
description "$NAME $ECID-HO.ngv.eircom.net"
ip-address $CLD_IP
pri-utility-addr $CLD_PRIMARY_IP
sec-utility-addr $CLD_SECONDARY_IP
netmask $NETMASK
gateway $CLD_GATEWAY
done
exit
exit

media-manager 
realm-config 
identifier $ECID-HO.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net"
network-interfaces M00:$VLANID.4
mm-in-realm enabled
mm-same-ip disabled
media-policy rtpsiptoscodes
in-manipulationid HO_Internet_in
out-manipulationid HO_Internet_out
manipulation-string ngv.eircom.net
class-profile sipqosmarking
access-control-trust-level low
codec-policy g722_g711_g729_amrwb
invalid-signal-threshold 30
maximum-signal-threshold 160
untrusted-signal-threshold 30
deny-period 60
done
exit
exit

session-router 
sip-interface 
realm-id $ECID-HO.ngv.eircom.net
description "$NAME $ECID-HO.ngv.eircom.net"
state enabled
sip-ports 
address $CLD_IP_HO
port 5060
transport-protocol UDP
allow-anonymous registered
done
address $CLD_IP_HO
port 5060
transport-protocol TCP
allow-anonymous registered
done
exit
proxy-mode Proxy
redirect-action Proxy
nat-traversal always
nat-interval 60
tcp-nat-interval 720
registration-caching enabled
min-reg-expire 900
registration-interval 900
route-to-registrar enabled
secured-network enabled
options +reg-local-expires
options +strip-route-headers
options +via-header-transparency
trust-mode registered
max-nat-interval 3600
sip-ims-feature enabled
network-id ngv.eircom.net
tcp-keepalive enabled
done
exit
exit

media-manager 
steering-pool 
ip-address $CLD_IP_HO
start-port 30000
end-port 49999
realm-id $ECID-HO.ngv.eircom.net
network-interface M00:$VLANID.4
done
exit
exit

session-router 
local-policy 
from-address *
to-address *
source-realm $ECID-HO.ngv.eircom.net
description "$NAME $ECID-HO.ngv.eircom.net"
state enabled
next-hop sag:core-ICSCF
realm Core_Realm_Reg
terminate-recursion disabled
app-protocol SIP
done
exit
exit
exit

EOF



#print $cld_template;
open (my $fh, ">:crlf", "$ECID-$VIM-CLD-$ptype.txt") or die "Cannot open $ECID-$VIM-CLD-$ptype.txt: $!";
print $fh $cld_template;
close $fh;
}

sub rollback_CLD_HO () {
my $sa_cld_rollback;

$cld_rollback = << "EOF";
conf ter
session-router
local-policy
no
$ECID.ngv.eircom.net
*
*
1
exit

sip-interface
no
$ECID.ngv.eircom.net
1
exit

EOF


$cld_rollback = "conf ter\nsession-router\n" if not $full_provisioning;

if (@sa_list > 0) {
        my $count = 0;
        my $sa_cld_rollback;

       foreach (@sa_list) {
                $count++;
                $sa_cld_rollback = << "EOF";
session-agent
no
$ECID-$VIM-SA$count
1
exit

sip-manipulation
no
$ECID\_$VIM\_SM$count
1
exit
EOF

	$cld_rollback = $cld_rollback.$sa_cld_rollback;
	}
}

if ($full_provisioning) {
	my $pre_media_rollback = $cld_rollback;
	$cld_rollback = << "EOF";
exit

media-manager
realm-config
no
$ECID.ngv.eircom.net
1
exit
steering-pool
no
$CLD_IP
30000
$ECID.ngv.eircom.net
1
exit
exit

system
network-interface
no
M00:$VLANID
1
exit
exit
exit

EOF

	$cld_rollback = $pre_media_rollback.$cld_rollback;
}

open (my $fh, ">:crlf", "$ECID-$VIM-CLD-rollback-$ptype.txt") or die "Cannot open $ECID-$VIM-CLD-rollback-$ptype.txt: $!";
print $fh $cld_rollback;
close $fh;
}

sub print_SRL_HO () {

$srl_template = << "EOF";
conf ter
system 
network-interface 
name M00
sub-port-id $VLANID
description "$NAME $ECID.ngv.eircom.net"
ip-address $SRL_IP
pri-utility-addr $SRL_PRIMARY_IP
sec-utility-addr $SRL_SECONDARY_IP
netmask $NETMASK
gateway $SRL_GATEWAY
done
exit
exit

media-manager 
realm-config 
identifier $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net"
network-interfaces M00:$VLANID.4
mm-in-realm enabled
media-policy rtpsiptoscodes
out-manipulationid enterprise-fixup
manipulation-string ngv.eircom.net
class-profile sipqosmarking
access-control-trust-level high
trunk-context $LWRCASE_ECID.ngv.eircom.net
codec-policy g722_g711_g729_amrwb
invalid-signal-threshold 5
maximum-signal-threshold 100
untrusted-signal-threshold 10
deny-period 60
done
exit
exit

session-router 
sip-interface 
realm-id $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net"
state enabled
sip-ports 
address $SRL_IP
port 5060
transport-protocol UDP
allow-anonymous agents-only
done
address $SRL_IP
port 5060
transport-protocol TCP
allow-anonymous agents-only
done
exit
proxy-mode Proxy
redirect-action Proxy
nat-traversal always
nat-interval 60
tcp-nat-interval 60
registration-caching enabled
min-reg-expire 1800
registration-interval 1800
route-to-registrar enabled
options +preserve-user-info
options +strip-route-headers
options +via-header-transparency
trust-mode agents-only
max-nat-interval 3600
sip-ims-feature enabled
network-id ngv.eircom.net
done
exit
exit

media-manager 
steering-pool 
ip-address $SRL_IP
start-port 30000
end-port 49999
realm-id $ECID.ngv.eircom.net
network-interface M00:$VLANID.4
done
exit
exit

session-router 
local-policy 
from-address *
to-address *
source-realm $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net"
state enabled
next-hop sag:core-ICSCF
realm Core_Realm_Non_Reg
terminate-recursion disabled
app-protocol SIP
done
exit
exit
exit

EOF

if (@sa_list > 0) {
	my $count = 0;
	my $sa_srl_template;
	$sa_srl_template = << "EOF";
conf ter
session-router
EOF
	if ($full_provisioning) {
		$srl_template = $srl_template.$sa_srl_template;
	} else {
		$srl_template = $sa_srl_template;
	}

	foreach (@sa_list) {
		$count++;
		$sa_srl_template = << "EOF";
session-agent
hostname $ECID-$VIM-SA$count
ip-address $_
port 5060
state enabled
app-protocol SIP
transport-method UDP
realm-id $ECID.ngv.eircom.net
description "$NAME $ECID.ngv.eircom.net SA$count"
proxy-mode Proxy
redirect-action Proxy
trust-me enabled
in-manipulationid $ECID\_$VIM\_SM$count
trunk-group $VIM-TG$count
stop-recurse 401,407
max-register-sustain-rate 60
register-burst-window 1
sustain-rate-window 10
done
exit
sip-manipulation 
name $ECID\_$VIM\_SM$count
description "$NAME $ECID.ngv.eircom.net"
header-rules 
name enterprise_fixup
header-name to
action sip-manip
msg-type any
new-value TGRP_Enterprise_Common
done
name pai_fixup
header-name to
action sip-manip 
msg-type request
new-value PAI_Fixup
done
name add_psi_prefix
header-name to 
action sip-manip
msg-type request
new-value add_psi_prefix_Retail
done
exit
done
exit
EOF

	$srl_template = $srl_template.$sa_srl_template;

	}

	$sa_srl_template = << "EOF";
exit
exit
EOF

	$srl_template = $srl_template.$sa_srl_template;
}


#print $srl_template;
open (my $fh, ">:crlf", "$ECID-$VIM-SRL-$ptype.txt") or die "Cannot open $ECID-$VIM-SRL-$ptype.txt: $!";
print $fh $srl_template;
close $fh;
}

sub rollback_SRL_HO () {
my $sa_srl_rollback;

$srl_rollback = << "EOF";
conf ter
session-router
local-policy
no
$ECID.ngv.eircom.net
*
*
1
exit

sip-interface
no
$ECID.ngv.eircom.net
1
exit

EOF

$srl_rollback = "conf ter\nsession-router\n" if not $full_provisioning;

if (@sa_list > 0) {
        my $count = 0;
        my $sa_srl_rollback;


       foreach (@sa_list) {
                $count++;
                $sa_srl_rollback = << "EOF";
session-agent
no
$ECID-$VIM-SA$count
1
exit

sip-manipulation
no
$ECID\_$VIM\_SM$count
1
exit
EOF

	$srl_rollback = $srl_rollback.$sa_srl_rollback;
	}

}

if ($full_provisioning) {
	my $pre_media_rollback = $srl_rollback;
	$srl_rollback = << "EOF";
exit

media-manager
realm-config
no
$ECID.ngv.eircom.net
1
exit
steering-pool
no
$SRL_IP
30000
$ECID.ngv.eircom.net
1
exit
exit

system
network-interface
no
M00:$VLANID
1
exit
exit
exit

EOF

	$srl_rollback = $pre_media_rollback.$srl_rollback;
}

open (my $fh, ">:crlf", "$ECID-$VIM-SRL-rollback-$ptype.txt") or die "Cannot open $ECID-$VIM-SRL-rollback-$ptype.txt: $!";
print $fh $srl_rollback;
close $fh;
}


