import os
import requests
import urllib
from flask import Flask, request, redirect, abort, current_app
from PIL import Image, ImageOps
from io import BytesIO
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from auth import validate_twilio_request
from display import show_image
from error import NoImagesError

load_dotenv()

app = Flask(__name__)

auth_token = os.environ['TWILIO_AUTH_TOKEN']
pixabay_api_key = os.environ['PIXABAY_API_KEY']
display_environment = os.environ['DISPLAY_ENV']

@app.route("/")
def info():
    """Send a basic response informational response"""
    return 'Inky Text for Image API'

@app.route("/image", methods=['GET', 'POST'])
@validate_twilio_request(auth_token)
def image():
    """Send a dynamic reply to an incoming text message"""
    
    # Start our TwiML response
    resp = MessagingResponse()

    # Fetch an image from the Pixabay API and resize
    try:
        body = request.values.get('Body', None)
        encoded_query = urllib.parse.quote_plus(body)
        request_url = "https://pixabay.com/api/?key={}&q={}&min_width=600&min_height=448&orientation=horizontal&safesearch=true".format(pixabay_api_key, encoded_query)
        response = requests.get(request_url).json()
        image_results = response['hits']
        if len(image_results) < 1:
            raise NoImagesError
        first_image_url = response['hits'][0]['webformatURL']
        first_image_tags = response['hits'][0]['tags']
        first_image = requests.get(first_image_url)
        img = Image.open(BytesIO(first_image.content))
        resized_image = ImageOps.fit(img,(600,448))
    except NoImagesError:
        resp.message("Unable to find an image based on that phrase. Please try something else.")
        return str(resp)


    if display_environment == 'DISPLAY':
        resp.message('Found an image with these tags:{}. Displaying on test machine.'.format(first_image_tags))
    elif display_environment == "INKY":
        show_image(resized_image)
        resp.message('Displaying image on Inky with these tags:{}.'.format(first_image_tags))
    else:
        resp.message('Found an image with these tags:{}. Not displaying anywhere.'.format(first_image_tags))
        resized_image.show()

    return str(resp)
