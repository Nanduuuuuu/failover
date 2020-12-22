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
logTime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

logLabel = [error + 'Error' + reset,
            warning + 'Warning' + reset,
            success + 'Success' + reset,
            failed + 'Failed' + reset,
            initiate + 'Initiated' + reset,
            mixBlue + 'Completed' + reset,
            Bold + Italic + White + 'Info' + reset]
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


logger(logLabel[6], mixBlue + 'Failover Code Logging Started, Version : 1.0, author:nanduu' + reset)


def _restartRadiusd_(label):
    logger(logLabel[6], 'Restarting radiusd with {} '.format(mixBlue + label + reset) + mixLogSpec + 'database')


def __connect__(props, label):
    try:
        try:
            connect = mysql.connect(**props)
            if connect.is_connected():
                logger(logLabel[2],
                       'Connected to {} '.format(mixBlue + label + reset) + mixGreen + "database successfully")
                return connect
        except Error as __connect_err:
            logger(logLabel[0],
                   error + 'Found error while connecting to {} '.format(mixBlue + label + reset)
                   + error + "database")
            if __connect_err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger(logLabel[0], error + 'Access Denied to User "{}"@"{}" in {} database'.format(
                    props['user'], props['host'], label) + reset)
                return 0
            if __connect_err.errno == errorcode.CR_UNKNOWN_HOST or errorcode.ER_HOSTNAME:
                logger(logLabel[0], error + 'Unknown host/port in ' + mixBlue + label + reset + error +
                       ' database connection property')
                return 0
            if __connect_err.errno == errorcode.ER_ATTRIBUTE_IGNORED:
                logger(logLabel[0],
                       error + 'Unknown database in {} connection property'.format(mixBlue + label + reset))
            else:
                return 0
    except AttributeError as err:
        pass


def __create__(props, label):
    _create_table_query = "create table test.test (ID int)"
    try:
        try:
            _create_connect_ = __connect__(props, label)
            _create_cursor_ = _create_connect_.cursor()
            _create_cursor_.execute(_create_table_query)
            logger(logLabel[2],
                   'Test table created successfully in {} '.format(mixBlue + label + reset) + mixGreen + "database")
            return 1
        except Error as createErr:
            if createErr.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                logger(logLabel[0], Red +
                       "Table already exists in {} ".format(mixBlue + label + reset) +
                       Err + "database, dropping table automatically")
                __drop__(props, label)
                return 0
            if createErr.errno == errorcode.CR_UNKNOWN_HOST or errorcode.ER_HOSTNAME:
                logger(logLabel[0], error + 'Unknown host in ' + mixBlue + label + reset + error +
                       ' connection property, please correct host address')
            else:
                return 0
    except AttributeError as err:
        pass


def __write__(props, label):
    try:
        try:
            _write_connect_ = mysql.connect(**props)
            _write_cursor_ = _write_connect_.cursor()
            _write_cursor_.execute('insert into test (ID) values (1)')
            _write_connect_.commit()
            logger(logLabel[2],
                   'Data written successfully into {} '.format(mixBlue + label + reset) + mixGreen + "database")
            return 1
        except Error as writeErr:
            logger(logLabel[0],
                   error + 'Found error while writing data into {} '.format(mixBlue + label + reset)
                   + error + "database")
            if writeErr.errno == errorcode.ER_UNKNOWN_TABLE:
                logger(logLabel[0], 'Unknown table in {} '.format(mixBlue + label + reset) + mixGreen + "database")
                return 0
            if writeErr.sqlstate == '42S02':
                logger(logLabel[0],
                       "Table doesn't exists in {} ".format(mixBlue + label + reset) + mixGreen +
                       "database, write operation failed {} ".format(Err + 'EXITING CODE' + reset))
                return 0
            else:
                logger(logLabel[0], 'Failed writing into database')
                return 0
    except AttributeError as err:
        pass


def __drop__(props, label):
    try:
        _drop_connect_ = mysql.connect(**props)
        _drop_cursor_ = _drop_connect_.cursor()
        _drop_cursor_.execute('drop table if exists test')
        logger(logLabel[2], "Dropped test table in {} ".format(mixBlue + label + reset) + mixGreen + "database")
        return 1
    except Error as _dropErr_:
        if _dropErr_.errno == errorcode.ER_UNKNOWN_TABLE:
            logger(logLabel[0], "Table doesn't exists in {} ".format(mixBlue + label + reset) + mixGreen + "database")
            return 0
        else:
            return 0
    except AttributeError as err:
        pass


def __read__(props, label):
    try:
        try:
            _read_connect_ = mysql.connect(**props)
            _read_cursor_ = _read_connect_.cursor()
            _read_cursor_.execute("select id from test limit 1")
            _read_result = _read_cursor_.fetchone()
            for read in _read_result:
                if read == 1:
                    logger(logLabel[2], 'Read data successfully from {} '.format(
                        mixBlue + label + reset) + mixGreen + "database")
            _read_connect_.commit()
            return 1
        except Error as readErr:
            logger(logLabel[0],
                   error + 'Found error reading data from {} '.format(mixBlue + label + reset)
                   + error + "database")
            if readErr.errno == errorcode.ER_UNKNOWN_TABLE:
                logger(logLabel[0],
                       Red + 'Unknown table in {} '.format(mixBlue + label + reset) + mixGreen + "database")
                return 0
            if readErr.sqlstate == '42S02':
                logger(logLabel[0],
                       "Table doesn't exists in {} ".format(mixBlue + label + reset) + mixGreen +
                       "database, read operation failed {} ".format(Err + 'EXITING CODE' + reset))
                return 0
            else:
                return 0
    except AttributeError as err:
        pass


def _check_(props, label):
    logger(logLabel[4], 'Starting {} '.format(mixBlue + label + reset) + mixGreen + "database performance check")
    try:
        try:
            if __create__(props, label) and __write__(props, label) and __read__(props, label) == 1:
                __drop__(props, label)
                logger(logLabel[2],
                       '{} '.format(mixGreen + label + reset)
                       + mixBlue + "database performance check completed successfully")
                return 1
            else:
                logger(logLabel[3],
                       error + 'Performance validation failed in {} '.format(mixBlue + label + reset)
                       + error + "database")
                return 0
        except Error as checkErr:
            if checkErr.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger(logLabel[0], error + 'Access Denied to User "{}"@"{}" in {} database'.format(
                    props['user'], props['host'], label) + reset)
                return 0
            else:
                return 0
    except AttributeError as err:
        pass


_check_(props=primary, label='Primary')
_check_(props=failover, label='Failover')

logger(logLabel[6], mixBlue + 'Failover Code Logging Completed' + reset)
