#!/user/bin/python
# -*- coding: utf-8 -*-
'''
python3 socket 文件传输--服务端（Windows版本）：
v1.0.6
1、添加压缩文件接收、解压、清除
2、主要功能：文件夹接收、单文件接收、多层次单文件接收
-----------------------------------------
v1.5:
1、接收客户端传递过来的文件
'''
import socket, os, logging, time
import zipfile
from datetime import datetime

socket = socket.socket()
socket.bind(("127.0.0.1", 9999))
socket.listen(20)
SIZE = 1024 * 1024 * 2000
# 保存文件的路径
savepath = "D:\\workspace\\python\\demo\\sc1\\py_s\\ss\\"

def Service():
    while True:
        conn, addr = socket.accept()
        print('Accept new connection from %s:%s...' % addr)
        conn.sendall(bytes("Welcome from server!", encoding="utf-8"))
        print(conn)
        try:
            while True:

                relPath = str(conn.recv(1024), encoding="gbk")
                absPath = str(conn.recv(1024), encoding="gbk")
                print("---relPath---", relPath)
                # 创建文件夹
                lastLocation = relPath.rfind("\\")
                if lastLocation > 0:
                    fp = relPath[0:lastLocation]
                    folderPath = os.path.join(savepath, fp)
                    if not os.path.isdir(folderPath):
                        os.makedirs(folderPath)

                print("---absPath---", absPath)
                f_dir = os.path.split(absPath)[0]
                fname = os.path.split(absPath)[1]
                fnameSave = os.path.join(savepath, relPath)
                # fnameSave = os.path.join(savepath, fname)
                print("fnameSave==", fnameSave, os.path.isfile(fnameSave))

                locateTemp = fnameSave.rfind("\\")
                sRelPath = fnameSave[0: locateTemp]

                absPathTemp = absPath.split(".")
                absType = absPathTemp[len(absPathTemp) - 1]

                if absType != "zip" and not os.path.isdir(savepath):
                    os.makedirs(savepath)
                ff = open(fnameSave, 'wb')  # 按照配置的路径进行存储
                starttime = datetime.now()
                print("start...")
                recvdata = conn.recv(SIZE)
                if not recvdata:
                    print("reach the end of file")
                    break
                else:
                    ff.write(recvdata)
                ff.close()

                listTmep = fnameSave.split(".")
                fileType = listTmep[len(listTmep) - 1]
                if fileType == "zip":
                    print("zip文件，请解压...", fnameSave)
                    zf = zipfile.ZipFile(fnameSave, "r")
                    for file in zf.namelist():
                        zf.extract(file, sRelPath)
                    zf.close()
                    os.remove(fnameSave)
                endtime = datetime.now()
                print("end...花费时间(s)", (endtime - starttime).seconds)
        except Exception as e:
            logging.error("服务器异常...")
            logging.exception(e)
        finally:
            conn.close()

    print("receive finished")
    print("connection from %s:%s closed." % addr)

if __name__ == '__main__':
    Service()
