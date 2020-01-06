#!/usr/bin/env python3

import sys, os
import Handler, ClientClass


if __name__ == "__main__":
    # server = EpollServer(9190)
    # server.run()
    client = ClientClass.TcpClientShell("202.38.88.230", 9190)

