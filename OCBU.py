# coding: utf-8
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import shutil
import sys
import logging
import time
import datetime
from subprocess import Popen, PIPE, check_output
import errno
import _winreg
import configparser
from inspect import currentframe
import re
import locale
import traceback
import codecs
import psutil
from cryptography.fernet import Fernet
# noinspection PyUnresolvedReferences
import subprocessww


# <editor-fold desc="Constant">
time_start_script = datetime.datetime.now()
sleep_delay = 0.05
vShadow = 'vshadow.exe'
SevenZ = '7z.exe'
SnapShot = False
Ora_DB_Shutdown = False
debugMode = False
version = 230117.2016
# os.system('mode 150,300')
os.system('color 0A')
prefixData = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
nameScript = os.path.basename(__file__)
pathToScriptDir = sys.path[0]
keyCrypto = Fernet('AJM4lrTR-74MUmQISJc4tpD-65EpsTBC40ziduRfp7M=')

if len(sys.argv) > 1:
    scriptMode = sys.argv[1]
    if scriptMode == '/b':
        scriptMode = 'BackUp'
    else:
        print ('Unknown incoming parameter: ' + scriptMode)
        sys.exit(1)
else:
    scriptMode = 0


# </editor-fold>


class IniClass:
    """Ключ, значение, текст сообщения для input"""

    def __init__(self, ini_file, ini_section):
        self.iniFile = ini_file
        self.section = ini_section
        self.parsing = configparser.ConfigParser()
        self.parsing.read(self.iniFile, 'UTF-8')

    def read(self, key):
        """Возвращаем значение ключа или False"""
        if not self.parsing.has_section(self.section):
            logger.error(
                line_number() + 'From file: ' + self.iniFile + '\nNot found section: ' + self.section)
            sys.exit(1)
        elif self.parsing.has_option(self.section, key):
            return self.parsing[self.section][key]
        else:
            logger.error(line_number() + 'From file: ' + self.iniFile + '\nNot found key: ' + key + ', in section '
                         + self.iniFile)
            sys.exit(1)

    def write(self, key, value):
        """Сохраняем значения"""
        if not self.parsing.has_section(self.section):
            self.parsing[self.section] = {}
        self.parsing[self.section][key] = value
        with codecs.open(self.iniFile, 'w', "utf8") as configfile:
            self.parsing.write(configfile)
            configfile.close()
        return value


class CmdClass:
    def __init__(self, return_std_out, exit_on_error):
        self.session = None
        self.return_std_out = return_std_out
        self.exit_on_error = exit_on_error
        self.str_log = ''

    def run(self, command, std_in, char_by_char=False):
        self.session = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        if not std_in:
            if char_by_char and self.return_std_out:
                std_out_string = ''
                sub_str_log = ''
                len_std_out_string = 0
                pid = str(self.session.pid)
                query_pid = 'tasklist /fi "pid eq ' + pid + '" /fo list'
                while True:
                    char = self.session.stdout.read(1)
                    # read char by char before the line break
                    while not (char in ['\n', '\r', '']):
                        std_out_string += char
                        char = self.session.stdout.read(1)
                    # skip lines consisting of spaces and 0%
                    if not (std_out_string.count(' ') == len(std_out_string) or std_out_string.strip() == '0%'):
                        std_out_string = self.format_string(std_out_string, '', False)
                        # format the lines with %
                        if std_out_string.find('% ') != -1:
                            if len(std_out_string) > len_std_out_string:
                                len_std_out_string = len(std_out_string)
                            sys.stdout.write('\r' + std_out_string + ' ' * (len_std_out_string - len(std_out_string)))
                            file_arch_name = std_out_string[std_out_string.rfind('% ') + 6:]
                            if sub_str_log != file_arch_name:
                                # logger.debug(sub_str_log + '\n' + file_arch_name)
                                sub_str_log = file_arch_name
                                self.str_log = str(self.str_log) + str(std_out_string) + chr(10)
                        else:
                            print std_out_string
                            self.str_log = self.str_log + std_out_string + chr(10)
                    std_out_string = ''
                    if not (pid in str(check_output(query_pid)).decode('cp866').encode('utf8')):
                        sys.stdout.write('\r100' + std_out_string[3:] + '\n\r')
                        break
                if self.session.poll() == 0:
                    for std_out_string in self.session.stdout.readlines():
                        std_out_string = self.format_string(std_out_string, '', False)
                        if std_out_string.strip() != '':
                            self.str_log = self.str_log + std_out_string + chr(10)
                            print std_out_string
                            logger.debug(line_number() + self.str_log)
                if self.str_log == '':
                    out, error = self.session.communicate()
                    self.format_string(out, error, True)
            else:
                return self.read()

    def read(self):
        out, error = self.session.communicate()
        return self.format_string(out, error)

    def write(self, sql_command):
        self.session.stdin.write(sql_command.encode('cp866'))
        return self.read()

    def format_string(self, out_string, error_string='', fs_log=True):
        bool_result = True
        full_out_string = (out_string + error_string).decode('cp866').encode('utf8')
        if full_out_string:
            full_out_string = '\n'.join([line for line in full_out_string.split('\r\n') if line.strip() != ''])
            error_tuple = ['ERROR', 'ORA-', 'Invalid', 'warning']
            for x in error_tuple:
                if x.lower() in full_out_string.lower():
                    bool_result = False
            if fs_log:
                logger.debug(line_number() + full_out_string)
        if error_string:
            bool_result = False
        if self.exit_on_error and not bool_result:
            logger.error(line_number() + full_out_string)
            exit()
        if self.return_std_out:
            return full_out_string
        return bool_result


