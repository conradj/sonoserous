# Output Sonos events to a web API #
Simple utility to send Sonos events (volume changes, track changes, track information etc) to a Web API.

What's that? You haven't got a Web API to send this info to? Go here, for a simple API with a web socket implementation for real time updates.

![Sonos Volume Updating](http://conradj.github.io/images/sonos.gif)
This shows me changing the volume on a Sonos client and viewing the change on a web page hosted on the internet.

# IMAGINE THE POSSIBILITIES!#


Uses https://github.com/SoCo/SoCo to do all of the hard work

/// TODO
- Vol slider on Mac OSX Sonos controller seems affected by something in this code. Not sure if it's something I cna fix. Doesn't happen on Android controller...
- Manage multiple rooms and groups
- Error handling for radio streams etc
- Error handling for no server available
- Send loads more track and room info
- Make project properly http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
    - With this https://github.com/audreyr/cookiecutter-pypackage
