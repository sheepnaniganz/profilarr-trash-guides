def _get_safe_name(name, remove_not=False):
    result = name
    if remove_not:
        result = result.replace("Not ", "")
    return (
        result.replace("/", "-")
        .replace("[", "(")
        .replace("]", ")")
        .replace("HDR10Plus", "HDR10+")
        .replace("10 bit", "10bit")
        .replace("Atmos", "ATMOS")
        .strip()
    )


def get_name(service, name, remove_not=False):
    return f"{service.capitalize()} - {_get_safe_name(name, remove_not)}"
