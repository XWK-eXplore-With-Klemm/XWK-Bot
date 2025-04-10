import network
import time
import os
import urequests

# WiFi credentials - replace with your actual credentials
WIFI_SSID = "ullwpa"
WIFI_PASSWORD = "oldenburg"

# Phew file URLs and paths
PHEW_FILES = [
    {
        "url": "https://raw.githubusercontent.com/pimoroni/phew/main/phew/__init__.py",
        "path": "/lib/phew/__init__.py"
    },
    {
        "url": "https://raw.githubusercontent.com/pimoroni/phew/main/phew/server.py",
        "path": "/lib/phew/server.py"
    },
    {
        "url": "https://raw.githubusercontent.com/pimoroni/phew/main/phew/template.py",
        "path": "/lib/phew/template.py"
    },
    {
        "url": "https://raw.githubusercontent.com/pimoroni/phew/main/phew/dns.py",
        "path": "/lib/phew/dns.py"
    }
]

def ensure_directory(path):
    """Create directory if it doesn't exist"""
    try:
        dirs = path.rstrip('/').split('/')
        current_dir = ''
        for d in dirs:
            if d:
                current_dir += '/' + d
                try:
                    os.mkdir(current_dir)
                except OSError:
                    # Directory might already exist
                    pass
    except Exception as e:
        print(f"Error creating directory {path}: {e}")

def download_file(url, path):
    """Download a file from url and save it to path"""
    try:
        print(f"Downloading {url} to {path}")
        response = urequests.get(url)
        if response.status_code == 200:
            # Ensure the directory exists
            dir_path = '/'.join(path.split('/')[:-1])
            ensure_directory(dir_path)
            
            # Write the file
            with open(path, 'w') as f:
                f.write(response.text)
            print(f"Successfully downloaded {path}")
        else:
            print(f"Failed to download {url}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    finally:
        response.close()

def connect_wifi():
    """Connect to WiFi network using provided credentials"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f'Connecting to WiFi network "{WIFI_SSID}"...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection with timeout
        max_wait = 10
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print("Waiting for connection...")
            time.sleep(1)
            
    if wlan.isconnected():
        print("Network Config:", wlan.ifconfig())
        return True
    else:
        print("Failed to connect to WiFi")
        return False

def download_phew():
    """Download all phew files"""
    print("Starting phew download...")
    for file in PHEW_FILES:
        download_file(file["url"], file["path"])
    print("Phew download complete")

# Main execution
if connect_wifi():
    download_phew()
else:
    print("Cannot download phew files - no WiFi connection")



