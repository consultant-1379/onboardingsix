#!/bin/bash

function check_file_exists {
FILE=$1
MESSAGE="PROBLEM: File ${FILE} does not exist, exiting"
if [ ! -r ${FILE} ]; then
        if [ $# -eq 2 ]; then
          MESSAGE=$2
        fi
        echo $MESSAGE
        exit 1
else
   echo "File ${FILE} exists, continuing"
fi
}

function check_directory_exists {
DIR=$1
if [ ! -d ${DIR} ]; then
  echo "PROBLEM: directory ${DIR} does not exist, exiting "
  exit 1
else
  echo "Directory ${DIR} exists, continuing"
fi
}

function create_or_recreate_directory {
DIR=$1
if [ -d ${DIR} ]; then
   echo "Deleting directory ${DIR}"
   rm -rf ${DIR}
   echo "Recreating directory ${DIR}"
   mkdir -p ${DIR}
else
   echo "Creating directory ${DIR}"
   mkdir -p ${DIR}
fi
}

function check_directory_exit_if_empty {
DIR=$1
check_directory_exists $DIR
MESSAGE="Directory ${DIR} empty, exiting"
if [ $# -eq 2 ]; then
     MESSAGE=$2
fi
if [ `ls $DIR | wc -l` -eq 0 ]; then
     echo $MESSAGE
     exit 1
fi
}

use_expect()
{
COMMAND=$1
PASSWD=$2
EXPECT=/usr/bin/expect
$EXPECT - <<EOF
        set force_conservative 1
        set timeout -1
        set prompt ".*(%|#|\\$|>):? $"
        spawn -noecho $COMMAND
        while {"1" == "1"} {
                expect {
                        "assword: " {
                                send_user "sending password"
                                send "$PASSWD\r"
                        }
                        "Are you sure" {
                                send "yes\r"
                        }
                        timeout {
                                send_user "expect timed out, exiting"
                                exit 1
                        }
                        -re \$prompt {
                                send "ls\r"
                        }
                        eof {
                                break
                        }
                }
        }
EOF
}

check_vm_exists(){
VM=$1
virsh list --all
if [ `virsh list --all | grep -c $VM` -eq 0 ]; then
  echo "No VM found $VM in virsh list, exiting"
  exit 1
else
  echo "Found $VM in virsh list, continuing"
fi

}

[ -z "${ECHO}" ] && ECHO=/bin/echo
[ -z "${SSH}" ] && SSH="/usr/bin/ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
[ -z "${SCP}" ] && SCP=/usr/bin/scp

execute_command_or_script_on_remote_server()
{

SERVER=$1
USER=$2
PASSWD=$3
CMD_SCRIPT="$4"

use_expect "$SSH ${USER}@${SERVER} ${CMD_SCRIPT}" $PASSWD
}

copy_file_to_remote_server()
{

SERVER=$1
USER=$2
PASSWD=$3
LOCAL_FILE=$4
LOCATION=$5

use_expect "$SCP ${LOCAL_FILE} ${USER}@${SERVER}:${LOCATION}" $PASSWD

}

copy_file_from_remote_server()
{

SERVER=$1
USER=$2
PASSWD=$3
REMOTE_FILE=$4
LOCAL_FILE=$5

use_expect "$SCP ${USER}@${SERVER}:${REMOTE_FILE} ${LOCAL_FILE}" $PASSWD

}

unmount_if_needed_mount_iso_on_directory()
{
ISO_FILE=$1
MOUNT_POINT=$2
if [ `mount | awk '{print $3}' | grep -c ${MOUNT_POINT} ` -gt 0 ]; then
 ${ECHO} "${MOUNT_POINT} already mounted, unmounting it, before reusing mount point with ${ISO_FILE}"
 umount ${MOUNT_POINT}
 if [[ $? -ne 0 || `mount | awk '{print $3}' | grep -c ${MOUNT_POINT}` -gt 0 ]]; then
   ${ECHO} " problem unmounting ${MOUNT_POINT} , exiting"
   mount
   exit 1
   fi
fi
echo "mounting $ISO_FILE on ${MOUNT_POINT}"
mount -o loop $ISO_FILE ${MOUNT_POINT}/
mount 
}



#TODO Needs to be tested more
timeout_if_response_not_recevied()
{
if [ $# -ne 4 ]; then
echo "This function takes 4 arguments [command to run], [expected response] [number of retries] [sleep time for each retry]"
exit
fi

CMD=$1
EXPECTED_RESPONSE=$2
NUMBER_OF_RETRIES=$3
TIME_TO_WAIT=$4

RETRY_COUNT=0
RESPONSE=`CMD`

 while [ $RETRY_COUNT -lt $NUMBER_OF_RETRIES ]; do
             echo "Waiting for $SG to be in state running"
             RETRY_COUNT=`expr $RETRY_COUNT + 1`
             echo "RETRY COUNT = $RETRY_COUNT "
             sleep 5
             STATE_OF_SG=`virsh list --all | grep $SG | awk '{print $3}'`
             if [ -z "${STATE_OF_SG}" ]; then
               echo "$SG does not exist yet"
               hagrp -state | grep $SG
               virsh list --all | grep $SG
             else
              echo "$SG is in state $STATE_OF_SG"
              hagrp -state | grep $SG
              virsh list --all | grep $SG
             fi
             if [ "$STATE_OF_SG" == "running" ]; then
               echo "$SG is in state running now"
               break
             fi
 done

if [ $RETRY_COUNT -eq $NUMBER_OF_RETRIES ]; then
  echo "Problem as $SG is still not in state running"
  hagrp -state | grep $SG
  virsh list --all | grep $SG
  exit 1
fi
}

SETCOLOR_SUCCESS="echo -en \\033[1;32m"
SETCOLOR_FAILURE="echo -en \\033[1;31m"
SETCOLOR_NORMAL="echo -en \\033[0;39m"

echo_success() {
  $SETCOLOR_SUCCESS
  echo $1
  $SETCOLOR_NORMAL
  echo -ne "\r"
  return 0
}

echo_failure() {
  $SETCOLOR_FAILURE
  echo $1
  $SETCOLOR_NORMAL
  return 1
}
