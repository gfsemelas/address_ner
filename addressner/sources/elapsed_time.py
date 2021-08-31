def elapsed_time(t):
    """
    Function to print a time in nanoseconds in format 00:00:00.

    :param t: time
    :return:
    """
    hours, rem = divmod(t, 3600)
    minutes, seconds = divmod(rem, 60)
    return '{:0>2}:{:0>2}:{:0>2}'.format(int(hours), int(minutes), round(seconds))
