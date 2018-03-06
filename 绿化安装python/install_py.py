#!/usr/bin/python
#coding=utf-8
#-------------------------------------------------------------------------------
# Name:        绿化安装python34
# Purpose:
#
# Author:      sea
#
# Created:     06-03-2018
# Copyright:   (c) sea 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import sys
import shutil
from subprocess import check_call
if sys.hexversion > 0x03000000:
    import winreg
else:
    import _winreg as winreg

#python 安装目录
PYTHON_PATH = "C:\\Python34"
#PYTHON_PATH = os.getcwd() #获得当前工作目录

class Win32Environment:
    """Utility class to get/set windows environment variable"""

    def __init__(self, scope):
        assert scope in ('user', 'system')
        self.scope = scope
        if scope == 'user':
            self.root = winreg.HKEY_CURRENT_USER
            self.subkey = 'Environment'
        else:
            self.root = winreg.HKEY_LOCAL_MACHINE
            self.subkey = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'

    def getenv(self, name):
        key = winreg.OpenKey(self.root, self.subkey, 0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, name)
        except WindowsError:
            value = ''
        return value

    def setenv(self, name, value):
        # Note: for 'system' scope, you must run this as Administrator
        key = winreg.OpenKey(self.root, self.subkey, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)
        # For some strange reason, calling SendMessage from the current process
        # doesn't propagate environment changes at all.
        # TODO: handle CalledProcessError (for assert)
        check_call('''\"%s" -c "import win32api, win32con; assert win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')"''' % sys.executable)

def setEnvironmentPath():
    '''
    设置环境路径
    '''
    print("设置更新 PATH...")
    env = Win32Environment(scope="system")
    pathList = env.getenv('PATH').split(';') #获取当前环境路径
    newPathList = [PYTHON_PATH, os.path.join(PYTHON_PATH, "Scripts")] #加入新的python执行路径
    newPathList.extend( [value for value in pathList if not ("python" in value.lower())]) #如果已经存在python路径则剔除掉
    newPath = ";".join(newPathList)
    print("新 PATH 值: " + newPath)
    env.setenv('PATH', newPath)

def copyFilesToSystem():
    '''
    复制文件到系统
    '''
    system32Path = os.path.join(os.environ["WINDIR"], "system32")
    print("复制文件到 " + system32Path)
    shutil.copy(os.path.join(PYTHON_PATH, "python34.dll"),  system32Path)
    pywin32_path = os.path.join(PYTHON_PATH, "Lib\site-packages\pywin32_system32")
    shutil.copy(os.path.join(pywin32_path, "pythoncom34.dll"),  system32Path)
    shutil.copy(os.path.join(pywin32_path, "pywintypes34.dll"),  system32Path)


def main():
    copyFilesToSystem()
    setEnvironmentPath()
    pass

if __name__ == '__main__':
    main()
