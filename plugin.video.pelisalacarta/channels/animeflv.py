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
CHANNEL_HOST = "http://animeflv.net/"
CHANNEL_DEFAULT_HEADERS = [
    ["User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0"],
    ["Accept-Encoding", "gzip, deflate"],
    ["Referer", CHANNEL_HOST]
]

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
    logger.info("pelisalacarta.channels.animeflv mainlist")

    itemlist = list([])
    itemlist.append(Item(channel=item.channel, action="novedades_episodios", title="Últimos episodios",
                         url=CHANNEL_HOST, viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="menuseries", title="Series",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/?orden=nombre&mostrar=series")))
    itemlist.append(Item(channel=item.channel, action="menuovas", title="OVAS",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/?orden=nombre&mostrar=ovas")))
    itemlist.append(Item(channel=item.channel, action="menupeliculas", title="Películas",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/?orden=nombre&mostrar=peliculas")))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/?buscar=")))

    return itemlist


def menuseries(item):
    logger.info("pelisalacarta.channels.animeflv menuseries")

    itemlist = list()
    itemlist.append(Item(channel=item.channel, action="letras", title="Por orden alfabético",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/?orden=nombre&mostrar=series")))
    itemlist.append(Item(channel=item.channel, action="generos", title="Por géneros",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/?orden=nombre&mostrar=series")))
    itemlist.append(Item(channel=item.channel, action="series", title="En emisión",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/en-emision/?orden=nombre&mostrar=series"),
                         viewmode="movies_with_plot"))

    return itemlist


def menuovas(item):
    logger.info("pelisalacarta.channels.animeflv menuovas")

    itemlist = list()
    itemlist.append(Item(channel=item.channel, action="letras", title="Por orden alfabético",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/?orden=nombre&mostrar=ovas")))
    itemlist.append(Item(channel=item.channel, action="generos", title="Por géneros",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/?orden=nombre&mostrar=ovas")))
    itemlist.append(Item(channel=item.channel, action="series", title="En emisión",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/en-emision/?orden=nombre&mostrar=ovas"),
                         viewmode="movies_with_plot"))

    return itemlist


def menupeliculas(item):
    logger.info("pelisalacarta.channels.animeflv menupeliculas")

    itemlist = list()
    itemlist.append(Item(channel=item.channel, action="letras", title="Por orden alfabético",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/?orden=nombre&mostrar=peliculas")))
    itemlist.append(Item(channel=item.channel, action="generos", title="Por géneros",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/?orden=nombre&mostrar=peliculas")))
    itemlist.append(Item(channel=item.channel, action="series", title="En emisión",
                         url=urlparse.urljoin(CHANNEL_HOST, "animes/en-emision/?orden=nombre&mostrar=peliculas"),
                         viewmode="movies_with_plot"))

    return itemlist


def letras(item):
    logger.info("pelisalacarta.channels.animeflv letras")

    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_DEFAULT_HEADERS, host=CHANNEL_HOST)

    data = scrapertools.get_match(data, '<div class="alfabeto_box"(.*?)</div>')
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
    logger.info("pelisalacarta.channels.animeflv generos")

    itemlist = []
    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_DEFAULT_HEADERS, host=CHANNEL_HOST)

    data = scrapertools.get_match(data, '<div class="generos_box"(.*?)</div>')
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


def search(item, texto):
    logger.info("pelisalacarta.channels.animeflv search")
    if item.url == "":
        item.url = urlparse.urljoin(CHANNEL_HOST, "animes/?buscar=")
    texto = texto.replace(" ", "+")
    item.url = "{0}{1}".format(item.url, texto)
    return series(item)

def newest(categoria):
    itemlist = []

    if categoria == 'anime':
        itemlist = novedades_episodios(Item(url = "http://animeflv.net/"))

    return itemlist


def novedades_episodios(item):
    logger.info("pelisalacarta.channels.animeflv novedades")

    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_DEFAULT_HEADERS, host=CHANNEL_HOST)

    '''
    <div class="not">
        <a href="/ver/cyclops-shoujo-saipu-12.html" title="Cyclops Shoujo Saipu 12">
        <img class="imglstsr lazy" src="http://cdn.animeflv.net/img/mini/957.jpg" border="0">
        <span class="tit_ep"><span class="tit">Cyclops Shoujo Saipu 12</span></span>
        </a>
    </div>
    '''

    patronvideos = '<div class="not"[^<]+<a href="([^"]+)" title="([^"]+)"[^<]+<img class="[^"]+" ' \
                   'src="([^"]+)"[^<]+<span class="tit_ep"><span class="tit">([^<]+)<'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    itemlist = []

    for match in matches:
        scrapedtitle = scrapertools.entityunescape(match[3])
        fulltitle = scrapedtitle
        # directory = match[1]
        scrapedurl = urlparse.urljoin(item.url, match[0])
        scrapedthumbnail = urlparse.urljoin(item.url, match[2].replace("mini", "portada"))
        scrapedplot = ""
        #if DEBUG: logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(scrapedtitle, scrapedurl, scrapedthumbnail))

        new_item = Item(channel=item.channel, action="findvideos", title=scrapedtitle, url=scrapedurl,
                        thumbnail=scrapedthumbnail, plot=scrapedplot, fulltitle=fulltitle)

        content_title = scrapertools.entityunescape(match[1])
        if content_title:
            episode = scrapertools.get_match(content_title, '\s+(\d+)$')
            content_title = content_title.replace(episode, '')
            season, episode = numbered_for_tratk(content_title, 1, episode)
            new_item.hasContentDetails = "true"
            new_item.contentTitle = content_title
            new_item.contentSeason = season
            new_item.contentEpisodeNumber = int(episode)

        itemlist.append(new_item)

    return itemlist


def series(item):
    logger.info("pelisalacarta.channels.animeflv series")

    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_DEFAULT_HEADERS, host=CHANNEL_HOST)

    '''
    <div class="aboxy_lista">
        <a href="/ova/nurarihyon-no-mago-ova.html" title="Nurarihyon no Mago OVA">
            <img class="lazy portada" src="/img/blank.gif"
                data-original="http://cdn.animeflv.net/img/portada/1026.jpg" alt="Nurarihyon no Mago OVA"/>
        </a>
        <span style="float: right; margin-top: 0px;" class="tipo_1"></span>
        <a href="/ova/nurarihyon-no-mago-ova.html" title="Nurarihyon no Mago OVA" class="titulo">
            Nurarihyon no Mago OVA
        </a>
        <div class="generos_links">
            <b>Generos:</b>
            <a href="/animes/genero/accion/">Acci&oacute;n</a>,
            <a href="/animes/genero/shonen/">Shonen</a>,
            <a href="/animes/genero/sobrenatural/">Sobrenatural</a>
        </div>
        <div class="sinopsis">
            La historia empieza en alrededor de 100 a&ntilde;os despu&eacute;s de la desaparici&oacute;n de
            Yamabuki Otome, la primera esposa Rihan Nura. Rihan por fin recobr&oacute; la compostura y la vida
            vuelve a la normalidad. A medida que la cabeza del Clan Nura, est&aacute; ocupado trabajando en la
            construcci&oacute;n de un mundo armonioso para los seres humanos y youkai. Un d&iacute;a, &eacute;l
            ve a Setsura molesta por lo que decide animarla tomando el clan para ir a disfrutar de las aguas
            termales &hellip;
        </div>
    </div>
    '''

    patron = '<div class="aboxy_lista"[^<]+'
    patron += '<a href="([^"]+)"[^<]+<img class="[^"]+" src="[^"]+" data-original="([^"]+)"[^<]+</a[^<]+'
    patron += '<span[^<]+</span[^<]+'
    patron += '<a[^>]+>([^<]+)</a.*?'
    patron += '<div class="sinopsis">(.*?)</div'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        title = scrapertools.unescape(scrapedtitle)
        fulltitle = title
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        plot = scrapertools.htmlclean(scrapedplot)
        show = title
        #if DEBUG:logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))
        itemlist.append(Item(channel=item.channel, action="episodios", title=title, url=url, thumbnail=thumbnail,
                             plot=plot, show=show, fulltitle=fulltitle, fanart=thumbnail, folder=True))

    patron = '<a href="([^"]+)">\&raquo\;</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = ">> Pagina Siguiente"
            scrapedthumbnail = ""
            scrapedplot = ""

            itemlist.append(Item(channel=item.channel, action="series", title=scrapedtitle, url=scrapedurl,
                                 thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True,
                                 viewmode="movies_with_plot"))

    return itemlist


def episodios(item):
    logger.info("pelisalacarta.channels.animeflv episodios")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_DEFAULT_HEADERS, host=CHANNEL_HOST)

    '''
    <div class="tit">Listado de episodios <span class="fecha_pr">Fecha Pr&oacute;ximo: 2013-06-11</span></div>
    <ul class="anime_episodios" id="listado_epis">
        <li><a href="/ver/aiura-9.html">Aiura 9</a></li>
        <li><a href="/ver/aiura-8.html">Aiura 8</a></li>
        <li><a href="/ver/aiura-7.html">Aiura 7</a></li>
        <li><a href="/ver/aiura-6.html">Aiura 6</a></li>
        <li><a href="/ver/aiura-5.html">Aiura 5</a></li>
        <li><a href="/ver/aiura-4.html">Aiura 4</a></li>
        <li><a href="/ver/aiura-3.html">Aiura 3</a></li>
        <li><a href="/ver/aiura-2.html">Aiura 2</a></li>
        <li><a href="/ver/aiura-1.html">Aiura 1</a></li>
    </ul>
    '''

    data = scrapertools.find_single_match(data, '<div class="tit">Listado de episodios.*?</div>(.*?)</ul>')
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.unescape(scrapedtitle)
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = item.thumbnail
        plot = item.plot

        # TODO crear funcion que pasandole el titulo y buscando en un array de series establezca el valor el nombre
        # y temporada / capitulo para que funcione con trak.tv

        season = 1
        episode = 1
        patron = re.escape(item.show) + "\s+(\d+)"
        # logger.info("title {0}".format(title))
        # logger.info("patron {0}".format(patron))

        try:
            episode = scrapertools.get_match(title, patron)
            episode = int(episode)
            # logger.info("episode {0}".format(episode))
        except IndexError:
            pass
        except ValueError:
            pass

        episode_title = scrapertools.find_single_match(title, "\d+:\s*(.*)")
        if episode_title == "":
            episode_title = "Episodio "+str(episode)

        season, episode = numbered_for_tratk(item.show, season, episode)

        if len(str(episode)) == 1:
            title = str(season)+"x0"+str(episode)
        else:
            title = str(season)+"x"+str(episode)

        title = item.show+" - "+title+" "+episode_title

        #if DEBUG: logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url,
                             thumbnail=thumbnail, plot=plot, show=item.show, fulltitle="{0} {1}"
                             .format(item.show, title), fanart=thumbnail, viewmode="movies_with_plot", folder=True))

    if config.get_library_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la biblioteca de XBMC", url=item.url,
                             action="add_serie_to_library", extra="episodios", show=item.show))
        itemlist.append(Item(channel=item.channel, title="Descargar todos los episodios de la serie", url=item.url,
                             action="download_all_episodes", extra="episodios", show=item.show))

    return itemlist


def findvideos(item):
    logger.info("pelisalacarta.channels.animeflv findvideos")

    data = scrapertools.anti_cloudflare(item.url, headers=CHANNEL_DEFAULT_HEADERS, host=CHANNEL_HOST)

    # if 'infoLabels' in item:
    #     del item.infoLabels

    url_anterior = scrapertools.find_single_match(data, '<a href="(/ver/[^"]+)".+?prev.png')
    url_siguiente = scrapertools.find_single_match(data, '<a href="(/ver/[^"]+)"[^.]+next.png')

    data = scrapertools.get_match(data, "var videos \= (.*?)$")

    itemlist = []

    data = data.replace("\\\\", "")
    data = data.replace("\\/", "/")
    logger.info("data="+data)

    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel = item.channel
        videoitem.show = item.show
        videoitem.folder = False

    if url_anterior:
        title_anterior = url_anterior.replace("/ver/", '').replace('-', ' ').replace('.html', '')
        itemlist.append(Item(channel=item.channel, action="findvideos", title="Anterior: " + title_anterior,
                        url=CHANNEL_HOST + url_anterior, thumbnail=item.thumbnail, plot=item.plot, show=item.show,
                        fanart=item.thumbnail, folder=True))

    if url_siguiente:
        title_siguiente = url_siguiente.replace("/ver/", '').replace('-', ' ').replace('.html', '')
        itemlist.append(Item(channel=item.channel, action="findvideos", title="Siguiente: " + title_siguiente,
                        url=CHANNEL_HOST + url_siguiente, thumbnail=item.thumbnail, plot=item.plot, show=item.show,
                        fanart=item.thumbnail, folder=True))

    return itemlist


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
    logger.info("pelisalacarta.channels.animeflv numbered_for_tratk")
    show = show.lower()

    new_season = season
    new_episode = episode
    dict_series = {}

    name_file = os.path.splitext(os.path.basename(__file__))[0]
    fname = os.path.join(config.get_data_path(), "settings_channels", name_file + "_data.json")

    if os.path.isfile(fname):

        data = ""

        try:
            f = open(fname, "r")
            for line in f:
                data += line
            f.close()

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
        logger.info("ha encontrado algo: "+str(dict_series[show]))

        if len(dict_series[show]['season_episode']) > 1:
            for row in dict_series[show]['season_episode']:

                if new_episode > row[1]:
                    new_episode -= row[1]
                    new_season = row[0]
                    break

        else:
            new_season = dict_series[show]['season_episode'][0][0]
            new_episode += dict_series[show]['season_episode'][0][1]

    logger.info("pelisalacarta.channels.animeflv numbered_for_tratk: "+str(new_season)+":"+str(new_episode))
    return new_season, new_episode
