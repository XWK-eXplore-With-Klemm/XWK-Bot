import os
import bot
from machine import Timer

class MenuState:
    def __init__(self):
        self.files = []
        self.current_index = 0
        self.total_files = 0
        self.initialized = False
        self.last_button_state = {'up': False, 'down': False, 'a': False}
        self.timer = None
        self.waiting_for_start = True

    def init_if_needed(self):
        """Initialize menu on first run"""
        if self.initialized:
            return True
            
        if self.waiting_for_start:
            if bot.is_pressed(bot.BUTTON_A):
                self.waiting_for_start = False
            return False
            
        self.files = get_python_files()[:11]  # Limit to 11 files
        self.total_files = len(self.files)
        
        if self.total_files == 0:
            bot.write("No Python files found!", color=bot.RED)
            return False
            
        display_menu(self)  # Initial display
        self.initialized = True
        return True

    def check(self, timer=None):
        """Non-blocking menu update"""
        if not self.init_if_needed():
            return
            
        # Handle button presses with debouncing
        up_pressed = bot.is_pressed(bot.BUTTON_UP)
        down_pressed = bot.is_pressed(bot.BUTTON_DOWN)
        a_pressed = bot.is_pressed(bot.BUTTON_A)
        
        # Only handle button if it was just pressed
        if up_pressed and not self.last_button_state['up']:
            old_index = self.current_index
            self.current_index = (self.current_index - 1) % self.total_files
            display_menu(self, old_index)
            
        if down_pressed and not self.last_button_state['down']:
            old_index = self.current_index
            self.current_index = (self.current_index + 1) % self.total_files
            display_menu(self, old_index)
            
        if a_pressed and not self.last_button_state['a']:
            selected_file = self.files[self.current_index]
            execute_file(selected_file)
            display_menu(self)
        
        # Update button states for next check
        self.last_button_state['up'] = up_pressed
        self.last_button_state['down'] = down_pressed
        self.last_button_state['a'] = a_pressed

    def start(self):
        """Start the menu with a timer"""
        if self.timer is None:
            bot.write("Press A to select program", color=bot.WHITE)
            self.timer = Timer(1)  # Use timer 1
            self.timer.init(period=100, mode=Timer.PERIODIC, callback=self.check)  # Check every 200ms

    def stop(self):
        """Stop the menu"""
        if self.timer is not None:
            self.timer.deinit()
            self.timer = None

def get_python_files():
    """List all .py files in root directory except boot.py, main.py, and webrepl_cfg.py"""
    files = []
    blacklist = ['boot.py', 'main.py', 'webrepl_cfg.py']
    for file in os.listdir('/'):
        if file.endswith('.py') and file not in blacklist:
            files.append(file)
    return sorted(files)

def display_menu(menu_state, old_index=None):
    """Display the file selection menu on TFT with 13 lines"""
    def format_filename(filename, prefix="  "):
        # Max length = 25 chars including prefix
        max_length = 23  # 25 - 2 (prefix length)
        if len(filename) > max_length:
            return prefix + filename[:max_length-2] + ".."
        return prefix + filename
    
    if old_index is None:
        # First display - draw everything
        bot.reset_terminal()
        
        # Line 1: Title
        bot.write("Select a Program:", color=bot.CYAN)
        
        # Lines 2-12: Show up to 11 files
        for i in range(min(11, menu_state.total_files)):
            prefix = "> " if i == menu_state.current_index else "  "
            color = bot.MAGENTA if i == menu_state.current_index else bot.GREY
            bot.write(format_filename(menu_state.files[i], prefix), color=color)
        
        # Fill remaining lines up to line 12 if less than 11 files
        for i in range(11 - min(11, menu_state.total_files)):
            bot.write("")
        
        # Line 13: Controls
        bot.write("UP/DOWN:Select  A:Run", color=bot.WHITE, newline=False) # Don't advance line otherwise the terminal will be reset on the next write
    else:
        # Only update the changed lines
        # Clear and update old selection (remove highlight)
        bot.write(" " * 25, line=old_index+1)  # Clear the entire line first
        bot.write(format_filename(menu_state.files[old_index], "  "), color=bot.GREY, line=old_index+1, newline=False)
        
        # Clear and update new selection (add highlight)
        bot.write(" " * 25, line=menu_state.current_index+1)  # Clear the entire line first
        bot.write(format_filename(menu_state.files[menu_state.current_index], "> "), color=bot.MAGENTA, line=menu_state.current_index+1, newline=False)

def execute_file(filename):
    """Execute the selected Python file"""
    bot.reset_terminal()
    try:
        with open(filename, 'r') as f:
            code = f.read()
        exec(code, globals())
    except Exception as e:
        bot.write("Error:", color=bot.RED)
        bot.write(str(e), color=bot.RED)

# Global menu instance
menu = MenuState()

def start():
    """Start the menu - this is the main entry point"""
    menu.start()

def stop():
    """Stop the menu"""
    menu.stop()
