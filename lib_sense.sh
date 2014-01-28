#! /bin/sh
# /etc/init.d/lib_sense

### BEGIN INIT INFO
# Provides:		lib_sense
# Required-Start:	$remote_fs $sys_log $all
# Required-Stop:	$remote_fs $sys_log
# Default-Start:	2 3 4 5
# Default-Stop:		0 1 6
# Short-Description:	LIB temp sensors
# Description:		Runs LIB temp sensorpi serv
### END INIT INFO
case "$1" in
    start)
        echo "Starting Lib Sense"
	python /home/pi/CEIT_Temperature/lib_temp.py 401 &
	;;
    stop)
	echo "Stopping Lib Sense"
	killall python 
   	;;
    restart)
	echo "Restarting Lib Sense"
	/etc/init.d/lib_sense.sh stop
	/etc/init.d/lib_sense.sh start
	;; 
    *)

esac

exit 0
