#!/usr/bin/env python3

import sys, os
import ServerClass


if __name__ == "__main__":
    server = ServerClass.Server(port=9190)
    server.run()

