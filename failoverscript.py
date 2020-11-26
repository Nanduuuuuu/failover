import mysql.connector as mysql
from mysql.connector import Error
from mysql.connector import errorcode
from datetime import datetime, timedelta
import subprocess as process


"""                                          
    Failover Script for radacct databases.
"""

primary = {'host': 'localhost', 'port': '3306', 'user': 'root', 'password': 'Mysql++1', 'database': 'mysql'}
failover = {'host': 'localhost', 'port': '3307', 'user': 'root', 'password': 'Maria++1', 'database': 'mysql'}


def logging(logData):
    try:
        print("{} >>> {}".format(datetime.now().strftime("%Y-%m-%d.%H:%M:%S"), logData))
    except Error as logging_err:
        print(logging_err)


logging('Starting Radacct Failover Script')


def db_connect(host, user, password, port, database):
    try:
        logging('Checking database statistics')
        x = mysql.connect(host=host, user=user, password=password, port=port, database=database)
        logging('Connecting to database {}'.format(database))
        if x.is_connected():
            return 0
    except Error as radacct_err:
        if radacct_err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logging('Please check the credentials entered')
            return 0
        elif radacct_err.errno == errorcode.CR_UNKNOWN_HOST:
            logging('Please check connection parameters')
            return 0


def restart_radiusd():
    try:
        logging('Restarting radius server, starting radius with failover database : {}'.format(failover['host']))
        """
        status = process.run(['systemctl', 'restart', 'radiusd-acct'], stdout=process.PIPE, stderr=process.STDOUT)
        if status.returncode == 0:
            logging('Radiusd restarted with failover database {}'.format(failover['host']))
        elif status.returncode == 1:
            logging('Radiusd cannot be started')
        """
    except Error as err:
        print(err)


def switch_accounting():
    try:
        logging('Collecting account switching statistics')
        xyz = mysql.connect(**primary)
        logging('Connecting to primary database {}'.format(primary['host']))
        xyz_cursor = xyz.cursor()
        xyz_query = 'select 1'
        xyz_cursor.execute(xyz_query)
        xyz_result = xyz_cursor.fetchone()
        for x in xyz_result:
            if x == 0:
                logging('Connected to primary database'.format(primary['host']))
            else:
                logging('Failed connecting to primary database with host: {}:{}'.format(primary['host'],
                                                                                        primary['port']))
                logging('Trying to connect to failover database with host:  {}:{}'.format(failover['host'],
                                                                                          failover['port']))
                "failover database connection"
                abc = mysql.connect(**failover)
                abc_cursor = abc.cursor()
                abc_query = 'select 1'
                abc_cursor.execute(abc_query)
                abc_result = abc_cursor.fetchone()
                for a in abc_result:
                    if a == 1:
                        logging('Connected to failover database, initiating radiusd restart')
                        restart_radiusd()
                    else:
                        logging('Failover database is unavailable, please check with admin')
    except Error as switch_err:
        logging(switch_err)


switch_accounting()
