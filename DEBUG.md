# MEMORY

```python
#Fresh ESP32-Wroom-32 with Micropython v1.24.1

import gc
print("Memory Free:", gc.mem_free())
gc.collect()  # run garbage collection to free ram
print("Memory Free:", gc.mem_free())

import micropython
micropython.mem_info()
micropython.mem_info(1)

# stack: 736 out of 15360
# GC: total: 56000, used: 8400, free: 47600, max new split: 110592
# No. of 1-blocks: 176, 2-blocks: 21, max blk sz: 32, max free sz: 2964

# Show which modules are loaded:
import sys
print(sys.modules)

```

## What happens on import?

Example for 30kB lib:

- Disk to RAM: MicroPython reads bot.py (30 KB) from flash/storage into RAM temporarily to parse it.
- Parsing into Abstract Syntax Tree, then compiled into bytecode. 30 KB .py file typically compiles to ~5-15 KB of bytecode which is permanently allocated in memory.

```python
import bot                              # Memory Free: 80352 = uses 77791bytes
gc.collect()                            # Memory Free: 127376 = uses 30768bytes
```

## Unload modules

```python
to_unload = ['bot', 'sysfont', 'hcsr04', 'flashbdev', 'ini_parser', 'ST7735']
for mod in to_unload:
    if mod in sys.modules:
        del sys.modules[mod]
del bot  # Remove from namespace
gc.collect()
print(sys.modules)                      # []
print("Memory Free:", gc.mem_free())    # Memory Free: 153552
```

# NON-BLOCKING / MULTITASKING

## Timer

```python
def start(self):
    """Start the menu with a timer"""
    if self.timer is None:
        bot.write("Press A to select program", color=bot.WHITE)
        self.timer = Timer(1)  # Use timer 1
        self.timer.init(period=100, mode=Timer.PERIODIC, callback=self.check)  # Check every 200ms
```     

## Threads _thread

- Preemptive multitasking using the _thread module
- Each thread gets a stack (~8-16 KB default on ESP32, configurable but minimum ~2 KB).

```python
import _thread
import time
def blink():
    while True:
        print("Blink")
        time.sleep(1)
_thread.start_new_thread(blink, ())  # Start thread
```



## uasyncio 

- Event Loop: A single-threaded loop schedules tasks, avoiding the RAM cost of multiple threads.
- Memory: Base uasyncio uses ~5-10 KB, plus ~1-5 KB per task, depending on complexity.
- Cooperative multitasking using coroutines and an event loop. Single-threaded, tasks yield control at await points.

```python
import uasyncio
async def blink():                      # = coroutine meaning it can pause execution (yield control) at specific points (e.g., await) and resume later.
    while True:
        print("Blink")
        await uasyncio.sleep(1)         # Non-blocking delay
                                        # await suspends blink, yielding control back to the event loop.
                                        # The event loop adds a task to wake blink after 1 second, using a timer (no busy-waiting).
uasyncio.run(blink())
```
