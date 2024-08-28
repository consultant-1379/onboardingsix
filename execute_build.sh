#!/bin/bash --login
# build project
PROFILE=$1
printenv
echo "STARTING_BUILD"
cd $HOME
MAVEN_GOALS="clean install"
## execute the deploy phase, only when the maven release:perform is executed
## by default it will checkout the latest code into checkout subfolder of $project/target
## so this folder becomes the hostname prefix
if [[ "$HOSTNAME" =~ ^checkout.* ]]; then
   MAVEN_GOALS="clean deploy"
fi
maven --settings $HOME/.m2/settings.xml -Dmaven.repo.local=$HOME/.m2/repository -Duser.home=$HOME "-P$PROFILE,local_build" ${MAVEN_GOALS}

EXIT_CODE=$?
echo "exit_code $EXIT_CODE"
exit $EXIT_CODE
