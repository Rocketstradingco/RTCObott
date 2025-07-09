import subprocess
import sys
import os
import time
import signal
from dotenv import load_dotenv # Add this line

def main():
    load_dotenv() # Add this line to load .env file
    env = os.environ.copy()
    if not env.get('DISCORD_TOKEN'):
        print('Error: DISCORD_TOKEN not set. Check your .env file.')
        return
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