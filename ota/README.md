# PERFORM UPDATE

- Code changes
- > ota/generate_filelist.sh
- commit

This esp micropython robot project is now publicly hosted on github. Let's work on a KISS OTA.

How about a bash script that creates a list of all files in micropython/

Then save this list in the repo.

Next we add a button in the @index.html sidebar-footer "UPDATE". This uses the built in @microWebSrv.py .

It then calls a function which 
- gets the file list from github
- checks for newer files with different size (is there a file date in micropython?, if not possible update all) and update them
- reboot

what do you think about it? any better ideas? don't write code yet


## DEBUG

# Manual Execution:
from lib.ota import OTAUpdater
updater = OTAUpdater()
updater.update_all()

# Try local request
import urequests
try:
    print("\nTrying local network request...")
    # Replace with your router's IP if different
    response = urequests.get("http://10.10.46.1")
    print("Response status:", response.status_code)
    response.close()
except Exception as e:
    print("Error:", e)


# Try a simple HTTP request first
import urequests
try:
    print("\nTrying simple HTTP request...")
    response = urequests.get("http://httpbin.org/get")
    print("Response status:", response.status_code)
    print("Response content:", response.text)
    response.close()
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'errno'):
        print("Error number:", e.errno)



# Try manual request
import urequests
try:
    print("\nTrying simple HTTP request...")
    response = urequests.get("http://xwk.ull.at/projects/xwk-bot/filelist.json")
    print("Response status:", response.status_code)
    print("Response content:", response.text)
    response.close()
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'errno'):
        print("Error number:", e.errno)