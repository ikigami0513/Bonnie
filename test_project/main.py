import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from Bonnie.server import BonnieHTTPServer

if __name__ == "__main__":
    server = BonnieHTTPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
