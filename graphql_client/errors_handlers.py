from ast import literal_eval


def extract_error_message(error: str, default_message: str) -> str:
    try:
        return literal_eval(error)["message"]

    except (KeyError, TypeError):
        return default_message
