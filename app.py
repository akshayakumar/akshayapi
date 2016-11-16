#!/usr/bin/env python

import urllib
import os
import json
import requests

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    '''
    res = "Ho Ho Ho"
    return res    
    
    if req.get("result").get("action") == "apicem":
        
        url = "https://sandboxapic.cisco.com:443/api/v1/ticket"
        payload = "{ \n    \"username\" : \"devnetuser\",\n\"password\" : \"Cisco123!\"\n}\n"
        headers = {
           'content-type': "application/json",
           'cache-control': "no-cache",
           }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        s = json.loads(response.text)
        
        apicurl = "https://sandboxapic.cisco.com:443/api/v1/network-device/1/14"
        apicheaders = {
           'x-auth-token': s["response"]["serviceTicket"],
            'cache-control': "no-cache",
         }
        apicresponse = requests.request("GET", apicurl, headers=apicheaders)
        switchresponse = json.loads(apicresponse.text)
        switchlist=""
        for switch in switchresponse:
            switchlist = switchlist +" "+ "Switch_type" +" "+ str(switch['type'])
        res = {
        "speech": switchlist,
        "displayText": switchlist,
        # "data": data,
        # "contextOut": [],
        "source": "akshayapi"
        }
    '''
    
    if req.get("result").get("action") == "yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
            return {}
        yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
        result = urllib.urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWebhookResult(data)
        return res    
        
    return {}

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today at " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "akshayapi"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
