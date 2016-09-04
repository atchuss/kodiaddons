# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para hdfull
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re
import sys
import urllib
import urlparse

from core import config
from core import jsontools
from core import logger
from core import scrapertools
from core.item import Item
from platformcode import platformtools
from core import servertools

import xbmc

host = "http://hdfull.tv"
account = ( config.get_setting('hdfulluser', 'hdfull') != "" )


def settingCanal(item):
    return platformtools.show_channel_settings()

def login():
    logger.info("pelisalacarta.channels.hdfull login")

    data = agrupa_datos( scrapertools.cache_page(host) )

    patron = "<input type='hidden' name='__csrf_magic' value=\"([^\"]+)\" />"
    sid = scrapertools.find_single_match(data, patron)

    post = urllib.urlencode({'__csrf_magic':sid})+"&username="+config.get_setting('hdfulluser', 'hdfull')+"&password="+config.get_setting('hdfullpassword', 'hdfull')+"&action=login"

    data = scrapertools.cache_page(host,post=post)

def mainlist(item):
    logger.info("pelisalacarta.channels.hdfull mainlist")

    itemlist = []

    itemlist.append( Item( channel=item.channel, action="menupeliculas", title="Películas", url=host, folder=True ) )
    itemlist.append( Item( channel=item.channel, action="menuseries", title="Series", url=host, folder=True ) )
    itemlist.append( Item( channel=item.channel, action="search", title="Buscar..." ) )
    if not account:
        itemlist.append( Item( channel=item.channel , title=bbcode_kodi2html("[COLOR orange][B]Habilita tu cuenta para activar los items de usuario...[/B][/COLOR]"), action="settingCanal", url="" ) )
    else:
        login()
        itemlist.append( Item(channel=item.channel, action="settingCanal"    , title="Configuración..."     , url="" ))

    return itemlist

def menupeliculas(item):
    logger.info("pelisalacarta.channels.hdfull menupeliculas")

    itemlist = []

    if account:
        itemlist.append( Item( channel=item.channel, action="items_usuario", title=bbcode_kodi2html("[COLOR orange][B]Favoritos[/B][/COLOR]"), url=host+"/a/my?target=movies&action=favorite&start=-28&limit=28", folder=True ) )

    itemlist.append( Item( channel=item.channel, action="fichas", title="ABC", url=host+"/peliculas/abc", folder=True ) )
    itemlist.append( Item( channel=item.channel, action="fichas", title="Últimas películas" , url=host+"/peliculas", folder=True ) )
    itemlist.append( Item( channel=item.channel, action="fichas", title="Películas Estreno", url=host+"/peliculas-estreno", folder=True ) )
    itemlist.append( Item( channel=item.channel, action="fichas", title="Películas Actualizadas", url=host+"/peliculas-actualizadas", folder=True ) )
    itemlist.append( Item( channel=item.channel, action="fichas", title="Rating IMDB", url=host+"/peliculas/imdb_rating", folder=True ) )
    itemlist.append( Item( channel=item.channel, action="generos", title="Películas por Género", url=host, folder=True))

    return itemlist

