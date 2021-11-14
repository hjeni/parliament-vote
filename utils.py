import os


def mkdir_safe(dir_path):
    """
    Creates directory at given path when it doesn't already exist
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


def get_dir_size(path):
    """
    Returns size of a directory at given path in bytes.
    """
    size = 0
    for d, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(d, f)
            size += os.path.getsize(fp)
    return size


def print_progress(current, start, end=None, log_every=250):
    """
    Prints information about the progress of a task
    """
    if current % log_every != (start - 1) % log_every:
        return

    complete = current - start + 1
    total = '?' if end is None else end - start
    ratio = '?' if end is None else round(complete / total * 100, 2)
    print(f'[PROGRESS] {complete}/{total} ~ {ratio} % complete. ID: {current}')





