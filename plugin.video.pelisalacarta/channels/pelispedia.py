# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import re
import urllib
import urlparse

from core import channeltools
from core import config
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import platformtools

__channel__ = "pelispedia"
DEBUG = config.get_setting("debug")

CHANNEL_HOST = "http://www.pelispedia.tv/"
CHANNEL_DEFAULT_HEADERS = [
    ["User-Agent", "Mozilla/5.0"],
    ["Accept-Encoding", "gzip, deflate"],
    ["Referer", CHANNEL_HOST]
]

# Configuracion del canal
try:
    __modo_grafico__ = config.get_setting('modo_grafico',__channel__)
    __perfil__= int(config.get_setting('perfil',__channel__))
except:
    __modo_grafico__ = True
    __perfil__= 0

# Fijar perfil de color
perfil = [['0xFF6E2802','0xFFFAA171','0xFFE9D7940'],
          ['0xFFA5F6AF','0xFF5FDA6D','0xFF11811E'],
          ['0xFF58D3F7','0xFF2E64FE','0xFF0404B4']]
color1, color2, color3 = perfil[__perfil__]

parameters= channeltools.get_channel_parameters(__channel__)
fanart_host= parameters['fanart']
thumbnail_host= parameters['thumbnail']


def mainlist(item):
    logger.info("pelisalacarta.channels.pelispedia mainlist")

    itemlist = list()
    itemlist.append(Item(channel=__channel__, title="Películas", text_color=color1, fanart=fanart_host, folder=False
                         , thumbnail=thumbnail_host, text_blod=True))
    itemlist.append(Item(channel=__channel__, action="listado", title="    Novedades", text_color=color2,
                         url=urlparse.urljoin(CHANNEL_HOST, "movies/all/"), fanart=fanart_host, extra="movies",
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Directors%20Chair.png"))
    itemlist.append(Item(channel=__channel__, action="listado_alfabetico", title="     Por orden alfabético", text_color=color2,
                         url=urlparse.urljoin(CHANNEL_HOST, "movies/all/"), extra="movies", fanart=fanart_host,
                         thumbnail = "https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/A-Z.png"))
    itemlist.append(Item(channel=__channel__, action="listado_genero", title="     Por género", text_color=color2,
                         url=urlparse.urljoin(CHANNEL_HOST, "movies/all/"), extra="movies", fanart=fanart_host,
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Genre.png"))
    itemlist.append(Item(channel=__channel__, action="listado_anio", title="     Por año", text_color=color2,
                         url=urlparse.urljoin(CHANNEL_HOST, "movies/all/"), extra="movies", fanart=fanart_host,
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Year.png"))
    #itemlist.append(Item(channel=__channel__, action="search", title="     Buscar...", text_color=color2,
    #                     url=urlparse.urljoin(CHANNEL_HOST, "buscar/?s="), extra="movies", fanart=fanart_host))

    itemlist.append(Item(channel=__channel__, title="Series", text_color=color1, fanart=fanart_host, folder=False
                         , thumbnail=thumbnail_host, text_blod=True))
    itemlist.append(Item(channel=__channel__, action="listado", title="    Novedades", text_color=color2,
                         url=urlparse.urljoin(CHANNEL_HOST, "series/all/"), extra="serie", fanart=fanart_host,
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/TV%20Series.png"))
    itemlist.append(Item(channel=__channel__, action="listado_alfabetico", title="     Por orden alfabético",
                         text_color=color2, extra="serie", fanart=fanart_host,
                         thumbnail = "https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/A-Z.png"))
    itemlist.append(Item(channel=__channel__, action="listado_genero", title="     Por género", extra="serie",
                         text_color=color2, fanart=fanart_host, url=urlparse.urljoin(CHANNEL_HOST, "series/all/"),
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Genre.png"))
    itemlist.append(Item(channel=__channel__, action="listado_anio", title="     Por año", extra="serie", text_color=color2,
                         fanart=fanart_host, url=urlparse.urljoin(CHANNEL_HOST, "series/all/"),
                         thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Year.png"))
    #itemlist.append(Item(channel=__channel__, action="search", title="     Buscar...", text_color=color2,
    #                     url=urlparse.urljoin(CHANNEL_HOST, "series/buscar/?s="), extra="serie", fanart=fanart_host))

    itemlist.append(Item(channel=__channel__, title="", fanart=fanart_host, folder=False, thumbnail=thumbnail_host))

    itemlist.append(Item(channel=__channel__, action="settings", title="Configuración", text_color=color1,
                         fanart=fanart_host,text_blod=True,
                         thumbnail="http://media.tvalacarta.info/pelisalacarta/squares/thumb_configuracion.png"))

    return itemlist


def settings(item):
    return platformtools.show_channel_settings()


def listado_alfabetico(item):
    logger.info("pelisalacarta.channels.pelispedia listado_alfabetico")

    itemlist = []

    for letra in ['0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                  'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:

        cadena = "series/letra/"
        if item.extra == "movies":
            cadena = 'movies/all/?letra='
            if letra == '0-9':
                cadena += "Num"
            else:
                cadena += letra
        else:
            if letra == '0-9':
                cadena += "num/"
            else:
                cadena += letra+"/"

        itemlist.append(Item(channel=__channel__, action="listado", title=letra, url=urlparse.urljoin(CHANNEL_HOST, cadena),
                             extra=item.extra, text_color=color2,
                             thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/A-Z.png"))

    return itemlist


def listado_genero(item):
    logger.info("pelisalacarta.channels.pelispedia listado_genero")

    itemlist = []

    data = scrapertools.anti_cloudflare(item.url , host=CHANNEL_HOST , headers=CHANNEL_DEFAULT_HEADERS )
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    if item.extra == "movies":
        cadena = 'movies/all/?gender='
        patron = '<select name="gender" id="genres" class="auxBtn1">.*?</select>'
        data = scrapertools.find_single_match(data, patron)
        patron = '<option value="([^"]+)".+?>(.*?)</option>'

    else:
        cadena = "series/genero/"
        patron = '<select id="genres">.*?</select>'
        data = scrapertools.find_single_match(data, patron)
        patron = '<option name="([^"]+)".+?>(.*?)</option>'


    matches = re.compile(patron, re.DOTALL).findall(data)

    for key, value in matches[1:]:
        cadena2 = cadena + key
        if item.extra != "movies":
            cadena2 += "/"

        itemlist.append(Item(channel=__channel__, action="listado", title=value, url=urlparse.urljoin(CHANNEL_HOST, cadena2),
                             extra=item.extra, text_color= color2, fanart=fanart_host,
                             thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Genre.png"))

    return itemlist


def listado_anio(item):
    logger.info("pelisalacarta.channels.pelispedia listado_anio")

    itemlist = []

    data = scrapertools.anti_cloudflare(item.url , host=CHANNEL_HOST , headers=CHANNEL_DEFAULT_HEADERS )
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    if item.extra == "movies":
        cadena = 'movies/all/?year='
        patron = '<select name="year" id="years" class="auxBtn1">.*?</select>'
        data = scrapertools.find_single_match(data, patron)
        patron = '<option value="([^"]+)"'
        titulo = 'Películas del año '
    else:
        cadena = "series/anio/"
        patron = '<select id="year">.*?</select>'
        data = scrapertools.find_single_match(data, patron)
        patron = '<option name="([^"]+)"'
        titulo = 'Series del año '

    matches = re.compile(patron, re.DOTALL).findall(data)

    for value in matches[1:]:
        cadena2 = cadena + value

        if item.extra != "movies":
            cadena2 += "/"

        itemlist.append(Item(channel=__channel__, action="listado", title=titulo+value, extra=item.extra,
                             url=urlparse.urljoin(CHANNEL_HOST, cadena2), text_color= color2, fanart=fanart_host
                             ))

    return itemlist


def search(item, texto):
    # Funcion de busqueda desactivada
    logger.info("pelisalacarta.channels.pelispedia search texto={0}".format(texto))

    item.url = item.url + "%" + texto.replace(' ', '+') + "%"

    try:
        return listado(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def newest(categoria):
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = urlparse.urljoin(CHANNEL_HOST, "movies/all/")
            item.extra = "movies"

        else:
            return []

        itemlist = listado(item)
        if itemlist[-1].action == "listado":
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

def listado(item):
    logger.info("pelisalacarta.channels.pelispedia listado")
    itemlist = []

    action = "findvideos"
    if item.extra == 'serie':
        action = "temporadas"

    data = scrapertools.anti_cloudflare(item.url , host=CHANNEL_HOST , headers=CHANNEL_DEFAULT_HEADERS )
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    # logger.info("data -- {}".format(data))

    patron = '<li[^>]+><a href="([^"]+)" alt="([^<]+).*?<img src="([^"]+).*?>.*?<span>\(([^)]+).*?' \
             '<p class="font12">(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedyear, scrapedplot in matches[:28]:
        title = "{title} ({year})".format(title=scrapertools.unescape(scrapedtitle.strip()), year=scrapedyear)
        plot = scrapertools.entityunescape(scrapedplot)

        new_item= Item(channel=__channel__, title=title, url=urlparse.urljoin(CHANNEL_HOST, scrapedurl), action=action,
                       thumbnail=scrapedthumbnail, plot=plot, context="", extra=item.extra, text_color= color3)

        if item.extra == 'serie':
            new_item.show = scrapertools.unescape(scrapedtitle.strip())
        else:
            new_item.fulltitle = scrapertools.unescape(scrapedtitle.strip())
            new_item.infoLabels = {'year':scrapedyear}
            #logger.debug(new_item.tostring())

        itemlist.append(new_item)

    # Obtenemos los datos basicos de todas las peliculas mediante multihilos
    tmdb.set_infoLabels(itemlist, __modo_grafico__)

    # numero de registros que se muestran por página, se fija a 28 por cada paginación
    if len(matches) >= 28:

        file_php = "more"
        tipo_serie = ""

        if item.extra == "movies":
            anio = scrapertools.find_single_match(item.url, "(?:year=)(\w+)")
            letra = scrapertools.find_single_match(item.url, "(?:letra=)(\w+)")
            genero = scrapertools.find_single_match(item.url, "(?:gender=|genre=)(\w+)")
            params = "letra={letra}&year={year}&genre={genero}".format(letra=letra, year=anio, genero=genero)

        else:
            tipo2 = scrapertools.find_single_match(item.url, "(?:series/|tipo2=)(\w+)")
            tipo_serie = "&tipo=serie"

            if tipo2 != "all":
                file_php = "letra"
                tipo_serie += "&tipo2="+tipo2

            genero = ""
            if tipo2 == "anio":
                genero = scrapertools.find_single_match(item.url, "(?:anio/|genre=)(\w+)")
            if tipo2 == "genero":
                genero = scrapertools.find_single_match(item.url, "(?:genero/|genre=)(\w+)")
            if tipo2 == "letra":
                genero = scrapertools.find_single_match(item.url, "(?:letra/|genre=)(\w+)")

            params = "genre={genero}".format(genero=genero)

        url = "http://www.pelispedia.tv/api/{file}.php?rangeStart=28&rangeEnd=28{tipo_serie}&{params}".\
            format(file=file_php, tipo_serie=tipo_serie, params=params)

        if "rangeStart" in item.url:
            ant_inicio = scrapertools.find_single_match(item.url, "rangeStart=(\d+)&")
            inicio = str(int(ant_inicio)+28)
            url = item.url.replace("rangeStart="+ant_inicio, "rangeStart="+inicio)

        itemlist.append(Item(channel=__channel__, action="listado", title=">> Página siguiente", extra=item.extra,
                             url=url, thumbnail=thumbnail_host, fanart= fanart_host, text_color= color2))

    return itemlist


def episodios(item):
    logger.info("pelisalacarta.channels.pelispedia episodios")

    itemlist = []

    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url , host=CHANNEL_HOST , headers=CHANNEL_DEFAULT_HEADERS )

    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    patron = '<li class="clearfix gutterVertical20"><a href="([^"]+)".*?><small>(.*?)</small>.*?' \
             '<span class.+?>(.*?)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedname in matches:
        logger.info("scrap {}".format(scrapedtitle))
        patron = 'Season\s+(\d),\s+Episode\s+(\d+)'
        match = re.compile(patron, re.DOTALL).findall(scrapedtitle)
        season, episode = match[0]

        if 'season' in item.infoLabels and int(item.infoLabels['season']) != int(season):
            continue

        title = "{season}x{episode}: {name}".format(season=season, episode=episode.zfill(2),
                                                    name=scrapertools.unescape(scrapedname))
        new_item = item.clone(title=title, url=scrapedurl, action="findvideos", text_color=color3)
        if 'infoLabels' not in new_item:
            new_item.infoLabels={}

        new_item.infoLabels['season'] = season
        new_item.infoLabels['episode'] = episode.zfill(2)

        itemlist.append(new_item)

    #TODO no hacer esto si estamos añadiendo a la biblioteca
    if not item.extra:
        # Obtenemos los datos de todos los capitulos de la temporada mediante multihilos
        tmdb.set_infoLabels(itemlist, __modo_grafico__)
        for i in itemlist:
            if i.infoLabels['title']:
                # Si el capitulo tiene nombre propio añadirselo al titulo del item
                i.title = "%sx%s %s" % (i.infoLabels['season'], i.infoLabels['episode'], i.infoLabels['title'])
            if i.infoLabels.has_key('poster_path'):
                # Si el capitulo tiene imagen propia remplazar al poster
                i.thumbnail = i.infoLabels['poster_path']

    itemlist.sort(key=lambda item: item.title, reverse=config.get_setting('orden_episodios',__channel__))

    # Opción "Añadir esta serie a la biblioteca de XBMC"
    if config.get_library_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=__channel__, title="Añadir esta serie a la biblioteca de XBMC", url=item.url,
                             action="add_serie_to_library", extra="episodios", show=item.show, category="Series",
                             text_color=color1,thumbnail=thumbnail_host, fanart= fanart_host))

    return itemlist

def temporadas(item):
    logger.info("pelisalacarta.channels.pelispedia episodios")

    itemlist = []

    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url, host=CHANNEL_HOST, headers=CHANNEL_DEFAULT_HEADERS)

    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    if not item.fanart:
        patron = '<div class="hero-image"><img src="([^"]+)"'
        item.fanart = scrapertools.find_single_match(data, patron)

    patron = '<h3 class="pt15 pb15 dBlock clear seasonTitle">([^<]+).*?'
    patron += '<div class="bpM18 bpS25 mt15 mb20 noPadding"><figure><img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 1:
        for scrapedseason,scrapedthumbnail in matches:
            temporada = scrapertools.find_single_match(scrapedseason, '(\d+)')
            newItem = item.clone(text_color=color2, action="episodios", season=temporada, thumbnail=scrapedthumbnail)
            newItem.infoLabels['season'] = temporada
            newItem.extra=""
            itemlist.append(newItem)


        # Obtenemos los datos de todas las temporadas de la serie mediante multihilos
        tmdb.set_infoLabels(itemlist, __modo_grafico__)
        for i in itemlist:
            i.title = "%s. %s" % (i.infoLabels['season'], i.infoLabels['tvshowtitle'])
            if i.infoLabels['title']:
                # Si la temporada tiene nombre propio añadirselo al titulo del item
                i.title += " - %s" % (i.infoLabels['title'])
            if i.infoLabels.has_key('poster_path'):
                # Si la temporada tiene poster propio remplazar al de la serie
                i.thumbnail = i.infoLabels['poster_path']

        itemlist.sort(key=lambda item: item.title)

        # Opción "Añadir esta serie a la biblioteca de XBMC"
        if config.get_library_support() and len(itemlist) > 0:
            itemlist.append(Item(channel=__channel__, title="Añadir esta serie a la biblioteca de XBMC", url=item.url,
                                 action="add_serie_to_library", extra="episodios", show=item.show, category="Series",
                                 text_color=color1, thumbnail=thumbnail_host, fanart=fanart_host))

        return itemlist
    else:
        return episodios(item)



def findvideos(item):
    logger.info("pelisalacarta.channels.pelispedia findvideos")

    itemlist = []

    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url , host=CHANNEL_HOST , headers=CHANNEL_DEFAULT_HEADERS )
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    patron = '<iframe src=".+?id=(\d+)'
    key = scrapertools.find_single_match(data, patron)
    data = scrapertools.anti_cloudflare( CHANNEL_HOST+'api/iframes.php?id={0}&update1.1'.format(key) , host=CHANNEL_HOST , headers=CHANNEL_DEFAULT_HEADERS )

    # Descarta la opción descarga que es de publicidad
    patron = '<a href="(?!http://go.ad2up.com)([^"]+)".+?><img src="/api/img/([^.]+)'
    matches = scrapertools.find_multiple_matches(data, patron)

    for scrapedurl, scrapedtitle in matches:
        # En algunos vídeos hay opción flash "vip" con varias calidades
        if "api/vip.php" in scrapedurl:
            data_vip = scrapertools.anti_cloudflare(scrapedurl , host=CHANNEL_HOST , headers=CHANNEL_DEFAULT_HEADERS )
            patron = '<a href="([^"]+)".+?><img src="/api/img/([^.]+).*?<span class="text">([^<]+)<'
            matches_vip = re.compile(patron, re.DOTALL).findall(data_vip)
            for url, titlevip, calidad in matches_vip:
                title = "Ver vídeo en ["+titlevip+"] "+calidad
                itemlist.append(item.clone(title=title, url=url, action="play"))
        else:
            title = "Ver vídeo en ["+scrapedtitle+"]"
            itemlist.append(item.clone(title=title, url=scrapedurl, action="play", extra=item.url))

    # Opción "Añadir esta serie a la biblioteca de XBMC"
    if item.extra == "movies" and config.get_library_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=__channel__, title="Añadir esta película a la biblioteca de XBMC", url=item.url,
                             action="add_pelicula_to_library", extra="findvideos", fulltitle=item.title, text_color= color2))

    return itemlist


def play(item):
    logger.info("pelisalacarta.channels.pelispedia play url={0}".format(item.url))

    itemlist = []
    # Para videos flash y html5
    if item.url.startswith("http://www.pelispedia.tv"):
        key = scrapertools.find_single_match(item.url, 'index.php\?id=([^&]+)&sub=([^&]+)&.+?imagen=([^&]+)')
        subtitle = ""
        thumbnail = ""

        if len(key) > 2:
            thumbnail = key[2]
        if key[1] != "":
            url_sub = "http://www.pelispedia.tv/sub/%s.srt" % key[1]
            data_sub = scrapertools.anti_cloudflare(url_sub, host=CHANNEL_HOST)
            subtitle = save_sub(data_sub)
        if "Player_Html5" in item.url:
            url = "http://www.pelispedia.tv/Pe_Player_Html5/pk/pk_2/plugins/protected.php"
            post = "fv=21&url="+urllib.quote(key[0])+"&sou=pic"
        else:
            url = "http://www.pelispedia.tv/Pe_flsh/plugins/gkpluginsphp.php"
            post = "link="+urllib.quote(key[0])

        data = scrapertools.cache_page(url, post=post, headers=CHANNEL_DEFAULT_HEADERS)
        media_urls = scrapertools.find_multiple_matches(data, '(?:link|url)":"([^"]+)"')
        # Si hay varias urls se añade la última que es la de mayor calidad
        if len(media_urls) > 0:
            url = media_urls[len(media_urls)-1].replace("\\", "")
            itemlist.append(Item(channel=__channel__, title=item.title, url=url, server="directo", action="play",
                                 subtitle=subtitle, thumbnail=thumbnail))

    elif item.url.startswith("http://www.pelispedia.biz"):
        logger.info("estoy en el otro html5")
        key = scrapertools.find_single_match(item.url, 'v=([^&]+).+?imagen=([^&]+)')

        thumbnail = ""
        if len(key) > 1:
            thumbnail = key[1]

        data = scrapertools.anti_cloudflare(item.url , host=CHANNEL_HOST , headers=CHANNEL_DEFAULT_HEADERS )

        media_url = scrapertools.find_single_match(data, '"file":"([^"]+)"').replace("\\", "")
        sub = scrapertools.find_single_match(data, 'file:\s"([^"]+)".+?label:\s"Spanish"')
        itemlist.append(Item(channel=__channel__, title=item.title, url=media_url, server="directo", action="play",
                             subtitle=sub, thumbnail=thumbnail))

    else:
        itemlist = servertools.find_video_items(data=item.url)
        for videoitem in itemlist:
            videoitem.title = item.title
            videoitem.channel = __channel__

    return itemlist


def save_sub(data):
    import os
    try:
        ficherosubtitulo = os.path.join( config.get_data_path(), 'subtitulo_pelispedia.srt' )
        if os.path.exists(ficherosubtitulo):
            try:
                os.remove(ficherosubtitulo)
            except IOError:
                logger.info("Error al eliminar el archivo "+ficherosubtitulo)
                raise

        fichero = open(ficherosubtitulo,"wb")
        fichero.write(data)
        fichero.close()
        subtitle = ficherosubtitulo
    except:
        subtitle = ""
        logger.info("Error al descargar el subtítulo")

    return ficherosubtitulo
