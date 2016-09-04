# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import os
import re
import sys
import urlparse

from core import config
from core import jsontools
from core import logger
from core import scrapertools
from core.item import Item

DEBUG = config.get_setting("debug")
CHANNEL_HOST = "http://animeflv.me/"
CHANNEL_DEFAULT_HEADERS = [
    ["User-Agent", "Mozilla/5.0"],
    ["Accept-Encoding", "gzip, deflate"],
    ["Referer", CHANNEL_HOST]
]
header_string = "|User-Agent=Mozilla/5.0" \
                "&Referer=http://animeflv.me&Cookie="


'''
### PARA USAR CON TRATK.TV ###

season: debe ir en orden descendente
episode: la "temporada 1" siempre son "0 capitulos", la "temporada 2" es el "numero de capitulos de la temporada 1"

FAIRY TAIL:
    - SEASON 1: EPISODE 48 --> [season 1, episode: 0]
    - SEASON 2: EPISODE 48 --> [season 2, episode: 48]
    - SEASON 3: EPISODE 54 --> [season 3, episode: 96 ( [48=season2] +[ 48=season1] )]
    - SEASON 4: EPISODE 175 --> [season 4: episode: 150 ( [54=season3] + [48=season2] + [48=season3] )]

animeflv_data.json
{
    "TVSHOW_RENUMBER": {
        "Fairy Tail": {
            "season_episode": [
                [4, 150],
                [3, 96],
                [2, 48],
                [1, 0]
            ]
        },
        "Fairy Tail (2014)": {
            "season_episode": [
                [6, 51],
                [5, 0]
            ]
        }
    }
}
'''


def mainlist(item):
    logger.info("pelisalacarta.channels.animeflv_me mainlist")

    itemlist = list()

    itemlist.append(Item(channel=item.channel, action="letras", title="Por orden alfabético",
                         url=urlparse.urljoin(CHANNEL_HOST, "ListadeAnime")))
    itemlist.append(Item(channel=item.channel, action="generos", title="Por géneros",
                         url=urlparse.urljoin(CHANNEL_HOST, "ListadeAnime")))
    itemlist.append(Item(channel=item.channel, action="series", title="Por popularidad",
                         url=urlparse.urljoin(CHANNEL_HOST, "/ListadeAnime/MasVisto")))
    itemlist.append(Item(channel=item.channel, action="series", title="Novedades",
                         url=urlparse.urljoin(CHANNEL_HOST, "ListadeAnime/LatestUpdate")))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar...",
                         url=urlparse.urljoin(CHANNEL_HOST, "Buscar?s=")))

    return itemlist


def letras(item):
    logger.info("pelisalacarta.channels.animeflv_me letras")

    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_DEFAULT_HEADERS, host=CHANNEL_HOST)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    data = scrapertools.get_match(data, '<div class="alphabet">(.+?)</div>')
    patron = '<a href="([^"]+)[^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=item.channel, action="series", title=title, url=url, thumbnail=thumbnail,
                             plot=plot, viewmode="movies_with_plot"))

    return itemlist


def generos(item):
    logger.info("pelisalacarta.channels.animeflv_me generos")

    itemlist = []
    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_DEFAULT_HEADERS, host=CHANNEL_HOST)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    data = scrapertools.get_match(data, '<div class="barTitle">Buscar por género</div><div class="barContent">' +
                                  '<div class="arrow-general"></div><div>(.*?)</div>')
    patron = '<a href="([^"]+)[^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=item.channel, action="series", title=title, url=url, thumbnail=thumbnail,
                             plot=plot, viewmode="movies_with_plot"))

    return itemlist


