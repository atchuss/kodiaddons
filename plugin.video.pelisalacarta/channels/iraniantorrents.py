# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para megaforo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re
import urlparse
import cookielib
import urllib,urllib2

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from platformcode import platformtools

DEBUG = config.get_setting("debug")
MAIN_HEADERS = []
MAIN_HEADERS.append( ["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"] )
MAIN_HEADERS.append( ["Accept-Encoding","text/plain"] )
#MAIN_HEADERS.append( ["Accept-Encoding","gzip, deflate"] )
MAIN_HEADERS.append( ["Accept-Language","es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"] )
MAIN_HEADERS.append( ["Connection","keep-alive"] )
MAIN_HEADERS.append( ["Host","www.iraniantorrents.com"] )
MAIN_HEADERS.append( ["Referer","http://http://www.iraniantorrents.com/"] )
MAIN_HEADERS.append( ["User-Agent","Mozilla/5.0 (Windows NT 6.2; rv:23.0) Gecko/20100101 Firefox/23.0"] )

def login():
    logger.info("[iraniantorrents.py] login")

    # Calcula el hash del password
    LOGIN = config.get_setting("iraniantorrentsuser", "iraniantorrents")
    PASSWORD = config.get_setting("iraniantorrentspassword", "iraniantorrents")
    logger.info("LOGIN="+LOGIN)
    logger.info("PASSWORD="+PASSWORD)
    # Hace el submit del login
    post = "user="+LOGIN+"&passwrd="+PASSWORD


    login_url = 'http://www.iraniantorrents.com/smf/index.php?action=login2&user=%s&passwrd=%s' %(LOGIN, PASSWORD)
    #login_data = urllib.urlencode({'user':LOGIN, 'passwrd':PASSWORD})
    #login_data = urllib.urlencode({'user':LOGIN, 'passwrd':PASSWORD})
    #req = urllib2.Request(login_url, login_data)
    req = urllib2.Request(login_url)
    for hdc, hdv in MAIN_HEADERS:
        req.add_header(hdc,hdv)
    #cj = cookielib.LWPCookieJar()
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    response = opener.open(req)
    data = response.read()
    response.close()

    #cookiepath = 'C:/Users/Javier/AppData/Roaming/Kodi/addons/plugin.video.pelisalacarta/zCookie.txt'
    patron = '<Cookie (.+?)\ for www.iraniantorrents.com'
    cookies = '; '.join(re.compile(patron,re.DOTALL).findall(str(cj)))

    # CONTENIDO DE cj    
    #<cookielib.CookieJar[<Cookie PHPSESSID=pcdq422ku80vqsgr4ud5qg0mu1 for www.iraniantorrents.com/>, <Cookie SMFCookie12=a%3A4%3A%7Bi%3A0%3Bs%3A5%3A%2217028%22%3Bi%3A1%3Bs%3A40%3A%224c8a3e4cdcc81ad72de1d95b496e0274d18ab462%22%3Bi%3A2%3Bi%3A1472842924%3Bi%3A3%3Bi%3A0%3B%7D for www.iraniantorrents.com/>]>
  
    #logger.info("post="+post)
    #data = scrapertools.cache_page("http://www.iraniantorrents.com/smf/index.php?action=login2" , post=post, headers=MAIN_HEADERS)
    return True, cookies

#def downloadpage(url,post=None,headers=DEFAULT_HEADERS,follow_redirects=True, timeout=DEFAULT_TIMEOUT, header_to_get=None):
#def cache_page  (url,post=None,headers=DEFAULT_HEADERS,modo_cache=CACHE_ACTIVA, timeout=DEFAULT_TIMEOUT):

def getlastpage(data):
    patronplot = '<option value=.*?by=DESC&amp;pages=(\d+)"'
    matches = re.compile(patronplot,re.DOTALL).findall(data)
    pag = '0'
    if len(matches)>0:
        for pags in matches:
            if int(pags)>int(pag):
                pag = pags
    return pag

