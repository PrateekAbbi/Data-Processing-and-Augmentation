from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import json
import urllib.request
import certifi
import ssl

from . import main

@csrf_exempt
@require_http_methods(['POST'])
def fetch_incidents(request):
    url = ""
    output_table = {
        "day_of_the_week": [],
        "time_of_day": [],
        "weather": [],
        "location_rank": [],
        "side_of_town": [],
        "incident_rank": [],
        "nature": [],
        "EMSSTAT": []
    }
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        url = data["url"]
        # type = data['type']
    
    # Set a user agent to mimic a web browser request.    
    headers = {'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"}
    
    # Create a secure SSL context using certifi's CA bundle.
    context = ssl.create_default_context(cafile=certifi.where())       
    # Open the URL and read the data (PDF content).
    data = urllib.request.urlopen(urllib.request.Request(url, headers=headers), context=context).read()

    # Save the downloaded data to a temporary PDF file.
    with open('temp.pdf', 'wb') as f:
        f.write(data)

    output_table = main.main(url=url)
    
    nature = output_table['nature']
    side = output_table['side_of_town']

    return JsonResponse({'nature': nature, 'side': side}, safe=False)