def search(item, texto):
    logger.info("pelisalacarta.channels.animeflv_net search")

    texto = texto.replace(" ", "%20")
    item.url = "{0}{1}".format(item.url, texto)
    try:
        return series(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []


def series(item):
    logger.info("pelisalacarta.channels.animeflv_me series")

    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_DEFAULT_HEADERS, host=CHANNEL_HOST)
    head = header_string + get_cookie_value()

    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    patron = "<td title='<img.+?src=\"([^\"]+)\".+?<a.+?href=\"([^\"]+)\">(.*?)</a><p>(.*?)</p>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedthumbnail, scrapedurl, scrapedtitle, scrapedplot in matches:
        title = scrapedtitle.strip()  # scrapertools.unescape(scrapedtitle)
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = scrapedthumbnail
        plot = scrapertools.htmlclean(scrapedplot)
        show = title
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))
        itemlist.append(Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail+ head,
                             plot=plot, show=show, fanart=thumbnail + head, viewmode="movies_with_plot"))

    pagina = scrapertools.find_single_match(data, '<li class=\'current\'>.*?</li><li><a href="([^"]+)"')

    if pagina:
        scrapedurl = pagina
        scrapedtitle = ">> Página Siguiente"
        scrapedthumbnail = ""
        scrapedplot = ""

        itemlist.append(Item(channel=item.channel, action="series", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True,
                             viewmode="movies_with_plot"))

    return itemlist


def episodios(item):
    logger.info("pelisalacarta.channels.animeflv_me episodios")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_DEFAULT_HEADERS, host=CHANNEL_HOST)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    patron = "<p><span>(.*?)</span>"
    aux_plot = scrapertools.find_single_match(data, patron)

    patron = '<td><ahref="([^"]+)">(.*?)</a></td><td>(.*?)</td>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    pelicula = False
    for scrapedurl, scrapedtitle, scrapeddate in matches:
        title = scrapedtitle.strip()  # scrapertools.unescape(scrapedtitle)
        url = scrapedurl
        thumbnail = item.thumbnail
        plot = aux_plot  # item.plot
        date = scrapeddate.strip()

        # TODO crear funcion que pasandole el titulo y buscando en un array de series establezca el valor el nombre
        # y temporada / capitulo para que funcione con trak.tv

        season = 1
        episode = 1
        patron = "Episodio\s+(\d+)"
        # logger.info("title {0}".format(title))
        # logger.info("patron {0}".format(patron))
        try:
            episode = scrapertools.get_match(title, patron)
            episode = int(episode)
            # logger.info("episode {0}".format(episode))
        except IndexError:
            pelicula = True
            pass
        except ValueError:
            pass

        if pelicula:
            title = "{0} ({1})".format(title, date)
            if DEBUG:
                logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))
            item.url = url
            itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url,
                                 thumbnail=thumbnail, plot=plot, fulltitle="{0} {1}".format(item.show, title),
                                 fanart=thumbnail, viewmode="movies_with_plot", folder=True))
        else:
            season, episode = numbered_for_tratk(item.show, season, episode)

            if len(str(episode)) == 1:
                title = "{0}x0{1}".format(season, episode)
            else:
                title = "{0}x{1}".format(season, episode)

            title = "{0} {1} ({2})".format(title, "Episodio " + str(episode), date)

            if DEBUG:
                logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

            itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url,
                                 thumbnail=thumbnail, plot=plot, show=item.show, fulltitle="{0} {1}"
                                 .format(item.show, title), fanart=thumbnail, viewmode="movies_with_plot", folder=True))

    if config.get_library_support() and len(itemlist) > 0 and not pelicula:
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la biblioteca de XBMC", url=item.url,
                             action="add_serie_to_library", extra="episodios", show=item.show))
        itemlist.append(Item(channel=item.channel, title="Descargar todos los episodios de la serie", url=item.url,
                             action="download_all_episodes", extra="episodios", show=item.show))

    elif config.get_library_support() and len(itemlist) == 1 and pelicula:
        itemlist.append(Item(channel=item.channel, action="add_pelicula_to_library", url=item.url,
                             title="Añadir película a la biblioteca", thumbnail=item.thumbnail,
                             fulltitle=item.fulltitle))

    return itemlist


