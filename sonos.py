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
import logging

def trackChange(sonosDevice):
    # get track change events
    try:
        # save_av_transport = None
        trackEvent = sonosDevice["trackSubscription"].events.get(timeout=0.5)
        
        try:
            print ("<<<<<<<<<<<<<<<<< START Track Event Change >>>>>>>>>>>>>>>>>>>")
            print ('trackevent: {}'.format(trackEvent))
            print ('transport state: {}'.format(trackEvent.transport_state))
            event = {}
            print('speaker: {}'.format(sonosDevice["speaker"].id))
            event["locationId"] = sonosDevice["speaker"].id
            # creates an event for each speaker in the group later
            event["locationName"] = ""
            if trackEvent.variables.get('av_transport_uri'):
                sonosDevice["save_av_transport"] = trackEvent.av_transport_uri
                print ('got it')
            else:
                print ('missing')

            print ("save_av_transport: {}".format(sonosDevice["save_av_transport"]))
            # pprint (trackEvent.variables)
            
            if trackEvent.current_track_duration == '0:00:00':
                print ('>>Playing stream (eg radio)')
                #print ('content:  {}'.format(trackEvent.current_track_meta_data.stream_content))
                #print ('show:     {}'.format(trackEvent.current_track_meta_data.radio_show))
                #print ('station:  {}'.format(trackEvent.enqueued_transport_uri_meta_data.title))

            elif trackEvent.current_track_duration == '':
                print ('>>Playing from line in')
                #print ('Source:  {}'.format(trackEvent.enqueued_transport_uri_meta_data.title))
                #print ('not handled....yet')

            else:
                print ('>>Playing from queues')
                #print ('Artist:      {}'.format(trackEvent.current_track_meta_data.creator))
                #print ('Album:       {}'.format(trackEvent.current_track_meta_data.album))
                #print ('Playlist:    {}'.format(trackEvent.enqueued_transport_uri_meta_data.title))
                #print ('Track:       {}'.format(trackEvent.current_track_meta_data.title))
                #print ('Track uri    {}'.format(trackEvent.current_track_uri))
                #pprint (trackEvent.current_track_meta_data.item_id)
                #pprint (dir(trackEvent.current_track_meta_data.resources))
                #pprint (trackEvent.current_track_meta_data.restricted)
                #pprint (trackEvent.current_track_meta_data.tag)
                #pprint (dir(trackEvent.enqueued_transport_uri_meta_data))
                
                event["artistName"] = trackEvent.current_track_meta_data.creator.encode("utf-8")
                event["albumName"] = trackEvent.current_track_meta_data.album.encode("utf-8")
                event["trackName"] = trackEvent.current_track_meta_data.title.encode("utf-8")
                event["playlist"] = ''
                #event["playlist"] = str(trackEvent.enqueued_transport_uri_meta_data.title).strip()
                event["trackuri"] = trackEvent.current_track_uri
                
                print (event["albumName"])
                #result = sonosDevice["speaker"].search_track(event["artistName"],event["albumName"],event["trackName"], True)
                #result = sonosDevice["speaker"].get_albums_for_artist(event["artistName"])
               
                #print ('Track uri    {}'.format(trackEvent.current_track_uri))
                
                #if trackEvent.next_track_meta_data:
                    #print ('next Artist: {}'.format(trackEvent.next_track_meta_data.creator))
                    #print ('next Album:  {}'.format(trackEvent.next_track_meta_data.album))
                    #print ('next Track:  {}'.format(trackEvent.next_track_meta_data.title))
                
                
                print("transport_state: {}".format(trackEvent.transport_state))
                if trackEvent.transport_state == "PLAYING":
                    if sonosDevice["last_track_event"] != event:
                        print ("saving event: {}".format(event))
                        # stop duplicate events being created
                        sonosDevice["last_track_event"] = event
                        for player in sonosDevice["speaker"].group:
                            print (u"group with: {}".format(player.player_name))
                            event["locationName"] = player.player_name
        
                            try:
                                s = requests.Session()
                                a = requests.adapters.HTTPAdapter(max_retries=3)
                                b = requests.adapters.HTTPAdapter(max_retries=3)
                                s.mount('http://', a)
                                s.mount('https://', b)
                                r = s.post(eventApi + "/scrobble", json=event)
                                pprint (u"r.text: {}".format(r.text))
                                pprint (u"r.status_code: {}".format(r.status_code))
                            except KeyError:
                                print ("KeyError")
                            except requests.exceptions.ConnectionError:
                                print ("ConnectionError")
                            #except:
                            #    print ('error getting api')
                            #    raise exception
                        
                            # stop the location name being part of the compare due to speaker Groups
                            event["locationName"] = ""
                    else:
                        print ("duplicate event")
                    
                if trackEvent.variables.get('transport_status'):
                    #error (eg unsupported account)
                    print ("transport_status: {}".format(trackEvent.transport_status))
                    
                print ("<<<<<<<<<<<<<<<<< END Track Event Change >>>>>>>>>>>>>>>>>>>")
        except KeyError:
            print ("BLOODY BUGGER!")
        except AttributeError as e:
            print ("Attribute Error: {}".format(e))
        #except:
        #    print ("Track Event Error")
        #    raise exception
            
            #return False
    except Empty:
        #print ("empty track event")
        pass
    except KeyError:
            print ("BLOODY woop!")
            return False
    #except:
    #    print ('error getting track event')
    #    raise exception
    #    return False

    return True
            


