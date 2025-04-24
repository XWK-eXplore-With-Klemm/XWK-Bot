function initEditor() {
    document.getElementById("action-rename").style.display = 'none';
    document.getElementById("action-delete").style.display = 'none';
    document.getElementById("action-save").style.display = 'none';
    document.getElementById("action-save-run").style.display = 'none';
    document.getElementById("action-stop").style.display = 'none';
    var editor = ace.edit("editor");
    window.globalEditor = editor;
    editor.setTheme("ace/theme/dracula");
    editor.session.setMode("ace/mode/plain_text");
    editor.setValue("\n<- Select a file to edit\n");
    window.editor = editor;
    loadDirPath("/");
    // updateTitle();
    initSplitter();
}

function initSplitter() {
    const splitter = document.getElementById('splitter');
    const term = document.getElementById('term');
    let startY;
    let startHeight;

    function onStart(e) {
        // Get starting position from either mouse or touch event
        startY = e.type === 'mousedown' ? e.clientY : e.touches[0].clientY;
        startHeight = parseInt(document.defaultView.getComputedStyle(term).height, 10);

        if (e.type === 'mousedown') {
            document.documentElement.addEventListener('mousemove', onMove);
            document.documentElement.addEventListener('mouseup', onEnd);
        } else {
            document.documentElement.addEventListener('touchmove', onMove);
            document.documentElement.addEventListener('touchend', onEnd);
        }
    }

    function onMove(e) {
        e.preventDefault(); // Prevent scrolling on touch devices
        const currentY = e.type === 'mousemove' ? e.clientY : e.touches[0].clientY;
        const delta = startY - currentY;
        const newHeight = Math.max(40, Math.min(window.innerHeight - 200, startHeight + delta));
        term.style.height = newHeight + 'px';
        editor.resize();
    }

    function onEnd(e) {
        document.documentElement.removeEventListener('mousemove', onMove);
        document.documentElement.removeEventListener('mouseup', onEnd);
        document.documentElement.removeEventListener('touchmove', onMove);
        document.documentElement.removeEventListener('touchend', onEnd);
    }

    splitter.addEventListener('mousedown', onStart);
    splitter.addEventListener('touchstart', onStart);
}

function showNotification(text, seconds) {
    var notification = document.getElementById("notification");
    notification.innerHTML = text;
    notification.style.display = "block";
    if (seconds) {
        setTimeout(hideNotification, seconds * 1000);
    }
}
function hideNotification() {
    var notification = document.getElementById("notification");
    notification.style.display = "none";
}

function loadedFile(fname, lines) {
    console.log("[DEBUG] Starting to load into editor:", {
        filename: fname,
        contentLength: lines.length
    });
    
    try {
        editor.setValue(lines);
        console.log("[DEBUG] Content set in editor");
        
        var components = fname.split(".");
        var mode = "plain_text";
        if (components.length > 1) {
            let display = "none";
            var ext = components[components.length - 1];
            if (ext == "py") { mode = "python"; display = "inline-block"; }
            if (ext == "html") mode = "html";
            if (ext == "css") mode = "css";
            if (ext == "js") mode = "javascript";

            document.getElementById("action-save-run").style.display = display;
            document.getElementById("action-stop").style.display = display;
        }
        editor.session.setMode("ace/mode/" + mode);
        console.log("[DEBUG] Editor mode set to:", mode);
        
        window.activeFilePath = fname;
        window.activeFileName = fname;
        document.getElementById("active-path").innerHTML = fname;
        document.getElementById("action-rename").style.display = 'inline-block';
        document.getElementById("action-delete").style.display = 'inline-block';
        document.getElementById("action-save").style.display = 'inline-block';
        
        editor.selection.clearSelection();
        showNotification("Loaded: " + fname, 1);
        console.log("[DEBUG] File load complete");
    } catch (error) {
        console.error("[DEBUG] Error loading into editor:", error);
        showNotification("Error loading into editor: " + error, 4);
    }
}

// Files to hide by default
const BLACKLISTED_FILES = [
    'boot.py',
    'config.ini',
    'webrepl_cfg.py',
    '*.json'
];

// Helper function to check if a filename matches a pattern
function matchesPattern(filename, pattern) {
    if (!pattern.includes('*')) {
        return filename === pattern;
    }
    const regex = new RegExp('^' + pattern.replace(/\./g, '\\.').replace(/\*/g, '.*') + '$');
    return regex.test(filename);
}

// Helper function to check if a file should be hidden
function isFileBlacklisted(filename) {
    return BLACKLISTED_FILES.some(pattern => matchesPattern(filename, pattern));
}

let showAllFiles = false;

function loadDirPath(path) {
    window.activeFileDir = path;
    showNotification("Loading directory: " + path);
    fetch("/dir?path=" + path).then(response => response.json()).then(json => updateFileList(json));
}

function updateFileList(json) {
    var files = json.files;
    var dirs = json.dirs;
    var left = document.getElementById("left");
    left.innerHTML = "";
    
    function addSpan(title, className, action) {
        var span = document.createElement("span");
        span.innerHTML = title;
        span.className = className;
        if (action) { span.onclick = action; }
        left.appendChild(span);
    }

    // Show visible files first
    addSpan("PROGRAMS", "left_title");
    addSpan("NEW FILE...", "left_element left_action", actionCreateNewFile);
    for (var fileName of files) {
        if (!isFileBlacklisted(fileName)) {
            addSpan(fileName, "left_element left_file", actionActivateFile);
        }
    }

    // Add toggle button for system files
    addSpan(showAllFiles ? "« LESS" : "MORE »", "left_element left_title mt-1em", function() {
        showAllFiles = !showAllFiles;
        updateFileList(json);  // Refresh the list
    });

    // Show system stuff if expanded
    if (showAllFiles) {
        addSpan("↻ refresh", "left_element left_action", actionRefreshDirectory);
        
        addSpan("DIRS", "left_title");
        if (window.activeFileDir != "/") {
            addSpan("..", "left_element left_dir", actionActivateParentDirectory);
        }
        for (var dirName of dirs) {
            addSpan(dirName, "left_element left_dir", actionActivateDirectory);
        }
        addSpan("NEW DIRECTORY...", "left_element left_action", actionCreateNewDirectory);
        
        addSpan("FILES", "left_title");

        // Show blacklisted files
        for (var fileName of files) {
            if (isFileBlacklisted(fileName)) {
                addSpan(fileName, "left_element left_file", actionActivateFile);
            }
        }
    }

    showNotification("Loaded directory: " + window.activeFileDir, 1);
}

function handleKeyDown(event) {
    if ((event.ctrlKey || event.metaKey) && event.code == 'KeyS') {
        actionSaveFile();
        event.preventDefault();
    }
}
// function updateTitle() {
//     fetch("/info").then(response => response.json()).then(json => document.title = json.name);
// }

