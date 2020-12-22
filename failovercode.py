from datetime import datetime
import fileinput
import subprocess as process
import mysql.connector as mysql
from mysql.connector import Error, errorcode

primary = {'host': 'localhost', 'port': '3306', 'user': 'dbaStack', 'password': 'dbaStack', 'database': 'test',
           'auth_plugin': 'mysql_native_password'}
failover = {'host': 'localhost', 'port': '3307', 'user': 'dbaStack', 'password': 'dbaStack', 'database': 'test',
            'auth_plugin': 'mysql_native_password'}

"""Color-Codes"""
Italic = '\33[3m'
Bold = '\33[1m'
Green = '\033[92m'
Red = '\33[31m'
reset = '\033[0m'
Yellow = '\33[33m'
Blue = '\033[94m'
Violet = '\33[35m'
Cyan = '\u001b[36m'
White = '\u001b[37m'
mixLogDesc = Bold + Italic + Cyan
mixLogSpec = Bold + Italic + Green
Err = Bold + Italic + Red
mixBlue = Bold + Italic + Blue
p = Bold + Cyan
error = Bold + Italic + Red
warning = Bold + Italic + Green
success = Bold + Italic + Yellow
failed = Bold + Italic + Violet
mixGreen = Bold + Italic + Green
initiate = Bold + Italic + Blue
"""Color-Codes"""
# logTime = datetime.now().strftime("%Y-%m-%d.%H:%M:%S")
logTime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

logLabel = [error + 'Error' + reset,
            warning + 'Warning' + reset,
            success + 'Success' + reset,
            failed + 'Failed' + reset,
            initiate + 'Initiated' + reset,
            mixBlue + 'Completed' + reset]
dbLabel = ['Primary', 'Failover']
filename = 'C:\\Users\\LENOVO\\Desktop\\host.txt'
directory = 'C:\\Users\\LENOVO\\Desktop\\'


def logger(logState, logData):
    try:
        print("{} {} {} {} {}".format(Bold + Yellow + datetime.now().strftime("%Y-%m-%d.%H:%M:%S") + reset,
                                      Bold + Red + '>>>' + reset, logState, p + Bold + '->' + reset,
                                      mixLogSpec + logData + reset))
    except RuntimeError:
        print('logging failed, please correct your code again')


logger(logLabel[4], mixBlue + 'Failover Code Logging Started, Version : 1.0, author:nanduu' + reset)


def setFailover():
    primaryDB = primary['host']
    failoverDB = failover['host']
    with fileinput.FileInput(filename, inplace=True, backup='') as file:
        for line in file:
            print(line.replace(primaryDB, failoverDB), end='')
    return failover


def setPrimary():
    primaryDB = primary['host']
    failoverDB = failover['host']
    with fileinput.FileInput(filename, inplace=True, backup='') as file:
        for line in file:
            print(line.replace(failoverDB, primaryDB), end='')
    return primary


def writeLog(log):
    with open(directory + 'failoverLog_{}.txt'.format(logTime), 'a') as failover_log:
        failover_log.write(Green + logTime + reset + Red + " >>> " + reset + Yellow + log + reset + '\n')


def _restartRadiusd_(label):
    logger(logLabel[2], mixLogSpec + 'Radiusd restarted successfully with {}'.format(label) + reset)
    """
    restart = process.run(['systemctl', 'restart', 'radiusd-acct'], stdout=process.PIPE, stderr=process.STDOUT)
    if restart.returncode == 0:
        logger(logLabel[2], mixLogSpec + 'Radiusd restarted successfully with {}'.format(label) + reset)
    else:
        logger(logLabel[0], mixLogSpec + 'Radiusd restarted successfully with {}'.format(label) + reset)
    """


def __connect__(props, label):
    try:
        connect = mysql.connect(**props)
        if connect.is_connected():
            return connect
    except Error as __connect_err:
        if __connect_err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logger(logLabel[0], error + 'Access Denied to User "{}"@"{}" in {} database'.format(
                props['user'], props['host'], label) + reset)
            return 0
        if __connect_err.errno == errorcode.CR_UNKNOWN_HOST or errorcode.ER_HOSTNAME:
            logger(logLabel[0], error + 'Unknown host in ' + mixBlue + label + reset + error +
                   'connection property, please correct host address')
            return 0
        if __connect_err.errno == errorcode.ER_UNKNOWN_TABLE:
            logger(logLabel[0], error + 'Unknown database in {} connection property'.format(mixBlue + label + reset))
        else:
            return 0


def __create_table__(props, label):
    _create_table_query = "create table test.test (ID int)"
    try:
        _create_connect_ = __connect__(props, label)
        _create_cursor_ = _create_connect_.cursor()
        _create_cursor_.execute(_create_table_query)
        return 1
    except Error as createErr:
        if createErr.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            logger(logLabel[0], Red +
                   "Table already exists in {} ".format(mixBlue + label + reset) +
                   Err + "database, dropping table for you")
            return 0


def __write_data__(props, label):
    try:
        _write_connect_ = mysql.connect(**props)
        _write_cursor_ = _write_connect_.cursor()
        _write_cursor_.execute('insert into test (ID) values (1)')
        _write_connect_.commit()
        return 1
    except Error as writeErr:
        if writeErr.errno == errorcode.ER_UNKNOWN_TABLE:
            logger(logLabel[0], 'Unknown table in {} '.format(mixBlue + label + reset) + mixGreen + "database")
            return 0
        else:
            return 0


