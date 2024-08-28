#!/bin/bash
SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
SCRIPTPATH_FOLDER=$(basename $SCRIPTPATH)

echo "PREBUILD_IMAGES"
GROUP_ID=$(id -g)
GROUP_NAME=$(id -gn)
USER_ID=$(id -u)
USER_NAME=$(id -un)

rm -rf .env
touch .env

if [ $? -gt 0 ]; then
	echo "UNABLE TO SET DOCKER-COMPOSE ENVIRONMENT FILE"
	exit 1
fi

echo "WORKDIR=$SCRIPTPATH" >> .env
echo "GROUP_ID=$GROUP_ID" >> .env
echo "GROUP_NAME=$GROUP_NAME" >> .env
echo "USER_ID=$USER_ID" >> .env
echo "USER_NAME=$USER_NAME" >> .env
echo "BUILD_FOLDER=$SCRIPTPATH_FOLDER" >> .env

export IMAGE_REPOSITORY=armdocker.rnd.ericsson.se/proj_oss_releases/enm/eric-enm-os-builders
export IMAGE_TAG=1.1.0-1


echo "IMAGE_REPOSITORY=$IMAGE_REPOSITORY" >> .env
echo "IMAGE_TAG=$IMAGE_TAG" >> .env
exit 0
