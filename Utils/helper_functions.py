import time


# Generic class to repeatedly try something
def repeated_try(callback, function_name, **kwargs):
    max_try = 5
    try_count = 0
    success = False
    ret = None
    while try_count < max_try:
        try:
            ret = callback(**kwargs)
            success = True
            break
        except Exception as e:
            print("Warning, Error in repeated try of function " + function_name + ": " + str(e) +
                  "...trying again (" + str(try_count) + "/" + str(max_try) + "...")
            try_count += 1
            time.sleep(1)

    assert success

    return ret