def ce_exit(number):
    os.system('color 0C')
    time.sleep(sleep_delay)
    logger.error(line_number() + 'Error, rollback:')
    if SnapShot:
        shadow_copy('delete', SnapShot)
    if Ora_DB_Shutdown:
        logger.error(line_number() + 'Startup database oracle')
        run_sql_query.run('sqlplus -s ' + connString, True)
        if run_sql_query.write(r"Startup;"):
            logger.info(line_number() + 'Ok, startup oracle database')
        else:
            logger.info(line_number() + 'Error, startup oracle database')
    path_exist([controlFile, pFile, pathOraControlFile], 'delete')
    raw_input('Critical error, press Enter to exit ... ')
    sys.exit(number)


def line_number():
    cf = currentframe()
    return '#' + str(cf.f_back.f_lineno) + ' '


def reg_get_val(hkey, rgv_path, key, msg):
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
        open_key = _winreg.OpenKey(hkey_val[hkey], rgv_path, 0, _winreg.KEY_READ | _winreg.KEY_WOW64_32KEY)
    except OSError as rgv_e:
        if rgv_e.errno == errno.ENOENT:
            logger.error(msg + ' section ' + hkey + chr(92) + rgv_path)
            time.sleep(sleep_delay)
            return False
    try:
        result = _winreg.QueryValueEx(open_key, key)[0]
    except OSError as e_rgv:
        if e_rgv.errno == errno.ENOENT:
            time.sleep(sleep_delay)
            logger.error(msg + ' key ' + key + ' in section ' + hkey + chr(92) + rgv_path)
            result = False
    finally:
        open_key.Close()
        return result


def path_exist(pe_path, pe_mode='check'):
    """pe_mode check, create, delete;\n
    pe_path list or tuple;\n
    return boolean"""
    for pe_tmp in pe_path:
        if pe_mode == 'create':
            if os.path.exists(pe_tmp):
                logger.debug(line_number() + 'Ok, folder exist: ' + pe_tmp)
                time.sleep(sleep_delay)
                continue
            try:
                os.makedirs(pe_tmp)
            except OSError as de_e:
                logger.error(line_number() + 'Error creation folder: ' + de_e.strerror.decode('cp1251').encode('utf8'))
                time.sleep(sleep_delay)
                return False
            logger.debug(line_number() + 'Ok, folder created: ' + pe_tmp)
            time.sleep(sleep_delay)
            continue
        elif pe_mode == 'delete':
            if not os.path.exists(pe_tmp):
                logger.debug(line_number() + 'Ok, file or folder not exist: ' + pe_tmp)
                time.sleep(sleep_delay)
                continue
            try:
                if os.path.isfile(pe_tmp):
                    os.remove(pe_tmp)
                else:
                    shutil.rmtree(pe_tmp)
            except OSError as de_e:
                logger.error(line_number() + 'Error delete ' + pe_tmp + ' ' +
                             de_e.strerror.decode('cp1251').encode('utf8'))
                time.sleep(sleep_delay)
                return False
            logger.debug(line_number() + 'Ok, delete: ' + pe_tmp)
            time.sleep(sleep_delay)
            continue
        elif pe_mode == 'check':
            if os.path.exists(pe_tmp):
                logger.debug(line_number() + 'Ok, folder exist: ' + pe_tmp)
                time.sleep(sleep_delay)
                continue
            logger.error(line_number() + 'Error, not found file or folder: ' + pe_tmp)
            time.sleep(sleep_delay)
            return False
        else:
            logger.error(line_number() + 'Unknown argument: ' + pe_mode)
            time.sleep(sleep_delay)
            return False
    return True


