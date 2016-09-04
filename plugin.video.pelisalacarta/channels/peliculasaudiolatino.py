# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para peliculasaudiolatino
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re
import sys
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


DEBUG = config.get_setting("debug")
    

def mainlist(item):
    logger.info("channels.peliculasaudiolatino mainlist")

    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Recién agregadas", action="peliculas", url="http://peliculasaudiolatino.com/ultimas-agregadas.html", viewmode="movie"))
    itemlist.append( Item(channel=item.channel, title="Recién actualizadas", action="peliculas", url="http://peliculasaudiolatino.com/recien-actualizadas.html", viewmode="movie"))
    itemlist.append( Item(channel=item.channel, title="Las más vistas", action="peliculas", url="http://peliculasaudiolatino.com/las-mas-vistas.html", viewmode="movie"))
    
    itemlist.append( Item(channel=item.channel, title="Listado por géneros" , action="generos", url="http://peliculasaudiolatino.com"))
    itemlist.append( Item(channel=item.channel, title="Listado por años" , action="anyos", url="http://peliculasaudiolatino.com"))
    
    itemlist.append( Item(channel=item.channel, title="Buscar..." , action="search") )
    return itemlist

def peliculas(item):
    logger.info("channels.peliculasaudiolatino peliculas")

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Extrae las entradas de la pagina seleccionada
    patron  = '<td><a href="([^"]+)"><img src="([^"]+)" class="[^"]+" alt="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""

        # Añade al listado
        itemlist.append( Item(channel=item.channel, action="findvideos", title=title , fulltitle=title, url=url , thumbnail=thumbnail , plot=plot , folder=True) )

    # Extrae la marca de siguiente página
    next_page = scrapertools.find_single_match(data,'<a href="([^"]+)"><span class="icon-chevron-right">')
    if next_page!="":
        itemlist.append( Item(channel=item.channel, action="peliculas", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page).replace("/../../","/"), viewmode="movie", folder=True) )

    return itemlist

def generos(item):
    logger.info("channels.peliculasaudiolatino generos")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Limita el bloque donde buscar
    data = scrapertools.find_single_match(data,'<table class="generos"(.*?)</table>')

    # Extrae las entradas
    patron = '<a href="([^"]+)">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if (DEBUG): scrapertools.printMatches(matches)
                                          
    for match in matches:
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedtitle = match[1].strip()
        scrapedthumbnail = ""
        scrapedplot = ""
        logger.info(scrapedtitle)

        itemlist.append( Item(channel=item.channel, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True, viewmode="movie") )

    itemlist = sorted(itemlist, key=lambda Item: Item.title)    
    return itemlist
    
def anyos(item):
    logger.info("channels.peliculasaudiolatino anyos")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Limita el bloque donde buscar
    data = scrapertools.find_single_match(data,'<table class="years"(.*?)</table>')
    logger.info("channels.peliculasaudiolatino data="+data)

    # Extrae las entradas
    patron = '<a href="([^"]+)">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if (DEBUG): scrapertools.printMatches(matches)
                                          
    for scrapedurl,scrapedtitle in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=item.channel, action="peliculas", title=title , url=url , thumbnail=thumbnail , plot=plot, folder=True, viewmode="movie") )

    return itemlist

