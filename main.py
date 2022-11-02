# coding: utf-8
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import datetime
import os
import logging
import sys
import time
from subprocess import Popen, PIPE, check_output
import errno
import _winreg
import configparser
import inspect
import re
import locale

if len(sys.argv) > 1:
    scriptMode = sys.argv[1]
    if scriptMode == '/b':
        scriptMode = 'BackUp'
    else:
        print ('Unknown incoming parameter: ' + scriptMode)
        sys.exit(1)
else:
    scriptMode = 0


class IniClass:
    """Ключ, значение, текст сообщения для input"""
    def __init__(self, ini_file, ini_section):
        self.iniFile = ini_file
        self.section = ini_section
        self.parsing = configparser.ConfigParser()
        self.parsing.read(self.iniFile)

    def read(self, key):
        """Возвращаем значение ключа или False"""
        if not self.parsing.has_section(self.section):
            logger.error('From file: ' + self.iniFile + '\nNot found section: ' + self.section)
            sys.exit(1)
        elif self.parsing.has_option(self.section, key):
            return self.parsing[self.section][key]
        else:
            logger.error('From file: ' + self.iniFile + '\nNot found key: ' + key + ', in section ' + self.iniFile)
            sys.exit(1)

    def write(self, key, value):
        """Сохраняем значения"""
        if not self.parsing.has_section(self.section):
            self.parsing[self.section] = {}
        self.parsing[self.section][key] = value
        with open(self.iniFile, 'w') as configfile:
            self.parsing.write(configfile)
        return value


'''
def ini_initialization(param_name, txt_for_input, param_value, mode='write'):
    if mode == 'write':
        if not ini.has_section(IniSection):
            ini[IniSection] = {}
        if not param_value:
            ini[IniSection][param_name] = raw_input(txt_for_input)
        else:
            ini[IniSection][param_name] = param_value
        with open(iniFile, 'w') as configfile:
            ini.write(configfile)
        return ini[IniSection][param_name]
    if not ini.has_section(IniSection):
        return False
    elif ini.has_option(IniSection, param_name):
        return ini[IniSection][param_name]
    else:
        return False
'''


def run_sql_query(sql_command, connect_string, check_connect=0):
    session = Popen(['sqlplus', '-S', connect_string], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    session.stdin.write(sql_command)
    out, error = session.communicate()
    out = out.replace("\r", "").replace("\n\n", "")
    error = error.replace("\r", "").replace("\n\n", "")
    if error == "" and out[:5] != "ERROR":
        logger.info(out)
        time.sleep(1)
        if check_connect:
            return True
        else:
            return out
    else:
        logger.error(out + error)
        time.sleep(1)
        return False


def reg_get_val(hkey, path, key, msg):
    # initializing variables
    hkey_val = {
        "HKEY_CLASSES_ROOT": _winreg.HKEY_CLASSES_ROOT,
        "HKEY_CURRENT_USER": _winreg.HKEY_CURRENT_USER,
        "HKEY_LOCAL_MACHINE": _winreg.HKEY_LOCAL_MACHINE,
        "HKEY_USERS": _winreg.HKEY_USERS,
        "HKEY_CURRENT_CONFIG": _winreg.HKEY_CURRENT_CONFIG,
    }
    open_key = ''
    result = False
    try:
        open_key = _winreg.OpenKey(hkey_val[hkey], path, 0, _winreg.KEY_READ | _winreg.KEY_WOW64_32KEY)
    except OSError as e:
        if e.errno == errno.ENOENT:
            logger.error(msg + ' section ' + hkey + chr(92) + path)
            time.sleep(1)
            return False
    try:
        result = _winreg.QueryValueEx(open_key, key)[0]
    except OSError as e:
        if e.errno == errno.ENOENT:
            time.sleep(1)
            logger.error(msg + ' key ' + key + ' in section ' + hkey + chr(92) + path)
            result = False
    finally:
        open_key.Close()
        return result

'''
def run_subprocess(cmd):
    cmd = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    std_out_string = ''
    while str(cmd.pid) in str(check_output('tasklist /fi "pid eq ' + str(cmd.pid) + '" /fo list').decode('cp866').encode('utf8')):
        char = cmd.stdout.read(1)
        while not (char in ['\n', '\r', '']):
            std_out_string += char
            char = cmd.stdout.read(1)
        if std_out_string.count(' ') == len(std_out_string):
            std_out_string = ''
        else:
            if len(std_out_string) > 8:
                if std_out_string[3] == '%':  # and std_out_string[8] == '+':
                    sys.stdout.write('\r' + std_out_string.decode('cp866').encode('utf8'))
                else:
                    print (std_out_string.decode('cp866').encode('utf8'))
            std_out_string = ''
    if not run.poll() == 0:
        for std_out_string in run.stdout.readlines():
            if not std_out_string.strip() == '':
                print (std_out_string.decode('cp866').encode('utf8').strip())
'''

dt = datetime.datetime.now()
# config logger
dirLog = os.path.dirname(os.path.realpath(__file__)) + r'\Logs'
if not os.path.exists(dirLog):
    os.makedirs(dirLog)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter(chr(10) + "%(asctime)s - %(levelname)s <PID %(process)d:%(processName)s> "
                                 "%(name)s.%(funcName)s():" + chr(10) + "%(message)s")
fileHandler = logging.FileHandler(dirLog + r'\Debuglog.log')
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)
# consoleHandler = logging.StreamHandler()
# consoleHandler.setFormatter(logFormatter)
# logger.addHandler(consoleHandler)

