#!/usr/bin/env python3

import sys, os
import struct
import select
import logging
import threading
import socket


class FileClient(object):
    # This class would be created in client to transfer files.

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.read_lock = threading.Lock()
        self.write_lock = threading.Lock()

        self.MIN_BLOCK = 1 * 1024 * 1024       # minimum block is set as 10K.
        self.MAX_BLOCK =  10 * 1024 * 1024
        self.MAX_THREAD = 60             # maximum number of thread is set as 40.

    def InitialStatus(self, fp, threadNum=None):
        self.fPath = fp
        self.fName = os.path.basename(fp)
        self.fSize = os.path.getsize(fp)

        if self.fSize > (self.MAX_THREAD * self.MAX_BLOCK):
            self.blockSize = self.MAX_BLOCK
        elif self.fSize < self.MIN_BLOCK:
            self.blockSize = self.MIN_BLOCK
        else:
            self.blockSize = self.MIN_BLOCK 

        if threadNum is None:
            self.threadNum = 40
        else:
            self.threadNum = threadNum
            


    def Status(self):
        pass

    # use multi-threading to send file to (host,port).
    def SendFile(self, file_path):
        # multi-threading parameter initialization.
        threads = []
        fd_read = open(self.fName, "rb")
        # start multi-threading.
        for i in range(self.threadNum):
            start = i * self.blockSize
            end = (i + 1) * self.blockSize
            if i == thread_num - 1:
                end = file_size
            sock = socket_conn(self.ip, self.port)
            threads.append(threading.Thread(target=self.thread_run, name=str(i), args=(fd_read, sock, start, end)))
        for i in range(thread_num):
            threads[i].start()
        for i in range(thread_num):
            threads[i].join()
        print("pid: ", os.getpid(), " send file finished.")
        fd_read.close()
        sys.exit(0)

    # read from fd_read and write to fd_write with [start, end)
    def ThreadRun(self, fd_read, fd_write, start, end):
        chunk_size = 1 * 1024 * 1024  # block size read each time, may affect the speed, the bigger the better.
        while True:
            if start + chunk_size >= end:
                chunk_size = end - start
            # use lock to protect fd_read.seek
            self.read_lock.acquire()
            fd_read.seek(start)
            data = fd_read.read(chunk_size)
            self.read_lock.release()
            fd_write.sendall(data)  # For socket.

            start = start + chunk_size
            if start >= end:
                # add the code to check the file in server.
                fd_write.close()
                break
        return 0


def socket_conn(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock
    except Exception as err:
        print("Something wrong to prepare socket: %s".format(err))
        sys.exit(1)


class FileServerThread(object):
    def __init__(self, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('', port))
            self.sock.listen(5)
        except Exception as err:
            print("Something wrong to prepare socket: %s".format(err))
            sys.exit(1)

    def run(self):
        while True:
            try:
                client_sock, client_addr = self.sock.accept()
            except Exception:
                print("something wrong in the sock.accept().")
            t = threading.Thread(target=self.handle, args=(client_sock, client_addr))
            t.setDaemon(True)
            t.start()
    
    def handle(self):
        pass




class FileThreadPool(object):
    pass