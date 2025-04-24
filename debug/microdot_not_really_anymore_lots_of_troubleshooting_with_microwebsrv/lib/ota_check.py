import os
import machine
import bot

def check_and_update():
    """Check for OTA update flag, increment attempts, and perform update with failsafe"""
    # Early exit if no flag exists
    if 'ota_flag.txt' not in os.listdir():
        print("ota_check: no flag file found.")
        return False

    # Read and increment attempt count
    try:
        with open('ota_flag.txt', 'r') as f:
            attempt_count = int(f.read().strip())
    except (OSError, ValueError) as e:
        print(f"Error reading OTA flag, starting at 0: {str(e)}")
        attempt_count = 0

    attempt_count += 1
    print(f"OTA update attempt {attempt_count} of 3...")

    # Write incremented count back to file
    try:
        with open('ota_flag.txt', 'w') as f:
            f.write(str(attempt_count))
    except OSError as e:
        print(f"Error writing OTA attempt count: {str(e)}")

    # Failsafe: abort after 3 attempts
    if attempt_count > 3:
        print("Failsafe triggered: OTA update failed after 3 attempts. Clearing flag and aborting.")
        bot.write("OTA update failed 3 times", color=bot.RED)
        bot.write("Try again in webbrowser", color=bot.GREY)
        try:
            os.remove('ota_flag.txt')
        except OSError as e:
            print(f"Error removing OTA flag: {str(e)}")
        return False

    # Perform the update
    try:
        from lib.ota import OTAUpdater
        updater = OTAUpdater()
        bot.write("OTA update please wait...", color=bot.RED)
        bot.write("If stuck please reset", color=bot.GREY)
        success = updater.update_all()
    except Exception as e:
        print(f"OTA update attempt {attempt_count} failed: {str(e)}")
        success = False

    # Handle result
    if success:
        print("OTA update completed successfully, clearing flag...")
        try:
            os.remove('ota_flag.txt')
        except OSError as e:
            print(f"Error removing OTA flag after success: {str(e)}")
        return True
    else:
        print(f"OTA update attempt {attempt_count} failed. Flag retained for next attempt.")
        return False

# Run the check
if check_and_update():
    machine.reset()