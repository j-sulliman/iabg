def intersight_get(resource_path, private_key,
                   public_key, query_params=None, host='https://intersight.com'):
    # Import "intersight_rest" Package
    import intersight_rest as isREST
    # Import JSON Package
    import json
    import pprint as pp
    # Load Public/Private Keys
    isREST.set_private_key(private_key)
    isREST.set_public_key(public_key)
    # Load host
    # isREST.intersight_rest.host = 'https://intersight.com/api/v1'
    isREST.intersight_rest.host = (host if host.endswith('/api/v1') else f'{host + "/api/v1"}')

    if query_params != None:
        options = {
            "http_method": "get",
            "resource_path": resource_path,
            "query_params": query_params
        }
    elif query_params == None:
        options = {
            "http_method": "get",
            "resource_path": resource_path
        }

    # -- Send GET Request --#
    try:
        results = isREST.intersight_call(**options)
        # print("Status Code: " + str(results.status_code))
        print("Status code {}, for resource path {}".format(results.status_code, resource_path))
        results = results.json()

    except ValueError:
        print("RSA Key error - check intersight private and public keys.")
        results = None
        pass

    return results
