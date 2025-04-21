function actionRefreshDirectory() {
    loadDirPath(window.activeFileDir);
}
function actionActivateDirectory(event) {
    var dpath = event.target.innerHTML;
    window.activeFileDir += dpath + "/";
    loadDirPath(window.activeFileDir);
}
function actionActivateParentDirectory(event) {
    var components = window.activeFileDir.split("/");
    if (components.length <= 2) return;
    components.splice(components.length - 2, 1);
    window.activeFileDir = components.join("/");
    loadDirPath(window.activeFileDir);
}
function actionCreateNewDirectory(event) {
    function createdDir(response) {
        loadDirPath(window.activeFileDir);
    }
    var dname = prompt("New directory name (in: " + window.activeFileDir + ")");
    if (dname) {
        dpath = window.activeFileDir + dname;
        showNotification("Creating directory: " + dpath);
        fetch("/newdir?path=" + dpath).then(response => response.json()).then(json => createdDir(json));
    }
}

function actionCreateNewFile(event) {
    var fname = prompt("New file name (in: " + window.activeFileDir + ")");
    if (fname) {
        fpath = window.activeFileDir + fname;
        showNotification("Creating file: " + fpath);
        fetch("/newfile?path=" + fpath)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                console.log('Success creating file:', data);
                // Load the newly created file
                return fetch("/file?path=" + fpath);
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(text => {
                loadedFile(fpath, text);
                loadDirPath(window.activeFileDir);  // Refresh directory listing
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification("Error: " + error, 4);
            });
    }
}
function actionActivateFile(event) {
    var fpath = window.activeFileDir + event.target.innerHTML;
    console.log("[DEBUG] Starting to load file:", fpath);
    showNotification("Loading file: " + fpath);
    
    fetch("/file?path=" + fpath)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();  // Get text instead of JSON
        })
        .then(text => {
            loadedFile(fpath, text);
        })
        .catch(error => {
            console.error("[DEBUG] Error loading file:", error);
            showNotification("Error loading file: " + error, 4);
        });
}
function actionSaveFile(callback) {
    showNotification("Saving file: " + window.activeFilePath);
    fetch('/savefileb', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
            'File-Path': window.activeFilePath
        },
        body: globalEditor.getValue(),
    })
    .then((response) => response.json())
    .then((data) => {
        console.log('Success saving:', data);
        showNotification("Saved", 1);
        if (callback) {
            callback();
        }
    })
    .catch((error) => {
        console.error('Error saving:', error);
        showNotification("Error saving file: " + error, 4);
    });
}
function actionSaveRunFile() {
    let fname = window.activeFilePath.split("/").filter(v=>v.length>0).join(".");
    if (!fname.endsWith(".py")) {
        showNotification("Can only run python files", 1);
        return;
    }
    fname = fname.substring(0, fname.length-3);
    actionSaveFile(function() {
        fetch("/run?name=" + fname).then(response => response.json()).then(json => {
            showNotification("Running file " + fname, 1);
        });
    });
}
function actionStop() {
    showNotification("Stopping active 'process'", 1);
    fetch("/run?stop=1").then(response => response.json()).then(json => {
        showNotification("Stopped", 1);
    });
}
function actionDeleteFile() {
    if (!window.activeFilePath) {
        showNotification("No file selected", 2);
        return;
    }

    if (!confirm("Are you sure you want to delete " + window.activeFilePath + "?")) {
        return;
    }

    showNotification("Deleting file: " + window.activeFilePath);
    
    fetch("/deletefile?path=" + window.activeFilePath)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            console.log('Success deleting:', data);
            showNotification("File deleted", 1);
            // Reset to root directory
            loadDirPath("/");
        })
        .catch(error => {
            console.error('Error deleting:', error);
            showNotification("Error deleting file: " + error, 4);
        });
}
function actionRenameFile() {
    if (!window.activeFilePath) {
        showNotification("No file selected", 2);
        return;
    }

    var newName = prompt("New name for " + window.activeFilePath + ":");
    if (!newName) {
        return;
    }

    // Get the directory path and construct new full path
    var dirPath = window.activeFilePath.substring(0, window.activeFilePath.lastIndexOf('/') + 1);
    var newPath = dirPath + newName;

    showNotification("Renaming file to: " + newPath);
    
    fetch("/renamefile?old_path=" + window.activeFilePath + "&new_path=" + newPath)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            console.log('Success renaming:', data);
            showNotification("File renamed", 1);
            // Load the renamed file
            return fetch("/file?path=" + newPath);
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(text => {
            loadedFile(newPath, text);
            loadDirPath(window.activeFileDir);  // Refresh directory listing
        })
        .catch(error => {
            console.error('Error renaming:', error);
            showNotification("Error renaming file: " + error, 4);
        });
}
function actionResetDevice() {
    if (!confirm("Are you sure you want to reset the device?")) {
        return;
    }

    showNotification("Resetting device...");
    
    fetch("/reset")
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            console.log('Device reset initiated');
            showNotification("Device is resetting, waiting for reconnect...", 4);
            
            // Try to reconnect every 3 seconds
            let attempts = 0;
            const maxAttempts = 20; // Try for about 1 minute
            const checkConnection = () => {
                attempts++;
                fetch("/info")
                    .then(response => {
                        if (response.ok) {
                            console.log('Device is back online');
                            window.location.reload();
                        } else {
                            throw new Error('Device not ready');
                        }
                    })
                    .catch(error => {
                        console.log('Reconnect attempt ' + attempts + ' failed');
                        if (attempts < maxAttempts) {
                            setTimeout(checkConnection, 3000);
                        } else {
                            showNotification("Could not reconnect to device. Please reload manually.", 4);
                        }
                    });
            };
            
            // Start checking after 5 seconds to give device time to reset
            setTimeout(checkConnection, 5000);
        })
        .catch(error => {
            console.error('Error resetting device:', error);
            showNotification("Error resetting device: " + error, 4);
        });
}
