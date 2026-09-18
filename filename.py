def to_filename_format( str ):
    sanitized_str = str.replace(".", "_").replace("/", "_")
    split_spaces = sanitized_str.split(" ")
    lower_case = [ word.lower() for word in split_spaces ]
    connect = '_'.join(lower_case)
    return connect

def get_recordname( artist, title ):
    return f"record.{to_filename_format(artist)}.{to_filename_format(title)}"