#!/bin/bash
PROFILE_DIR=profileDir

if [ "$#" -ne 1 ]; then
    echo "Error, please select a profile"
    echo "Usage: $0 <profile>"
    exit 1
fi

selectedProfile=$1

if [ ! -d ${PROFILE_DIR} ]; then
    echo "Error, misisng profile directory: ${PROFILE_DIR}"
    exit 1
fi

profileFile=${PROFILE_DIR}/${selectedProfile}.env
if [ ! -f ${profileFile} ]; then
    echo "Error, misisng profile file: ${profileFile}"
    exit 1
fi

echo "Loading profile ${profileFile}..."
source ${profileFile}
if [ $? -ne 0 ]; then
    echo "Error, invalid profile info in file: ${profileFile}"
    exit 1
fi

echo "Launching profile ${profileFile}..."

cd backend;
python manage.py makemigrations
python manage.py migrate
python manage.py bgtask_stop
python manage.py runserver 0.0.0.0:${BACKEND_PORT} & #// Run in background
backendPid=$!


echo "Started backend ${profileFile}..."
cd ../frontend/fe/


echo "Launching frontend ${profileFile}..."
# Adding BACKEND_PORT to environment file. The prefix REACT_APP_ is needed
echo "REACT_APP_BACKEND_PORT=${BACKEND_PORT}" > .env

if [ $PROD = 'True' ]; then
  echo "Building production profile..."
  yarn build prod
  yarn serve -s build -l ${FRONTEND_PORT} &
  frontendPid=$!
else
  PORT=${FRONTEND_PORT} yarn start &
  frontendPid=$!
fi


clean_up() {
  echo "Signal received. Terminating ${backendPid} and ${frontendPid}..."
  kill ${backendPid}
  kill ${frontendPid}
  echo "Terminated backend and frontend"
  exit $1
}
trap clean_up SIGHUP SIGINT SIGTERM

echo "Waiting for backend pid ${backendPid}..."
wait $backendPid

echo "Waiting for frontend pid ${frontendPid}..."
wait $frontendPid