logger.info('\nStart logger'
            + '\nDefault Encoding =             ' + sys.getdefaultencoding()
            + '\nКодировка системы Win32/rus =  ' + locale.getpreferredencoding()
            + '\nКодировка Stdout Win32/rus =   ' + sys.stdout.encoding
            + '\nКодировка системы Linux =      ' + locale.getpreferredencoding()
            + '\nКодировка Stdout Linux =       ' + sys.stdout.encoding
            + '\nMode script =                  ' + str(scriptMode))

# iniFile = 'settings.ini'
# IniSection = 'default'
# ini = configparser.ConfigParser()
# ini.read(iniFile)

ini = IniClass('settings.ini', 'default')

if scriptMode == 0:
    while True:
        oraLogin = ini.write('l', (raw_input('Enter login (press Enter to set \'sys\'): ') or 'sys'))
        oraPassword = ini.write('p', raw_input('Enter password: '))
        oraInstance = ini.write('i', (raw_input('Enter the instance name (press Enter to set \'gas\'): ') or 'gas'))
        connString = oraLogin + '/' + oraPassword + '@' + oraInstance + ' as sysdba'
        if run_sql_query("select banner from v$version;", connString, 1):
            print ('Connect to the DB Oracle TRUE')
            break
        print (connString)


'''        

if scriptMode == 0:
    while True:
        oraLogin = ini_initialization('l', '', (raw_input('Enter login: ') or 'sys'))
        oraPassword = ini_initialization('p', 'Enter password: ', (raw_input('Enter password: ') or 'oracle'))
        oraInstance = ini_initialization('i', '', (raw_input('Enter the instance name: ') or 'gas'))
        connString = oraLogin + '/' + oraPassword + '@' + oraInstance + ' as sysdba'
        if run_sql_query("select banner from v$version;", connString, 1):
            print ('Connect to the DB Oracle TRUE')
            break
        else:
            print ('Connect to the DB Oracle FAILED, repeat:')
            ini.remove_option(IniSection, 'l')
            ini.remove_option(IniSection, 'p')
            ini.remove_option(IniSection, 'i')
    while True:
        oraHome = raw_input(chr(10) + 'Enter name OraHome (press enter to default HOME0): ') or 'HOME0'
        oracleBase = reg_get_val('HKEY_LOCAL_MACHINE', r'SOFTWARE\ORACLE' + chr(92) + oraHome, 'ORACLE_BASE',
                                 'OraHome not found in')
        if not oracleBase:
            print (r'OraHome not found key ORACLE_BASE in HKEY_LOCAL_MACHINE\SOFTWARE\ORACLE' + chr(92) + oraHome)
            continue
        if oracleBase[-1] == chr(92):
            oracleBase = oracleBase[:-1]
        ini_initialization('oracleBase', inspect.currentframe().f_lineno, oracleBase, 'write')
        oraPathDirAdmin = str(oracleBase) + chr(92) + 'admin'
        if not os.path.exists(oraPathDirAdmin):
            logger.error('Not found dir ' + oraPathDirAdmin)
            print ('CRITICAL ERROR^ Not found path: ' + oraPathDirAdmin)
            os.system("pause")
            sys.exit(1)
        else:
            ini_initialization('oraHome', inspect.currentframe().f_lineno, oraPathDirAdmin, 'write')
            break
    dirBU = ini_initialization('dirBU', 'Enter the path to the backup files: ', 0)
    if not os.path.exists(dirBU):
        try:
            os.makedirs(dirBU)
        except OSError as e:
            if e.errno == 2:
                ini.remove_option(IniSection, 'dirBU')
                print ('Path not found: "' + dirBU + '"')
                sys.exit(1)
    with open(iniFile, 'w') as configfile:
        ini.write(configfile)
exit()
'''

