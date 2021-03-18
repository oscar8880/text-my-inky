import os
import requests
import urllib
from flask import Flask, request, redirect, abort, current_app
from PIL import Image, ImageOps
from io import BytesIO
from functools import wraps
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

auth_token = os.environ['TWILIO_AUTH_TOKEN']
pixabay_api_key = os.environ['PIXABAY_API_KEY']
display_environment = os.environ['DISPLAY_ENV']

def validate_twilio_request(f):
    """Validates that incoming requests genuinely originated from Twilio"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Create an instance of the RequestValidator class
        validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN'))

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

@app.route("/sms", methods=['GET', 'POST'])
@validate_twilio_request
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    resp.message('You said: ' + body)

    return str(resp)

@app.route("/image", methods=['GET', 'POST'])
@validate_twilio_request
def fetch_image():
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    encoded_query = urllib.parse.quote_plus(body)
    request_url = "https://pixabay.com/api/?key={}&q={}&min_width=600&min_height=448&orientation=horizontal&safesearch=true".format(pixabay_api_key, encoded_query)
    response = requests.get(request_url).json()
    first_image_url = response['hits'][0]['webformatURL']
    first_image_tags = response['hits'][0]['tags']
    first_image = requests.get(first_image_url)
    img = Image.open(BytesIO(first_image.content))
    resized_image = ImageOps.fit(img,(600,448))
    
    # Start our TwiML response
    resp = MessagingResponse()

    if display_environment == 'TEST':
        # Show image 
        resized_image.show()
        resp.message('Found an image with these tags:{}. But not displaying on Inky.'.format(first_image_tags))
    else:
        # Do pimoroni inky stuff
        resp.message('Displaying image on Inky with these tags:{}.'.format(first_image_tags))

    return str(resp)

@app.route("/")
def info():
    return 'Twilio Flask API'