def shadow_copy(action, sc_id):
    """action: create, delete, check, mount\n
    sc_id: create (disk_name), delete/check/mount (id_snapshot, disk_name)"""
    sc_result = []
    sc_snap_shot = []
    for x in sc_id:
        if action == 'create':
            sc_cmd = CmdClass(True, False).run(vShadow + ' -p -nw ' + x, False)
            sc_bool_flag = sc_cmd
            if sc_bool_flag:
                sc_snap_shot = (re.findall(r'SNAPSHOT ID = ({.*})', sc_cmd)) + \
                               (re.findall(r'Creation Time: (.{19})', sc_cmd))
                logger.debug(line_number() + 'Ok, shadow copy of disk ' + x + ' created, SNAPSHOT ID = ' +
                             sc_snap_shot[0] + ', date: ' + sc_snap_shot[1])
                sc_snap_shot[0] = [x, sc_snap_shot[0]]
            else:
                logger.error(line_number() + 'Error, a shadow copy of disk ' + x + ' has not been created')
                if len(sc_result):
                    logger.error(line_number() + 'Rollback: deleting previously created shadow copies')
                    shadow_copy('delete', sc_result)
                ce_exit(1)
        elif action == 'delete':
            sc_cmd = CmdClass(True, False).run(vShadow + ' -ds=' + x[1], False)
            sc_bool_flag = sc_cmd
            if sc_bool_flag:
                sc_snap_shot = (re.findall(r'Deleting shadow copy ({.*})', sc_cmd))
                logger.debug(line_number() + 'Ok, shadow copy deleted, SNAPSHOT ID = ' + sc_snap_shot[0])
                path_exist((mountPoint + '\\' + sc_snap_shot[0],), 'delete')
            else:
                logger.error(line_number() + 'Error, the shadow copy could not be deleted')
                logger.error(line_number() + 'Error, delete the snapshot manually SNAPSHOT ID = ' + x[1])
        elif action == 'check':
            sc_cmd = CmdClass(True, False).run(vShadow + ' -q', False)
            sc_snap_shot = re.findall(r'SNAPSHOT ID = ' + x[1], sc_cmd)
            if len(sc_snap_shot):
                logger.debug(line_number() + 'Ok, shadow copy exists, SNAPSHOT ID = ' + x[1])
            else:
                logger.debug(line_number() + 'Error, shadow copy does not exist, SNAPSHOT ID = ' + x[1])
                return False
        elif action == 'mount':
            try:
                mount_path = mountPoint + '\\' + x[1]
                assert (path_exist((mount_path,), 'create'))
                sc_cmd = CmdClass(True, False).run(vShadow + ' -el=' + x[1] + ',"' + mount_path + '"', False)
                sc_snap_shot = (re.findall("Shadow copy exposed as '("
                                           + re.sub(ur'[а-яА-Я]+', '', mount_path).
                                           replace('\\', r'\\') + r")\\'", sc_cmd))
                sc_snap_shot[0] = [x[0], mount_path]
                logger.debug(line_number() + 'Ok, shadow copy exposed as ' + sc_snap_shot[0][1])
            except Exception as sc_e:
                logger.error(line_number() + 'Error: ' + sc_e.message +
                             ' , rollback: deleting previously created shadow copies')
                shadow_copy('delete', sc_id)
                logging.error(traceback.format_exc())
                ce_exit(1)
        sc_result.append(sc_snap_shot[0], )
    return sc_result


def date_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def decode_mbcs_utf8(dmu_str, revers=False):
    if not revers:
        if type(dmu_str) is list:
            dmu_result = [dmu_result.encode(sys.getfilesystemencoding()).decode('utf8') for dmu_result in dmu_str]
        else:
            dmu_result = dmu_str.encode(sys.getfilesystemencoding()).decode('utf8')
        return dmu_result
    else:
        if type(dmu_str) is list:
            dmu_result = [dmu_result.encode('utf8').decode(sys.getfilesystemencoding()) for dmu_result in dmu_str]
        else:
            dmu_result = dmu_str.encode('utf8').decode(sys.getfilesystemencoding())
        return dmu_result


