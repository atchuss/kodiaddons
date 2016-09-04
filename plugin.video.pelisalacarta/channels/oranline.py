# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para oranline
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
import sys
import urlparse

from core import channeltools
from core import config
from core import logger
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item


# Configuracion del canal
__modo_grafico__ = config.get_setting('modo_grafico', "oranline")
__perfil__ = int(config.get_setting('perfil', "oranline"))

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE']]
color1, color2, color3 = perfil[__perfil__]

DEBUG = config.get_setting("debug")
host = "http://www.oranline.com/"
parameters = channeltools.get_channel_parameters("oranline")
viewmode_options = {0: 'movie_with_plot', 1: 'movie', 2: 'list'}
viewmode = viewmode_options[config.get_setting('viewmode', "oranline")]


def mainlist(item):
    logger.info("pelisalacarta.channels.oranline mainlist")
    itemlist = []
    item.viewmode = viewmode

    itemlist.append(item.clone(title="Películas", text_color=color2, action="",
                               text_blod=True))
    itemlist.append(item.clone(action="peliculas", title="      Novedades", text_color=color1,
                               url=urlparse.urljoin(host, "ultimas-peliculas-online/"),
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/"
                                         "0/Directors%20Chair.png"))

    itemlist.append(item.clone(action="peliculas", title="      Más vistas", text_color=color1,
                               url=urlparse.urljoin(host, "mas-visto/"),
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/"
                                         "0/Favorites.png"))
    itemlist.append(item.clone(action="generos", title="      Filtradas por géneros", text_color=color1,
                               url=host,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/"
                                         "0/Genre.png"))

    url = urlparse.urljoin(host, "category/documental/")
    itemlist.append(item.clone(title="Documentales", text_blod=True, text_color=color2, action=""))
    itemlist.append(item.clone(action="peliculas", title="      Novedades", text_color=color1,
                               url=url,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/"
                                         "0/Documentaries.png"))
    url = urlparse.urljoin(host, "category/documental/?orderby=title&order=asc&gdsr_order=asc")
    itemlist.append(item.clone(action="peliculas", title="      Por orden alfabético", text_color=color1,
                               url=url,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/"
                                         "0/A-Z.png"))
    itemlist.append(item.clone(title="", action=""))
    itemlist.append(item.clone(action="search", title="Buscar...", text_color=color3,
                               thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/"
                                         "channels/oranline/buscar.png"))

    itemlist.append(item.clone(action="configuracion", title="Configurar canal...", text_color="gold", folder=False))
    return itemlist


def configuracion(item):
    from platformcode import platformtools
    platformtools.show_channel_settings()
    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("Container.Refresh")


def search(item, texto):
    logger.info("pelisalacarta.channels.oranline search")
    item.url = "http://www.oranline.com/?s="
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%{0}".format(line))
        return []