def findvideos(item):
    logger.info("pelisalacarta.channels.animeflv_me findvideos")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_DEFAULT_HEADERS, host=CHANNEL_HOST)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)

    data = scrapertools.find_single_match(data, "var part = \[([^\]]+)\]")

    patron = '"([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    list_quality = ["360", "480", "720", "1080"]

    # eliminamos la fecha del titulo a mostrar
    patron = "(.+?)\s\(\d{1,2}/\d{1,2}/\d{4}\)"
    title = scrapertools.find_single_match(item.title, patron)

    for _id, scrapedurl in enumerate(matches):
        itemlist.append(Item(channel=item.channel, action="play", url=scrapedurl, show=re.escape(item.show), fanart="",
                             title="Ver en calidad [{0}]".format(list_quality[_id]), thumbnail="", plot=item.plot,
                             folder=True, fulltitle=title, viewmode="movies_with_plot"))

    return sorted(itemlist, key=lambda it: int(scrapertools.find_single_match(it.title, "\[(.+?)\]")), reverse=True)


def numbered_for_tratk(show, season, episode):
    """
    Devuelve la temporada y episodio convertido para que se marque correctamente en tratk.tv

    :param show: Nombre de la serie a comprobar
    :type show: str
    :param season: Temporada que devuelve el scrapper
    :type season: int
    :param episode: Episodio que devuelve el scrapper
    :type episode: int
    :return: season, episode
    :rtype: int, int
    """
    logger.info("pelisalacarta.channels.animeflv_me numbered_for_tratk")
    show = show.lower()

    new_season = season
    new_episode = episode
    dict_series = {}

    name_file = os.path.splitext(os.path.basename(__file__))[0]
    fname = os.path.join(config.get_data_path(), "settings_channels", name_file + "_data.json")

    if os.path.isfile(fname):

        data = ""

        try:
            with open(fname, "r") as f:
                for line in f:
                    data += line
        except EnvironmentError:
            logger.info("ERROR al leer el archivo: {0}".format(fname))

        json_data = jsontools.load_json(data)

        if 'TVSHOW_RENUMBER' in json_data:
            dict_series = json_data['TVSHOW_RENUMBER']

        # ponemos en minusculas el key, ya que previamente hemos hecho lo mismo con show.
        for key in dict_series.keys():
            new_key = key.lower()
            if new_key != key:
                dict_series[new_key] = dict_series[key]
                del dict_series[key]

    if show in dict_series:
        logger.info("ha encontrado algo: {0}".format(dict_series[show]))

        if len(dict_series[show]['season_episode']) > 1:
            for row in dict_series[show]['season_episode']:

                if new_episode > row[1]:
                    new_episode -= row[1]
                    new_season = row[0]
                    break

        else:
            new_season = dict_series[show]['season_episode'][0][0]
            new_episode += dict_series[show]['season_episode'][0][1]

    logger.info("pelisalacarta.channels.animeflv_me numbered_for_tratk: {0}:{1}".format(new_season, new_episode))
    return new_season, new_episode


def get_cookie_value():
    cookies = os.path.join(config.get_data_path(), 'cookies', 'animeflv.me.dat')
    cookiedatafile = open(cookies, 'r')
    cookiedata = cookiedatafile.read()
    cookiedatafile.close()
    cfduid = scrapertools.find_single_match(cookiedata, "animeflv.*?__cfduid\s+([A-Za-z0-9\+\=]+)")
    cfduid = "__cfduid=" + cfduid + ";"
    cf_clearance = scrapertools.find_single_match(cookiedata, "animeflv.*?cf_clearance\s+([A-Za-z0-9\+\=\-]+)")
    cf_clearance = " cf_clearance=" + cf_clearance
    cookies_value = cfduid + cf_clearance

    return cookies_value