def dir_size(ds_path):
    ds_size = 0
    for sub_path, dirs, files in os.walk(ds_path):
        for f in files:
            fp = os.path.join(sub_path, f)
            ds_size += os.stat(fp).st_size
    return ds_size


def clean_backup_dir(cbd_cleaning_plan, cbd_path, file_prefix):
    # clean_backup_dir
    cbd_cleaning_plan = re.split(r'/', cbd_cleaning_plan)
    cbd_cleaning_plan_day = int(cbd_cleaning_plan[0])
    cbd_cleaning_plan_week = int(cbd_cleaning_plan[1])
    cbd_cleaning_plan_month = int(cbd_cleaning_plan[2])
    cbd_dict_weekly = {}
    cbd_dict_month = {}
    only_files = [f for f in os.listdir(cbd_path) if os.path.isfile(os.path.join(cbd_path, f))]
    only_files.sort(reverse=True)
    for tmpFileName in only_files:
        date_file_name = re.search(file_prefix + r'_(\d{8})_\d{6}\.', tmpFileName)
        if date_file_name:
            date_file_name = date_file_name.group(1)
            cbd_year = int(date_file_name[0:4])
            cbd_month = int(date_file_name[4:6])
            cbd_day = int(date_file_name[6:])
            iso_calendar = datetime.date(cbd_year, cbd_month, cbd_day).isocalendar()
            cbd_week_key = str(iso_calendar[0]) + str(iso_calendar[1])
            cbd_month_key = str(cbd_year) + str(cbd_month)
            flag_delete = True
            if cbd_cleaning_plan_day > 0:
                cbd_cleaning_plan_day -= 1
                continue
            if cbd_cleaning_plan_week >= 0 or cbd_dict_weekly.get(cbd_week_key, False):
                if not cbd_dict_weekly.get(cbd_week_key, False):
                    cbd_cleaning_plan_week -= 1
                    flag_delete = False
            if cbd_cleaning_plan_month >= 0 or cbd_dict_month.get(cbd_month_key, False):
                if not cbd_dict_month.get(cbd_month_key, False):
                    cbd_cleaning_plan_month -= 1
                    flag_delete = False
            if flag_delete and cbd_dict_month.get(cbd_month_key, False):
                path_exist([cbd_path + chr(92) + cbd_dict_month.get(cbd_month_key, False)], 'delete')
            else:
                path_exist([cbd_path + chr(92) + tmpFileName], 'delete')
            cbd_dict_weekly[cbd_week_key] = tmpFileName
            cbd_dict_month[cbd_month_key] = tmpFileName


# <editor-fold desc="Config logger">
dirLog = pathToScriptDir + r'\Logs'
if not os.path.exists(dirLog):
    os.makedirs(dirLog)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logFormatterFile = logging.Formatter("\n%(asctime)s %(levelname)s "
                                     "<PID %(process)d:%(processName)s> %(name)s.%(funcName)s():\n%(message)s")
pathLogFile = dirLog + r'\Debug_' + prefixData + '.txt'
fileHandler = logging.FileHandler(pathLogFile)
fileHandler.setFormatter(logFormatterFile)
logger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
logFormatterConsole = logging.Formatter("%(asctime)s %(message)s", "%H:%M")
consoleHandler.setFormatter(logFormatterConsole)
logger.addHandler(consoleHandler)
logger.propagate = False

# noinspection PyUnresolvedReferences
logger.debug(line_number() +
             '\nStart logger'
             + '\nDefault Encoding =   ' + sys.getdefaultencoding()
             + '\nКодировка системы =  ' + locale.getpreferredencoding()
             + '\nКодировка Stdout =   ' + sys.stdout.encoding
             + '\nКодировка Stdin =    ' + sys.stdin.encoding
             + '\nMode script =        ' + str(scriptMode)
             + '\nVersion =            ' + str(version)
             + '\npathToScriptDir =    ' + pathToScriptDir)

ini = IniClass(pathToScriptDir + r'\settings.ini', 'default')
logger.debug(line_number() + 'Ini: file - settings.ini, section - default')
# </editor-fold>

