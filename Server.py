#!/usr/bin/env python3

import sys, os
import logging
import socket
import select
import threading
import FileTranfer


if __name__ == "__main__":
    server = FileTranfer.FileServerThread(9190)
    server.run()

