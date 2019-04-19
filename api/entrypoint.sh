#!/bin/bash

log()
{
   if [ "$1" == "notice" ]; then
#      logger -p user.$1 -t " $(date "+%F %T")=> $2"
      echo -e " $(date "+%F %T") => \e[32m$2\e[0m"
   else 
      echo -e " $(date "+%F %T") => \e[91m$2\e[0m"
   fi
}


args=("$@")

case $1 in
    production)
        log notice "Running Gunicorn in Production Mode"
        exec /usr/local/bin/gunicorn app:app --user=flask -b 0.0.0.0:8080 -w 4 
       ;;
    development)
        log notice "Running in Development Mode"
        exec flask run --host=0.0.0.0 --port 8080
        ;;
    
    *)
        if [ -f ./entrypoint-extras.sh ]; then
            ./entrypoint-extras.sh ${args[@]}
        else
            exec "$@"
        fi
        ;;
esac
