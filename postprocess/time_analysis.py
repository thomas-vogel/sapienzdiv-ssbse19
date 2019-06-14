# author: Thomas Vogel


def get_duration(app_folder_path):
    try:
        duration_file = open(app_folder_path + "/intermediate/duration.txt")
        lines = duration_file.readlines()
        for idx, line in enumerate(lines):
            duration = float(line)
    except:
        duration = -1
    return duration