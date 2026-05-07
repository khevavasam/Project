import ujson
import os

HISTORY_DIR = "history"

# Create a folder if it does not exist
if HISTORY_DIR not in os.listdir():
    os.mkdir(HISTORY_DIR)


def save_file(filename: str, json_data):
    """Saves a JSON string or dictionary to a file."""
    if isinstance(json_data, dict):
        json_data = ujson.dumps(json_data)
    path = f"{HISTORY_DIR}/{filename}.txt"
    print(f"Saving {filename} to {path}")
    with open(path, "w") as f:
        f.write(json_data)


def trim_history(max_files):
    """Keeps only the newest HRV/KUBIOS result files."""
    files = [f for f in list_files() if f.startswith("HRV ") or f.startswith("KUBIOS ")]

    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            if _file_time(files[j]) < _file_time(files[i]):
                files[i], files[j] = files[j], files[i]

    while len(files) > max_files:
        oldest = files.pop(0)
        path = "{}/{}.txt".format(HISTORY_DIR, oldest)
        print("Removing old history:", path)
        os.remove(path)


def _file_time(filename):
    path = "{}/{}.txt".format(HISTORY_DIR, filename)
    try:
        return os.stat(path)[8]
    except:
        return _file_number(filename)


def list_files():
    """Returns a list of all .txt file names in the history folder (without extensions)."""
    files = [f[:-4] for f in os.listdir(HISTORY_DIR) if f.endswith(".txt")]

    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            if _file_number(files[j]) < _file_number(files[i]):
                files[i], files[j] = files[j], files[i]

    return files


def _file_number(filename):
    if filename.startswith("MEASUREMENT "):
        try:
            return int(filename.split("MEASUREMENT ")[1])
        except:
            pass
    if filename.startswith("HRV "):
        try:
            return int(filename.split("HRV ")[1])
        except:
            pass
    if filename.startswith("KUBIOS "):
        try:
            return int(filename.split("KUBIOS ")[1])
        except:
            pass
    return 999999


def open_file(filename: str) -> dict:
    """Opens a file and returns a dictionary (parsed JSON)."""
    path = f"{HISTORY_DIR}/{filename}.txt"
    with open(path, "r") as f:
        return ujson.loads(f.read())


def quick_save(json_data):
    """Quickly saves JSON to the next file: MEASUREMENT X.txt"""
    print("quick_save")
    existing = list_files()
    max_id = 0
    for name in existing:
        if name.startswith("MEASUREMENT "):
            try:
                num = int(name.split("MEASUREMENT ")[1])
                if num > max_id:
                    max_id = num
            except:
                continue
    next_id = max_id + 1
    print(f"Next ID: {next_id}")
    save_file(f"MEASUREMENT {next_id}", json_data)
    return f"MEASUREMENT {next_id}"