def newest(categoria):
    logger.info("pelisalacarta.channels.oranline newest")
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = urlparse.urljoin(host, "ultimas-peliculas-online/")
            itemlist = peliculas(item)

            if itemlist[-1].action == "peliculas":
                itemlist.pop()

        if categoria == 'documentales':
            item.url = urlparse.urljoin(host, "category/documental/")
            itemlist = peliculas(item)

            if itemlist[-1].action == "peliculas":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def peliculas(item):
    logger.info("pelisalacarta.channels.oranline peliculas")
    itemlist = []
    nItemxPage = 250 if __modo_grafico__ else 100  # o los que haya en la pagina

    # Descarga la página
    data = scrapertools.downloadpage(item.url)

    # Extrae las entradas (carpetas)
    #bloque = scrapertools.find_multiple_matches(data, '<li class="item">(.*?)</li>')
    bloque = scrapertools.find_multiple_matches(data, '<li class="item">(.*?)<\/li>')

    item_inicial = int(item.extra) if item.extra else 0
    items_total = len(bloque)
    item_final = item_inicial + nItemxPage if (item_inicial + nItemxPage) < items_total else items_total
    bloque = bloque[item_inicial:item_final]

    for match in bloque:
        #patron = 'href="([^"]+)".*?title="([^"]+)".*?src="([^"]+)".*?' \
        #         'div class="idiomas">(.*?)<div class="calidad">(.*?)</div>'
        patron = 'href="(.*?)".*title="(.*?)".*src="(.*?)"'
        matches = scrapertools.find_multiple_matches(match, patron)

        #for scrapedurl, scrapedtitle, scrapedthumbnail, idiomas, calidad in matches:
        for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        #   title = scrapedtitle + "  ["
            title = scrapedtitle
        #   if '<div class="esp">' in idiomas:
        #       title += "ESP/"
        #   if '<div class="lat">' in idiomas:
        #       title += "LAT/"
        #   if '<div class="ing">' in idiomas:
        #       title += "ING/"
        #   if '<div class="vos">' in idiomas:
        #       title += "VOS/"
        #   if title[-1:] != "[":
        #       title = title[:-1] + "]"
        #   else:
        #       title = title[:-1]
        #   if "span" in calidad:
        #       calidad = scrapertools.find_single_match(calidad, '<span[^>]+>([^<]+)<')
        #       title += " (" + calidad.strip() + ")"

        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, scrapedurl, scrapedthumbnail))

        filtro_thumb = scrapedthumbnail.replace("http://image.tmdb.org/t/p/w185", "")
        filtro_list = {"poster_path": filtro_thumb}
        filtro_list = filtro_list.items()

        new_item = item.clone(action="findvideos", title=title, url=scrapedurl, thumbnail=scrapedthumbnail,
                              fulltitle=scrapedtitle, infoLabels={'filtro': filtro_list},
                              contentTitle=scrapedtitle, context="05", text_color=color1, viewmode="list")
        itemlist.append(new_item)

    try:
        tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    except:
        pass

    if itemlist:
        # Paginacion solo cuando hay resultados:
        #   Se pagina en subpaginas cuando el resultado es mayor q nItemxPage
        #   Se pagina normal cuando ya no hay mas resultados por mostrar en la url
        if item_final < items_total:
            # Siguiente sub pagina
            itemlist.append(item.clone(action="peliculas", title=">> Página siguiente", url=item.url,
                                 text_color=color3, extra=str(nItemxPage)))
        else:
            # Siguiente pagina en web
            next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"\s+><span [^>]+>&raquo;</span>')
            if next_page != "":
                itemlist.append(item.clone(action="peliculas", title=">> Página siguiente", extra= '0',
                                           url=next_page.replace("&#038;", "&"), text_color=color3))
            else:
                itemlist = sorted(itemlist, key=lambda x: x.title.lower())
    return itemlist


def generos(item):
    logger.info("pelisalacarta.channels.oranline generos")
    itemlist = []

    genres = {'Deporte': '3/Sports%20Film.jpg', 'Película de la televisión': '3/Tv%20Movie.jpg',
              'Estrenos de cine': '0/New%20Releases.png', 'Estrenos dvd y hd': '0/HDDVD%20Bluray.png'}
    # Descarga la página
    data = scrapertools.downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<div class="sub_title">Géneros</div>(.*?)</ul>')
    # Extrae las entradas
    patron = '<li><a href="([^"]+)".*?<i>(.*?)</i>.*?<b>(.*?)</b>'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    for scrapedurl, scrapedtitle, cuantas in matches:
        scrapedtitle = scrapedtitle.strip().capitalize()
        title = scrapedtitle + " (" + cuantas + ")"
        name_thumb = scrapertools.slugify(scrapedtitle)
        if scrapedtitle == "Foreign" or scrapedtitle == "Suspense" or scrapedtitle == "Thriller":
            thumbnail = "https://raw.githubusercontent.com/master-1970/resources/master/images/genres/2/%s.jpg" \
                        % name_thumb.capitalize()
        elif scrapedtitle in genres:
            thumbnail = "https://raw.githubusercontent.com/master-1970/resources/master/images/genres/%s" \
                        % genres[scrapedtitle]
        else:
            thumbnail = "https://raw.githubusercontent.com/master-1970/resources/master/images/genres/1/%s.jpg" \
                        % name_thumb.replace("-", "%20")

        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, scrapedurl, thumbnail))
        itemlist.append(item.clone(action="peliculas", title=title, url=scrapedurl, thumbnail=thumbnail,
                                   text_color=color2))

    return itemlist


