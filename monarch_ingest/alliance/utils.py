from typing import Optional


def get_data(entry, path) -> Optional[str]:
    """
    Given a dot delimited JSON tag path,
    returns the value of the field in the entry.

    :param entry:
    :param path:
    :return: str value of the given path into the entry
    """
    ppart = path.split(".")

    tag = ppart.pop(0)
    while True:
        if tag in entry:
            entry = entry[tag]
        else:
            return None
        if len(ppart) == 0:
            return entry
        else:
            tag = ppart.pop(0)
