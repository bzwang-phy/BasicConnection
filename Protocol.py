#!/usr/bin/env python3

import sys, os
import struct
import select
import logging
import threading
import socket


"""
HEAD STRUCT:
+----+-------+-------+------+
|TYP | STATE |  LEN  | DATA |
+----+-------+-------+------+
| 1  |   1   |   4   |  m   |
+----+-------+-------+------+

TYP: command(0x01), file(0x02), Tcp stream(0x03)
STATE:  0x01(request), 0x02(response)
LEN:
DATA:   command or filename.
"""

# state(1 byte) :
# STATE_COMM = 0      # waiting for communication.
# STATE_FILE = 1      #
# STATE_STREAM = 3

TYPE_COMMAND = b'\x01'
TYPE_FILE = b'\x02'
TYPE_STREAM = b'\x03'
STATE_REQUEST = b'\x01'
STATE_RESPONSE = b'\x02'
LEN_HEADER = 6


class MessageSocket(object):
    # This class is used to package the (client) socket with "Message" protocol.

    def __init__(self, sock, is_server=False, poll=None, conns=None):
        self.sock = sock
        self.sock_fd = self.sock.fileno()
        self.is_server = is_server
        if is_server:
            self.conns = conns
            self.epoll = poll
            self.sock.setblocking(0)
            self.epoll.register(self.sock_fd, select.EPOLLIN)
            self.conns[self.sock_fd] = self

    def handle_event(self, event):
        if event & select.EPOLLIN:
            data = self.sock.recv(1024)
            if data:
                if data[0] == 0x01: # command
                    self.command_handler(data)
                elif data[0] == 0x02: # file
                    pass
                elif data[0] == 0x03: # Tcp stream
                    pass
            # if client closed, we still get a POLLIN and return "".
            if not data:
                self.destroy()

    def command_handler(self, data):
        while len(data) < LEN_HEADER:
            data += self.sock.recv(1024)
        length, = struct.unpack(">I", data[2:6])
        while len(data[LEN_HEADER:]) < length:
            data += self.sock.recv(1024)
        # receiving data finished and begin to analyse.
        if data[1] == 0x01:   # request
            cmd, = struct.unpack(">"+str(length)+"s", data[LEN_HEADER:])
            cmd = str(cmd, encoding='utf-8')
            print(os.system(cmd))
            # self.sock.sendall(response)
        elif data[1] == 0x02:    #response
            response = data[3:]
            print(response)
        else:
            logging.ERROR("The format of data received is wrong.")

    def file_handler(self):
        pass

    def command_send(self, state, command):
        header = TYPE_COMMAND + state
        length = len(command)
        header += struct.pack(">I", length)
        command = bytes(command, encoding='utf-8')
        data = struct.pack(">"+str(length)+"s", command)
        data = header + data
        self.sock.sendall(data)

    def destroy(self):
        self.sock.close()
        if self.is_server:
            self.epoll.unregister(self.sock_fd)
            del self.conns[self.sock_fd]