'''
oraHome = ini_initialization('oraHome', inspect.currentframe().f_lineno, '', 'read')

pFile = dirBU + r'\initGAS.ORA'
if os.path.exists(pFile):
    os.remove(pFile)
controlFile = dirBU + r'\CRGAS.SQL'
if os.path.exists(controlFile):
    os.remove(controlFile)
mountPoint = dirBU + r'\mountpoint'
if not os.path.exists(mountPoint):
    os.makedirs(mountPoint)

logger.info('Ini initialization finished')
exit()
os.system("cls")

vShadow = 'vshadow.exe'
exit()
run = Popen([vShadow, '-p', '-nw', oracleBase[:2]], stdin=PIPE, stdout=PIPE, stderr=PIPE)
outVSS, errorVSS = run.communicate()
if not outVSS.lower().find('errorVSS') == -1:
    logger.error('Shadow copy creation:' + outVSS)
    exit()
else:
    logger.info('Shadow copy creation:' + outVSS)
snapShot = (re.findall(r'SNAPSHOT ID = (\{.*\})', outVSS)) + (re.findall(r'Creation Time: (.{19})', outVSS))
print (dt.strftime('%Y.%m.%d %H:%M:%S ') + ' Shadow copy created, SNAPSHOT ID = ' + snapShot[0])

run = Popen([vShadow, '-el=' + str(snapShot[0]) + ',' + mountPoint], stdin=PIPE, stdout=PIPE, stderr=PIPE)
outVSS, errorVSS = run.communicate()
if not outVSS.lower().find('errorVSS') == -1:
    logger.error('Shadow copy mounted:' + outVSS)
    exit()
else:
    logger.info('Shadow copy mounted:' + outVSS)
print (dt.strftime('%Y.%m.%d %H:%M:%S') + ' Shadow copy exposed as ' + mountPoint)

destinationBackUp = dirBU + r'\Oracle_' + dt.strftime('%Y%m%d_%H%M%S') + '.gzip'
if os.path.exists(destinationBackUp[1:-1]):
    os.remove(destinationBackUp[1:-1])
run_subprocess('7z.exe a -tzip -bsp1 "' + destinationBackUp + '" "' + mountPoint + chr(92) + '"')

run = Popen([vShadow, '-ds=' + str(snapShot[0])], stdin=PIPE, stdout=PIPE, stderr=PIPE)
outVSS, errorVSS = run.communicate()
if not outVSS.lower().find('errorVSS') == -1:
    logger.error('Shadow copy deleted:' + outVSS)
    exit()
else:
    logger.info('Shadow copy deleted:' + outVSS)
print (dt.strftime('%Y.%m.%d %H:%M:%S') + ' ' + 'Shadow copy deleted, SNAPSHOT ID = ' + snapShot[0])
#
exit()

run_sql_query(r"Alter database backup controlfile to trace as '" + pFile + "';", connString)
run_sql_query(r"Create pfile='" + controlFile + "' from spfile;", connString)
run_sql_query(r"Shutdown immediate;", connString)
run_sql_query(r"Startup;", connString)

os.system("pause")
exit()

# logger.debug(inspect.currentframe().f_lineno)
'''