def menuseries(item):
    logger.info("pelisalacarta.channels.hdfull menuseries")

    itemlist = []

    if account:
        itemlist.append( Item( channel=item.channel, action="items_usuario", title=bbcode_kodi2html("[COLOR orange][B]Siguiendo[/B][/COLOR]"), url=host+"/a/my?target=shows&action=following&start=-28&limit=28", folder=True ) )
        itemlist.append( Item( channel=item.channel, action="items_usuario", title=bbcode_kodi2html("[COLOR orange][B]Para Ver[/B][/COLOR]"), url=host+"/a/my?target=shows&action=watch&start=-28&limit=28", folder=True ) )

    itemlist.append( Item( channel=item.channel, action="series_abc", title="A-Z", folder=True ) )

    itemlist.append( Item(channel=item.channel, action="novedades_episodios", title="Últimos Emitidos", url=host+"/a/episodes?action=latest&start=-24&limit=24&elang=ALL", folder=True ) )
    itemlist.append( Item(channel=item.channel, action="novedades_episodios", title="Episodios Estreno", url=host+"/a/episodes?action=premiere&start=-24&limit=24&elang=ALL", folder=True ) )
    itemlist.append( Item(channel=item.channel, action="novedades_episodios", title="Episodios Actualizados", url=host+"/a/episodes?action=updated&start=-24&limit=24&elang=ALL", folder=True ) )
    itemlist.append( Item(channel=item.channel, action="fichas", title="Últimas series", url=host+"/series", folder=True ) )
    itemlist.append( Item(channel=item.channel, action="fichas", title="Rating IMDB", url=host+"/series/imdb_rating", folder=True ) )
    itemlist.append( Item(channel=item.channel, action="generos_series", title="Series por Género", url=host, folder=True ) )
    itemlist.append( Item( channel=item.channel, action="listado_series", title="Listado de todas las series", url=host+"/series/list", folder=True ) )

    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.channels.hdfull search")

    data = agrupa_datos( scrapertools.cache_page(host) )

    texto = texto.replace('+','%20')

    sid = scrapertools.get_match(data, '.__csrf_magic. value="(sid:[^"]+)"')
    item.extra = urllib.urlencode({'__csrf_magic':sid})+'&menu=search&query='+texto
    item.url = host+"/buscar"

    try:
        return fichas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def series_abc(item):
    logger.info("pelisalacarta.channels.hdfull series_abc")

    itemlist=[]

    az = "ABCDEFGHIJKLMNOPQRSTUVWXYZ#"

    for l in az:
        itemlist.append( Item( channel=item.channel, action='fichas', title=l, url=host+"/series/abc/"+l.replace('#' ,'9') ) )

    return itemlist

def items_usuario(item):
    logger.info("pelisalacarta.channels.hdfull menupeliculas")

    itemlist = []

    ## Carga estados
    status = jsontools.load_json(scrapertools.cache_page(host+'/a/status/all'))

    ## Fichas usuario
    url = item.url.split("?")[0]
    post = item.url.split("?")[1]

    old_start = scrapertools.get_match(post, 'start=([^&]+)&')
    limit = scrapertools.get_match(post, 'limit=(\d+)')
    start = "%s" % ( int(old_start) + int(limit) )

    post = post.replace("start="+old_start, "start="+start)
    next_page = url + "?" + post

    ## Carga las fichas de usuario
    data = scrapertools.cache_page(url, post=post)
    fichas_usuario = jsontools.load_json( data )

    for ficha in fichas_usuario:

        try: title = ficha['title']['es'].strip()
        except: title = ficha['title']['en'].strip()

        try: title = title.encode('utf-8')
        except: pass

        show = title

        try: thumbnail = host+"/thumbs/" + ficha['thumbnail']
        except: thumbnail = host+"/thumbs/" + ficha['thumb']

        try:
            url = urlparse.urljoin( host, '/serie/'+ ficha['permalink'] ) + "###" + ficha['id'] + ";1"
            action = "episodios"
            sstr = get_status(status, 'shows', ficha['id'])
            if "show_title" in ficha:
                action = "findvideos"
                try: serie = ficha['show_title']['es'].strip()
                except: serie = ficha['show_title']['en'].strip()
                temporada = ficha['season']
                episodio = ficha['episode']
                serie = bbcode_kodi2html("[COLOR whitesmoke][B]" + serie + "[/B][/COLOR]")
                if len(episodio) == 1: episodio = '0' + episodio
                try: title = temporada + "x" + episodio + " - " + serie + ": " + title
                except: title = temporada + "x" + episodio + " - " + serie.decode('iso-8859-1') + ": " + title.decode('iso-8859-1')
                url = urlparse.urljoin( host, '/serie/' + ficha['permalink'] + '/temporada-' + temporada +'/episodio-' + episodio ) + "###" + ficha['id'] + ";3"
        except:
            url = urlparse.urljoin( host, '/pelicula/'+ ficha['perma'] ) + "###" + ficha['id'] + ";2"
            action = "findvideos"
            sstr = get_status(status, 'movies', ficha['id'])
        if sstr != "": title+= sstr

        #try: title = title.encode('utf-8')
        #except: pass

        itemlist.append( Item( channel=item.channel, action=action, title=title, fulltitle=title, url=url, thumbnail=thumbnail, show=show, folder=True ) )

    if len(itemlist) == int(limit):
        itemlist.append( Item( channel=item.channel, action="items_usuario", title=">> Página siguiente", url=next_page, folder=True ) )

    return itemlist

