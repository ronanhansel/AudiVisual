import numpy as np
import requests

import access_tok
import credentials
import getBaseColour
from io import BytesIO
import urllib.request
from PIL import Image
from retrying import retry


def refresh_token(old_token):
    headers = {
        'Authorization': 'Basic '
                         'YjM2M2Q5YWNhNzFlNDg5Mjg4Y2Y3NWNmYTM2ZjBjYjM6NWVhOTc5MjhlNWI2NDI4MWI3NTJkMTI1YTEwMGRjNjY=',
    }

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': 'AQDI_k6i2ZeW9v7yfsC2-THiGM6cejnJP5kOQ2nvSQs1HG'
                         '-u8fVINjGvZlZIrz3Jn7Fye4hXA1tVghY_5bbGo9q9Q5RWbG65RSVww4ImI-zm1y5tsVTctK9wdVOie6MbT7I'
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    response_token = response.json()
    newtok = response_token['access_token']
    f = open("access_tok.py", "rt")
    data = f.read()
    data = data.replace(old_token, newtok)
    f.close()
    f = open("access_tok.py", "wt")
    f.write(data)
    f.close()
    return newtok


def makeColour(url: str):
    size = (100, 100)
    k = 8
    colour_tol = 0
    image = Image.open(BytesIO(urllib.request.urlopen(url).read()))
    artwork = np.asarray(image)
    background_color = getBaseColour.SpotifyBackgroundColor(
        img=artwork, image_processing_size=size)
    r, g, b = np.array(background_color.best_color(k=k, color_tol=colour_tol), dtype=int)
    print(r, g, b)
    return r, g, b


def colourise(token: str):
    headers_play = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    params_play = (
        ('market', 'ES'),
        ('additional_types', 'episode'),
    )
    response_play = requests.get('https://api.spotify.com/v1/me/player/currently-playing',
                                 headers=headers_play, params=params_play)

    if response_play.text == '':
        print('Not Playing')
    else:
        response_data = response_play.json()
        if len(response_data) == 1:
            print('Invalid token')
            raise Exception('Token Invalid')
        else:
            url = response_data['item']['album']['images'][1]['url']
            colour = makeColour(url)
            return colour
