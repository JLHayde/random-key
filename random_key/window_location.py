import win32gui
import win32process
import psutil


def get_process_name(pid):
    try:
        return psutil.Process(pid).name()
    except Exception:
        return "Unknown"


def find_minecraft_window():
    def callback(hwnd, results):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if "minecraft" in title.lower():
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                proc = psutil.Process(pid)
                proc_name = proc.name()
                # Print for debugging
                print(f"Found title: {title}, hwnd: {hwnd}, proc: {proc_name}")
                results.append((hwnd, title, proc_name, pid))
            except psutil.NoSuchProcess:
                pass
        return True

    results = []
    win32gui.EnumWindows(callback, results)
    return results


def get_window_rect(hwnd):
    return win32gui.GetWindowRect(hwnd)
