#!/bin/sh
#set -x
###############################################################
# DO NOT REMOVE
# This script file is used as part of the build process
# This script extracts RPM dependencies
###############################################################
/usr/share/maven/bin/mvn dependency:copy-dependencies  -DoutputDirectory=target/deps

echo "Expand deps called"
cd target/deps
echo "cd to target deps dir"


for i in *rpm ; do rpm2cpio $i | cpio -idmv ; done

cd ../

exit

