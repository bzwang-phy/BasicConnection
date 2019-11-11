#!/usr/bin/env python3

import sys, os
import struct
import select
import logging
import threading
import socket


class PlainBox(object):
    def __init__(self, sockIn):
        self.sockIn = sockIn
        self.sockOut = None
    
    hand


class SOCKS5(object):
    # This class is used to package the (client) socket with SOCKS5 protocol.
    HEAD_STRUCT = ">c256sQ"
    SIZE_STRUCT = struct.calcsize(HEAD_STRUCT)

    def __init__(self, client_sock, poll):
        self.sock = client_sock
        self.epoll = poll
        self.sock.setblocking(0)
        self.epoll.register(self.sock.fileno(), select.EPOLLIN)

    def handle_event(self, event):
        pass





class StreamSocket(object):
    pass