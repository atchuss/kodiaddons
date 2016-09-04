# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

from channels import filtertools


HOST = 'http://seriesdanko.com/'
IDIOMAS = {'es': 'Español', 'la': 'Latino', 'vos': 'VOS', 'vo': 'VO'}
list_idiomas = [v for v in IDIOMAS.values()]
CALIDADES = ['SD', 'MicroHD', 'HD/MKV']

'''
configuración para mostrar la opción de filtro, actualmente sólo se permite en xbmc, se cambiará cuando
'platformtools.show_channel_settings' esté disponible para las distintas plataformas
'''
OPCION_FILTRO = config.is_xbmc()
CONTEXT = ("", "menu filtro")[OPCION_FILTRO]
DEBUG = config.get_setting("debug")


def mainlist(item):
    logger.info("pelisalacarta.seriesdanko mainlist")

    itemlist = list()
    itemlist.append(Item(channel=item.channel, title="Novedades", action="novedades", url=HOST))
    itemlist.append(Item(channel=item.channel, title="Más vistas", action="mas_vistas", url=HOST))
    itemlist.append(Item(channel=item.channel, title="Listado Alfabético", action="listado_alfabetico", url=HOST))
    itemlist.append(Item(channel=item.channel, title="Todas las series", action="listado_completo", url=HOST))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=HOST))

    if OPCION_FILTRO:
        itemlist.append(Item(channel=item.channel, title="[COLOR yellow]Configurar filtro para series...[/COLOR]",
                             action="open_filtertools"))

    return itemlist


def open_filtertools(item):

    return filtertools.mainlist_filter(channel=item.channel, list_idiomas=list_idiomas, list_calidad=CALIDADES)


def novedades(item):
    logger.info("pelisalacarta.seriesdanko novedades")

    itemlist = list()

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)

    patron = '<a title="([^"]+)" href="([^"]+)".*?>'
    patron += "<img.*?src='([^']+)'"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl, scrapedthumb in matches:
        # patron = "^(.*?)(?:Ya Disponible|Disponible|Disponbile|disponible|\(Actualizada\))$"
        # match = re.compile(patron, re.DOTALL).findall(scrapedtitle)
        title = scrapertools.decodeHtmlentities(scrapedtitle)

        itemlist.append(Item(channel=item.channel, title=title, url=urlparse.urljoin(HOST, scrapedurl),
                        action="episodios", thumbnail=scrapedthumb))

    return itemlist


def mas_vistas(item):
    logger.info("pelisalacarta.seriesdanko mas_vistas")

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)

    patron = "<div class='widget HTML' id='HTML3'.+?<div class='widget-content'>(.*?)</div>"
    data = scrapertools.get_match(data, patron)

    itemlist = series_seccion(data,item)
    if len(itemlist) > 0:
        itemlist = sorted(itemlist, key=lambda x: x.title.lower())
    
    return itemlist
    #return series_seccion(data,item)


def listado_completo(item):
    logger.info("pelisalacarta.seriesdanko listado_completo")

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)
    patron = '<div class="widget HTML" id="HTML10".+?<div class="widget-content">(.*?)</div>'
    data = scrapertools.get_match(data, patron)

    return series_seccion(data,item)


def series_seccion(data,item):
    logger.info("pelisalacarta.seriesdanko series_seccion")

    itemlist = []
    patron = "<a href='([^']+)'.*?>(.*?)</a>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        itemlist.append(Item(channel=item.channel, action="episodios", title=scrapedtitle, show=scrapedtitle,
                             url=urlparse.urljoin(HOST, scrapedurl)))

    return itemlist


def listado_alfabetico(item):
    logger.info("pelisalacarta.seriesdanko listado_alfabetico")

    itemlist = []

    for letra in ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                  'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
        itemlist.append(Item(channel=item.channel, action="series_por_letra", title=letra,
                             url=urlparse.urljoin(HOST, "series.php?id={letra}".format(letra=letra))))

    return itemlist


# La página de series por letra es igual que la de buscar
def series_por_letra(item):
    return search(item, '')


