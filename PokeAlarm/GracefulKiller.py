import signal
import time
import logging

log = logging.getLogger('Manager')

class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        log.error("inited")

    def exit_gracefully(self, signum, frame):
        log.error("hello")
        self.kill_now = True
