#!/user/bin/python
# -*- coding: utf-8 -*-
'''
python3 socket 文件传输----客户端（Windows版本）：
v1.0.6
1、添加根目录下文件夹复制、打包、传递
2、win32con 监控类型：创建、复制、删除、修改、重命名、写入等
3、只监控最后写入
4、实现功能：文件夹复制传递、单文件创建传递
-------------------------------------------------
v1.5:
1、监控指定文件夹变化
2、瓶颈在文件大小：即写文件时间，如果读取文件时，
    文件没有写入完成，就会报错。
    解决方法：添加等待时间time.sleep(3)#等待3秒
'''
import socket, os, time, logging
import zipfile
import sys
import win32file
import win32con

socket = socket.socket()
socket.connect(("127.0.0.1", 9999))
SIZE = 1024 * 1024 * 2000

print(socket.recv(SIZE))
print("sending please wait for a second....")

ACTIONS = {
    1: "Created",
    2: "Deleted",
    3: "Updated",
    4: "Renamed from something",
    5: "Renamed to something"
}
FILE_LIST_DIRECTORY = 0x0001

#监控的文件夹
path_to_watch = 'E:\\temp'
print('Watching changes in', path_to_watch)
hDir = win32file.CreateFile(
    path_to_watch,
    FILE_LIST_DIRECTORY,
    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
    None,
    win32con.OPEN_EXISTING,
    win32con.FILE_FLAG_BACKUP_SEMANTICS,
    None
)

def make_zip(source_dir, output_filename):
    zipf = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)  # 相对路径
            zipf.write(pathfile, arcname)
    zipf.close()
    return output_filename

def sendFile(absolutePath, relativePath, filetype):
    print("---absolutePath---", absolutePath)
    print("---relativePath---", relativePath)
    if filetype == "zip":
        absPathTemp = absolutePath.replace(path_to_watch + "\\", "")
        socket.sendall(bytes(absPathTemp, encoding="gbk"))
    else:
        socket.sendall(bytes(relativePath, encoding="gbk"))
    f2 = open(absolutePath, 'rb')
    socket.sendall(bytes(f2.name, encoding="gbk"))
    data = f2.read(SIZE)
    socket.sendall(data)
    f2.close()

while 1:
    results = win32file.ReadDirectoryChangesW(
        hDir,
        1024,
        True,  # 是否监控文件夹tree
        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,  # 文件修改通知：最后写入
        None,
        None)
    print(results)
    print("--------")
    for action, filename in results:
        full_filename = os.path.join(path_to_watch, filename)
        print(full_filename, ACTIONS.get(action, "Unknown"))
        print("action", action)
        # action: 1 创建 2 删除 3更新 4 重命名前（Renamed from something） 5 重命名后（Renamed to something）
        if action == 3 or action == 5:
            print("permission =======")
            print(full_filename)
            time.sleep(2)  # 睡眠时间：等待文件复制完成
            try:
                if os.path.exists(full_filename) and os.path.isfile(full_filename):

                    # 发送单个文件
                    sendFile(full_filename, filename, "other")
                elif os.path.exists(full_filename) and os.path.isdir(full_filename) and len(results) == 1:
                    print("folder name--", results[0][1])
                    # 压缩文件夹
                    tempZipFile = make_zip(full_filename, path_to_watch + "\\" + results[0][1] + ".zip")
                    # 发送单个文件
                    sendFile(tempZipFile, filename, "zip")
                    os.remove(tempZipFile)

            except Exception as e:
                logging.error("文件打开异常...")
                logging.exception(e)
            finally:
                pass
print("sended!")
socket.close()
print("connection closed")