def findvideos(item):
    logger.info("pelisalacarta.channels.oranline findvideos")
    itemlist = []

    try:
        filtro_idioma = config.get_setting("filterlanguages", item.channel)
        filtro_enlaces = config.get_setting("filterlinks", item.channel)
    except:
        filtro_idioma = 4
        filtro_enlaces = 2

    dict_idiomas = {'Español': 3, 'Latino': 2, 'VOSE': 1, 'Inglés': 0}

    data = scrapertools.downloadpage(item.url)
    year = scrapertools.find_single_match(data, 'Año de lanzamiento.*?href.*?>(\d+)</a>')

    if year != "":
        item.infoLabels['filtro'] = ""
        item.infoLabels['year'] = int(year)

        if item.infoLabels['plot'] == "":
            # Ampliamos datos en tmdb
            try:
                tmdb.set_infoLabels_item(item, __modo_grafico__)
            except:
                pass

    if item.infoLabels['plot'] == "":
        plot = scrapertools.find_single_match(data, '<h2>Sinopsis</h2>.*?>(.*?)</p>')
        item.infoLabels['plot'] = plot

    if filtro_enlaces != 0:
        list_enlaces = bloque_enlaces(data, filtro_idioma, dict_idiomas, "online", item)
        if list_enlaces:
            itemlist.append(item.clone(action="", title="Enlaces Online", text_color=color1,
                                       text_blod=True))
            itemlist.extend(list_enlaces)
    if filtro_enlaces != 1:
        list_enlaces = bloque_enlaces(data, filtro_idioma, dict_idiomas, "descarga", item)
        if list_enlaces:
            itemlist.append(item.clone(action="", title="Enlaces Descarga", text_color=color1,
                                       text_blod=True))
            itemlist.extend(list_enlaces)

    # Opción "Añadir esta película a la biblioteca de XBMC"
    if itemlist:
        itemlist.append(item.clone(channel="trailertools", title="Buscar Tráiler", action="buscartrailer", context="",
                                   text_color="magenta"))    
        if item.extra != "findvideos":
            if config.get_library_support():
                itemlist.append(Item(channel=item.channel, title="Añadir enlaces a la biblioteca", text_color="green",
                                     filtro=True, action="add_pelicula_to_library", fulltitle=item.fulltitle,
                                     extra="findvideos", url=item.url, infoLabels={'title': item.fulltitle}))
    
    else:
        itemlist.append(item.clone(title="No hay enlaces disponibles", action="", text_color=color3))

    return itemlist


def bloque_enlaces(data, filtro_idioma, dict_idiomas, type, item):
    logger.info("pelisalacarta.channels.oranline bloque_enlaces")

    lista_enlaces = []
    bloque = scrapertools.find_single_match(data, '<div id="' + type + '">(.*?)</table>')
    patron = 'tr>[^<]*<td>.*?href="([^"]+)".*?<span>([^<]+)</span>' \
             '.*?<td>([^<]+)</td>.*?<td>([^<]+)</td>'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    filtrados = []
    for scrapedurl, server, language, calidad in matches:
        language = language.strip()
        server = server.lower()
        if server == "ul":
            server = "uploadedto"
        if server == "streamin":
            server = "streaminto"
        if server == "waaw":
            server = "netutv"
        mostrar_server = True
        if config.get_setting("hidepremium") == "true":
            mostrar_server = servertools.is_server_enabled(server)
        if mostrar_server:
            try:
                servers_module = __import__("servers." + server)
                title = "   Mirror en " + server + " (" + language + ") (Calidad " + calidad.strip() + ")"
                if filtro_idioma == 4 or item.filtro or item.extra == "findvideos":
                    lista_enlaces.append(item.clone(title=title, action="play", server=server, text_color=color2,
                                                    url=scrapedurl, idioma=language))
                else:
                    idioma = dict_idiomas[language]
                    if idioma == filtro_idioma:
                        lista_enlaces.append(item.clone(title=title, text_color=color2, action="play",
                                                        url=scrapedurl, server=server))
                    else:
                        if language not in filtrados: filtrados.append(language)
            except:
                pass

    if filtro_idioma != 4:
        if len(filtrados) > 0:
            title = "Mostrar enlaces filtrados en %s" % ", ".join(filtrados)
            lista_enlaces.append(item.clone(title=title, action="findvideos", url=item.url, text_color=color3,
                                            filtro=True))

    return lista_enlaces


def play(item):
    logger.info("pelisalacarta.channels.oranline play")
    itemlist = []
    enlace = servertools.findvideosbyserver(item.url, item.server)
    itemlist.append(item.clone(url=enlace[0][1]))

    return itemlist