def listado_series(item):
    logger.info("pelisalacarta.channels.hdfull listado_series")

    itemlist = []

    data = agrupa_datos( scrapertools.cache_page(item.url) )

    patron = '<div class="list-item"><a href="([^"]+)"[^>]+>([^<]+)</a></div>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        url = scrapedurl + "###0;1"
        itemlist.append( Item( channel=item.channel, action="episodios", title=scrapedtitle, fulltitle=scrapedtitle, url=url, show=scrapedtitle ) )

    return itemlist

def fichas(item):
    logger.info("pelisalacarta.channels.hdfull series")
    itemlist = []

    ## Carga estados
    status = jsontools.load_json(scrapertools.cache_page(host+'/a/status/all'))

    if item.title == "Buscar...":
        data = agrupa_datos( scrapertools.cache_page(item.url,post=item.extra) )

        s_p = scrapertools.get_match(data, '<h3 class="section-title">(.*?)<div id="footer-wrapper">').split('<h3 class="section-title">')

        if len(s_p) == 1:
            data = s_p[0]
            if 'Lo sentimos</h3>' in s_p[0]:
                return [ Item( channel=item.channel, title=bbcode_kodi2html("[COLOR gold][B]HDFull:[/B][/COLOR] [COLOR blue]"+texto.replace('%20',' ')+"[/COLOR] sin resultados") ) ]
        else:
            data = s_p[0]+s_p[1]
    else:
        data = agrupa_datos( scrapertools.cache_page(item.url) )

    data = re.sub(
        r'<div class="span-6[^<]+<div class="item"[^<]+' + \
         '<a href="([^"]+)"[^<]+' + \
         '<img.*?src="([^"]+)".*?' + \
         '<div class="left"(.*?)</div>' + \
         '<div class="right"(.*?)</div>.*?' + \
         'title="([^"]+)".*?' + \
         'onclick="setFavorite.\d, (\d+),',
         r"'url':'\1';'image':'\2';'langs':'\3';'rating':'\4';'title':\5;'id':'\6';",
        data
    )

    patron  = "'url':'([^']+)';'image':'([^']+)';'langs':'([^']+)';'rating':'([^']+)';'title':([^;]+);'id':'([^']+)';"
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedlangs, scrapedrating, scrapedtitle, scrapedid in matches:

        thumbnail = scrapedthumbnail.replace("/tthumb/130x190/","/thumbs/")

        title = scrapedtitle.strip()
        show = title

        if scrapedlangs != ">":
            textoidiomas = extrae_idiomas(scrapedlangs)
            title+= bbcode_kodi2html(" ( [COLOR teal][B]" + textoidiomas + "[/B][/COLOR])")

        valoracion = ''
        if scrapedrating != ">":
            valoracion = re.sub(r'><[^>]+>(\d+)<b class="dec">(\d+)</b>', r'\1,\2', scrapedrating)
            title+= bbcode_kodi2html(" ([COLOR orange]" + valoracion + "[/COLOR])")

        url = urlparse.urljoin(item.url, scrapedurl)

        if "/serie" in url or "/tags-tv" in url:
            action = "episodios"
            url+=  "###" + scrapedid + ";1"
            type = "shows"
        else:
            action = "findvideos"
            url+=  "###" + scrapedid + ";2"
            type = "movies"

        sstr = get_status(status, type, scrapedid)
        if sstr != "": title+= sstr

        if item.title == "Buscar...":
            tag_type = scrapertools.get_match(url,'l.tv/([^/]+)/')
            title+= bbcode_kodi2html(" - [COLOR blue]" + tag_type.capitalize() + "[/COLOR]")

        from core import config
        jjspa = config.get_setting("hdfull_spa")
        jjbna = config.get_setting("hdfull_bna")
        jjmin = config.get_setting("hdfull_min")
        jjok = True

        if jjspa == 'true' and 'SPA' not in title:
            jjok = False
        
        if jjbna == 'true':
            jjmin = int(jjmin)+5
            jjcad = ''
            for x in range(jjmin, 10):
                jjcad += str(x)

        if jjbna == 'true' and (valoracion[0:1] not in jjcad or valoracion == ''):
            jjok = False

        logger.info("JJPALC valr : " + str(valoracion))

        if jjok:
            itemlist.append( Item( channel=item.channel, action=action, title=title, url=url, fulltitle=title, thumbnail=thumbnail, show=show, folder=True ) )

    ## Paginación
    next_page_url = scrapertools.find_single_match(data,'<a href="([^"]+)">.raquo;</a>')
    if next_page_url!="":
        itemlist.append( Item( channel=item.channel, action="fichas", title=">> Página siguiente", url=urlparse.urljoin(item.url,next_page_url), folder=True ) )

    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.hdfull episodios")

    itemlist = []

    ## Carga estados
    status = jsontools.load_json(scrapertools.cache_page(host+'/a/status/all'))

    url_targets = item.url

    if "###" in item.url:
        id = item.url.split("###")[1].split(";")[0]
        type = item.url.split("###")[1].split(";")[1]
        item.url = item.url.split("###")[0]

    ## Temporadas
    data = agrupa_datos( scrapertools.cache_page(item.url) )

    if id == "0":
        ## Se saca el id de la serie de la página cuando viene de listado_series
        id = scrapertools.get_match(data, "<script>var sid = '([^']+)';</script>")
        url_targets = url_targets.replace('###0','###' + id)

    sstr = get_status(status, "shows", id)
    if sstr != "" and account and item.category != "Series" and "XBMC" not in item.title:
        if config.get_library_support():
            title = bbcode_kodi2html(" ( [COLOR gray][B]" + item.show + "[/B][/COLOR] )")
            itemlist.append( Item( channel=item.channel, action="episodios", title=title, fulltitle=title, url=url_targets, thumbnail=item.thumbnail, show=item.show, folder=False ) )
        title = sstr.replace('green','red').replace('Siguiendo','Abandonar')
        itemlist.append( Item( channel=item.channel, action="set_status", title=title, fulltitle=title, url=url_targets, thumbnail=item.thumbnail, show=item.show, folder=True ) )
    elif account and item.category != "Series" and "XBMC" not in item.title:
        if config.get_library_support():
            title = bbcode_kodi2html(" ( [COLOR gray][B]" + item.show + "[/B][/COLOR] )")
            itemlist.append( Item( channel=item.channel, action="episodios", title=title, fulltitle=title, url=url_targets, thumbnail=item.thumbnail, show=item.show, folder=False ) )
        title = bbcode_kodi2html(" ( [COLOR orange][B]Seguir[/B][/COLOR] )")
        itemlist.append( Item( channel=item.channel, action="set_status", title=title, fulltitle=title, url=url_targets, thumbnail=item.thumbnail, show=item.show, folder=True ) )

    patron  = "<li><a href='([^']+)'>[^<]+</a></li>"

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl in matches:

        ## Episodios
        data = agrupa_datos( scrapertools.cache_page(scrapedurl) )

        sid = scrapertools.get_match(data,"<script>var sid = '(\d+)'")
        ssid = scrapertools.get_match(scrapedurl,"temporada-(\d+)")
        post = "action=season&start=0&limit=0&show=%s&season=%s" % (sid, ssid)

        url = host+"/a/episodes"

        data = scrapertools.cache_page(url,post=post)

        episodes = jsontools.load_json( data )

        for episode in episodes:

            thumbnail = host+"/thumbs/" + episode['thumbnail']

            temporada = episode['season']
            episodio = episode['episode']
            if len(episodio) == 1: episodio = '0' + episodio

            if episode['languages'] != "[]":
                idiomas = "( [COLOR teal][B]"
                for idioma in episode['languages']: idiomas+= idioma + " "
                idiomas+= "[/B][/COLOR])"
                idiomas = bbcode_kodi2html(idiomas)
            else: idiomas = ""

            if episode['title']:
                try: title = episode['title']['es'].strip()
                except: title = episode['title']['en'].strip()

            if len(title) == 0: title = "Temporada " + temporada + " Episodio " + episodio

            try: title = temporada + "x" + episodio + " - " + title.decode('utf-8') + ' ' + idiomas
            except: title = temporada + "x" + episodio + " - " + title.decode('iso-8859-1') + ' ' + idiomas
            #try: title = temporada + "x" + episodio + " - " + title + ' ' + idiomas
            #except: pass
            #except: title = temporada + "x" + episodio + " - " + title.decode('iso-8859-1') + ' ' + idiomas

            sstr = get_status(status, 'episodes', episode['id'])
            if sstr != "": title+= sstr

            try: title = title.encode('utf-8')
            except:  title = title.encode('iso-8859-1')

            url = urlparse.urljoin( scrapedurl, 'temporada-' + temporada +'/episodio-' + episodio ) + "###" + episode['id'] + ";3"

            itemlist.append( Item( channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url, thumbnail=thumbnail, show=item.show, folder=True ) )

    if config.get_library_support() and len(itemlist)>0:
        itemlist.append( Item( channel=item.channel, title="Añadir esta serie a la biblioteca de XBMC", url=url_targets, action="add_serie_to_library", extra="episodios", show=item.show ) )
        itemlist.append( Item( channel=item.channel, title="Descargar todos los episodios de la serie", url=url_targets, action="download_all_episodes", extra="episodios", show=item.show ) )

    return itemlist

