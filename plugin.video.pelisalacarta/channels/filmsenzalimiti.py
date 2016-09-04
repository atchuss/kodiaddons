# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para filmsenzalimiti
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re
import sys

from core import config
from core import logger
from core import scrapertools
from core.item import Item


DEBUG = config.get_setting("debug")


def mainlist(item):
    logger.info("[filmsenzalimiti.py] mainlist")
    
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Film Del Cinema", action="novedades" , url="http://www.filmsenzalimiti.net/genere/film"))
    itemlist.append( Item(channel=item.channel, title="Film Dvdrip"    , action="novedades", url="http://www.filmsenzalimiti.net/genere/dvd-rip"))
    itemlist.append( Item(channel=item.channel, title="Film Sub Ita"   , action="novedades", url="http://www.filmsenzalimiti.net/genere/subita"))
    itemlist.append( Item(channel=item.channel, title="Serie TV"       , action="novedades", url="http://www.filmsenzalimiti.net/genere/serie-tv"))
    itemlist.append( Item(channel=item.channel, title="Film per genere", action="categorias", url="http://www.filmsenzalimiti.net/"))
    itemlist.append( Item(channel=item.channel, action="search"     , title="Cerca" ))
    return itemlist

def categorias(item):
    logger.info("[filmsenzalimiti.py] novedades")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<li><a href\="\#">Dvdrip per Genere</a>(.*?)</ul>')
    patron = '<li><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=item.channel, action="novedades", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist


def search(item,texto):
    logger.info("[filmsenzalimiti.py] "+item.url+" search "+texto)
    item.url = "http://www.filmsenzalimiti.co/?s="+texto
    try:
        return novedades(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []


def novedades(item):
    logger.info("[filmsenzalimiti.py] novedades")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    '''
    <div class="post-item-side">
    <a href="http://www.filmsenzalimiti.net/lost-in-mancha.html"> <img src="http://www.filmsenzalimiti.net/wp-content/uploads/2013/08/Lost-in-Mancha.jpg" width="103px" height="160px" alt="img" title="Lost in Mancha" class="post-side-img"/></a>
    <h3><a href="http://www.filmsenzalimiti.net/video.html" rel="nofollow" target="_blank"><img class="playbtn" src="http://www.filmsenzalimiti.net/wp-content/themes/FilmSenzaLimiti/images/playbtn.png" border="0"/></a></h3>
    </div>
    '''
    patronvideos  = '<div class="post-item-side"[^<]+'
    patronvideos += '<a href="([^"]+)"[^<]+<img.*?src="([^"]+)"'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.get_filename_from_url(scrapedurl).replace("-"," ").replace("/","").replace(".html","").capitalize().strip()
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=item.channel, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Siguiente
    try:
        pagina_siguiente = scrapertools.get_match(data,'class="nextpostslink" rel="next" href="([^"]+)"')
        itemlist.append( Item(channel=item.channel, action="novedades", title=">> Avanti" , url=pagina_siguiente , folder=True) )
    except:
        pass

    return itemlist
