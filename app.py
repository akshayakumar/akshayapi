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

    #print("Request:")
    #print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
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
        if req.get("result").get("parameters").get("needinfo") == "devices":
            url = "https://sandboxapic.cisco.com:443/api/v1/network-device/1/14"
            headers = {
               'x-auth-token': s["response"]["serviceTicket"],
               'cache-control': "no-cache",
            }
            apicresponse = requests.request("GET", url, headers=headers)
            switchresponse = json.loads(apicresponse.text)
            switchlist=" Sure, Here is the list of devices in the network.." + "\n"
            for switch in switchresponse['response']:
                switchlist = switchlist + "Hostname: "+ switch['hostname']+" IP-Address: "+ switch['managementIpAddress']+" DeviceType: "+ switch['type']+" Version:"+str(switch['softwareVersion'])+"\n"
            res = {
            "speech": switchlist,
            "displayText": switchlist,
            # "data": data,
            # "contextOut": [],
            "source": "akshayapi"
            }
            return res

        if req.get("result").get("parameters").get("needinfo") == "clients":
            url = "https://sandboxapic.cisco.com:443/api/v1/host?limit=100&offset=1"
            headers = {
               'x-auth-token': s["response"]["serviceTicket"],
               'cache-control': "no-cache",
            }
            apicresponse = requests.request("GET", url, headers=headers)
            clientresponse = json.loads(apicresponse.text)
            clientlist=" Sure, Here is the list of clients in the network.." + "\n"
            for client in clientresponse['response']:
                if client['hostType'] == "wired":
                    clientlist = clientlist + " Wired Client IP Address:"+ client['hostIp']+" Client Devicetype:"+client['hostType']+" Swith IP :"+str(client['connectedNetworkDeviceIpAddress'])+"\n"
                if client['hostType'] == "wireless":
                    clientlist = clientlist + " Wireless Client IP Address:"+ client['hostIp']+" Client Devicetype:"+client['hostType']+" Access Point IP:"+str(client['connectedNetworkDeviceIpAddress'])+"\n"
            
            res = {
            "speech": clientlist,
            "displayText": clientlist,
            # "data": data,
            # "contextOut": [],
            "source": "akshayapi"
            }
            return res
        if req.get("result").get("parameters").get("needinfo") == "apps":
            url = "https://sandboxapic.cisco.com:443/api/v1/application"
            headers = {
                'x-auth-token': s["response"]["serviceTicket"],
                'cache-control': "no-cache",
            }
            apicresponse = requests.request("GET", url, headers=headers)
            appsresponse = json.loads(apicresponse.text)
            appslist = " Sure, Here is the list of application configured in network QoS.." + "\n"
            for app in appsresponse['response']:
                    appslist = appslist + app['name'] +", "

            appslist = appslist + "\n"+ "\n"+ "For more information about specific application ask: appinfo <Application name>"

            res = {
                "speech": appslist,
                "displayText": appslist,
                # "data": data,
                # "contextOut": [],
                "source": "akshayapi"
            }
            return res
        if req.get("result").get("parameters").get("needinfo") == "appinfo":
            url = "https://sandboxapic.cisco.com:443/api/v1/application?name="+req.get("result").get("parameters").get("appname")
            headers = {
                'x-auth-token': s["response"]["serviceTicket"],
                'cache-control': "no-cache",
            }
            apicresponse = requests.request("GET", url, headers=headers)
            appresponse = json.loads(apicresponse.text)
            if appresponse['response'] != 'null':
                for app in appresponse['response']:
                    appinfo = " Sure, Here is the information about the application"+"\n"
                    appinfo = appinfo + "Name: " + app['name']+ "\n"+ ",  Category: "+ app['category']+",  Traffic Class: "+app['trafficClass']+",  Protocol: "+app['appProtocol']
                    if app['appProtocol']=="tcp":
                         appinfo = appinfo + ",TCP Port:"+app['tcpPorts']
                    if app['appProtocol'] == "udp":
                         appinfo = appinfo + ",UDP Port:" + app['udpPorts']
            else:
                appinfo = "Application doesn't exist"
            res = {
                    "speech": appinfo,
                    "displayText": appinfo,
                    # "data": data,
                    # "contextOut": [],
                    "source": "akshayapi"
            }
            return res
    if req.get("result").get("action") == "yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        print "yqlquery" + "  " + str(type(yql_query))
        if yql_query is None:
            return {}
        yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
        print "yqlquery" + "  " + str(type(yql_url))
        result = urllib.urlopen(yql_url).read()
        data = json.loads(result)
        print "data" + "  " + str(type(data))
        res = makeWebhookResult(data)
        print "res" + "  " + str(type(res))
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

   # print("Response:")
    #print(speech)

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
