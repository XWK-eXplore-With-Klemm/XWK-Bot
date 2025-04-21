https://github.com/vsolina/micropython-web-editor/tree/development

For WeMos LOLIN D32 ESP32 WROOM 32

# TODO
FIRMWARE:
- Captive portal
- AP: Mode: write AP with pulsing background?

- What is weditor/pmanager.py?
- weditor/start.py remove hardcoded bot.stop/shutup etc. separate custom file?
- script.js: make blacklist customizable per project "BLACKLISTED_FILES"
- Make shell a bit larger (higher)
- Make "New file" and "new dir" a button


PCB:
- Reverse on-off labels
- Bigger and better labels for buttons
- Bigger and better labels for battery terminals!!!
- Bigger LOGO



# SYNC CODE WITH XWKBOT

## Just copy
- weditor/js/actions.js   (new actions delete,rename,reset)
- weditor/js/script.js    (console splitter, new actions, filters file mgr 
- weditor/index.html      (title, new actions, splitter, editor config, call webrepl_auto.js
- weditor/style.css
- weditor/xwk-logo.png

## Copy and adapt
- weditor/start.py        (chunked load/save!!!, customized stop action, new actions, mem usage log)
-                         (remove hardcoded bot.stop/shutup)

## New in xwkbot
- weditor/js/webrepl_auto.js (auto enter password to auto activate console)


# SYNC BACK TO XWKBOT

script.js: wildcard blacklist for *.json
```
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
```

# Command line tools (for AI)

Upload files:
```bash
ampy --port /dev/ttyUSB0 put lib/pixel_painter_lib.py /lib/pixel_painter_lib.py
```

Reset ESP32:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 run
```

