import subprocess
import sys
import os
import time
import signal


def main():
    env = os.environ.copy()
    app_proc = subprocess.Popen([sys.executable, 'app.py'], env=env)
    bot_proc = subprocess.Popen([sys.executable, 'bot.py'], env=env)
    procs = [app_proc, bot_proc]
    try:
        while all(p.poll() is None for p in procs):
            time.sleep(0.5)
    except KeyboardInterrupt:
        for p in procs:
            try:
                p.send_signal(signal.SIGINT)
            except Exception:
                pass
    finally:
        for p in procs:
            p.wait()


if __name__ == '__main__':
    main()
