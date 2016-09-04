# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para pornhub
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item

DEBUG = config.get_setting("debug")


def mainlist(item):
    logger.info("[pornhub.py] mainlist")
    itemlist = []
    itemlist.append( Item(channel=item.channel, action="peliculas", title="Novedades", fanart=item.fanart, url = "http://es.pornhub.com/video?o=cm"))
    itemlist.append( Item(channel=item.channel, action="categorias", title="Categorias", fanart=item.fanart, url = "http://es.pornhub.com/categories?o=al"))
    itemlist.append( Item(channel=item.channel, action="search", title="Buscar", fanart=item.fanart, url = "http://es.pornhub.com/video/search?search=%s&o=mr"))
    return itemlist


def search(item,texto):
    logger.info("[pornhub.py] search")

    item.url = item.url % texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []
    
def categorias(item):
    logger.info("[pornhub.py] categorias")
    itemlist = []
    
    # Descarga la página
    data = scrapertools.downloadpage(item.url)
    data = scrapertools.find_single_match(data,'<div id="categoriesStraightImages">(.*?)</ul>')

    # Extrae las categorias
    patron  = '<li class="cat_pic" data-category=".*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'alt="([^"]+)"'
        
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        url = urlparse.urljoin(item.url,scrapedurl + ("&o=cm" if "?" in scrapedurl else "?o=cm"))
        itemlist.append( Item(channel=item.channel, action="peliculas", title=scrapedtitle, url=url, fanart=item.fanart, thumbnail=scrapedthumbnail))
    
    itemlist.sort(key=lambda x: x.title)
    return itemlist

def peliculas(item):
    logger.info("[pornhub.py] peliculas")
    itemlist = []
       
    # Descarga la página
    data = scrapertools.downloadpage(item.url)

    videodata = scrapertools.find_single_match(data,'<ul class="[^>]+search-video-thumbs">(.*?)<div class="reset"></div>')

    # Extrae las peliculas
    patron = '<div class="phimage">.*?'
    patron += '<a href="([^"]+)" title="([^"]+).*?'
    patron += '<var class="duration">([^<]+)</var>(.*?)</div>.*?'
    patron += 'data-smallthumb="([^"]+)"'
    
    matches = re.compile(patron,re.DOTALL).findall(videodata)
    
    for url,scrapedtitle,duration,scrapedhd,thumbnail in matches:       
        title=scrapedtitle.replace("&amp;amp;", "&amp;") +" ("+duration+")"
        
        scrapedhd = scrapertools.find_single_match(scrapedhd,'<span class="hd-thumbnail">(.*?)</span>')
        if (scrapedhd == 'HD') : title += ' [HD]'
        
        url= urlparse.urljoin(item.url,url)
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url ,fanart=item.fanart, thumbnail=thumbnail, folder = False) )
        
    # Paginador
    patron = '<li class="page_next"><a href="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if matches:
        url=urlparse.urljoin(item.url,matches[0].replace('&amp;','&'))
        itemlist.append(Item(channel=item.channel, action="peliculas", title=">> Página siguiente" ,fanart=item.fanart, url=url))
         
    return itemlist


def play(item):
    logger.info("[pornhub.py] play")
    itemlist=[]

    # Descarga la página
    data = scrapertools.downloadpage(item.url)
    patron = "var player_quality_([\d]+)p = '([^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for calidad, url in matches:
        itemlist.append( Item(channel=item.channel, action="play", title=calidad, fulltitle=item.title, url=url ,fanart=item.fanart, thumbnail=item.thumbnail, folder = False) )
 
    itemlist.sort(key=lambda x: x.title, reverse= True)
    return itemlist
