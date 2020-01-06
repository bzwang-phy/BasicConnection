#!/usr/bin/env python3

import sys, os, time
import logging
import socket
import select
import threading
from collections import defaultdict
import Handler


POLLNULL = 0b00000000
POLLIN = 0b00000001
POLLOUT = 0b00000010
POLLERR = 0b00000100
POLLHUP = 0b00001000
POLLNVAL = 0b00010000

TIMEOUT = 10


class Server(object):
    def __init__(self, port, ip=''):
        if hasattr(select, 'epoll'):
            self.server = EpollServer()
        elif hasattr(select, 'select'):
            self.server = SelectServer()
        elif hasattr(select, 'kqueue'):
            self.server = KqueueServer()
        else:
            raise Exception('can not find any available module in "select" ')
        self.server.init(port)
        self.fdDict = {}   #  fd:(sock,handler)
        self.handler = Handler.CMDMessage
        self.stop = False
    
    def poll(self, timeout=None):
        events = self.server.poll(timeout)
        return events

    def register(self, fd, mode):
        pass
    
    def remove(self, fd, mode):
        pass

    def handleEvent(self, sock, event):
        pass
    
    def run(self):
        while not self.stop:
            try:
                events = self.poll(TIMEOUT)
            except Exception as e:
                logging.info(e)
            # print(events)
            for fd, event in events:
                if fd == self.server.sockfd:
                    clientSock, clientAddr = self.server.sock.accept()
                    clientSock.setblocking(0)
                    clientfd = clientSock.fileno()
                    self.fdDict[clientfd] = (clientSock, self.handler(clientSock))
                    self.server.register(clientfd, POLLIN)
                    logging.info("A connection from %s".format(clientAddr))
                elif event & POLLHUP:
                    self.clear(fd)
                elif event & POLLIN:
                    clientSock, handler = self.fdDict.get(fd, None)
                    if clientSock:
                        data = clientSock.recv(1)
                        if data:
                            handler.in_event(event, data)
                            self.server.modify(fd, POLLIN | POLLOUT | POLLHUP)
                        if not data:
                            handler.notDataN += 1
                            if handler.notDataN > 10:
                                self.clear(fd)
                    else:
                        logging.warning("Something wrong in clientSock.")
                elif event & POLLOUT:
                    pass

    def clear(self, fd):
        self.server.unregister(fd)
        sock = self.fdDict.get(fd, None)[0]
        sock.close()
        del self.fdDict[fd]

                


        




class SelectServer(object):
    def init(self, port):
        self.sock = ListenSocket(port, '')
        self.sockfd = self.sock.fileno()
        self.rSet = set(self.sockfd)
        self.wSet = set()
        self.xSet = set()
    
    # This function is used to obtain all events.
    def poll(self, timeout=None):
        r, w, x = select.select(rSet, wSet, xSet, timeout)
        events = defaultdict(lambda: POLLNULL)
        for fd in r:
            events[fd] |= POLLIN
        for fd in w:
            events[fd] |= POLLOUT
        for fd in x:
            events[fd] |= POLLERR
        return events
    
    def register(self, fd, mode):
        if mode & POLLIN:
            rSet.add(fd)
        if mode & POLLOUT:
            wSet.add(fd)
        if mode & POLLERR:
            xSet.add(fd)
    
    def remove(self, fd, mode):
        if (mode & POLLIN) and (fd in self.rSet):
            self.rSet.remove(fd)
        if (mode & POLLOUT) and (fd in self.wSet):
            self.wSet.remove(fd)
        if (mode & POLLERR) and (fd in self.xSet):
            self.xSet.remove(fd)


class KqueueServer():
    pass


class EpollServer(object):
    def init(self, port):
        self.sock = ListenSocket(port, '')
        self.sockfd = self.sock.fileno()
        print("socket {0} is ready.".format(self.sockfd))
        self.epoll = select.epoll()
        self.epoll.register(self.sockfd, select.EPOLLIN)

    # This function is used to obtain all events.
    def poll(self, timeout=4):
        events = self.epoll.poll(timeout)
        return events
    
    def register(self, fd, mode):
        self.epoll.register(fd, mode)
    
    def unregister(self, fd, mode=None):
        self.epoll.unregister(fd)
    
    def modify(self, fd, mode):
        self.epoll.modify(fd, mode)




    def __init__(self, port=0):
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


def ListenSocket(port, ip=''):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((ip, port))
        sock.listen(5)
    except Exception as err:
        print("Something wrong to prepare socket: %s".format(err))
        sys.exit(1)
    return sock


class ThreadServer(object):
    def __init__(self, port, ip4=''):
        self.sock = ListenSocket(port, ip=ip4)

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

