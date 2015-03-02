from __future__ import print_function
from __future__ import unicode_literals
#import soco
from soco import SoCo
import json
import requests
import soco
from pprint import pprint
from soco.events import event_listener, parse_event_xml
import argparse
import ConfigParser


def trackChange(sonosDevice):
    # get track change events
    try:
        save_av_transport = None
        trackEvent = sonosDevice["trackSubscription"].events.get(timeout=0.5)
        print ("track event change")

        try:
            if trackEvent.variables.get('av_transport_uri'):
                save_av_transport = trackEvent.av_transport_uri
                print ('got it')
            else:
                print ('missing')

            print (save_av_transport)
            pprint (trackEvent.variables)

            if trackEvent.current_track_duration == '0:00:00':
                print ('>>Playing stream (eg radio)')
                print ('content:  {}'.format(trackEvent.current_track_meta_data.stream_content))
                print ('show:     {}'.format(trackEvent.current_track_meta_data.radio_show))
                print ('station:  {}'.format(trackEvent.enqueued_transport_uri_meta_data.title))

            elif trackEvent.current_track_duration == '':
                print ('>>Playing from line in')
                print ('not handled....yet')
                print ('Source:  {}'.format(trackEvent.enqueued_transport_uri_meta_data.title))

            else:
                print ('>>Playing from queue')
                print ('Artist:      {}'.format(trackEvent.current_track_meta_data.creator))
                print ('Album:       {}'.format(trackEvent.current_track_meta_data.album))
                print ('Track:       {}'.format(trackEvent.current_track_meta_data.title))
                print ('Playlist:    {}'.format(trackEvent.enqueued_transport_uri_meta_data.title))
                print ('Track uri    {}'.format(trackEvent.current_track_uri))
                if trackEvent.next_track_meta_data:
                    print ('next Artist: {}'.format(trackEvent.next_track_meta_data.creator))
                    print ('next Album:  {}'.format(trackEvent.next_track_meta_data.album))
                    print ('next Track:  {}'.format(trackEvent.next_track_meta_data.title))

                if trackEvent.variables.get('transport_status'):
                    #error (eg unsupported account)
                    print (trackEvent.transport_status)
        except KeyError:
            print ("BLOODY BUGGER!")
        except:
            print ("Track Event Error")
        
    except Empty:
        print ("empty track event")
        pass
    except:
        print ('error getting track event')

    
            


#def controlChange(controlEvent):

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

roomsApi = weburl + config.get('API', 'rooms')
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

try:
    from queue import Empty
except:  # Py2.7
    from Queue import Empty

devices = soco.discover()
controlDeviceSubscriptions = [] # volume & eq change events
trackDeviceSubscriptions = [] # track change events
topologyDeviceSubscriptions = [] # room change events


sonosDevices = []

# Display a list of speakers
for device in devices:
    sonosDevice = {}
    try:
        sonosDevice["speaker"] = device
        sonosDevice["controlSubscription"] = device.renderingControl.subscribe()
        sonosDevice["trackSubscription"] = device.avTransport.subscribe()
    
        print ("%s (%s)" % (sonosDevice["speaker"].player_name, sonosDevice["speaker"].ip_address))
        room = {}
        room["name"] = sonosDevice["speaker"].player_name
        room["volume"] = sonosDevice["speaker"].volume
        room["mute"] = sonosDevice["speaker"].mute
        r = requests.put(roomsApi, json=room)
        pprint (r.text)
        pprint (r.status_code)
        pprint (r.content)

        sonosDevices.insert(0, sonosDevice)
        pprint ("GET GERE")

        
        """controlDeviceSubscriptions.insert(0, device.renderingControl.subscribe())
        trackDeviceSubscriptions.insert(0, device.avTransport.subscribe())
        topologyDeviceSubscriptions.insert(0, device.zoneGroupTopology.subscribe())"""
    except KeyError:
        print ("Unexpected error:")

checkEvents = True

while checkEvents is True:
    for sonosDevice in sonosDevices:
        print ("%s (%s)" % (sonosDevice["speaker"].player_name, sonosDevice["speaker"].ip_address))
        trackChange(sonosDevice)
        
    
        try:
            # get volume change events
            pprint ("volume event")
            controlEvent = sonosDevice["controlSubscription"].events.get(timeout=0.5)
            pprint (controlEvent.variables)
            print ("%s (%s)" % (sonosDevice["speaker"].volume, sonosDevice["speaker"].mute))
            room = {}
            room["name"] = sonosDevice["speaker"].player_name
            room["volume"] = sonosDevice["speaker"].volume
            room["mute"] = sonosDevice["speaker"].mute
            r = requests.put(roomsApi, json=room)
            pprint (r.text)
            pprint (r.status_code)
            pprint (r.content)
    
        except Empty:
            print ("empty vol event")
            pass

        except KeyboardInterrupt:
            print ("interrupt1?")
            for controlDeviceSubscription in controlDeviceSubscriptions:
                controlDeviceSubscription.unsubscribe()

            for trackDeviceSubscription in trackDeviceSubscriptions:
                trackDeviceSubscription.unsubscribe()

            for topologyDeviceSubscription in topologyDeviceSubscriptions:
                topologyDeviceSubscription.unsubscribe()

            print ("interrupt2?")
 
            event_listener.stop()
            print ("interrupt3?")
            checkEvents = False
            break

"""      
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
        r = requests.post(url, params=json.dumps(data))
        pprint (r.text)
        pprint (r.status_code)
        pprint (r.content)
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
        break"""