def search(item,texto):
    logger.info("channels.peliculasaudiolatino search")
    itemlist = []

    texto = texto.replace(" ","+")
    try:
        # Series
        item.url="http://peliculasaudiolatino.com/busqueda.php?q=%s"
        item.url = item.url % texto
        item.extra = ""
        itemlist.extend(peliculas(item))
        itemlist = sorted(itemlist, key=lambda Item: Item.title) 
        
        return itemlist
        
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def findvideos(item):
    logger.info("channels.peliculasaudiolatino videos")
    # Descarga la página

    data = scrapertools.cachePage(item.url)
    data = scrapertools.find_single_match(data,'<div class="opciones">(.*?)<div id="sidebar"')
    logger.info("channels.peliculasaudiolatino videos data="+data)

    title = item.title
    scrapedthumbnail = item.thumbnail
    itemlist = []
    '''
    <table class="table_links">
    <thead>
    <tr>
        <th class="infotx" align="left">Colaborador</th>
        <th class="infotx" align="left">Servidor</th>
        <th class="infotx" align="left">Audio</th>
        <th class="infotx" align="left">Calidad</th>
        <th class="infotx" align="left">Enlace</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <th align="left"><a href="http://peliculasaudiolatino.com/perfil/carlosaugus22.html" target="_blank"><img class="smallpic" src="http://peliculasaudiolatino.com/userpic/nopic.png" height="20" width="20" alt="carlosaugus22"><span class="infotx">carlosaugus22</span></a></th>
    <th align="left"><img src="http://www.google.com/s2/favicons?domain=vidxtreme.to" width="16" alt="vidxtreme.to"/>
    <span class="infotx">vidxtreme.to</span></th>
    <th align="left"><img src="http://peliculasaudiolatino.com/images/la_la.png" width="22" alt="Latino" align=absmiddle></th>
    <th align="left"><img src="http://peliculasaudiolatino.com/images/1ts.png" alt="TS"> TS</th>
    <th class="slink" align="left"><div id="btnp"><a href="http://peliculasaudiolatino.com/vpaste/VmtaYVUxWnRWa1pOVkZwVFZrVnJPUT09K1A=.html" rel="nofollow" target="_blank"><span class="icon-play2"></span> Ver</a></div> </th>
    </tr>
    <tr>
    <th class="headtable" align="left"><a href="http://peliculasaudiolatino.com/perfil/carlosaugus22.html" target="_blank"><img class="smallpic" src="http://peliculasaudiolatino.com/userpic/nopic.png" height="20" width="20" alt="carlosaugus22"><span class="infotx">carlosaugus22</span></a></th>
    <th align="left"><img src="http://www.google.com/s2/favicons?domain=streamin.to" width="16" alt="streamin.to"/><span class="infotx">streamin.to</span></th>
    <th align="left"><img src="http://peliculasaudiolatino.com/images/la_la.png" width="22" alt="Latino" align=absmiddle></th>
    <th align="left"><img src="http://peliculasaudiolatino.com/images/1ts.png" alt="TS"> TS</th>
    '''
    patron = '<span class="infotx">([^<]+)</span></th[^<]+'
    patron += '<th align="left"><img src="[^"]+" width="\d+" alt="([^"]+)"[^<]+</th[^<]+'
    patron += '<th align="left"><img[^>]+>([^<]+)</th[^<]+'
    patron += '<th class="slink" align="left"><div id="btnp"><a href="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if (DEBUG): scrapertools.printMatches(matches)
    for servidor,idioma,calidad,scrapedurl in matches:
        url = scrapedurl
        title = "Ver en "+servidor+" ["+idioma+"]["+calidad+"]"
        itemlist.append( Item(channel=item.channel, action="play", title=title , fulltitle=item.fulltitle, url=url , thumbnail=scrapedthumbnail , folder=False) )

    return itemlist

def play(item):
    logger.info("channels.peliculasaudiolatino play")
    itemlist=[]

    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)

    url = scrapertools.find_single_match(data,'src="(http://peliculasaudiolatino.com/show/[^"]+)"')
    logger.info("url="+url)

    data2 = scrapertools.cachePage(url)
    logger.info("data2="+data2)

    listavideos = servertools.findvideos(data2)
    for video in listavideos:
        scrapedtitle = item.title+video[0]
        videourl = video[1]
        server = video[2]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+videourl+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=item.channel, action="play", title=scrapedtitle , fulltitle=item.fulltitle, url=videourl , server=server , folder=False) )
    
    return itemlist