def novedades_episodios(item):
    logger.info("pelisalacarta.channels.hdfull novedades_episodios")

    itemlist = []

    ## Carga estados
    status = jsontools.load_json(scrapertools.cache_page(host+'/a/status/all'))

    ## Episodios
    url = item.url.split("?")[0]
    post = item.url.split("?")[1]

    old_start = scrapertools.get_match(post, 'start=([^&]+)&')
    start = "%s" % ( int(old_start) + 24 )

    post = post.replace("start="+old_start, "start="+start)
    next_page = url + "?" + post

    data = scrapertools.cache_page(url, post=post)

    episodes = jsontools.load_json( data )

    for episode in episodes:

        thumbnail = host+"/thumbs/" + episode['thumbnail']

        temporada = episode['season']
        episodio = episode['episode']
        if len(episodio) == 1: episodio = '0' + episodio

        if episode['languages'] != "[]":
            idiomas = "( [COLOR teal][B]"
            for idioma in episode['languages']: idiomas+= idioma + " "
            idiomas+= "[/B][/COLOR])"
            idiomas = bbcode_kodi2html(idiomas)
        else: idiomas = ""

        try: show = episode['show']['title']['es'].strip()
        except: show = episode['show']['title']['en'].strip()

        show = bbcode_kodi2html("[COLOR whitesmoke][B]" + show + "[/B][/COLOR]")

        if episode['title']:
            try: title = episode['title']['es'].strip()
            except: title = episode['title']['en'].strip()

        if len(title) == 0: title = "Temporada " + temporada + " Episodio " + episodio

        try: title = temporada + "x" + episodio + " - " + show.decode('utf-8') + ": " + title.decode('utf-8') + ' ' + idiomas
        except: title = temporada + "x" + episodio + " - " + show.decode('iso-8859-1') + ": " + title.decode('iso-8859-1') + ' ' + idiomas

        sstr = get_status(status, 'episodes', episode['id'])
        if sstr != "": title+= sstr

        try: title = title.encode('utf-8')
        except:  title = title.encode('iso-8859-1')
        #try: show = show.encode('utf-8')
        #except:  show = show.encode('iso-8859-1')

        url = urlparse.urljoin( host, '/serie/'+ episode['permalink'] +'/temporada-' + temporada +'/episodio-' + episodio ) + "###" + episode['id'] + ";3"

        itemlist.append( Item( channel=item.channel, action="findvideos", title=title, fulltitle=title, url=url, thumbnail=thumbnail, folder=True ) )

    if len(itemlist) == 24:
        itemlist.append( Item( channel=item.channel, action="novedades_episodios", title=">> Página siguiente", url=next_page, folder=True ) )

    return itemlist

