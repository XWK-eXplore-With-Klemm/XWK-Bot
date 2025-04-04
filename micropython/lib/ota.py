import ujson
import uhashlib
import urequests
import os
from ini_parser import IniParser

class OTAUpdater:
    def __init__(self):
        self.config = IniParser()
        self.filelist_url = None
        self.filelist = None
        
    def load_config(self):
        """Load OTA configuration from config.ini"""
        try:
            with open('/config.ini', 'r') as f:
                self.config.loads(f.read())
            self.filelist_url = self.config.get('OTA_FILELIST')
            if not self.filelist_url:
                print("Error: OTA_FILELIST not configured")
                return False
            print(f"OTA_FILELIST URL: {self.filelist_url}")
            return True
        except Exception as e:
            print("Error loading config:", e)
            return False
            
    def get_filelist(self):
        """Download and parse filelist.json"""
        try:
            print("Downloading filelist...")
            print(f"URL: {self.filelist_url}")
            response = urequests.get(self.filelist_url)
            print(f"Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"Error: HTTP {response.status_code}")
                response.close()
                return False
            self.filelist = ujson.loads(response.text)
            response.close()
            print("Filelist downloaded successfully")
            return True
        except Exception as e:
            print("Error downloading filelist:", e)
            if hasattr(e, 'errno'):
                print(f"Error number: {e.errno}")
            return False
            
    def get_file_hash(self, filename):
        """Calculate MD5 hash of a file"""
        try:
            md5 = uhashlib.md5()
            with open(filename, 'rb') as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    md5.update(chunk)
            return ''.join(['{:02x}'.format(b) for b in md5.digest()])
        except Exception as e:
            print(f"Error calculating hash for {filename}:", e)
            return None
            
    def update_file(self, rel_path, remote_size, remote_hash):
        """Update a single file if needed"""
        local_path = f"/{rel_path}"
        
        # Check if file exists
        try:
            local_size = os.stat(local_path)[6]
        except OSError:
            local_size = 0
            
        print(f"\nChecking {rel_path}:")
        print(f"  Remote size: {remote_size}, Local size: {local_size}")
        
        # If sizes match, check hash
        if local_size == remote_size:
            local_hash = self.get_file_hash(local_path)
            if local_hash == remote_hash:
                print("  File is up to date")
                return True
                
        # Download and update file
        try:
            print("  Downloading new version...")
            url = f"{self.filelist_url.rsplit('/', 1)[0]}/{rel_path}"
            print(f"  Download URL: {url}")
            response = urequests.get(url)
            print(f"  Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: HTTP {response.status_code}")
                response.close()
                return False
                
            # Save file
            with open(local_path, 'wb') as f:
                f.write(response.content)
            response.close()
            
            print("  File updated successfully")
            return True
        except Exception as e:
            print(f"  Error updating file:", e)
            if hasattr(e, 'errno'):
                print(f"  Error number: {e.errno}")
            return False
            
    def update_all(self):
        """Update all files that need updating"""
        if not self.load_config():
            return False
            
        if not self.get_filelist():
            return False
            
        success = True
        for rel_path, file_info in self.filelist['files'].items():
            if not self.update_file(rel_path, file_info['size'], file_info['hash']):
                success = False
                
        return success 