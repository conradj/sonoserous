import urllib


url = "http://www.google-analytics.com/collect?v=1&tid=UA-59326609-1&cid=35009a79-1a05-49d7-b876-2b884d0f825b&t=event&ec=house%20monitor&ea=pingpihelloMatlidaandAmy&el=rpi"


for letter in 'Matlida':     # First Example
   print 'Current Letter :', letter
   response = urllib.urlopen(url).read()
   

   
exit()
