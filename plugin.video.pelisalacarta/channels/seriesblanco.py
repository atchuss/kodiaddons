# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
import os
import re
import sys
import urlparse

from channelselector import get_thumbnail_path
from core import channeltools
from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

from channels import filtertools


channel_xml = channeltools.get_channel_parameters("seriesblanco")
HOST = "http://seriesblanco.com/"
IDIOMAS = {'es': 'Español', 'en': 'Inglés', 'la': 'Latino', 'vo': 'VO', 'vos': 'VOS', 'vosi': 'VOSI', 'otro': 'OVOS'}
list_idiomas = [v for v in IDIOMAS.values()]
CALIDADES = ['SD', 'HDiTunes', 'Micro-HD-720p', 'Micro-HD-1080p', '1080p', '720p']

'''
configuración para mostrar la opción de filtro, actualmente sólo se permite en xbmc, se cambiará cuando
'platformtools.show_channel_settings' esté disponible para las distintas plataformas
'''
OPCION_FILTRO = config.is_xbmc()
CONTEXT = ("", "menu filtro")[OPCION_FILTRO]
DEBUG = config.get_setting("debug")


def mainlist(item):
    logger.info("pelisalacarta.seriesblanco mainlist")

    thumb_series = get_thumbnail("thumb_canales_series.png")
    thumb_series_az = get_thumbnail("thumb_canales_series_az.png")
    thumb_buscar = get_thumbnail("thumb_buscar.png")

    itemlist = list([])
    itemlist.append(Item(channel=item.channel, title="Series Listado Alfabetico", action="series_listado_alfabetico",
                         thumbnail=thumb_series_az))
    itemlist.append(Item(channel=item.channel, title="Todas las Series", action="series",
                         url=urlparse.urljoin(HOST, "lista_series/"), thumbnail=thumb_series))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=HOST, thumbnail=thumb_buscar))

    if OPCION_FILTRO:
        itemlist.append(Item(channel=item.channel, title="[COLOR yellow]Configurar filtro para series...[/COLOR]",
                             action="open_filtertools"))

    return itemlist


def open_filtertools(item):

    return filtertools.mainlist_filter(channel=item.channel, list_idiomas=list_idiomas, list_calidad=CALIDADES)


def series_listado_alfabetico(item):
    logger.info("pelisalacarta.seriesblanco series_listado_alfabetico")

    itemlist = []

    for letra in ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                  'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
        itemlist.append(Item(channel=item.channel, action="series_por_letra", title=letra,
                             url=urlparse.urljoin(HOST, "series/{0}/buscar_letra.html".format(letra.upper()))))

    return itemlist


# La página de series por letra es igual que la de buscar
def series_por_letra(item):
    return search(item, '')


def search(item, texto):
    logger.info("[pelisalacarta.seriesblanco search texto={0}".format(texto))

    itemlist = []
    if texto != "":
        item.url = urlparse.urljoin(HOST, "/search.php?q1={0}".format(texto))
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")
    patron = "<img class='ict' src='([^']+)'[^>]+></a>" \
             "<div style='text-align:center;line-height:20px;height:20px;'>" \
             "<a href='([^']+)' style='font-size: 11px;'>([^<]+)</a>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedthumb, scrapedurl, scrapedtitle in matches:
        itemlist.append(Item(channel=item.channel, title=scrapedtitle.strip(), url=urlparse.urljoin(HOST, scrapedurl),
                             action="episodios", show=scrapedtitle.strip(), thumbnail=scrapedthumb,
                             list_idiomas=list_idiomas, list_calidad=CALIDADES, context=CONTEXT))

    try:
        return itemlist
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def series(item):
    logger.info("pelisalacarta.seriesblanco series")

    itemlist = []

    JJSR_HEADERS = [['Referer', item.url],['User-Agent','Mozilla/5.0'],['X-Requested-With','XMLHttpRequest'],['Accept-Encoding','gzip, deflate'],['Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'],['Upgrade-Insecure-Requests',0]]
    data = scrapertools.cache_page(item.url, None, JJSR_HEADERS)
    logger.info("JJSRB---" + item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")

    patron = "<li><a href='([^']+)' title='([^']+)'>[^<]+</a></li>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    # como no viene el thumbnail en esta pagina ponemos el thumbnail generico del canal
    thumbnail = channel_xml.get("thumbnail", "")

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(Item(channel=item.channel, title=scrapedtitle.strip(), url=urlparse.urljoin(HOST, scrapedurl),
                             action="episodios", show=scrapedtitle.strip(), thumbnail=thumbnail,
                             list_idiomas=list_idiomas, list_calidad=CALIDADES, context=CONTEXT))

    return itemlist


def episodios(item):
    logger.info("pelisalacarta.seriesblanco episodios")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")

    data = re.sub(r"a></td><td> <img src=/banderas/", "a><idioma/", data)
    data = re.sub(r"<img src=/banderas/", "|", data)
    data = re.sub(r"\s\|", "|", data)
    data = re.sub(r"\.png border='\d+' height='\d+' width='\d+'[^>]+><", "/idioma><", data)
    data = re.sub(r"\.png border='\d+' height='\d+' width='\d+'[^>]+>", "", data)

    patron = "<img id='port_serie' src='([^']+)'.*?<li data-content=\"settings\"><p>(.*?)</p>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    thumbnail = ""
    plot = ""

    for scrapedthumbnail, scrapedplot in matches:
        thumbnail = scrapedthumbnail
        plot = scrapedplot

    '''
    <td>
        <a href='/serie/534/temporada-1/capitulo-00/the-big-bang-theory.html'>1x00 - Capitulo 00 </a>
    </td>
    <td>
        <img src=/banderas/vo.png border='0' height='15' width='25' />
        <img src=/banderas/vos.png border='0' height='15' width='25' />
    </td>
    '''

    patron = "<a href='([^']+)'>([^<]+)</a><idioma/([^/]+)/idioma>"

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedidioma in matches:
        idioma = ""
        for i in scrapedidioma.split("|"):
            idioma += " [" + IDIOMAS.get(i, "OVOS") + "]"
        title = item.show + " - " + scrapedtitle + idioma
        itemlist.append(Item(channel=item.channel, title=title, url=urlparse.urljoin(HOST, scrapedurl),
                             action="findvideos", show=item.show, thumbnail=thumbnail, plot=plot, language=idioma,
                             list_idiomas=list_idiomas, list_calidad=CALIDADES, context=CONTEXT))

    if len(itemlist) == 0 and "<title>404 Not Found</title>" in data:
        itemlist.append(Item(channel=item.channel, title="la url '" + item.url +
                                                        "' parece no estar disponible en la web. Iténtalo más tarde.",
                             url=item.url, action="series"))

    if len(itemlist) > 0 and OPCION_FILTRO:
        itemlist = filtertools.get_filtered_links(itemlist, item.channel)

    # Opción "Añadir esta serie a la biblioteca de XBMC"
    if config.get_library_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la biblioteca de XBMC", url=item.url,
                             action="add_serie_to_library", extra="episodios", show=item.show))

    return itemlist