def generos(item):
    logger.info("pelisalacarta.channels.hdfull generos")

    itemlist = []

    data = agrupa_datos( scrapertools.cache_page(item.url) )
    data = scrapertools.find_single_match(data,'<li class="dropdown"><a href="http://hdfull.tv/peliculas"(.*?)</ul>')

    patron  = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""

        itemlist.append( Item( channel=item.channel, action="fichas", title=title, url=url, folder=True ) )

    return itemlist

def generos_series(item):
    logger.info("pelisalacarta.channels.hdfull generos_series")

    itemlist = []

    data = agrupa_datos( scrapertools.cache_page(item.url) )
    data = scrapertools.find_single_match(data,'<li class="dropdown"><a href="http://hdfull.tv/series"(.*?)</ul>')

    patron  = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""

        itemlist.append( Item( channel=item.channel, action="fichas", title=title, url=url, folder=True ) )

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.channels.hdfull findvideos")

    itemlist=[]

    ## Carga estados
    status = jsontools.load_json(scrapertools.cache_page(host+'/a/status/all'))

    url_targets = item.url

    ## Vídeos
    if "###" in item.url:
        id = item.url.split("###")[1].split(";")[0]
        type = item.url.split("###")[1].split(";")[1]
        item.url = item.url.split("###")[0]

    if type == "2" and account and item.category != "Cine":
        title = bbcode_kodi2html(" ( [COLOR orange][B]Agregar a Favoritos[/B][/COLOR] )")
        if "Favorito" in item.title:
            title = bbcode_kodi2html(" ( [COLOR red][B]Quitar de Favoritos[/B][/COLOR] )")
        if config.get_library_support():
            title_label = bbcode_kodi2html(" ( [COLOR gray][B]" + item.show + "[/B][/COLOR] )")
            itemlist.append( Item( channel=item.channel, action="findvideos", title=title_label, fulltitle=title_label, url=url_targets, thumbnail=item.thumbnail, show=item.show, folder=False ) )

            title_label = bbcode_kodi2html(" ( [COLOR green][B]Tráiler[/B][/COLOR] )")

            itemlist.append( Item( channel=item.channel, action="trailer", title=title_label, fulltitle=title_label, url=url_targets, thumbnail=item.thumbnail, show=item.show ) )

        itemlist.append( Item( channel=item.channel, action="set_status", title=title, fulltitle=title, url=url_targets, thumbnail=item.thumbnail, show=item.show, folder=True ) )

    data = agrupa_datos( scrapertools.cache_page(item.url) )

    patron  = '<div class="embed-selector"[^<]+'
    patron += '<h5 class="left"[^<]+'
    patron += '<span[^<]+<b class="key">\s*Idioma.\s*</b>([^<]+)</span[^<]+'
    patron += '<span[^<]+<b class="key">\s*Servidor.\s*</b><b[^>]+>([^<]+)</b[^<]+</span[^<]+'
    patron += '<span[^<]+<b class="key">\s*Calidad.\s*</b>([^<]+)</span[^<]+</h5.*?'
    patron += '<a href="(http[^"]+)".*?'
    patron += '</i>([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for idioma,servername,calidad,url,opcion in matches:
        opcion = opcion.strip()
        if opcion != "Descargar":
            opcion = "Ver"
        title = opcion+": "+servername.strip()+" ("+calidad.strip()+")"+" ("+idioma.strip()+")"
        title = scrapertools.htmlclean(title)
        #Se comprueba si existe el conector y si se oculta en caso de premium
        servername = servername.lower().split(".")[0]

        if servername == "streamin": servername = "streaminto"
        if servername== "waaw": servername = "netutv"
        if servername == "ul": servername = "uploadedto"
        mostrar_server = True
        if config.get_setting("hidepremium")=="true":
            mostrar_server= servertools.is_server_enabled (servername)
        if mostrar_server:
            try:
                servers_module = __import__("servers."+servername)
                thumbnail = item.thumbnail
                plot = item.title+"\n\n"+scrapertools.find_single_match(data,'<meta property="og:description" content="([^"]+)"')
                plot = scrapertools.htmlclean(plot)
                fanart = scrapertools.find_single_match(data,'<div style="background-image.url. ([^\s]+)')

                url+= "###" + id + ";" + type

                itemlist.append( Item( channel=item.channel, action="play", title=title, fulltitle=title, url=url, thumbnail=thumbnail, plot=plot, fanart=fanart, show=item.show, folder=True ) )
            except:
                pass

    ## 2 = película
    if type == "2" and item.category != "Cine":
        ## STRM para todos los enlaces de servidores disponibles
        ## Si no existe el archivo STRM de la peícula muestra el item ">> Añadir a la biblioteca..."
        try: itemlist.extend( file_cine_library(item,url_targets) )
        except: pass

    return itemlist

