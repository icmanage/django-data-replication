def get_compute_secs(item):
    try:
        hours, minutes, secs = item.split(":")
    except (ValueError, AttributeError):
        pass
    else:
        try:
            return int(hours) * 3600 + int(minutes) * 60 + int(secs)
        except ValueError:
            pass
    return 0