def search(item, texto):
    logger.info("[pelisalacarta.seriesdanko search texto={0}".format(texto))

    if texto != "":
        item.url = urlparse.urljoin(HOST, "/pag_search.php?q1={0}".format(texto))

    try:
        return series(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def series(item):
    logger.info("pelisalacarta.seriesdanko series")

    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)

    patron = "<a href='([^']+)'[^>]+><img class='ict' src='([^']+)' alt='([^']+)'"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumb, scrapedtitle in matches:
        patron = "^(?:Capitulos de: )(.*?)$"
        match = re.compile(patron, re.DOTALL).findall(scrapedtitle)
        title = scrapertools.decodeHtmlentities(match[0])
        itemlist.append(Item(channel=item.channel, title=title, url=urlparse.urljoin(HOST, scrapedurl.replace("..", "")),
                             action="episodios", show=title.strip(), thumbnail=scrapedthumb, plot="",
                             list_idiomas=list_idiomas, list_calidad=CALIDADES, context=CONTEXT))


    if len(itemlist) > 0:
        itemlist = sorted(itemlist, key=lambda x: x.title.lower())

    return itemlist


def episodios(item):
    logger.info("pelisalacarta.seriesdanko episodios")

    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)

    data = re.sub(r"a> <img src=/assets/img/banderas/", "a><idioma>", data)
    data = re.sub(r"<img src=/assets/img/banderas/", "|", data)
    data = re.sub(r"\.png border='\d+' height='\d+' width='\d+'[^>]+>\s+<", "</idioma><", data)
    data = re.sub(r"\.png border='\d+' height='\d+' width='\d+'[^>]+>", "", data)

    patron = '<div id="T1".*?'
    patron += "<img src='([^']+)'"
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) > 0:
        thumbnail = matches[0]

    patron = "<a href='([^']+)'>(.*?)</a><idioma>(.*?)</idioma>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedidioma in matches:
        idioma = ""
        for i in scrapedidioma.split("|"):
            idioma += " [" + IDIOMAS.get(i, "OVOS") + "]"
        title = scrapedtitle + idioma

        itemlist.append(Item(channel=item.channel, title=title, url=urlparse.urljoin(HOST, scrapedurl),
                             action="findvideos", show=item.show, thumbnail=thumbnail, plot="", language=idioma,
                             list_idiomas=list_idiomas, list_calidad=CALIDADES, context=CONTEXT))

    if len(itemlist) > 0 and OPCION_FILTRO:
            itemlist = filtertools.get_filtered_links(itemlist, item.channel)

    # Opción "Añadir esta serie a la biblioteca de XBMC"
    if config.get_library_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la biblioteca de XBMC", url=item.url,
                             action="add_serie_to_library", extra="episodios", show=item.show))

    return itemlist


def findvideos(item):
    logger.info("pelisalacarta.seriesdanko findvideos")

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)

    online = re.findall('<table class=.+? cellpadding=.+? cellspacing=.+?>(.+?)</table>', data,
                        re.MULTILINE | re.DOTALL)

    return parse_videos(item, "Ver", online[0]) + parse_videos(item, "Descargar", online[1])


def parse_videos(item, tipo, data):
    logger.info("pelisalacarta.seriesdanko parse_videos")

    itemlist = []

    pattern = "<td.+?<img src='/assets/img/banderas/([^\.]+).+?</td><td.+?>(.*?)</td><td.+?" \
              "<img src='/assets/img/servidores/([^\.]+).+?</td><td.+?href='([^']+)'.+?>.*?</a></td>" \
              "<td.+?>(.+?)</td><td.+?>(.*?)</td>"

    links = re.findall(pattern, data, re.MULTILINE | re.DOTALL)

    for language, date, server, link, uploader, quality in links:
        if quality == "":
            quality = "SD"
        title = "{tipo} en {server} [{idioma}] [{quality}] ({uploader}: {fecha})".\
            format(tipo=tipo, server=server, idioma=IDIOMAS.get(language, "OVOS"), quality=quality, uploader=uploader,
                   fecha=date)

        itemlist.append(Item(channel=item.channel, title=title, url=urlparse.urljoin(HOST, link), action="play",
                             show=item.show, language=IDIOMAS.get(language, "OVOS"), quality=quality,
                             list_idiomas=list_idiomas, list_calidad=CALIDADES, context=CONTEXT+"|guardar filtro"))

    if len(itemlist) > 0 and OPCION_FILTRO:
        itemlist = filtertools.get_filtered_links(itemlist, item.channel)

    return itemlist


def play(item):
    logger.info("pelisalacarta.seriesdanko play url={0}".format(item.url))

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    patron = '<div id="url2".*?><a href="([^"]+)">.+?</a></div>'
    url = scrapertools.find_single_match(data, patron)

    itemlist = servertools.find_video_items(data=url)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.channel = item.channel

    return itemlist
