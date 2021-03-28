from functools import wraps
from django.http import HttpResponseRedirect


def authors_only(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        token = request.headers.get('Authorization', " ").split(' ')[1]
        decoded_payload = jwt_decode_handler(token)

        try:
            userId = decoded_payload['user_id']
            return function(request, *args, **kwargs)
        except ValidationError as v:
            return v
        else:
            return HttpResponseRedirect('/')

    return wrap

 
class MyDecorator: 
    def __init__(self, function): 
        self.function = function 
      
    def __call__(self, *args, **kwargs): 
  
        # We can add some code  
        # before function call 
  
        self.function(*args, **kwargs) 
  
        # We can also add some code 
        # after function call. 
      
  
