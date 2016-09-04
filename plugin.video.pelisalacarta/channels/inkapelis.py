# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Inkapelis
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item


__modo_grafico__ = config.get_setting("modo_grafico", "inkapelis")
__perfil__ = int(config.get_setting("perfil", "inkapelis"))

# Fijar perfil de color
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE']]
color1, color2, color3 = perfil[__perfil__]

DEBUG = config.get_setting("debug")
thumb_channel = "http://i.imgur.com/I7MxHZI.png"


def mainlist(item):
    logger.info("pelisalacarta.channels.inkapelis mainlist")
    itemlist = []

    itemlist.append(item.clone(title="Novedades", action="entradas", url="http://www.inkapelis.com/",
                               extra="Novedades", text_color=color1))
    itemlist.append(item.clone(title="Estrenos", action="entradas", url="http://www.inkapelis.com/genero/estrenos/",
                               text_color=color1))
    itemlist.append(item.clone(title="Géneros", action="generos", url="http://www.inkapelis.com/", text_color=color1))
    itemlist.append(item.clone(title="Buscar...", action="search", text_color=color1))
    itemlist.append(item.clone(action="", title=""))
    itemlist.append(item.clone(action="configuracion", title="Configurar canal...", text_color="gold", folder=False))
    return itemlist


def configuracion(item):
    from platformcode import platformtools
    platformtools.show_channel_settings()
    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("Container.Refresh")


def newest(categoria):
    logger.info("pelisalacarta.channels.inkapelis newest")
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = "http://www.inkapelis.com/"
            item.extra = "Novedades"
            itemlist = entradas(item)

            if itemlist[-1].action == "entradas":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def search(item, texto):
    logger.info("pelisalacarta.inkapelis search")
    itemlist = []
    item.extra = "Buscar"
    item.url = "http://www.inkapelis.com/?s=%s" % texto

    try:
        return entradas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def generos(item):
    logger.info("pelisalacarta.channels.inkapelis generos")
    itemlist = []

    item.text_color = color1
    data = scrapertools.downloadpage(item.url)
    matches = scrapertools.find_multiple_matches(data, '<li class="cat-item cat-item-.*?><a href="([^"]+)".*?>(.*?)<b>')

    for scrapedurl, scrapedtitle in matches:
        if scrapedtitle == "Eroticas +18 " and config.get_setting("enableadultmode"):
            itemlist.append(item.clone(action="eroticas", title=scrapedtitle, url=scrapedurl))
        elif (scrapedtitle != "Estrenos ") and (scrapedtitle != "Próximos Estrenos "):
            itemlist.append(item.clone(action="entradas", title=scrapedtitle, url=scrapedurl))

    return itemlist


