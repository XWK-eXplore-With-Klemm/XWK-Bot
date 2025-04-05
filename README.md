# XWK-Bot

https://github.com/XWK-eXplore-With-Klemm/XWK-Bot

Website with manual etc: https://xwk.ull.at


## Troubleshooting

import gc
print("Memory Free:", gc.mem_free())
print("Memory Allocated:", gc.mem_alloc())
print("Memory Total:", gc.mem_free() + gc.mem_alloc())
gc.collect()  # Force garbage collection
print("Memory after GC:", gc.mem_free())


## Upload file

 mpremote cp micropython/lib/ota.py :/lib/