import ujson
import uhashlib
import urequests
import os
import gc
from iniconf import Iniconf

""" Manual Execution:
from lib.ota import OTAUpdater
updater = OTAUpdater()
updater.update_all()
"""

class OTAUpdater:
    def __init__(self):
        self.config = Iniconf()
        self.filelist_url = None
        self.base_url = None
        self.filelist = None
        
    def load_config(self):
        """Load OTA configuration from config.ini"""
        try:
            self.filelist_url = self.config.get('OTA_FILELIST')
            if not self.filelist_url:
                print("Error: OTA_FILELIST not configured")
                return False
            
            self.base_url = self.config.get('OTA_BASE_URL')
            if not self.base_url:
                print("Error: OTA_BASE_URL not configured")
                return False
                
            print(f"OTA_FILELIST URL: {self.filelist_url}")
            print(f"OTA_BASE_URL: {self.base_url}")
            return True
        except Exception as e:
            print("Error loading config:", e)
            return False
            
    def get_filelist(self):
        """Download and parse filelist.json"""
        try:
            print(f"Downloading filelist from URL: {self.filelist_url}")
            
            headers = {
                'User-Agent': 'XWK-Bot OTA Updater',
                'Accept': 'application/json'
            }
            
            response = urequests.get(self.filelist_url, headers=headers)
            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error: HTTP {response.status_code}")
                response.close()
                return False
                
            content = response.text
            self.filelist = ujson.loads(content)
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
            # Only suppress ENOENT (file not found) error
            if str(e) == "[Errno 2] ENOENT":
                return None
            print(f"Error calculating hash for {filename}:", e)
            return None
            
    def update_file(self, rel_path, remote_size, remote_hash):
        """Update a single file if needed"""
        local_path = f"/{rel_path}"
        
        print(f"Checking {rel_path}: ", end='')
        
        try:
            local_hash = self.get_file_hash(local_path)
            if local_hash == remote_hash:
                print("unchanged")
                return True
            elif local_hash is None:
                print("new file")
            else:
                print(f"\n  Remote hash: {remote_hash}, Local hash: {local_hash}")
        except OSError:
            print("new file")
                
        try:
            url = f"{self.base_url}/{rel_path}"
            print(f"  Downloading {url}")
            
            headers = {
                'User-Agent': 'XWK-Bot OTA Updater',
                'Accept': '*/*'
            }
            
            response = urequests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"  Error: HTTP {response.status_code}")
                response.close()
                return False
                
            dir_path = '/'.join(local_path.split('/')[:-1])
            if dir_path:
                current_dir = ''
                for part in dir_path.split('/'):
                    if part:
                        current_dir = f"{current_dir}/{part}" if current_dir else f"/{part}"
                        try:
                            os.mkdir(current_dir)
                        except OSError:
                            pass
                
            CHUNK_SIZE = 1024
            with open(local_path, 'wb') as f:
                while True:
                    chunk = response.raw.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    gc.collect()
            
            response.close()
            gc.collect()
            
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
                
        if success:
            print("Update successful!")
        return success