def trailer(item):
    import youtube
    itemlist = []
    item.url = "https://www.googleapis.com/youtube/v3/search" + \
                "?q=" + item.show.replace(" ","+") + "+trailer+HD+Español" \
                "&regionCode=ES" + \
                "&part=snippet" + \
                "&hl=es_ES" + \
                "&key=AIzaSyAd-YEOqZz9nXVzGtn3KWzYLbLaajhqIDA" + \
                "&type=video" + \
                "&maxResults=50" + \
                "&pageToken="
    itemlist.extend(youtube.fichas(item))
    #itemlist.pop(-1)
    return itemlist

def file_cine_library(item,url_targets):
    import os
    from core import filetools
    librarypath = os.path.join(config.get_library_path(),"CINE")
    archivo = item.show.strip()
    strmfile = archivo+".strm"
    strmfilepath = filetools.join(librarypath,strmfile)

    if not os.path.exists(strmfilepath):
        itemlist = []
        itemlist.append( Item(channel=item.channel, title=">> Añadir a la biblioteca...", url=url_targets, action="add_file_cine_library", extra="episodios", show=archivo) )

    return itemlist


def add_file_cine_library(item):
    from platformcode import library, xbmctools
    new_item = item.clone(title=item.show, action="play_from_library")
    library.save_library_movie(new_item)
    itemlist = []
    itemlist.append(Item(title='El vídeo '+item.show+' se ha añadido a la biblioteca'))
    xbmctools.renderItems(itemlist, "", "", "")

    return

