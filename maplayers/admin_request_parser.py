def convert_text_to_dicts(text):
        arr = text.rsplit("\n")
        filter_func = lambda t : t.__contains__('=')
        text_with_equals_sign = _extract_first_set(filter(filter_func, arr))
        region_details = {}
        for string in text_with_equals_sign:
            key,value = string.split("=")
            region_details[key.strip()] = value.strip()
        return region_details
        
def _extract_first_set(listOfDetails):
    return listOfDetails[:17]
        