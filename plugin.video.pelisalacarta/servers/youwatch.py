# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para youwatch
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("pelisalacarta.servers.youwatch test_video_exists(page_url='%s')" % page_url)
    data = scrapertools.cache_page(page_url)
    if "File Not Found" in data: return False, "[Youwatch] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("pelisalacarta.servers.youwatch get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    url_redirect = scrapertools.find_single_match(data, '<iframe src="([^"]+)"')
    data = scrapertools.cache_page(url_redirect)

    url = scrapertools.get_match(data, '{file:"([^"]+)"')
    video_url = url + "|Referer=" + url_redirect
    video_urls = [[scrapertools.get_filename_from_url(url)[-4:] + " [youwatch]", video_url]]

    for video_url in video_urls:
        logger.info("pelisalacarta.servers.youwatch %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://chouhaa.info/embed-ihc21y2tqpnt.html
    # http://youwatch.org/ihc21y2tqpnt
    patronvideos = 'http://(?:youwatch.org|chouhaa.info)/(?:embed-|)([a-z0-9]+)'
    logger.info("pelisalacarta.servers.youwatch find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[youwatch]"
        url = "http://chouhaa.info/embed-%s.html" % match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'youwatch'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
