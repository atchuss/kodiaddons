# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para vertelenovelas
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re
import sys
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item


DEBUG = config.get_setting("debug")


def mainlist(item):
    logger.info("pelisalacarta.channels.vertelenovelas mainlist")
    
    itemlist = []

    itemlist.append( Item(channel=item.channel, title="Catálogo" , action="series", url="http://www.vertelenovelas.cc/", viewmode="movie"))
    itemlist.append( Item(channel=item.channel, title="Buscar"   , action="search"))

    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.channels.vertelenovelas search")

    texto = texto.replace(" ","+")
    item.url = "http://www.vertelenovelas.cc/ajax/autocompletex.php?q="+texto

    try:
        return series(item)
        
    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def series(item):
    logger.info("pelisalacarta.channels.vertelenovelas series")
    itemlist=[]

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)

    patron  = '<article.*?</article>'    
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for match in matches:
        title = scrapertools.find_single_match(match,'<span>([^<]+)</span>')
        if title=="":
            title = scrapertools.find_single_match(match,'<a href="[^"]+" class="title link">([^<]+)</a>')
        url = urlparse.urljoin(item.url,scrapertools.find_single_match(match,'<a href="([^"]+)"'))
        thumbnail = scrapertools.find_single_match(match,'<div data-src="([^"]+)"')
        if thumbnail=="":
            thumbnail = scrapertools.find_single_match(match,'<img src="([^"]+)"')
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"]")
        itemlist.append( Item(channel=item.channel, action="episodios", title=title , url=url , thumbnail=thumbnail) )
    
    next_page_url = scrapertools.find_single_match(data,'<a href="([^"]+)" class="next">')
    if next_page_url!="":
        itemlist.append( Item(channel=item.channel, action="series", title=">> Pagina siguiente" , url=urlparse.urljoin(item.url,next_page_url, viewmode="movie") , thumbnail="" , plot="" , folder=True) )

    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.vertelenovelas episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.find_single_match(data,'<h2>Cap(.*?)</ul>')
    patron  = '<li><a href="([^"]+)"><span>([^<]+)</span></a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        plot = ""
        thumbnail = ""
        url = urlparse.urljoin(item.url,scrapedurl)

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=item.channel, action="findvideos", title=title , url=url , thumbnail=thumbnail , plot=plot , folder=True) )
    
    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.channels.vertelenovelas findvideos")
    data = scrapertools.cache_page(item.url)
    itemlist=[]

    #<embed type="application/x-shockwave-flash" src="http://vertelenovelas.net/player.swf" width="680" height="430" id="mpl" name="mpl" quality="high" allowscriptaccess="always" allowfullscreen="true" wmode="transparent" flashvars="&file=http://content1.catalog.video.msn.com/e2/ds/4eeea8b3-6228-492b-a2be-e8b920cf4d4e.flv&backcolor=fd4bc5&frontcolor=fc9dde&lightcolor=ffffff&controlbar=over&volume=100&autostart=false&image=">
    #<embed type="application/x-shockwave-flash" src="http://vertelenovelas.net/player.swf" width="680" height="430" id="mpl" name="mpl" quality="high" allowscriptaccess="always" allowfullscreen="true" wmode="transparent" flashvars="&file=http://content1.catalog.video.msn.com/e2/ds/4eeea8b3-6228-492b-a2be-e8b920cf4d4e.flv&backcolor=fd4bc5&frontcolor=fc9dde&lightcolor=ffffff&controlbar=over&volume=100&autostart=false&image="></embed></d
    patron = '<embed type="application/x-shockwave-flash" src="http://vertelenovelas.net/player.swf".*?file=([^\&]+)&'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for match in matches:
        itemlist.append( Item(channel=item.channel, action="play", server="directo", title=item.title , url=match , thumbnail=item.thumbnail , plot=item.plot , folder=False) )

    #<embed width="680" height="450" flashvars="file=mp4:p/459791/sp/45979100/serveFlavor/flavorId/0_0pacv7kr/forceproxy/true&amp;image=&amp;skin=&amp;abouttext=&amp;dock=false&amp;streamer=rtmp://rtmpakmi.kaltura.com/ondemand/&amp;
    patron = '<embed width="[^"]+" height="[^"]+" flashvars="file=([^\&]+)&.*?streamer=(rtmp[^\&]+)&'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for final,principio in matches:
        itemlist.append( Item(channel=item.channel, action="play", server="directo", title=item.title , url=principio+final , thumbnail=item.thumbnail , plot=item.plot , folder=False) )

    #file=mp4:/c/g1MjYyYjpCnH8dRolOZ2G7u1KsleMuDS/DOcJ-FxaFrRg4gtDIwOjkzOjBrO8N_l0&streamer=rtmp://cp96275.edgefcs.net/ondemand&
    patron = 'file=([^\&]+)&streamer=(rtmp[^\&]+)&'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for final,principio in matches:
        itemlist.append( Item(channel=item.channel, action="play", server="directo", title=item.title , url=principio+"/"+final , thumbnail=item.thumbnail , plot=item.plot , folder=False) )


    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel=item.channel
        videoitem.action="play"
        videoitem.folder=False
        videoitem.title = "["+videoitem.server+"]"

    return itemlist