def __read_data__(props, label):
    try:
        _read_connect_ = mysql.connect(**props)
        _read_cursor_ = _read_connect_.cursor()
        _read_cursor_.execute("select id from test limit 1")
        _read_result = _read_cursor_.fetchone()
        for read in _read_result:
            if read == 1:
                pass
        _read_connect_.commit()
        return 1
    except Error as readErr:
        if readErr.errno == errorcode.ER_UNKNOWN_TABLE:
            logger(logLabel[0], Red + 'Unknown table in {} '.format(mixBlue + label + reset) + mixGreen + "database")
            return 0
        else:
            return 0


def __drop_table__(props, label):
    try:
        _drop_connect_ = mysql.connect(**props)
        _drop_cursor_ = _drop_connect_.cursor()
        _drop_cursor_.execute('drop table if exists test')
        logger(logLabel[2], "Dropped test table in {} ".format(mixBlue + label + reset) + mixGreen + "database")
        return 1
    except Error as _createErr_:
        if _createErr_.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            logger(logLabel[0], 'Table already exists in {} '.format(mixBlue + label + reset) + mixGreen + "database")
            return 0
        if _createErr_.errno == errorcode.ER_UNKNOWN_TABLE:
            logger(logLabel[0], "Table doesn't exists in {} ".format(mixBlue + label + reset) + mixGreen + "database")
            return 0
        else:
            return 0


def __performanceValidation__(props, label):
    """Performance validation checks for database stability/write/read"""
    try:
        _failover_connect_ = mysql.connect(**props)
        if _failover_connect_.is_connected():
            logger(logLabel[2],
                   'Connected to {} '.format(mixBlue + label + reset) + mixGreen + "database successfully")
            if __create_table__(props, label) == 1:
                logger(logLabel[2],
                       'Test table created successfully in {} '.format(mixBlue + label + reset) + mixGreen + "database")
                if __write_data__(props, label) == 1:
                    logger(logLabel[2],
                           'Data written successfully into {} '.format(mixBlue + label + reset) + mixGreen + "database")
                    if __read_data__(props, label) == 1:
                        logger(logLabel[2], mixGreen + 'Read data successfully from {} '.format(
                            mixBlue + label + reset) + mixGreen + "database")
                        __drop_table__(props, label)
                        return 1
                    else:
                        logger(logLabel[0],
                               error + 'Found error reading data from {} '.format(mixBlue + label + reset)
                               + error + "database")
                        __drop_table__(props, label)
                else:
                    logger(logLabel[0],
                           error + 'Found error while writing data in  {} '.format(mixBlue + label + reset)
                           + error + "database")
                    __drop_table__(props, label)
            else:
                logger(logLabel[0],
                       error + 'Found error while creating test table in  {} '.format(mixBlue + label + reset)
                       + error + "database")
                __drop_table__(props, label)
        else:
            logger(logLabel[0],
                   error + 'Found error while connecting to {} '.format(mixBlue + label + reset)
                   + error + "database")
            __drop_table__(props, label)
    except Error as failErr:
        if failErr.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logger(logLabel[0], error + 'Access Denied to User "{}"@"{}" in {} database'.format(
                props['user'], props['host'], label) + reset)
            return 0
        if failErr.errno == errorcode.CR_UNKNOWN_HOST or errorcode.ER_HOSTNAME:
            logger(logLabel[0], error + 'Unknown host/port in ' + mixBlue + label + reset + error +
                   ' database connection property, please correct host/port address')
        if failErr.errno == errorcode.ER_UNKNOWN_TABLE:
            logger(logLabel[0], error + 'Unknown database in {} connection property'.format(mixBlue + label + reset))
        else:
            __drop_table__(props, label)
            return 0


def doFailover():
    """When primary database performance validation failed, primary -> failover switch"""
    try:
        if __performanceValidation__(props=primary, label='Primary') == 1:
            logger(logLabel[2], '{} '.format(mixBlue + 'Primary' + reset) + mixGreen +
                   "database validation completed Successfully")
        else:
            logger(logLabel[4], mixBlue + 'Switching into failover database' + reset)
            setFailover()
            if __performanceValidation__(props=failover, label='Failover') == 1:
                logger(logLabel[2], '{} '.format(mixBlue + 'Failover' + reset) + mixGreen +
                       "database validation completed Successfully")
                _restartRadiusd_('Failover')
    except RuntimeError as runtimerr:
        logger(logLabel[2], runtimerr)


def reSwitch():
    """When failover database performance validation failed, failover -> primary switch"""
    try:
        if __performanceValidation__(props=failover, label='Failover') == 1:
            logger(logLabel[2], '{} '.format(mixBlue + 'Failover' + reset) + mixGreen +
                   "database validation completed Successfully")
        else:
            logger(logLabel[4], mixBlue + 'Switching into primary database' + reset)
            setPrimary()
            if __performanceValidation__(props=primary, label='Primary') == 1:
                logger(logLabel[2], '{} '.format(mixBlue + 'Primary' + reset) + mixGreen +
                       "database validation completed Successfully")
                _restartRadiusd_('Primary')
    except RuntimeError as runtimerr:
        logger(logLabel[2], runtimerr)


doFailover()
reSwitch()
logger(logLabel[5], mixBlue + 'Failover Code Logging Completed' + reset)

