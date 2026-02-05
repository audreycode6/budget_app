def validate_request_body_keys_exist(keys, body):
    for key in keys:
        if key not in body:
            return False
    return True


def stringify_attributes(list_of_attributes):
    """
    return formatted join of attributes
    """
    return ", ".join(list_of_attributes)