# <editor-fold desc="Create ini-file">
check_connect_DB = CmdClass(False, True)
if scriptMode != 'BackUp':
    while True:
        oraLogin = ini.write('l', (raw_input('Enter login (press Enter to set \'sys\'): ') or 'sys').decode('utf-8'))
        oraPassword = ini.write('p', keyCrypto.encrypt(raw_input('Enter password: ') or ' '))
        oraInstance = ini.write('i', (raw_input('Enter the instance name (press Enter to set \'gas\'): ')
                                      or 'gas').decode('utf-8'))
        connString = '"' + oraLogin + '/' + keyCrypto.decrypt(oraPassword) + '@' + oraInstance + ' as sysdba' + '"'
        check_connect_DB.run('sqlplus -s ' + connString, True)
        if check_connect_DB.write('select banner from v$version;'):
            logger.info(line_number() + 'Connect to the DB Oracle TRUE')
            time.sleep(sleep_delay)
            break
    while True:
        oraHome = (raw_input('Enter name OraHome (press enter to set HOME0): ') or 'HOME0').decode('utf-8')
        oracleBase = reg_get_val('HKEY_LOCAL_MACHINE', r'SOFTWARE\ORACLE' + chr(92) + oraHome, 'ORACLE_BASE',
                                 'OraHome not found in')
        oraPathDirAdmin = '\\'.join((str(oracleBase) + chr(92) + 'admin' + chr(92)).split(r'\\')).strip('\\')
        if path_exist([oraPathDirAdmin]):
            ini.write('oraPathDirAdmin', oraPathDirAdmin)
            break
    while True:
        ini.write('FreeSpace', (raw_input('stop the backup if the free space is less than ??% of the data '
                                          'size (press Enter to set 100%)): ') or '100').decode('utf-8'))
        try:
            FreeSpace = int(ini.read('FreeSpace'))
            break
        except ValueError:
            print("Enter an integer")
    ini.write('CompressMethod', (raw_input('Set compression Method (press Enter to set default -tzip)): ')
                                 or '-tzip').decode('utf-8'))
    ini.write('SuccessfulAutoClose', (raw_input('Close the window on successful completion '
                                                '(y or n, press Enter to set y)): ') or 'y').decode('utf-8'))
    while True:
        ini.write('CleaningPlan', (raw_input('Leave backups of the latest daily/weekly/monthly '
                                             '(press Enter to set 7/4/12)): ') or '7/4/12').decode('utf-8'))
        try:
            CleaningPlan = ini.read('CleaningPlan')
            CleaningPlan = re.split(r'/', CleaningPlan)
            int(CleaningPlan[0])
            int(CleaningPlan[1])
            int(CleaningPlan[2])
            break
        except ValueError:
            print("Enter an integer")
    while True:
        dirBU = raw_input('Enter the path to the backup files: ').decode('utf-8')
        if path_exist([dirBU]):
            ini.write('dirBU', dirBU)
            break

    logger.info(line_number() + 'Ini file crated.')
    raw_input('Ini file crated. To create a backup, run with the key /b. \nPress Enter to exit ... ')
    sys.exit(0)
# </editor-fold>

# <editor-fold desc="Connect to oracle DB, create backup controlfile and shutdown DB">
logger.info(line_number() + 'Connecting to the DB Oracle ...')
sss = bytes(ini.read('p'))
oraLogin, oraPassword, oraInstance, oraPathDirAdmin, dirBU = ini.read('l'), keyCrypto.decrypt(bytes(ini.read('p'))), \
        ini.read('i'), ini.read('oraPathDirAdmin'), ini.read('dirBU')
connString = '"' + oraLogin + '/' + oraPassword + '@' + oraInstance + ' as sysdba' + '"'

check_connect_DB.run('sqlplus -s ' + connString, True)
if check_connect_DB.write('select banner from v$version;'):
    logger.debug(line_number() + 'Ok, connected to the DB Oracle')

logger.info(line_number() + 'Checking the environment ...')
if debugMode:
    prefixName = 'Ora_' + oraInstance.upper()
    pathOraControlFile = r'C:\WINDOWS\TEMP' + chr(92) + prefixName
else:
    prefixName = 'Ora_' + oraInstance.upper() + '_' + prefixData
    pathOraControlFile = os.environ.get('TEMP') + chr(92) + prefixName

mountPoint = dirBU + r'\mountpoint'
pFile = pathOraControlFile + r'\initGAS.ORA'
controlFile = pathOraControlFile + r'\CRGAS.SQL'
pathListFile = pathToScriptDir + r'\ListFile.txt'
vShadow = pathToScriptDir + chr(92) + vShadow
SevenZ = pathToScriptDir + chr(92) + SevenZ

