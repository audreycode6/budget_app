def format_float_to_usd(num):
    return f"${num:,.2f}"


def validate_request_body_keys_exist(keys, body):
    for key in keys:
        if key not in body:
            return False
    return True
