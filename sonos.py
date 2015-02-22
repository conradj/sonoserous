from __future__ import print_function
#import soco
from soco import SoCo
import json
import requests
import soco
from pprint import pprint
from soco.events import event_listener
import argparse
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('sonos.cfg')

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--live', action='store_true', default=False)

args = parser.parse_args()
if args.live:
    pprint ("LIVE")
    weburl = config.get('Web', 'live')
else:
    pprint ("TEST")
    weburl = config.get('Web', 'test')

roomsApi = weburl + "/api/rooms"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

try:
    from queue import Empty
except:  # Py2.7
    from Queue import Empty

# pick a device
device = SoCo('192.168.1.143')
print (device.player_name)
room = {}
room["name"] = device.player_name
room["volume"] = device.volume
room["mute"] = device.mute
r = requests.put(roomsApi, json=room)
pprint (r.text)
pprint (r.status_code)
pprint (r.content)


sub = device.renderingControl.subscribe()
sub2 = device.avTransport.subscribe()
# Subscribe to ZGT events
sub3 = device.zoneGroupTopology.subscribe()
while True:
    try:
        pprint ("sub")
        event = sub.events.get(timeout=0.5)
        pprint (device.mute)
        pprint (device.volume)
        room["volume"] = device.volume
        room["mute"] = device.mute
        r = requests.put(roomsApi, json=room)
        pprint (r.text)
        pprint (r.status_code)
        pprint (r.content)
    except Empty:
        pass
    try:
        pprint ("sub2")
        event = sub2.events.get(timeout=0.5)
        #pprint (event.variables)
        #pprint (event.current_track_meta_data)
        if event.current_track_meta_data:
            pprint (event.current_track_meta_data)
            #if event.current_track_meta_data.radio_show in ['None', '']
            print ('>>Playing from queue')
            print ('Artist:      {}'.format(event.current_track_meta_data.creator))
            print ('Album:       {}'.format(event.current_track_meta_data.album))
            print ('Track:       {}'.format(event.current_track_meta_data.title))
            print ('Playlist:    {}'.format(event.enqueued_transport_uri_meta_data.title))
            print ('Track uri    {}'.format(event.current_track_uri))

        data = event.variables
        """ r = requests.post(url, params=json.dumps(data))
        pprint (r.text)
        pprint (r.status_code)
        pprint (r.content)"""
    except Empty:
        pass
    try:
        pprint ("sub3")
        event = sub3.events.get(timeout=0.5)
        print (event)
        print (event.sid)
        print (event.seq)

    except Empty:
        pass
    except KeyboardInterrupt:
        sub.unsubscribe()
        sub2.unsubscribe()
        event_listener.stop()
        break