iniFreeSpace = ini.read('FreeSpace')
iniCompressMethod = ini.read('CompressMethod')
iniSuccessfulAutoClose = ini.read('SuccessfulAutoClose')
if iniSuccessfulAutoClose.lower() == 'y':
    iniSuccessfulAutoClose = True
else:
    iniSuccessfulAutoClose = False
iniCleaningPlan = ini.read('CleaningPlan')

if not (path_exist([dirBU, mountPoint, pathOraControlFile], 'create')
        and path_exist([vShadow, SevenZ, oraPathDirAdmin], 'check')):
    ce_exit(1)
elif not debugMode:
    if not path_exist([pFile, controlFile], 'delete'):
        ce_exit(1)

check_connect_DB.return_std_out = True
check_connect_DB.run('sqlplus -s ' + connString, True)
SqlListFileDB = check_connect_DB.write('SET LINES 150 PAGES 999 '
                                       '\nCOL NAME FORMAT A110'
                                       '\nSELECT NAME, BYTES'
                                       '\nFROM (SELECT NAME, BYTES FROM V$DATAFILE'
                                       '\nUNION ALL'
                                       '\nSELECT NAME, BYTES FROM V$TEMPFILE'
                                       '\nUNION ALL'
                                       '\nSELECT LF.MEMBER "NAME", L.BYTES'
                                       '\nFROM V$LOGFILE LF, V$LOG L'
                                       '\nWHERE LF.GROUP# = L.GROUP#) USED,'
                                       '\n(SELECT SUM (BYTES) AS POO FROM DBA_FREE_SPACE) FREE'
                                       '\n/\n')

run_sql_query = check_connect_DB
logger.info(line_number() + 'Creating a controlfile ...')
run_sql_query.run('sqlplus -s ' + connString, True)
# noinspection PyTypeChecker
if run_sql_query.write(r"Alter database backup controlfile to trace as '" + decode_mbcs_utf8(pFile) + r"';"):
    logger.debug(line_number() + 'Ok, alter database backup controlfile to trace as ' + decode_mbcs_utf8(pFile))

logger.info(line_number() + 'Creating a pfile ...')
run_sql_query.run('sqlplus -s ' + connString, True)
# noinspection PyTypeChecker
if run_sql_query.write(r"Create pfile='" + decode_mbcs_utf8(controlFile) + "' from spfile;"):
    # noinspection PyTypeChecker
    logger.debug(line_number() + 'Ok, create pfile=' + decode_mbcs_utf8(controlFile) + ' from spfile')

try:
    SqlListFileDB = SqlListFileDB + chr(10) \
                    + decode_mbcs_utf8(pFile) + '\t' + str(os.path.getsize(decode_mbcs_utf8(pFile))) + chr(10) \
                    + decode_mbcs_utf8(controlFile) + '\t' + str(os.path.getsize(decode_mbcs_utf8(controlFile))) \
                    + chr(10) + decode_mbcs_utf8(oraPathDirAdmin) + '\t' \
                    + str(dir_size(decode_mbcs_utf8(oraPathDirAdmin))) + chr(10)
except Exception as e:
    logger.error(line_number() + 'Error: ' + e.message)
    ce_exit(1)

check_connect_DB.return_std_out = False

tmpListFileDB = ''
tmpShadowDisk = ''
bool_flag = SqlListFileDB
fullSize = 0.0
if bool_flag:
    listFileDB = SqlListFileDB.splitlines()

    for el_list in listFileDB:
        tmp = re.match(r'(\w:\\[^\t]*)\s*(\d*)', el_list, re.I)
        if tmp:
            if not (tmp.group(1).strip()[-4:].lower() == '.ctl' or tmp.group(1)[-10:].lower() == 'temp01.dbf'):
                fullSize += int(tmp.group(2).strip())
                tmp = tmp.group(1).strip()
                tmpListFileDB = tmp + '|' + tmpListFileDB
                tmpShadowDisk = tmp[:2] + '|' + tmpShadowDisk
listFileDB = tmpListFileDB[:-1].split('|')
ShadowDisk = tuple(set(tmpShadowDisk[:-1].split('|')))