def parseVideos(item, typeStr, data):
    videoPatternsStr = [
        '<tr.+?<span>(?P<date>.+?)</span>.*?banderas/(?P<language>[^\.]+).+?href="(?P<link>[^"]+).+?servidores/'
        '(?P<server>[^\.]+).*?</td>.*?<td>.*?<span>(?P<uploader>.+?)</span>.*?<span>(?P<quality>.*?)</span>.*?</tr>',
        '<tr.+?banderas/(?P<language>[^\.]+).+?<td[^>]*>(?P<date>.+?)</td>.+?href=[\'"](?P<link>[^\'"]+)'
        '.+?servidores/(?P<server>[^\.]+).*?</td>.*?<td[^>]*>.*?<a[^>]+>(?P<uploader>.+?)</a>.*?</td>.*?<td[^>]*>'
        '(?P<quality>.*?)</td>.*?</tr>'
    ]

    for vPatStr in videoPatternsStr:
        vPattIter = re.compile(vPatStr, re.MULTILINE | re.DOTALL).finditer(data)

        itemlist = []

        for vMatch in vPattIter:
            vFields = vMatch.groupdict()
            quality = vFields.get("quality")
            if not quality:
                quality = "SD"

            title = "{0} en {1} [{2}] [{3}] ({4}: {5})"\
                .format(typeStr, vFields.get("server"), IDIOMAS.get(vFields.get("language"), "OVOS"), quality,
                        vFields.get("uploader"), vFields.get("date"))
            itemlist.append(Item(channel=item.channel, title=title, url=urlparse.urljoin(HOST, vFields.get("link")),
                                 action="play", show=item.show, language=IDIOMAS.get(vFields.get("language"), "OVOS"),
                                 quality=quality, list_idiomas=list_idiomas, list_calidad=CALIDADES,
                                 context=CONTEXT+"|guardar filtro"))

        if len(itemlist) > 0 and OPCION_FILTRO:
            itemlist = filtertools.get_filtered_links(itemlist, item.channel)

        if len(itemlist) > 0:
            return itemlist

    return []


def extractVideosSection(data):
    result = re.findall('<table class="as_gridder_table">(.+?)</table>|<table class=\'zebra\'>(.+?)<[Bb][Rr]>|'
                        'data : "(action=load[^\"]+)"', data, re.MULTILINE | re.DOTALL)

    if len(result) == 1 and result[0][2]:
        return extractVideosSection(scrapertools.cachePagePost(HOST + 'ajax.php', result[0][2]))

    row = len(result) - 2
    idx = 1 if result[row][1] else 0

    return [result[row][idx], result[row + 1][idx]]


def findvideos(item):
    logger.info("pelisalacarta.seriesblanco findvideos")

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    online = extractVideosSection(data)
    return parseVideos(item, "Ver", online[0]) + parseVideos(item, "Descargar", online[1])


def play(item):
    logger.info("pelisalacarta.channels.seriesblanco play url={0}".format(item.url))

    if item.url.startswith(HOST):
        data = scrapertools.cache_page(item.url)

        patron = "<input type='button' value='Ver o Descargar' onclick='window.open\(\"([^\"]+)\"\);'/>"
        url = scrapertools.find_single_match(data, patron)
    else:
        url = item.url

    itemlist = servertools.find_video_items(data=url)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.channel = item.channel

    return itemlist


def get_thumbnail(thumb_name=None):
    img_path = config.get_runtime_path() + '/resources/images/squares'
    if thumb_name:
        file_path = os.path.join(img_path, thumb_name)
        if os.path.isfile(file_path):
            thumb_path = file_path
        else:
            thumb_path = urlparse.urljoin(get_thumbnail_path(), thumb_name)
    else:
        thumb_path = urlparse.urljoin(get_thumbnail_path(), thumb_name)

    return thumb_path
