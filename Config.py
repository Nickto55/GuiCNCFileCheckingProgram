from dateutil.utils import today


def outputFileDef():
    output_file = f"BD_CNCprog_{today}"
    if not output_file.endswith(".xlsx"):
        output_file += ".xlsx"
    return f"{output_file}"
