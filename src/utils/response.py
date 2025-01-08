from http.client import responses

def check_response(my_response, response):
    status_code = response.status_code
    if type(my_response) == str:
        try:
            if int(my_response) == status_code:
                return True
        except ValueError:
            if my_response == responses[status_code]:
                return True
    try:
        json = response.json()
        if my_response == json:
            return True
        if type(my_response) == str and my_response in json:
            return True
        if type(my_response) == str and my_response in json.values():
            return True
    except Exception:
        pass
    return False