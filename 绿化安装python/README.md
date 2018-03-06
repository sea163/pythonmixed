方便在动态拨号服务器上部署python

步骤:
1)从system32复制 python*.dll 到python根目录
2)从system32复制 (pywin32) pythoncom*.dll pywintypes*.dll
3)修改 vars.bat, install_py.cmd, install_py.py 中的路径信息
4)压缩打包

重新部署只需要解压到对应目录执行 install_py.cmd 后重启即可