def entradas(item):
    logger.info("pelisalacarta.channels.inkapelis entradas")

    itemlist = []
    item.text_color = color2
    # Descarga la página
    data = scrapertools.downloadpage(item.url)

    #IF en caso de busqueda
    if item.extra == "Buscar":
        # Extrae las entradas
        patron = '<div class="col-xs-2">.*?<a href="([^"]+)" title="([^"]+)"> <img src="([^"]+)"'
        matches = scrapertools.find_multiple_matches(data, patron)
        for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
            thumbnail = scrapedthumbnail.replace("w185", "original")
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+thumbnail+"]")
            itemlist.append(item.clone(action="findvideos", title=scrapedtitle, url=scrapedurl, thumbnail=thumbnail,
                                       contentTitle=scrapedtitle, fulltitle=scrapedtitle, context="05"))

    else:
        # Extrae las entradas
        if item.extra == "Novedades":
            data2 = data.split("<h3>Últimas Películas Agregadas</h3>", 1)[1]
            entradas = scrapertools.find_multiple_matches(data2, '<div class="col-mt-5 postsh">(.*?)</div></div></div>')
        else:
            entradas = scrapertools.find_multiple_matches(data, '<div class="col-mt-5 postsh">(.*?)</div></div></div>')
        
        patron = '<div class="poster-media-card([^"]+)">.*?<a href="([^"]+)" title="([^"]+)">' \
                 '.*?<div class="idiomes"><div class="(.*?)">.*?' \
                 '<img.*?src="([^"]+)".*?<span class="under-title">(.*?)</span>'
        for match in entradas:
            matches = scrapertools.find_multiple_matches(match, patron)
            for calidad, url, scrapedtitle, idioma, scrapedthumbnail, category in matches:
                #Salto entradas adultos
                if category == "Eroticas +18":
                    continue
                scrapedtitle = scrapedtitle.replace("Ver Pelicula ", "")
                title = scrapedtitle + "  [" + idioma + "] [" + calidad + "]"
                if 'class="proximamente"' in match:
                    title += " Próximamente "
                thumbnail = scrapedthumbnail.replace("w185", "original")
                if DEBUG: logger.info("title=["+title+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
                itemlist.append(item.clone(action="findvideos", title=title, url=url, contentTitle=scrapedtitle,
                                           fulltitle=scrapedtitle, thumbnail=thumbnail, context="05"))

    # Extrae la marca de la siguiente página
    next_page = scrapertools.find_single_match(data, '<span class="current">.*?<\/span><a href="([^"]+)"')
    if next_page != "":
        itemlist.append(item.clone(action="entradas", title="Siguiente", url=next_page, text_color=color3))

    return itemlist


def eroticas(item):
    logger.info("pelisalacarta.channels.inkapelis eroticas")

    itemlist = []
    # Descarga la página
    data = scrapertools.downloadpage(item.url)

    # Extrae las entradas
    entradas = scrapertools.find_multiple_matches(data, '<div class="col-mt-5 postsh">(.*?)</div></div></div>')
    patron = '<div class="poster-media-card([^"]+)">.*?<a href="([^"]+)" title="([^"]+)">' \
             '.*?<div class="idiomes"><div class="(.*?)">.*?' \
             '<img.*?src="([^"]+)"'
    for match in entradas:
        matches = scrapertools.find_multiple_matches(match, patron)
        for calidad, url, scrapedtitle, idioma, scrapedthumbnail in matches:
            title = scrapedtitle + "  [" + idioma + "] [" + calidad + "]"
            thumbnail = scrapedthumbnail.replace("w185", "original")
            if DEBUG: logger.info("title=["+title+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
            itemlist.append(item.clone(action="findvideos", title=title, url=url, thumbnail=thumbnail,
                                       extra="eroticas"))

    # Extrae la marca de la siguiente página
    next_page = scrapertools.find_single_match(data, '<span class="current">.*?<\/span><a href="([^"]+)"')
    if next_page != "":
        itemlist.append(item.clone(action="entradas", title="Siguiente", url=next_page))

    return itemlist
    

def findvideos(item):
    logger.info("pelisalacarta.inkapelis findvideos")
    itemlist = []
    item.text_color = color2
    
    # Descarga la pagina
    data = scrapertools.downloadpage(item.url)
    sinopsis = scrapertools.find_single_match(data, '<h2>Sinopsis</h2>.*?>(.*?)</p>')
    item.infoLabels["plot"] = scrapertools.htmlclean(sinopsis)
    # Busca en tmdb si no se ha hecho antes
    if item.extra != "eroticas":
        year = scrapertools.find_single_match(data, 'Año de lanzamiento.*?"ab">(\d+)')
        if year != "":
            try:
                item.infoLabels['year'] = year
                # Obtenemos los datos basicos de todas las peliculas mediante multihilos
                tmdb.set_infoLabels(item, __modo_grafico__)
            except:
                pass
        trailer_url = scrapertools.find_single_match(data, 'id="trailerpro">.*?src="([^"]+)"')
        item.infoLabels["trailer"] = "www.youtube.com/watch?v=TqqF3-qgJw4"

    patron = '<td><a href="([^"]+)".*?title="([^"]+)".*?<td>([^"]+)<\/td><td>([^"]+)<\/td>'
    matches = scrapertools.find_multiple_matches(data, patron)
    
    for url, server, idioma, calidad in matches:
        if server == "Embed":
            server = "Nowvideo"
        if server == "Ul":
            server = "Uploaded"
        title = server + "  [" + idioma + "] [" + calidad + "]"
        itemlist.append(item.clone(action="play", title=title, url=url))

    patron = 'id="(embed[0-9])".*?<div class="calishow">(.*?)<(.*?)<div class="clear">'
    matches = scrapertools.find_multiple_matches(data, patron)
    for title, calidad, url in matches:
        title = scrapertools.find_single_match(url, "(?:http://|https://|//)(.*?)(?:embed.|videoembed|)/")
        title = title.capitalize() + "  [" + calidad + "]"
        itemlist.append(item.clone(action="play", title=title, url=url))

    if itemlist:
        if not config.get_setting('menu_trailer', item.channel):
            itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Buscar Tráiler",
                                       text_color="magenta", context=""))
        if item.category != "Cine":
            if config.get_library_support():
                itemlist.append(Item(channel=item.channel, title="Añadir película a la biblioteca",
                                     action="add_pelicula_to_library", url=item.url, fulltitle=item.fulltitle,
                                     infoLabels={'title': item.fulltitle}, text_color="green"))

    return itemlist


def play(item):
    logger.info("pelisalacarta.inkapelis play")
    itemlist = servertools.find_video_items(data=item.url)

    return itemlist
