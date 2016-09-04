# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Pelisxporno
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re

from core import config
from core import logger
from core import scrapertools
from core.item import Item

DEBUG = config.get_setting("debug")
    

def mainlist(item):
    logger.info("[Pelisxporno.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=item.channel, action="lista"  , title="Novedades" , url="http://www.pelisxporno.com/?order=date" ) )
    itemlist.append( Item(channel=item.channel, action="categorias"  , title="Categorías" , url="http://www.pelisxporno.com" ) )
    itemlist.append( Item(channel=item.channel, action="search"  , title="Buscar" , url="http://www.pelisxporno.com/?s=%s" ) )

    return itemlist

def search(item,texto):
    logger.info("[Pelisxporno.py] search:" + texto)
    item.url = item.url % texto
    try:
        return lista(item) 
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def lista(item):
    logger.info("[Pelisxporno.py] lista")
    itemlist = []

    # Descarga la pagina  
    data = scrapertools.downloadpageGzip(item.url)

    # Extrae las entradas (carpetas)
                        
    patronvideos ='<div class="thumb">\n.*?<a href="([^"]+)" title="([^"]+)">.*?<img src="([^"]+)".*?\/>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        scrapedtitle = match[1]
        #scrapedtitle = scrapedtitle.replace("&#8211;","-")
        #scrapedtitle = scrapedtitle.replace("&#8217;","'")
        scrapedurl = match[0]
        scrapedthumbnail = match[2]
        #scrapedplot = match[0]  
        #if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        #scrapedplot=strip_tags(scrapedplot)
        itemlist.append( Item(channel=item.channel, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot="" , folder=True) )
 
 
    #Extrae la marca de siguiente página
    next_page = re.compile('<a class="page larger" href="([^"]+)">([^"]+)<\/a>',re.DOTALL).findall(data)
    if next_page:
      scrapedurl = next_page[0][0]
      page = next_page[0][1]
      itemlist.append( Item(channel=item.channel, action="lista", title="Página " + page , url=scrapedurl , plot="" , folder=True) )

    return itemlist

def categorias(item):
    logger.info("[Pelisxporno.py] categorias")
    itemlist = []

    # Descarga la pagina  
    data = scrapertools.downloadpageGzip(item.url)

    # Extrae las entradas (carpetas)
    bloque_cat = scrapertools.find_single_match(data, '<li id="categories-2"(.*?)</ul>')
    patronvideos ='<a href="([^"]+)" >(.*?)</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(bloque_cat)

    for scrapedurl, scrapedtitle in matches:
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"]")
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle , url=scrapedurl , folder=True) )

    return itemlist
