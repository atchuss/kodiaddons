# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Area-Documental
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import os
import urllib

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from lib import requests


DEBUG = config.get_setting("debug")
host = "http://www.area-documental.com"
headers = [['User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0']]


def mainlist(item):
    logger.info("pelisalacarta.channels.areadocumental mainlist")
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Novedades" , action="entradas", url="http://www.area-documental.com/resultados-reciente.php?buscar=&genero=", thumbnail= "http://i.imgur.com/Kxuf5ZS.png?1", fanart="http://i.imgur.com/Q7fsFI6.png"))
    itemlist.append(Item(channel=item.channel, title="Destacados"      , action="entradas", url="http://www.area-documental.com/resultados-destacados.php?buscar=&genero=", thumbnail= "http://i.imgur.com/Kxuf5ZS.png?1", fanart="http://i.imgur.com/Q7fsFI6.png"))
    itemlist.append(Item(channel=item.channel, title="Categorías"      , action="cat", url="http://www.area-documental.com/index.php", thumbnail= "http://i.imgur.com/Kxuf5ZS.png?1", fanart="http://i.imgur.com/Q7fsFI6.png"))
    itemlist.append(Item(channel=item.channel, title="Ordenados por..."      , action="indice", thumbnail= "http://i.imgur.com/Kxuf5ZS.png?1", fanart="http://i.imgur.com/Q7fsFI6.png"))
    itemlist.append(Item(channel=item.channel, title="Buscar..."      , action="search", thumbnail= "http://i.imgur.com/Kxuf5ZS.png?1"))
    return itemlist

def search(item, texto):
    logger.info("pelisalacarta.channels.areadocumental search")
    item.url = "http://www.area-documental.com/resultados.php?buscar=%s&genero=&x=0&y=0" % texto
    try:
        itemlist = entradas(item)
        return itemlist
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []


def indice(item):
    logger.info("pelisalacarta.channels.areadocumental indices")
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Título"      , action="entradas", url="http://www.area-documental.com/resultados-titulo.php?buscar=&genero=", thumbnail=item.thumbnail , fanart=item.fanart))
    itemlist.append(Item(channel=item.channel, title="Año"      , action="entradas", url="http://www.area-documental.com/resultados-anio.php?buscar=&genero=", thumbnail=item.thumbnail , fanart=item.fanart))
    return itemlist

def cat(item):
    logger.info("pelisalacarta.channels.areadocumental cat")
    itemlist = []
    data = scrapertools.cachePage(item.url)
    bloque = scrapertools.find_single_match(data, '<ul class="menu">(.*?)</nav>')
    matches = scrapertools.find_multiple_matches(bloque, "<li>.*?<a href='([^']+)'.*?>(.*?)</a>")
    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + "/" + scrapedurl
        if not "span" in scrapedtitle:
            scrapedtitle = "[COLOR gold]    **"+scrapedtitle+"**[/COLOR]"
            itemlist.append(Item(channel=item.channel, action="entradas", title=bbcode_kodi2html(scrapedtitle), url=scrapedurl, folder=True))
        else:
            scrapedtitle = scrapertools.htmlclean(scrapedtitle)
            itemlist.append(Item(channel=item.channel, action="entradas", title=scrapedtitle, url=scrapedurl, folder=True))
    return itemlist

def entradas(item):
    logger.info("pelisalacarta.channels.areadocumental entradas")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    data = scrapertools.unescape(data)
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"> ></a>')
    if next_page != "":
        data2 = scrapertools.unescape(scrapertools.cachePage(host+next_page))
        data += data2
    else: data2 = ""
    data = data.replace("\n","").replace("\t","")

    patron = '<div id="peliculas">.*?<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'target="_blank">(.*?)</a>(.*?)<p>(.*?)</p>'
    patron += '.*?</strong>: (.*?)<strong>.*?</strong>'
    patron += '(.*?)</div>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, year, scrapedplot, genero, extra in matches:
        infolabels={}
        plot={}
        scrapedurl = host +"/"+ scrapedurl
        scrapedthumbnail = host + urllib.quote(scrapedthumbnail)
        if "full_hd" in extra: scrapedtitle += " [COLOR gold][3D][/COLOR]"
        elif "720" in extra: scrapedtitle += " [COLOR gold][720p][/COLOR]"
        else: scrapedtitle += " [COLOR gold][SD][/COLOR]"
        infolabels['plot'] = scrapedplot
        infolabels['genre'] = genero
        year = year.replace("\xc2\xa0","").replace(" ","")
        if not year.isspace() and year != "":
            infolabels['year'] = int(year)
            scrapedtitle += "  ("+year+")"
        plot['infoLabels']=infolabels
        itemlist.append(Item(channel=item.channel, action="findvideos", title=bbcode_kodi2html(scrapedtitle) , fulltitle = scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=str(plot), fanart=item.fanart, folder=True) )

    next_page = scrapertools.find_single_match(data2, '<a href="([^"]+)"> ></a>')
    if next_page != "":	
        itemlist.append(Item(channel=item.channel, action="entradas", title=">> Siguiente", url=host+next_page, folder=True))
    return itemlist


def findvideos(item):
    logger.info("pelisalacarta.channels.areadocumental findvideos")
    itemlist = []
    data = requests.get(item.url).text

    subs = scrapertools.find_multiple_matches(data, 'file: "(/webvtt[^"]+)".*?label: "([^"]+)"')

    patron = 'file: "http://217.160.176.9/comun/videos/([^"]+)".*?label: "([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, quality in matches:
        url = "http://217.160.176.9/comun/videos/"+urllib.quote(url)
        for url_sub, label in subs:
            url_sub = host + urllib.quote(url_sub)
            label = label.encode('iso-8859-1').decode('utf8')
            title = "Ver video en [[COLOR green]"+quality+"[/COLOR]] "+"Sub "+ label
            itemlist.append(Item(channel=item.channel, action="play", server="directo", title=bbcode_kodi2html(title), url=url, thumbnail=item.thumbnail, plot=item.plot, subtitle=url_sub, extra=item.url, fanart=item.fanart, folder=False))

    return itemlist

def play(item):
    logger.info("pelisalacarta.channels.areadocumental play")
    itemlist = []
    headers.append(['Referer',item.extra])
    try:
        ficherosubtitulo = os.path.join( config.get_data_path(), 'subtitulo_areadocu.srt' )
        if os.path.exists(ficherosubtitulo):
            try:
                os.remove(ficherosubtitulo)
            except IOError:
                logger.info("Error al eliminar el archivo "+ficherosubtitulo)
                raise
        
        data2 = scrapertools.cache_page(item.subtitle, headers=headers)
        fichero = open(ficherosubtitulo,"wb")
        fichero.write(data2)
        fichero.close()
        subtitle = ficherosubtitulo
    except:
        subtitle = ""
        logger.info("Error al descargar el subtítulo")
    
    itemlist.append(Item(channel=item.channel, action="play", server="directo", title=bbcode_kodi2html(item.title), url=item.url, thumbnail=item.thumbnail, plot=item.plot, subtitle=subtitle, folder=False))

    return itemlist

def bbcode_kodi2html(text):
    if config.get_platform().startswith("plex") or config.get_platform().startswith("mediaserver"):
        import re
        text = re.sub(r'\[COLOR\s([^\]]+)\]',
                      r'<span style="color: \1">',
                      text)
        text = text.replace('[/COLOR]','</span>')
        text = text.replace('[CR]','<br>')
        text = re.sub(r'\[([^\]]+)\]',
                      r'<\1>',
                      text)
        text = text.replace('"color: white"','"color: auto"')

    return text
