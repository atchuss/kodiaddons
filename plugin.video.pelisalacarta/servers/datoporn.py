# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para datoporn
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re

from core import jsunpack
from core import logger
from core import scrapertools

	
def test_video_exists(page_url):
    logger.info("pelisalacarta.servers.datoporn test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if 'FILE NOT FOUND' in data:
        return False, "[Datoporn] El archivo no existe o ha sido borrado" 

    return True, ""


def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.datoporn url="+page_url)

    data = scrapertools.cache_page(page_url)

    match = scrapertools.find_single_match(data, "<script type='text/javascript'>(.*?)</script>")
    data = jsunpack.unpack(match)

    # Extrae la URL
    video_urls = []
    media_urls = scrapertools.find_multiple_matches(data,'\[\{file\:"([^"]+)"')
    for media_url in media_urls:
        video_urls.append( [ "."+media_url.rsplit('.',1)[1]+" [datoporn]", media_url])

    for video_url in video_urls:
        logger.info("pelisalacarta.servers.datoporn %s - %s" % (video_url[0],video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):

    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    patronvideos  = 'datoporn.com/(?:embed-|)([A-z0-9]+)'
    logger.info("pelisalacarta.servers.datoporn find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[datoporn]"
        url = "http://datoporn.com/embed-%s.html" % match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'datoporn' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
