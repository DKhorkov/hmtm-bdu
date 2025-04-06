from ast import literal_eval


def extract_error_message(error: str, default_message: str) -> str:
    try:
        if str(literal_eval(error)["message"]).startswith("permission denied: User with Email=") \
                and str(literal_eval(error)["message"]).endswith("has not confirmed it"):

            return "permission denied: User with this email has not confirmed it"

        return literal_eval(error)["message"]

    except (KeyError, TypeError):
        return default_message
