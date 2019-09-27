#!/usr/bin/env python3

import sys, os
import logging
import socket
import select
import threading
import protocol

# 0. command control,
# 1. resume from break-point
# 2. Multithreading
# 3. support Windows.


class EpollServer(object):
    def __init__(self, port):
        self.connections = {}
        self.requests = {}
        self.responses = {}
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.epoll = select.epoll()
        self.server_sock_run(port)

    def server_sock_run(self, port):
        try:
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.setblocking(0)
            self.server_sock.bind(('', port))
            self.server_sock.listen(5)
            self.epoll.register(self.server_sock.fileno(), select.EPOLLIN)
        except Exception as err:
            print("Something wrong to prepare server socket: %s".format(err))
            sys.exit(1)

    def run(self):
        while True:
            events = self.epoll.poll(4)
            for fd, event in events:
                if fd == self.server_sock.fileno():
                    client_sock, client_addr = self.server_sock.accept()
                    protocol.MessageSocket(client_sock, is_server=True, poll=self.epoll, conns=self.connections)
                    logging.info("a connection from %s".format(client_addr))
                else:
                    wrapped_sock = self.connections.get(fd, None)
                    if wrapped_sock:
                        wrapped_sock.handle_event(event)
                    else:
                        logging.warning("Wrapped socket doesn't exist.")

    def write_sock(self, fd):
        while len(self.responses.setdefault(fd, '')):
            length = self.connections[fd].send(self.responses[fd])
            self.responses[fd] = self.responses[fd][length:]

    def read_sock(self, fd):
        self.requests[fd] = self.connections[fd].recv(1024)
        with open("1.png", "ba+") as f:
            f.write(self.requests[fd])
        # print("data received: ", requests[fd])
        # if client closed, we still get a EPOLLIN and return "".
        if not self.requests[fd]:
            self.connections[fd].close()
            del self.connections[fd]
            del self.requests[fd]
            self.epoll.unregister(fd)

    def remove_sock(self, fd):
        self.epoll.unregister(fd)
        self.connections[fd].close()
        del self.connections[fd]
        del self.requests[fd]


class MultiProcServer(object):
    def __init__(self, port):
        self.port = port


class ThreadServer(object):
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
        connections = {}
        requests = {}
        responses = {}
        while True:
            try:
                client_sock, client_addr = self.sock.accept()
            except Exception:
                print("something wrong in the sock.accept().")


if __name__ == "__main__":
    server = EpollServer(9190)
    server.run()