logger.info(line_number() + 'Check free space ...')
hdd = psutil.disk_usage(dirBU[:2])
freeSpace = round(float(hdd.free) / 2 ** 30, 2)
fullSize = round(float(fullSize / 2 ** 30), 2)
logger.debug(line_number() + 'Free space available: ' + str(freeSpace) + ' Gb, data size: ' + str(fullSize) + ' Gb, '
             + 'control point free space: ' + str(fullSize * int(iniFreeSpace) / 100))
if fullSize * int(iniFreeSpace) / 100 > freeSpace:
    logger.info(line_number() + 'Not enough free space ...')
    ce_exit(100)

logger.info(line_number() + 'Shutdown database ...')
run_sql_query.run('sqlplus -s ' + connString, True)
if run_sql_query.write(r"Shutdown immediate;"):
    logger.debug(line_number() + 'Ok, shutdown immediate')
    Ora_DB_Shutdown = True
# </editor-fold>

mount = ''
try:
    logger.info(line_number() + 'Creating shadow copy ...')
    SnapShot = shadow_copy('create', ShadowDisk)
    logger.info(line_number() + 'Mount shadow copy ...')
    mount = shadow_copy('mount', SnapShot)
except BaseException as e:
    logger.error(line_number() + 'Error: ' + e.message)
    ce_exit(1)

logger.info(line_number() + 'Startup database ...')
run_sql_query.run('sqlplus -s ' + connString, True)
if run_sql_query.write(r"Startup;"):
    logger.debug(line_number() + 'Ok, startup')
    Ora_DB_Shutdown = False

fileBu = oraInstance + '_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.zip'
try:
    listFile = ''
    dctMount = dict(mount)
    # print dctMount
    for path in listFileDB:
        # xcv = decode_mbcs_utf8(path)
        listFile += '"' + dctMount[path[:2]] + path[2:] + '"' + chr(10)
    # print listFile
    listFile += '"' + pathListFile + '"' + chr(10)
    with codecs.open(pathListFile, 'w', "utf-8") as fileListFile:
        fileListFile.write(listFile)
        fileListFile.close()
    logger.info(line_number() + 'Create backup ')
    time.sleep(sleep_delay)
    print '\nCommand:        7z.exe a ' + iniCompressMethod + ' -bsp1 ' \
          + '\nDestination:    ' + dirBU + chr(92) + fileBu \
          + '\nSource:         ' + pathListFile + '\n'
    cmd7z = CmdClass(True, True).run('7z.exe a ' + iniCompressMethod + ' -bsp1 "' + dirBU + chr(92) + fileBu
                                     + '" -i@"' + pathListFile + '"', False, True)
    print '\n'
except OSError as e:
    logging.error(traceback.format_exc())
    time.sleep(sleep_delay)
    ce_exit(1)

logger.info(line_number() + 'Unmount shadow copy ...')
deletedSnapShot = shadow_copy('delete', SnapShot)
logger.info(line_number() + 'Remove temp folders ...')
path_exist([controlFile, pFile, pathOraControlFile, pathListFile], 'delete')

logger.info(line_number() + 'Cleaning the backup and log folder  ...')
clean_backup_dir(iniCleaningPlan, dirBU, oraInstance)
clean_backup_dir(iniCleaningPlan, dirLog, 'Debug')

time_end_script = datetime.datetime.now()
logger.info(line_number() + 'Started at     ' + time_start_script.strftime('%d.%m.%Y %H:%M:%S'))
logger.info(line_number() + 'Finished at    ' + time_end_script.strftime('%d.%m.%Y %H:%M:%S'))
time_work_script = time_end_script - time_start_script
# full length of the string - 46, length '21:07 #566 Duration:' - 21, time_work_script milliseconds - 7
len_space = 46 - 21 - len(str(time_work_script)[:-7])
logger.info(line_number() + 'Duration:' + ' ' * len_space + '{}'.format(str(time_work_script))[:-7] + '\n')

os.system('copy /y ' + pathLogFile + ' ' + pathLogFile[:-4] + '.log > null')
logger.info(line_number() + 'Add log file to archive')
cmd = CmdClass(False, True).run('7z.exe a "' + dirBU + chr(92) + fileBu + '" "'
                                + pathLogFile[:-4] + '.log' + '"', False, True)

path_exist([pathLogFile[:-4]], 'delete')
if iniSuccessfulAutoClose:
    sys.exit()
else:
    logger.info(line_number() + 'Backup completed\n')
    raw_input('Enter to exit ... ')
sys.exit()