def play(item):
    logger.info("pelisalacarta.channels.hdfull play")

    if "###" in item.url:
        id = item.url.split("###")[1].split(";")[0]
        type = item.url.split("###")[1].split(";")[1]
        item.url = item.url.split("###")[0]

    if "aHR0c" in item.url:
        import base64
        item.url = base64.decodestring(item.url.split("/")[-1])
        if "VideoMega" in item.title and not "videomega" in item.url:
            item.url = "http://videomega.tv/cdn.php?" + item.url

    itemlist = servertools.find_video_items(data=item.url)

    xbmc.log("PLAY_JJSR_url.....: %s" %(item.url)) # 333

    for videoitem in itemlist:

    #   xbmc.log("PLAY_JJSR_show.....: %s" %(item.show)) # 333
    #   xbmc.log("PLAY_JJSR_fulltitle: %s" %(item.fulltitle))
    #   xbmc.log("PLAY_JJSR_thumbnail: %s" %(item.thumbnail))
    #   xbmc.log("PLAY_JJSR_channel..: %s" %(item.channel))

    #   videoitem.title = item.show
    #   videoitem.fulltitle = item.fulltitle
        videoitem.title = item.fulltitle
        videoitem.fulltitle = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = item.channel
        post = "target_id=%s&target_type=%s&target_status=1" % (id, type)
        data = scrapertools.cache_page(host+"/a/status",post=post)

    return itemlist

