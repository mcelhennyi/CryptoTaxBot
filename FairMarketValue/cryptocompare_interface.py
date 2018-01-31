import http.client
import json
import time


def _send_request(self, date):
    connection = http.client.HTTPSConnection('min-api.cryptocompare.com', timeout=2)
    connection.request('GET', '/data/pricehistorical?fsym=BTC&tsyms=ETH,USD,EUR&ts='+ str(int(time.time())) +'&extraParams=your_app_name')
    response = connection.getresponse()
    if response.status is not 200:
        raise Exception("Request not good: " + str(response.status))

    return json.loads(response.read().decode('utf-8'))

print(_send_request('d', 'd'))