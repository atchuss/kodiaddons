# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para flashx
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import re

from core import logger
from core import jsunpack
from core import scrapertools


headers = [['User-Agent', 'Mozilla/5.0']]


def test_video_exists(page_url):
    logger.info("pelisalacarta.servers.flashx test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url, headers=headers)

    if 'FILE NOT FOUND' in data:
        return False, "[FlashX] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("pelisalacarta.servers.flashx url=" + page_url)

    # Lo pide una vez
    data = scrapertools.cache_page(page_url, headers=headers)
    # Si salta aviso, se carga la pagina de comprobacion y luego la inicial
    if "You try to access this video with Kodi" in data:
        url_reload = scrapertools.find_single_match(data, 'try to reload the page.*?href="([^"]+)"')
        data = scrapertools.cache_page(url_reload, headers=headers)
        data = scrapertools.cache_page(page_url, headers=headers)

    match = scrapertools.find_single_match(data, "<script type='text/javascript'>(.*?)</script>")

    if match.startswith("eval"):
        match = jsunpack.unpack(match)

    # Extrae la URL
    # {file:"http://f11-play.flashx.tv/luq4gfc7gxixexzw6v4lhz4xqslgqmqku7gxjf4bk43u4qvwzsadrjsozxoa/video1.mp4"}
    video_urls = []
    media_urls = scrapertools.find_multiple_matches(match, '\{file\:"([^"]+)"')
    for media_url in media_urls:
        if not media_url.endswith("png"):
            video_urls.append(["." + media_url.rsplit('.', 1)[1] + " [flashx]", media_url])

    for video_url in video_urls:
        logger.info("pelisalacarta.servers.flashx %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    # http://flashx.tv/z3nnqbspjyne
    # http://www.flashx.tv/embed-li5ydvxhg514.html
    patronvideos = 'flashx.(?:tv|pw)/(?:embed-|)([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.flashx find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[flashx]"
        url = "http://www.flashx.tv/playvid-%s.html" % match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'flashx'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