## --------------------------------------------------------------------------------
## --------------------------------------------------------------------------------

def agrupa_datos(data):
    ## Agrupa los datos
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|<!--.*?-->','',data)
    data = re.sub(r'\s+',' ',data)
    data = re.sub(r'>\s<','><',data)
    return data

def extrae_idiomas(bloqueidiomas):
    logger.info("idiomas="+bloqueidiomas)
    patronidiomas = '([a-z0-9]+).png"'
    idiomas = re.compile(patronidiomas,re.DOTALL).findall(bloqueidiomas)
    textoidiomas = ""
    for idioma in idiomas:
        textoidiomas = textoidiomas + idioma.upper() + " "

    return textoidiomas

def bbcode_kodi2html(text):
    if config.get_platform().startswith("plex") or config.get_platform().startswith("mediaserver"):
        import re
        text = re.sub(r'\[COLOR\s([^\]]+)\]',
                      r'<span style="color: \1">',
                      text)
        text = text.replace('[/COLOR]','</span>')
        text = text.replace('[CR]','<br>')
        text = re.sub(r'\[([^\]]+)\]',
                      r'<\1>',
                      text)
        text = text.replace('"color: white"','"color: auto"')

    return text

## --------------------------------------------------------------------------------

def set_status(item):

    if "###" in item.url:
        id = item.url.split("###")[1].split(";")[0]
        type = item.url.split("###")[1].split(";")[1]
        #item.url = item.url.split("###")[0]

    if "Abandonar" in item.title:
        path = "/a/status"
        post = "target_id=" + id + "&target_type=" + type + "&target_status=0"

    elif "Seguir" in item.title:
        target_status = "3"
        path = "/a/status"
        post = "target_id=" + id + "&target_type=" + type + "&target_status=3"

    elif "Agregar a Favoritos" in item.title:
        path = "/a/favorite"
        post = "like_id=" + id + "&like_type=" + type + "&like_comment=&vote=1"

    elif "Quitar de Favoritos" in item.title:
        path = "/a/favorite"
        post = "like_id=" + id + "&like_type=" + type + "&like_comment=&vote=-1"

    data = scrapertools.cache_page(host + path, post=post)

    title = bbcode_kodi2html("[COLOR green][B]OK[/B][/COLOR]")

    return [ Item( channel=item.channel, action="episodios", title=title, fulltitle=title, url=item.url, thumbnail=item.thumbnail, show=item.show, folder=False ) ]

def get_status(status,type,id):

    if type == 'shows':
        state = {'0':'','1':'Finalizada','2':'Pendiente','3':'Siguiendo'}
    else:
        state = {'0':'','1':'Visto','2':'Pendiente'}

    sstr = ""; sstr1 = ""; sstr2 = ""

    try:
        if id in status['favorites'][type]:
            sstr1 = bbcode_kodi2html( " [COLOR orange][B]Favorito[/B][/COLOR]" )
    except:
        sstr1 = ""

    try:
        if id in status['status'][type]:
            sstr2 = state[ status['status'][type][id] ]
            if sstr2 != "": sstr2 = bbcode_kodi2html( " [COLOR green][B]" + state[ status['status'][type][id] ] + "[/B][/COLOR]" )
    except:
        sstr2 = ""

    if sstr1 != "" or sstr2 != "":
        sstr = " (" + sstr1 + sstr2 + " )"

    return sstr

## --------------------------------------------------------------------------------
## --------------------------------------------------------------------------------
