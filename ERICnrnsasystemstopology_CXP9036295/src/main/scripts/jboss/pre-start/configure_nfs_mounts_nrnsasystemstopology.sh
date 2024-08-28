
SEC_KEY='/opt/ericsson/nr-nsa-systems-topology/lib/crypt.py'
NFS_NRNSA=/ericsson/tor/no_rollback/nr-nsa-systems-topology
NFS_CRONBACKUPS=$NFS_NRNSA/cron_backups
NFS_SECUREDIR=$NFS_NRNSA/secure
NFS_EXPORT=$NFS_NRNSA/export

DIR_ARR=($NFS_NRNSA $NFS_CRONBACKUPS $NFS_SECUREDIR $NFS_EXPORT)
SCRIPTING_GID=5003
LOG_TAG="PostInstall"
SCRIPT_NAME="${0}"

_MKDIR=/bin/mkdir
_CHMOD=/bin/chmod
_CHOWN=/bin/chown

###########################################################################################
#
# Logger Functions
#
############################################################################################
info()
{
  logger -t "${LOG_TAG}" -p user.notice "INFO ( ${SCRIPT_NAME} ): $1"
}

error()
{
  logger -t "${LOG_TAG}" -p user.err "ERROR ( ${SCRIPT_NAME} ): $1"
}

create_dir()
{
DIRECTORY=$1
if [ ! -d "$DIRECTORY" ];then
  info "Creating the $DIRECTORY directory"
  $_MKDIR "$DIRECTORY"
  if [ $? -ne 0 ];then
    error "Failed creating the $DIRECTORY directory"
    exit 1
  fi

  info "Changing the ownership of the $DIRECTORY directory"
  $_CHOWN root:$SCRIPTING_GID "$DIRECTORY"
  if [ $? -ne 0 ];then
    error "Failed to change the ownership of the $DIRECTORY directory"
    exit 1
  fi

  info "Changing the permission of the $DIRECTORY directory"
  $_CHMOD 0775 "$DIRECTORY"
  if [ $? -ne 0 ];then
    error "Failed to change the permission of the $DIRECTORY directory"
    exit 1
  fi
fi

}
#//////////////////////////////////////////////////////////////
# Main Part of Script
#/////////////////////////////////////////////////////////////
for i in ${DIR_ARR[@]}; do
  create_dir $i
done

# the secure directory needs different permissions
$_CHMOD 0770 "$NFS_SECUREDIR"
#generate the private key
$SEC_KEY setkey

# the export directory needs different permissions
$_CHMOD 0777 "$NFS_EXPORT"