def mainlist(item):
    logger.info("[iraniantorrents.py] mainlist")
    itemlist = []
    if config.get_setting("iraniantorrentsuser","iraniantorrents") == "":
        itemlist.append( Item( channel=item.channel , title="Habilita tu cuenta en la configuración..." , action="settingCanal" , url="") )
    else:
        loginOK,item.cookies = login()
        if loginOK:
        #if login():

            req = urllib2.Request('http://www.iraniantorrents.com/index.php?page=torrents&active=0&order=data&by=DESC&pages=1')
            MAIN_HEADERS.append(["Cookie",item.cookies])
            for hdc, hdv in MAIN_HEADERS:
                req.add_header(hdc,hdv)
            #req.add_header("Cookie",item.cookies)

            pfile(str(req.headers))

            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

            opener.addheaders = MAIN_HEADERS

            response = opener.open(req)
            data = response.read()


            response.close()

            #logger.info("CKJOIN2 = " + cookies2)

            #data = scrapertools.cache_page("http://www.iraniantorrents.com/index.php?page=torrents&active=0&order=data&by=DESC&pages=1")
            item.lastpage = getlastpage(data)
            item.currentpage = "1"
	    patronimage = '<a href="index.php\?page=torrent-details&amp;id=(.+?)".*?title=".*?">(.+?)<'
	    matches = re.compile(patronimage,re.DOTALL).findall(data)
	    for url,title in matches:
		if '#comments' not in url:
		    #item.url = "http://www.iraniantorrents.com/download.php?id=" + url
		    item.url = url
		    item.title = unicode(title, "iso-8859-1", errors="replace").encode("utf-8")
		    itemlist.append( Item( channel=item.channel , title=item.title , cookies=item.cookies , action="playvideo" , url=item.url  , folder=False ))
		    
	    if int(item.currentpage)<int(item.lastpage):
		newcurrentpage = str(int(item.currentpage) + 1)
		item.url = "http://www.iraniantorrents.com/index.php?page=torrents&active=0&order=data&by=DESC&pages=" + newcurrentpage
		item.title = "[COLOR gold]>>> Siguiente página >>>[/COLOR]"
		itemlist.append( Item( channel=item.channel , title=item.title , cookies=item.cookies , action="findvideos" , url=item.url , lastpage=item.lastpage , currentpage=newcurrentpage , folder=True ) )

            #itemlist.append( Item( channel=item.channel , title="Películas" , action="findvideos" , url="http://www.iraniantorrents.com/index.php?page=torrents&active=0&order=data&by=DESC&pages=1" , lastpage="" , currentpage="1" , folder=True ) )
        else:
            itemlist.append( Item( channel=item.channel , title="Cuenta incorrecta, revisa la configuración..." , action="" , url="" , folder=False ) )
    return itemlist

def settingCanal(item):
    return platformtools.show_channel_settings()

def findvideos(item):
    itemlist=[]

    req = urllib2.Request(item.url)
    for hdc, hdv in MAIN_HEADERS:
        req.add_header(hdc,hdv)
    req.add_header("Cookie",item.cookies)
    #cj = cookielib.LWPCookieJar()
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    response = opener.open(req)
    data = response.read()
    response.close()
    #cookiepath = 'C:/Users/Javier/AppData/Roaming/Kodi/addons/plugin.video.pelisalacarta/zCookie.txt'
    patron = '<Cookie (.+?)\ for www.iraniantorrents.com'
    cookies2 = '; '.join(re.compile(patron,re.DOTALL).findall(str(cj)))

    #data = scrapertools.cache_page(item.url)

    #if item.lastpage == "":
    #    item.lastpage = getlastpage(data)

    #itemlist.append( Item( channel=item.channel , title='PINCHAME. Gracias' , action="gracias" , url='http://www.erq.io/AFrMT'  , folder=False ))

    patronimage = '<a href="index.php\?page=torrent-details&amp;id=(.+?)".*?title=".*?">(.+?)<'
    matches = re.compile(patronimage,re.DOTALL).findall(data)
    for url,title in matches:
        if '#comments' not in url:
            #item.url = "http://www.iraniantorrents.com/download.php?id=" + url
            item.url = url
            item.title = unicode(title, "iso-8859-1", errors="replace").encode("utf-8")
            itemlist.append( Item( channel=item.channel , title=item.title , cookies=item.cookies , action="playvideo" , url=item.url  , folder=False ))
            
    if int(item.currentpage)<int(item.lastpage):
        newcurrentpage = str(int(item.currentpage) + 1)
        item.url = "http://www.iraniantorrents.com/index.php?page=torrents&active=0&order=data&by=DESC&pages=" + newcurrentpage
        item.title = "[COLOR gold]>>> Siguiente página >>>[/COLOR]"
        itemlist.append( Item( channel=item.channel , title=item.title , cookies=item.cookies , action="findvideos" , url=item.url , lastpage=item.lastpage , currentpage=newcurrentpage , folder=True ) )

#   if config.get_library_support():
#       itemlist.append( Item(channel=item.channel, title="Añadir esta serie a la biblioteca de XBMC", url=item.url, action="add_serie_to_library", extra="findvideos") )
    return itemlist


def playvideo(item):
    itemlist=[]

    logger.info("LASTCOOKIES: " + item.cookies)

    url = "http://www.iraniantorrents.com/index.php?page=downloadcheck&id=" + item.url
    req = urllib2.Request(url)
    #cj = cookielib.LWPCookieJar()
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    for hdc, hdv in MAIN_HEADERS:
        opener.add_header(hdc,hdv)
    req.add_header("Cookie",item.cookies)
    response = opener.open(req)
    data = response.read()
    response.close()

    with open( "C:/Users/Javier/AppData/Roaming/Kodi/addons/plugin.video.pelisalacarta/zzz2.html", "wb") as local_file:
        local_file.write(data)
        local_file.close

def gracias(item):
    import webbrowser
    new = 0
    autoraise = False
    url = "http://www.erq.io/AFrMT"
    webbrowser.open(url,new=new,autoraise=autoraise)

def pfile(data):
    with open( "C:/Users/Javier/AppData/Roaming/Kodi/addons/plugin.video.pelisalacarta/zzz2.html", "wb") as local_file:
        local_file.write(data)
        local_file.close
    return None
    

#   data = scrapertools.cache_page(url, post=None, headers=MAIN_HEADERS)
    
#   target = open('C:/Users/Javier/AppData/Roaming/Kodi/addons/plugin.video.pelisalacarta/zzz2.torrent', 'wb')
#   target.write(data)
#   target.close

    return None