#def controlChange(controlEvent):



def controlChange(sonosDevice):
    try:
        # get volume change events
        pprint ("volume event")
        controlEvent = sonosDevice["controlSubscription"].events.get(timeout=0.5)
        
        try:
            pprint (controlEvent.variables)
            print ("%s (%s)" % (sonosDevice["speaker"].volume, sonosDevice["speaker"].mute))
#            room = {}
#            room["name"] = sonosDevice["speaker"].player_name
#            room["volume"] = sonosDevice["speaker"].volume
#            room["mute"] = sonosDevice["speaker"].mute
            event = {}
            #event["LocationID"] = sonosDevice["speaker"].player_name;
            #r = requests.put(roomsApi, json=room)
            pprint (r.text)
            pprint (r.status_code)
            pprint (r.content)
        except:
            print ("Control Event Error")

    except Empty:
        print ("empty control event")
        pass
    except:
        print ('error getting control event')
        return False

    return True    
        
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
    pprint (weburl)

roomsApi = weburl + config.get('API', 'rooms')
pprint (roomsApi)
eventApi = weburl + config.get('API', 'events')
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

logging.basicConfig(filename='example.log',level=logging.DEBUG)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')

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
        sonosDevice["save_av_transport"] = None
        sonosDevice["last_track_event"] = {}
        print ("%s (%s)" % (sonosDevice["speaker"].player_name, sonosDevice["speaker"].ip_address))
        room = {}
        room["Name"] = sonosDevice["speaker"].player_name
        #room["volume"] = sonosDevice["speaker"].volume
        #room["mute"] = sonosDevice["speaker"].mute
        r = requests.post(roomsApi + "/findOrCreateOnName", json=room)
        pprint (r.text)
        pprint (r.status_code)
        pprint (r.content)
        sonosDevice["speaker"].id = r.json()["Location"]["id"]
        pprint (sonosDevice["speaker"].id);
        sonosDevices.insert(0, sonosDevice)
        pprint ("Added a device")

    except KeyError:
        print ("Unexpected error:")

checkEvents = True

while checkEvents is True:
    for sonosDevice in sonosDevices:
        #print ("%s (%s)" % (sonosDevice["speaker"].player_name, sonosDevice["speaker"].ip_address))
        try:
            #print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 1")
            #print (checkEvents is True)
            checkEvents = trackChange(sonosDevice)
            #print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 2")
            #print (checkEvents)
            #checkEvents = controlChange(sonosDevice)
            #print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 3")
            #print (checkEvents)
            #print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 4")
        except KeyboardInterrupt:
            print ("Interrupted")
            checkEvents = False
            break
            
for sonosDevice in sonosDevices:
    sonosDevice["controlSubscription"].unsubscribe()
    sonosDevice["trackSubscription"].unsubscribe()
 
event_listener.stop()