from flask import Flask, request, redirect, abort, current_app
from functools import wraps
from twilio.request_validator import RequestValidator

def validate_twilio_request(auth_token):
    def validate_twilio_request_decorator(f):
        """Validates that incoming requests genuinely originated from Twilio"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create an instance of the RequestValidator class
            validator = RequestValidator(auth_token)

            # Validate the request using its URL, POST data,
            # and X-TWILIO-SIGNATURE header
            request_valid = validator.validate(
                request.url,
                request.form,
                request.headers.get('X-TWILIO-SIGNATURE', ''))
            print(request_valid)

            # Continue processing the request if it's valid (or if DEBUG is True)
            # and return a 403 error if it's not
            if request_valid or current_app.debug:
                return f(*args, **kwargs)
            else:
                return abort(403)
        return decorated_function
    return validate_twilio_request_decorator
