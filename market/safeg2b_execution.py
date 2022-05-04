
import elevate, os, ctypes, subprocess

def __logger():
    import logging
    return logging.getLogger(f"{__package__}.safeg2b")

def safeg2b_get_exe_filename():
    return "G2BLauncher.exe"

def safeg2b_get_exe_directory():
    return "C:\\WINDOWS\\pps\\SafeG2B"

def safeg2b_is_running():
    
    ss = str(subprocess.check_output('tasklist', shell=True))
    filename = safeg2b_get_exe_filename()
    return filename in ss

def safeg2b_run():
    if safeg2b_is_running():
        __logger().info("SafeG2B is already running")
        return

    if not ctypes.windll.shell32.IsUserAnAdmin():
        __logger().info("Need privileged permission. Elevate.")
        elevate.elevate(show_console=False)    

    filename = safeg2b_get_exe_filename()
    directory = safeg2b_get_exe_directory()
    __logger().info("Start SafeG2B.")
    os.system(f"cd {directory} && start {os.path.join(directory, filename)}") 

if __name__ == "__main__":
    if not safeg2b_is_running():
        print("Run SafeG2B")
        safeg2b_run()
    else:
        print("Already Running")

