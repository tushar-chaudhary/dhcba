from flask import request
from functools import wraps

class Flask_docs:

    def __init__(self):
        pass

    def get_description(self,app,rule):
        @wraps(rule)
        def func(*args, **kwargs):
            if rule:
                pass

            return func(*args, **kwargs)

        # for rule in app.url_map.iter_rules():
        #     pass


    def from_app(self,app,all_method=False):

        for rule in app.url_map.iter_rules():
            if all_method:
                methods = (list(rule.methods))
            else:
                method = []
                if "GET" in rule.methods:
                    method.append("GET")
                if "POST" in rule.methods:
                    method.append("POST")
                methods = (method)
            url = (rule)
            line = ("{:50s} {:20s} {}".format(str(rule.endpoint), str(methods), str(url)))
            print(line)
