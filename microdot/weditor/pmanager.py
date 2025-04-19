import uio
import uos
import sys
import time
import _thread
import machine
import gc

import time

# Global stop flag
should_stop = False

class Term(uio.IOBase):
    def __init__(self):
        super().__init__()
        # more stuff here
        # self.toread = 2
        self.buff = b""#testing\x03"
        self.boff = 0
        self.reads = 0
        self.writes = 0
        self.writel = []

    def readinto(self, buf):
        self.reads += 1
        if len(self.buff) - self.boff > 0:
            buf[:] = self.buff[self.boff:self.boff+len(buf)]
            self.boff += len(buf)
            return len(buf)
        else:
            return 0 # None - continue

    def write(self, buf):
        self.writes += 1
        self.writel.append(str(buf))
    
    def send_buffer(self, buff):
        self.buff = buff
        self.boff = 0
        uos.dupterm_notify(None)


class ProgramThread:
    def __init__(self, module_name):
        self.module_name = module_name
        self.running = False
        self.thread_id = None

    def run(self):
        global should_stop
        self.running = True
        should_stop = False
        self.thread_id = _thread.get_ident()
        print(f"Starting program thread for {self.module_name}")
        try:
            # Read the module file
            with open(self.module_name + '.py', 'r') as f:
                code = f.read()
            
            # Split into lines and execute each line
            lines = code.split('\n')
            for line in lines:
                if should_stop:
                    break
                if line.strip() and not line.strip().startswith('#'):
                    try:
                        exec(line)
                    except Exception as e:
                        print(f"Error executing line: {str(e)}")
                time.sleep(0.1)  # Give chance for stop check
                
        except Exception as e:
            print(f"Error in program thread: {str(e)}")
        finally:
            self.running = False
            print(f"Program thread for {self.module_name} ended")

    def stop(self):
        global should_stop
        if self.running and self.thread_id:
            print(f"Stopping program thread for {self.module_name}")
            should_stop = True
            
            # Wait a bit for thread to notice stop flag
            time.sleep(0.2)
            
            # If still running, try to exit thread
            if self.running:
                print("Thread still running, attempting exit")
                _thread.exit()
            
            self.running = False
            print("Thread marked as stopped")

# Global program thread
current_program = None

def start_program(module_name):
    global current_program
    # Stop any running program
    if current_program:
        current_program.stop()
    
    # Create and start new program thread
    current_program = ProgramThread(module_name)
    _thread.start_new_thread(current_program.run, ())

def stop_program():
    global current_program
    if current_program:
        current_program.stop()
        current_program = None

def restart_process(pname):
    start_program(pname)

def stop_process():
    stop_program()
