import os
import requests
import urllib
from flask import Flask, request, redirect, abort, current_app
from datetime import datetime
from PIL import Image, ImageOps
from io import BytesIO
from threading import Thread
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from ratelimit import limits, RateLimitException
from auth import validate_twilio_request
from display import inky_display
from error import NoImagesError, DisplayTimingError

load_dotenv()

app = Flask(__name__)

DISPLAY_CHANGE_LIMIT = 20 #seconds

auth_token = os.environ['TWILIO_AUTH_TOKEN']
pixabay_api_key = os.environ['PIXABAY_API_KEY']
display_environment = os.environ['DISPLAY_ENV']

last_display_time = datetime(1970, 1, 1)

@app.errorhandler(NoImagesError)
def no_images_error(err):
    resp = MessagingResponse()
    resp.message(err.message)
    return str(resp)

@app.errorhandler(DisplayTimingError)
def display_timing_error(err):
    resp = MessagingResponse()
    resp.message('The display was recently changed, try again in {} seconds.'.format(err.time_remaining))
    return str(resp)

@app.errorhandler(RateLimitException)
def rate_limit_error(err):
    retry_time = round(err.period_remaining)
    resp = MessagingResponse()
    resp.message('Too many requests, try again in {} seconds.'.format(retry_time))
    return str(resp)

@app.route("/")
def index():
    """Send a basic informational response"""
    return 'Inky Text to Image API'

@app.route("/image", methods=['GET', 'POST'])
@limits(calls=10, period=60) #max 10 call per 60 seconds
@validate_twilio_request(auth_token)
def image():
    """Display an image based on SMS content"""
    
    # Start our TwiML response
    resp = MessagingResponse()

    # Fetch image results from the Pixabay API
    body = request.values.get('Body', None)
    encoded_query = urllib.parse.quote_plus(body)
    request_url = "https://pixabay.com/api/?key={}&q={}&min_width=600&min_height=448&orientation=horizontal&safesearch=true".format(pixabay_api_key, encoded_query)
    response = requests.get(request_url).json()
    image_results = response['hits']
    
    if len(image_results) < 1:
        raise NoImagesError
    
    # Check display wasn't changed recently
    global last_display_time
    now = datetime.now()
    time_diff = now - last_display_time

    if time_diff.seconds < DISPLAY_CHANGE_LIMIT:
        raise DisplayTimingError(DISPLAY_CHANGE_LIMIT - time_diff.seconds)
    
    # Get image file and resize
    
    first_image_url = response['hits'][0]['webformatURL']
    first_image = requests.get(first_image_url)
    img = Image.open(BytesIO(first_image.content))
    resized_image = ImageOps.fit(img,(600,448))     

    # Display the image according to chosen display_environment
    if display_environment == 'DISPLAY':
        resp.message("Found an image based on the phrase '{}'. Displaying on test machine.".format(body))
    elif display_environment == "INKY":
        resp.message("Displaying image on Inky based on the phrase '{}'.".format(body))
        thread = Thread(target=inky_display, kwargs={'image': resized_image})
        thread.start()
    else:
        resp.message("Found an image based on the phrase '{}'. Not displaying anywhere.".format(body))
        resized_image.show()
    
    last_display_time = datetime.now()
    
    # Send the SMS reply
    return str(resp)
