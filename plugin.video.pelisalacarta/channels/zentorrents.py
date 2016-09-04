# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para zentorrents
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re
import sys
import urllib
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item

try:
    import xbmc
    import xbmcgui
except: pass


DEBUG = config.get_setting("debug")
host = "http://www.zentorrents.com/"


def mainlist(item):
    logger.info("pelisalacarta.zentorrents mainlist")
    
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Películas"      , action="peliculas", url="http://www.zentorrents.com/peliculas" ,thumbnail="http://www.navymwr.org/assets/movies/images/img-popcorn.png", fanart="http://s18.postimg.org/u9wyvm809/zen_peliculas.jpg"))
    itemlist.append( Item(channel=item.channel, title="MicroHD" , action="peliculas", url="http://www.zentorrents.com/tags/microhd" ,thumbnail="http://s11.postimg.org/5s67cden7/microhdzt.jpg", fanart="http://s9.postimg.org/i5qhadsjj/zen_1080.jpg"))
    itemlist.append( Item(channel=item.channel, title="HDrip"  , action="peliculas", url="http://www.zentorrents.com/tags/hdrip", thumbnail="http://s10.postimg.org/pft9z4c5l/hdripzent.jpg", fanart="http://s15.postimg.org/5kqx9ln7v/zen_720.jpg"))
    itemlist.append( Item(channel=item.channel, title="Series"         , action="peliculas", url="http://www.zentorrents.com/series",  thumbnail="http://data2.whicdn.com/images/10110324/original.jpg", fanart="http://s10.postimg.org/t0xz1t661/zen_series.jpg"))
    itemlist.append( Item(channel=item.channel, title="Buscar..."      , action="search"   , url="http://www.zentorrents.com/buscar", thumbnail="http://newmedia-art.pl/product_picture/full_size/bed9a8589ad98470258899475cf56cca.jpg", fanart="http://s23.postimg.org/jdutugvrf/zen_buscar.jpg"))
    
    
    return itemlist
def bbcode_kodi2html(text):
    
    if config.get_platform().startswith("plex") or config.get_platform().startswith("mediaserver"):
        import re
        text = re.sub(r'\[COLOR\s([^\]]+)\]',
                      r'<span style="color: \1">',
                      text)
        text = text.replace('[/COLOR]','</span>')
        text = text.replace('[CR]','<br>')
        text = text.replace('[B]','<b>')
        text = text.replace('[/B]','</b>')
        text = text.replace('"color: yellow"','"color: gold"')
        text = text.replace('"color: white"','"color: auto"')
    
    return text


def search(item, texto):
    logger.info("pelisalacarta.palasaka search")
    itemlist = []
    
    try:
        texto = texto.replace(" ", "+")
        item.url += "/buscar?searchword=%s&ordering=&searchphrase=all&limit=\d+"
        item.url = item.url % texto
        itemlist.extend(buscador(item, texto.replace("+", " ")))
        
        return itemlist
    
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def buscador(item, texto):
    logger.info("pelisalacarta.zentorrents buscador")
    itemlist = []
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    if "highlight" in data:
        searchword = scrapertools.get_match(data, '<span class="highlight">([^<]+)</span>')
        data = re.sub(r'<span class="highlight">[^<]+</span>', searchword, data)
    '''
    <div class="moditemfdb">
        <a title="La hora decisiva [1080p]" href="/peliculas/51842-la-hora-decisiva-1080p">
            <img alt="La hora decisiva [1080p]" class="thumbnailresult"
                src="http://www.zentorrents.com/images/articles/51/51842t.jpg">
        </a>
        <div class="info">
            <div class="title">
                <a class="" href="/peliculas/51842-la-hora-decisiva-1080p">La hora decisiva [1080p]</a>
            </div>
            <p>Descargas/Películas			</p>
        </div>
        <div style="clear:both;"></div>
    </div>
    '''

    patron = '<div class="moditemfdb">'       # Empezamos el patrón por aquí para que no se cuele nada raro
    patron += '<a title="([^"]+)" '                       # scrapedtitulo
    patron += 'href="([^"]+)".*?'                         # scrapedurl
    patron += 'src="([^"]+)".*?'                          # scrapedthumbnail
    patron += '<p>([^<]+)</p>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches) == 0:
        itemlist.append(Item(channel=item.channel, title="[COLOR gold][B]Sin resultados...[/B][/COLOR]",
                             thumbnail="http://s6.postimg.org/55zljwr4h/sinnoisethumb.png",
                             fanart="http://s6.postimg.org/avfu47xap/sinnoisefan.jpg", folder=False))

    for scrapedtitulo, scrapedurl, scrapedthumbnail, scrapedplot in matches:
        # evitamos falsos positivos en los enlaces, ya que el buscador de la web muestra de todo,
        # tiene que ser una descarga y que el texto a buscar esté en el titulo
        if "Descargas/" in scrapedplot and texto.lower() in scrapedtitulo.lower():
            trailer = scrapedtitulo + " " + "trailer"
            if "series" in scrapedurl:
                trailer = scrapedtitulo + " " + "series" + "trailer"
            else:
                trailer = scrapedtitulo + " " + "trailer"

            trailer = re.sub(r"\[.*?\]|- .*?x\d+", "", trailer)
            trailer = urllib.quote(trailer)
            scrapedtitulo = scrapedtitulo.replace(scrapedtitulo, bbcode_kodi2html("[COLOR white]"+scrapedtitulo +
                                                                                  "[/COLOR]"))
            torrent_tag = bbcode_kodi2html("[COLOR pink] (Torrent)[/COLOR]")
            scrapedtitulo = scrapedtitulo + torrent_tag
            scrapedurl = "http://zentorrents.com" + scrapedurl

            itemlist.append(Item(channel=item.channel, title=scrapedtitulo, url=scrapedurl, action="fanart",
                                 thumbnail=scrapedthumbnail, fulltitle=scrapedtitulo, plot=trailer,
                                 fanart="http://s6.postimg.org/4j8vdzy6p/zenwallbasic.jpg", folder=True))

    return itemlist


def peliculas(item):
    logger.info("pelisalacarta.zentorrents peliculas")
    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|</p>|<p>|&amp;|amp;","",data)
    
    #<div class="blogitem "><a title="En Un Patio De Paris [DVD Rip]" href="/peliculas/17937-en-un-patio-de-paris-dvd-rip"><div class="thumbnail_wrapper"><img alt="En Un Patio De Paris [DVD Rip]" src="http://www.zentorrents.com/images/articles/17/17937t.jpg" onload="imgLoaded(this)" /></div></a><div class="info"><div class="title"><a title="En Un Patio De Paris [DVD Rip]" href="/peliculas/17937-en-un-patio-de-paris-dvd-rip" class="contentpagetitleblog">En Un Patio De Paris [DVD Rip]</a></div><div class="createdate">21/01/2015</div><div class="text">[DVD Rip][AC3 5.1 EspaÃ±ol Castellano][2014] Antoine es un m&uacute;sico de 40 a&ntilde;os que de pronto decide abandonar su carrera.</div></div><div class="clr"></div></div>
    
    patron =  '<div class="blogitem[^>]+>'
    patron += '<a title="([^"]+)" '
    patron += 'href="([^"]+)".*?'
    patron += 'src="([^"]+)".*?'
    patron += '<div class="createdate">([^<]+)</div>'
    
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    for scrapedtitulo, scrapedurl, scrapedthumbnail, scrapedcreatedate in matches:
        
        if "series" in scrapedurl:
            trailer = scrapedtitulo + " " + "series" + "trailer"
        else:
            trailer = scrapedtitulo + " " + "trailer"
        
        trailer= re.sub(r"\[.*?\]|- .*?x\d+","",trailer)
        trailer = urllib.quote(trailer)
        
        scrapedtitulo= scrapedtitulo.replace(scrapedtitulo,bbcode_kodi2html("[COLOR white]"+scrapedtitulo+"[/COLOR]"))
        scrapedcreatedate= scrapedcreatedate.replace(scrapedcreatedate,bbcode_kodi2html("[COLOR bisque]"+scrapedcreatedate+"[/COLOR]"))
        torrent_tag=bbcode_kodi2html("[COLOR pink]Torrent:[/COLOR]")
        scrapedtitulo = scrapedtitulo +  "(" +torrent_tag + scrapedcreatedate + ")"
        scrapedurl = "http://zentorrents.com" + scrapedurl
        itemlist.append( Item(channel=item.channel, title=scrapedtitulo, url=scrapedurl, action="fanart", thumbnail=scrapedthumbnail, fulltitle=scrapedtitulo, plot= trailer, fanart="http://s6.postimg.org/4j8vdzy6p/zenwallbasic.jpg", folder=True) )
    # 1080,720 y seies

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|</p>|<p>|&amp;|amp;","",data)
    
    #<div class="blogitem "><a title="En Un Patio De Paris [DVD Rip]" href="/peliculas/17937-en-un-patio-de-paris-dvd-rip"><div class="thumbnail_wrapper"><img alt="En Un Patio De Paris [DVD Rip]" src="http://www.zentorrents.com/images/articles/17/17937t.jpg" onload="imgLoaded(this)" /></div></a><div class="info"><div class="title"><a title="En Un Patio De Paris [DVD Rip]" href="/peliculas/17937-en-un-patio-de-paris-dvd-rip" class="contentpagetitleblog">En Un Patio De Paris [DVD Rip]</a></div><div class="createdate">21/01/2015</div><div class="text">[DVD Rip][AC3 5.1 EspaÃ±ol Castellano][2014] Antoine es un m&uacute;sico de 40 a&ntilde;os que de pronto decide abandonar su carrera.</div></div><div class="clr"></div></div>
    
    patron =  '<div class="blogitem[^>]+>'
    patron += '<a href="([^"]+)".*? '
    patron += 'title="([^"]+)".*? '
    patron += 'src="([^"]+)".*?'
    patron += '<div class="createdate">([^<]+)</div>'

    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    for scrapedurl, scrapedtitulo, scrapedthumbnail, scrapedcreatedate in matches:
        
        if "series" in scrapedurl:
            trailer = scrapedtitulo + " " + "series" + "trailer"
        else:
            trailer = scrapedtitulo + " " + "trailer"
        
        trailer= re.sub(r"\[.*?\]|- .*?x\d+","",trailer)
        trailer = urllib.quote(trailer)
        
        scrapedtitulo= scrapedtitulo.replace(scrapedtitulo,bbcode_kodi2html("[COLOR white]"+scrapedtitulo+"[/COLOR]"))
        scrapedcreatedate= scrapedcreatedate.replace(scrapedcreatedate,bbcode_kodi2html("[COLOR bisque]"+scrapedcreatedate+"[/COLOR]"))
        torrent_tag=bbcode_kodi2html("[COLOR pink]Torrent:[/COLOR]")
        scrapedtitulo = scrapedtitulo +  "(" +torrent_tag + scrapedcreatedate + ")"
        scrapedurl = "http://zentorrents.com" + scrapedurl
        itemlist.append( Item(channel=item.channel, title=scrapedtitulo, url=scrapedurl, action="fanart", thumbnail=scrapedthumbnail, fulltitle=scrapedtitulo, plot = trailer, fanart="http://s6.postimg.org/4j8vdzy6p/zenwallbasic.jpg", folder=True) )

    # Extrae el paginador
    patronvideos  = '<a href="([^"]+)" title="Siguiente">Siguiente</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        title= bbcode_kodi2html("[COLOR chocolate]siguiente>>[/COLOR]")
        itemlist.append( Item(channel=item.channel, action="peliculas", title= title , url=scrapedurl , thumbnail="http://s6.postimg.org/9iwpso8k1/ztarrow2.png", fanart="http://s6.postimg.org/4j8vdzy6p/zenwallbasic.jpg", folder=True) )
    
    return itemlist

def fanart(item):
    logger.info("pelisalacarta.peliculasdk fanart")
    itemlist = []
    url = item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    if "peliculas" in item.url:
    
        if "microhd" in url or "web" in url or "1080" in url or "bluray" in url or  "HDRip" in item.title:
            title= scrapertools.get_match(data,'<title>([^"]+) \[')
            title= re.sub(r"3D|[0-9]|SBS|\(.*?\)|\[.*?\]|","",title)
            title=title.replace('Perdón','perdon')
            title= title.replace(' ','%20')
        
    
        else:
                
            title= scrapertools.get_match(data,'<title>([^"]+) -')
            title= re.sub(r"3D|[0-9]|SBS|\(.*?\)|\[.*?\]|","",title)
            title= title.replace('á','a')
            title= title.replace('Á','A')
            title= title.replace('é','e')
            title= title.replace('í','i')
            title= title.replace('ó','o')
            title= title.replace('ú','u')
            title= title.replace('ñ','n')
            title= title.replace(' ','%20')

        url="http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title + "&language=es&include_adult=false"
        data = scrapertools.cachePage(url)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        patron = '"page":1.*?,"id":(.*?),.*?"backdrop_path":"\\\(.*?)"'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches)==0:
            extra=item.thumbnail
            show= item.thumbnail
            posterdb = item.thumbnail
            fanart_info = item.thumbnail
            fanart_trailer = item.thumbnail
            category= item.thumbnail
            itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.thumbnail,extra = extra, show= show, category= category,folder=True) )
        
        for id, fan in matches:
            try:
                posterdb = scrapertools.get_match(data,'"page":1,.*?"poster_path":"\\\(.*?)"')
                posterdb =  "https://image.tmdb.org/t/p/original" + posterdb
            except:
                posterdb = item.thumbnail
            fanart="https://image.tmdb.org/t/p/original" + fan
            item.extra= fanart
            url ="http://api.themoviedb.org/3/movie/"+id+"/images?api_key=2e2160006592024ba87ccdf78c28f49f"
            data = scrapertools.cachePage(url)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
            
            patron = '"backdrops".*?"file_path":".*?",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)"'
            matches = re.compile(patron,re.DOTALL).findall(data)
                    
            if len(matches) == 0:
                patron = '"backdrops".*?"file_path":"(.*?)",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)"'
                matches = re.compile(patron,re.DOTALL).findall(data)
                if len(matches) == 0:
                    fanart_info = item.extra
                    fanart_trailer = item.extra
                    fanart_2 = item.extra
            for fanart_info, fanart_trailer, fanart_2 in matches:
                fanart_info = "https://image.tmdb.org/t/p/original" + fanart_info
                fanart_trailer = "https://image.tmdb.org/t/p/original" + fanart_trailer
                fanart_2 = "https://image.tmdb.org/t/p/original" + fanart_2
                        
            #clearart, fanart_2 y logo
            url ="http://webservice.fanart.tv/v3/movies/"+id+"?api_key=dffe90fba4d02c199ae7a9e71330c987"
            data = scrapertools.cachePage(url)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
            patron = '"hdmovielogo":.*?"url": "([^"]+)"'
            matches = re.compile(patron,re.DOTALL).findall(data)
            if '"moviedisc"' in data:
                disc = scrapertools.get_match(data,'"moviedisc":.*?"url": "([^"]+)"')
            if '"movieposter"' in data:
                poster = scrapertools.get_match(data,'"movieposter":.*?"url": "([^"]+)"')
            if '"moviethumb"' in data:
                thumb = scrapertools.get_match(data,'"moviethumb":.*?"url": "([^"]+)"')
            if '"moviebanner"' in data:
                banner= scrapertools.get_match(data,'"moviebanner":.*?"url": "([^"]+)"')
            
            if len(matches)==0:
                extra=  posterdb
                show = fanart_2
                category = item.extra
                itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=item.thumbnail, fanart=item.extra, extra=extra, show=show, category= category, folder=True) )
        for logo in matches:
             if '"hdmovieclearart"' in data:
                  clear=scrapertools.get_match(data,'"hdmovieclearart":.*?"url": "([^"]+)"')
                  if '"moviebackground"' in data:
                      
                      extra=clear
                      show= fanart_2
                      if '"moviedisc"' in data:
                           category= disc
                      else:
                           category= clear
                      itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=logo, fanart=item.extra, extra=extra,show=show,  category= category,folder=True) )
                  else:
                        extra= clear
                        show=fanart_2
                        if '"moviedisc"' in data:
                             category= disc
                        else:
                            category= clear
                        itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=logo, fanart=item.extra, extra=extra,show=show,  category= category, folder=True) )
                    
             if '"moviebackground"' in data:
                 
                  if '"hdmovieclearart"' in data:
                       clear=scrapertools.get_match(data,'"hdmovieclearart":.*?"url": "([^"]+)"')
                       extra=clear
                       show= fanart_2
                       if '"moviedisc"' in data:
                            category= disc
                       else:
                            category= clear
                  else:
                        extra=logo
                        show= fanart_2
                        if '"moviedisc"' in data:
                            category= disc
                        else:
                            category= logo
                        itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=logo, fanart=item.extra, extra=extra,show=show,  category= category, folder=True) )
                    
                    
                    
                    
             if not '"hdmovieclearart"' in data and not '"moviebackground"' in data:
                      extra= logo
                      show=  fanart_2
                      if '"moviedisc"' in data:
                           category= disc
                      else:
                           category= item.extra
                      itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=logo, fanart=item.extra, extra=extra,show=show ,  category= category, folder=True) )
       
    else:
        if "series" in item.url:
            if "hdtv" in item.url or "720" in item.title or "1080p" in item.title:
                title= scrapertools.get_match(data,'<title>([^"]+) \[')
                title= re.sub(r"3D|'|,|[0-9]|#|;|\[.*?\]|SBS|-|","",title)
                title= title.replace('Temporada','')
                title= title.replace('Fin','')
                title= title.replace('x','')
                title= title.replace('Heli','Helix')
                title= title.replace('Anatomía','Anatomia')
                title= title.replace('á','a')
                title= title.replace('Á','A')
                title= title.replace('é','e')
                title= title.replace('í','i')
                title= title.replace('ó','o')
                title= title.replace('ú','u')
                title= title.replace('ñ','n')
                title= title.replace(' ','%20')
            
            
            else:
                title= scrapertools.get_match(data,'<title>([^"]+) -')
                title= re.sub(r"3D|'|,|[0-9]|#|;|´|VOSE|\[.*?\]|-|","",title)
                title= title.replace('Temporada','')
                title= title.replace('Fin','')
                title= title.replace('x','')
                title= title.replace('á','a')
                title= title.replace('Á','A')
                title= title.replace('é','e')
                title= title.replace('í','i')
                title= title.replace('ó','o')
                title= title.replace('ú','u')
                title= title.replace('ñ','n')
                title= title.replace('Anatomía','Anatomia')
                title= title.replace(' ','%20')
                
        url="http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
        if "Erase%20una%20vez%20%20" in title:
            url ="http://thetvdb.com/api/GetSeries.php?seriesname=Erase%20una%20vez%20(2011)&language=es"
        data = scrapertools.cachePage(url)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        patron = '<Data><Series><seriesid>([^<]+)</seriesid>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches)==0:
            extra= item.thumbnail
            show=  item.thumbnail
            fanart_info = item.thumbnail
            fanart_trailer = item.thumbnail
            category= ""
            itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.thumbnail ,extra=extra, category= category,  show=show , folder=True) )
        else:
            for id in matches:
                category = id
                id_serie = id
                url ="http://thetvdb.com/api/1D62F2F90030C444/series/"+id_serie+"/banners.xml"
                data = scrapertools.cachePage(url)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                patron = '<Banners><Banner>.*?<VignettePath>(.*?)</VignettePath>'
                matches = re.compile(patron,re.DOTALL).findall(data)
                if len(matches)==0:
                    extra=item.thumbnail
                    show= item.thumbnail
                    fanart_info = item.thumbnail
                    fanart_trailer = item.thumbnail
                    itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.thumbnail ,category = category, extra=extra, show=show, folder=True) )
            for fan in matches:
                fanart="http://thetvdb.com/banners/" + fan
                item.extra= fanart
                patron= '<Banners><Banner>.*?<BannerPath>.*?</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>'
                matches = re.compile(patron,re.DOTALL).findall(data)
                if len(matches)==0:
                    fanart_info= item.extra
                    fanart_trailer = item.extra
                    fanart_2 = item.extra
                for fanart_info, fanart_trailer, fanart_2 in matches:
                    fanart_info = "http://thetvdb.com/banners/" + fanart_info
                    fanart_trailer = "http://thetvdb.com/banners/" + fanart_trailer
                    fanart_2 = "http://thetvdb.com/banners/" + fanart_2
            #clearart, fanart_2 y logo
            for id in matches:
                url ="http://webservice.fanart.tv/v3/tv/"+id_serie+"?api_key=dffe90fba4d02c199ae7a9e71330c987"
                if "Castle" in title:
                    url ="http://webservice.fanart.tv/v3/tv/83462?api_key=dffe90fba4d02c199ae7a9e71330c987"
                data = scrapertools.cachePage(url)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                patron = '"clearlogo":.*?"url": "([^"]+)"'
                matches = re.compile(patron,re.DOTALL).findall(data)
                if '"tvposter"' in data:
                    tvposter = scrapertools.get_match(data,'"tvposter":.*?"url": "([^"]+)"')
                if '"tvbanner"' in data:
                    tvbanner = scrapertools.get_match(data,'"tvbanner":.*?"url": "([^"]+)"')
                if '"tvthumb"' in data:
                    tvthumb = scrapertools.get_match(data,'"tvthumb":.*?"url": "([^"]+)"')
                if '"hdtvlogo"' in data:
                    hdtvlogo = scrapertools.get_match(data,'"hdtvlogo":.*?"url": "([^"]+)"')
                if '"hdclearart"' in data:
                    hdtvclear = scrapertools.get_match(data,'"hdclearart":.*?"url": "([^"]+)"')
                if len(matches)==0:
                    if '"hdtvlogo"' in data:
                        if "showbackground" in data:
                            
                            if '"hdclearart"' in data:
                                thumbnail = hdtvlogo
                                extra=  hdtvclear
                                show = fanart_2
                            else:
                                thumbnail = hdtvlogo
                                extra= thumbnail
                                show = fanart_2
                            itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=thumbnail, fanart=item.extra, category=category, extra=extra, show=show, folder=True) )
                                                                        
                                                                        
                        else:
                            if '"hdclearart"' in data:
                                thumbnail= hdtvlogo
                                extra= hdtvclear
                                show= fanart_2
                            else:
                                thumbnail= hdtvlogo
                                extra= thumbnail
                                show= fanart_2
                            itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra, show=show,  category= category, folder=True) )
                    else:
                         extra=  item.thumbnail
                         show = fanart_2
                         itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url,  server="torrent", thumbnail=item.thumbnail, fanart=item.extra, extra=extra, show=show, category = category, folder=True) )
                                                                                                                                
            for logo in matches:
                if '"hdtvlogo"' in data:
                    thumbnail = hdtvlogo
                elif not '"hdtvlogo"' in data :
                           if '"clearlogo"' in data:
                            thumbnail= logo
                else:
                     thumbnail= item.thumbnail
                if '"clearart"' in data:
                    clear=scrapertools.get_match(data,'"clearart":.*?"url": "([^"]+)"')
                    if "showbackground" in data:
                                
                        extra=clear
                        show= fanart_2
                        itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,show=show, category= category,  folder=True) )
                    else:
                         extra= clear
                         show=fanart_2
                         itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,show=show, category= category, folder=True) )
                                     
                if "showbackground" in data:
                            
                    if '"clearart"' in data:
                        clear=scrapertools.get_match(data,'"clearart":.*?"url": "([^"]+)"')
                        extra=clear
                        show= fanart_2
                    else:
                        extra=logo
                        show= fanart_2
                        itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,show=show,  category = category, folder=True) )
                                     
                if not '"clearart"' in data and not '"showbackground"' in data:
                        if '"hdclearart"' in data:
                            extra= hdtvclear
                            show= fanart_2
                        else:
                            extra= thumbnail
                            show=  fanart_2
                        itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=thumbnail, fanart=item.extra, extra=extra,show=show , category = category, folder=True) )
    

    title ="Info"
    title = title.replace(title,bbcode_kodi2html("[COLOR skyblue]"+title+"[/COLOR]"))
    if not "series" in item.url:
       thumbnail = posterdb
    if "series" in item.url:
        if '"tvposter"' in data:
            thumbnail= tvposter
        else:
            thumbnail = item.thumbnail
        
        if "tvbanner" in data:
            category = tvbanner
        else:
            
            category = show


    itemlist.append( Item(channel=item.channel, action="info" , title=title , url=item.url, thumbnail=thumbnail, fanart=fanart_info, extra= extra, category = category, show= show, folder=False ))

    title= "[COLOR cadetblue]Trailer[/COLOR]"
    if len(item.extra)==0:
        fanart=item.thumbnail
    else:
        fanart = item.extra
    if "series" in item.url:
        if '"tvthumb"' in data:
            thumbnail = tvthumb
        else:
            thumbnail = item.thumbnail
        if '"tvbanner"' in data:
            extra= tvbanner
        elif '"tvthumb"' in data:
            extra = tvthumb
        else:
            extra = item.thumbnail
    else:
        if '"moviethumb"' in data:
            thumbnail = thumb
        else:
            thumbnail = posterdb
        
        if '"moviebanner"' in data:
            extra= banner
        else:
            if '"hdmovieclearart"' in data:
                extra = clear
            
            else:
                extra = posterdb


    itemlist.append( Item(channel=item.channel, action="trailer", title=title , url=item.url , thumbnail=thumbnail , plot=item.plot , fanart=fanart_trailer, extra=extra, folder=True) )
    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.zentorrents findvideos")
    
    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|&amp;|amp;","",data)
    
    patron = '<h1>(.*?)</h1>.*?'
    patron += 'src="([^"]+)".*?'
    patron += '</a></p><p><a href="([^"]+)"'
    
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    for scrapedtitulo, scrapedthumbnail, scrapedurl in matches:
        if "series" in item.url :
            patron='<h1>.*?(\d+)x(\d+).*?'
            matches = re.compile(patron,re.DOTALL).findall(data)
            for temp, epi in matches:
                plot= temp+"|"+epi
            title = scrapedtitulo
            title= re.sub(r"\[.*?\]|-|Temporada.*?\d+|\d+x\d+|Fin","",title)
            title= title.replace(' ','%20')
            url="http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query="+title+"&language=es&include_adult=false"
            if "%2090210%20Sensacion%20de%20vivir" in url:
                url="http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query=90210&language=es&include_adult=false"
            if "%20De%20vuelta%20al%20nido%20" in url:
                url ="http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query=packed%20to%20the%20rafter&language=es&include_adult=false"
            if "%20Asuntos%20de%20estado%20" in url:
                url="http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query=state%20of%20affair&language=es&include_adult=false"
            if "%20Como%20defender%20a%20un%20asesino%20" in url:
                url="http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query=how%20to%20get%20away%20with%20murder&language=es&include_adult=false"
            if "Rizzoli%20and%20Isles%20%20%20" in url:
                url="http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query=Rizzoli%20&%20Isles%20%20%20&language=es&include_adult=false"
            data = scrapertools.cachePage(url)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
            patron = 'page":1.*?,"id":(.*?),"'
            matches = re.compile(patron,re.DOTALL).findall(data)
            if len(matches)==0:
                thumbnail= item.thumbnail
                fanart = item.fanart
                id = ""
                temp=""
                epi=""
                
                title_tag=bbcode_kodi2html("[COLOR pink]Ver--[/COLOR]")
                scrapedtitulo = scrapedtitulo.replace(scrapedtitulo,bbcode_kodi2html("[COLOR bisque][B]"+scrapedtitulo+"[/B][/COLOR]"))
                scrapedtitulo = title_tag + scrapedtitulo
                scrapedurl = urlparse.urljoin(host,scrapedurl)
                itemlist.append( Item(channel=item.channel, title = scrapedtitulo , action="play", url=scrapedurl, server="torrent", thumbnail=thumbnail, fanart=fanart,  folder=False) )
            
            for id in matches:
                try:
                    backdrop=scrapertools.get_match(data,'page":1.*?,"id".*?"backdrop_path":"\\\(.*?)"')
                    fanart_3 = "https://image.tmdb.org/t/p/original" + backdrop
                    fanart = fanart_3
                except:
                    fanart= item.fanart
                url ="https://api.themoviedb.org/3/tv/"+id+"/season/"+temp+"/episode/"+epi+"/images?api_key=2e2160006592024ba87ccdf78c28f49f"
                data = scrapertools.cachePage(url)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                patron = '{"id".*?"file_path":"(.*?)","height"'
                matches = re.compile(patron,re.DOTALL).findall(data)
                if len(matches)==0:
                    thumbnail = item.thumbnail
                    
                    title_tag=bbcode_kodi2html("[COLOR pink]Ver--[/COLOR]")
                    scrapedtitulo = scrapedtitulo.replace(scrapedtitulo,bbcode_kodi2html("[COLOR bisque][B]"+scrapedtitulo+"[/B][/COLOR]"))
                    scrapedtitulo = title_tag + scrapedtitulo
                    scrapedurl = urlparse.urljoin(host,scrapedurl)
                    itemlist.append( Item(channel=item.channel, title = scrapedtitulo , action="play", url=scrapedurl, server="torrent", thumbnail=thumbnail, fanart=fanart,  folder=False) )
                for foto in matches:
                    thumbnail = "https://image.tmdb.org/t/p/original" + foto
                    
                    
                    
                    title_tag=bbcode_kodi2html("[COLOR pink]Ver--[/COLOR]")
                    scrapedtitulo = scrapedtitulo.replace(scrapedtitulo,bbcode_kodi2html("[COLOR bisque][B]"+scrapedtitulo+"[/B][/COLOR]"))
                    scrapedtitulo = title_tag + scrapedtitulo
                    scrapedurl = urlparse.urljoin(host,scrapedurl)
                    itemlist.append( Item(channel=item.channel, title=scrapedtitulo, url=scrapedurl, action="play", server="torrent", thumbnail=thumbnail, category = item.category, fanart=fanart, folder=False) )
            ###thumb temporada###
            url= "http://api.themoviedb.org/3/tv/"+id+"/season/"+temp+"/images?api_key=2e2160006592024ba87ccdf78c28f49f"
            data = scrapertools.cachePage( url )
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
            patron = '{"id".*?"file_path":"(.*?)","height"'
            matches = re.compile(patron,re.DOTALL).findall(data)
            if len(matches) == 0:
               thumbnail= item.thumbnail
            for thumtemp in matches:
                thumbnail= "https://image.tmdb.org/t/p/original"+ thumtemp
            
            ####fanart info####
            url ="http://api.themoviedb.org/3/tv/"+id+"/images?api_key=2e2160006592024ba87ccdf78c28f49f"
            data = scrapertools.cachePage( url )
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
            patron = '{"backdrops".*?"file_path":".*?","height".*?"file_path":"(.*?)",'
            matches = re.compile(patron,re.DOTALL).findall(data)
            if len(matches) == 0:
               fanart = item.fanart
            for fanart_4 in matches:
                fanart = "https://image.tmdb.org/t/p/original" + fanart_4
            extra= item.category+"|"+item.thumbnail+"|"+id+"|"+temp+"|"+epi+"|"+title
                    
            title ="Info"
            title = title.replace(title,bbcode_kodi2html("[COLOR skyblue]"+title+"[/COLOR]"))
            itemlist.append( Item(channel=item.channel, action="info_capitulos" , title=title , url=item.url, thumbnail=thumbnail, fanart=fanart, extra = extra, folder=False ))
        else:
        
             infotitle= bbcode_kodi2html("[COLOR pink][B]Ver--[/B][/COLOR]")
             scrapedtitulo= scrapedtitulo.replace(scrapedtitulo,bbcode_kodi2html("[COLOR bisque]"+scrapedtitulo+"[/COLOR]"))
             title= infotitle + scrapedtitulo
             scrapedurl = urlparse.urljoin(host,scrapedurl)
             if "peliculas" in item.url:
                 thumbnail= item.category
             else:
                 thumbnail = item.extra
        
             itemlist.append( Item(channel=item.channel, title =title , thumbnail=thumbnail, url=scrapedurl, fanart=item.show, action="play", folder=False) )
    
    
    return itemlist

def play(item):
    
    data = scrapertools.cache_page(item.url)
    logger.info("data="+data)
    itemlist = []
    
    
    try:
       link = scrapertools.get_match(data,"{ window.open\('([^']+)'")
       link = urlparse.urljoin(item.url,link)
       logger.info("link="+link)
    
    
       itemlist.append( Item(channel=item.channel, action=play, server="torrent",  url=link , folder=False) )
    except:
       itemlist.append( Item(channel=item.channel, title=item.plot, url=item.url, server="youtube", fanart=item.fanart, thumbnail=item.thumbnail, action="play", folder=False) )


    return itemlist

def trailer(item):
    logger.info("pelisalacarta.bityouth trailer")
    itemlist = []
    
    youtube_trailer = "https://www.youtube.com/results?search_query=" + item.plot + "español"
    
    data = scrapertools.cache_page(youtube_trailer)
    
    patron = '<a href="/watch?(.*?)".*?'
    patron += 'title="([^"]+)"'
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 :
        itemlist.append( Item(channel=item.channel, title="[COLOR gold][B]No hay Trailer[/B][/COLOR]", thumbnail ="http://s6.postimg.org/jp5jx97ip/bityoucancel.png", fanart ="http://s6.postimg.org/vfjhen0b5/bityounieve.jpg",folder=False) )
    
    for scrapedurl, scrapedtitle in matches:
        
        scrapedurl = "https://www.youtube.com/watch"+scrapedurl
        scrapedtitle = scrapertools.decodeHtmlentities( scrapedtitle )
        scrapedtitle=scrapedtitle.replace(scrapedtitle,"[COLOR pink][B]"+scrapedtitle+"[/B][/COLOR]")
        itemlist.append( Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, server="youtube", fanart="https://c401345.ssl.cf1.rackcdn.com/wp-content/uploads/2013/02/movie-trailer-michalowicz-open-forum-432.jpg", thumbnail=item.extra, action="play", folder=False) )
    
    return itemlist

def info(item):
    logger.info("pelisalacarta.zentorrents info")
    
    url=item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|\d+x\d+|&nbsp;|<a title.*?</a>","",data)
    title= scrapertools.get_match(data,'<title>([^"]+) -')
    title = title.replace(title,bbcode_kodi2html("[COLOR pink][B]"+title+"[/B][/COLOR]"))
    try:
        plot = scrapertools.get_match(data,'onload="imgLoaded.*?</div><p>(.*?)<p class="descauto">')
        plot = plot.replace(plot,bbcode_kodi2html("[COLOR orange][B]"+plot+"[/B][/COLOR]"))
        plot= scrapertools.decodeHtmlentities( plot )
        plot = plot.replace("<p>","")
        plot = plot.replace("</p>","")
        plot = plot.replace("&amp;quot;","")
        plot = plot.replace("</strong>","")
        plot = plot.replace("<strong>","")
        plot = plot.replace("<p class=\"ver_online\">","")
    except:
        title = "[COLOR red][B]LO SENTIMOS...[/B][/COLOR]"
        plot = "Esta serie no tiene informacion..."
        plot = plot.replace(plot,"[COLOR yellow][B]"+plot+"[/B][/COLOR]")
        photo="http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
        foto ="http://s6.postimg.org/ub7pb76c1/noinfo.png"
        info =""
        quit = "Pulsa"+" [COLOR hotpink][B]INTRO [/B][/COLOR]"+ "para quitar"
        
    
    if "series" in item.url:
        foto= item.category
        photo= item.extra
        quit = "Pulsa"+" [COLOR hotpink][B]INTRO [/B][/COLOR]"+ "para quitar"
    else:
        
        foto = item.show
        photo= item.extra
        quit = "Pulsa"+" [COLOR hotpink][B]INTRO [/B][/COLOR]"+ "para quitar"
    ventana2 = TextBox1(title=title, plot=plot, thumbnail=photo, fanart=foto, quit=quit)
    ventana2.doModal()

ACTION_SELECT_ITEM = 7
class TextBox1( xbmcgui.WindowDialog ):
        """ Create a skinned textbox window """
        def __init__( self, *args, **kwargs):
            
            self.getTitle = kwargs.get('title')
            self.getPlot = kwargs.get('plot')
            self.getThumbnail = kwargs.get('thumbnail')
            self.getFanart = kwargs.get('fanart')
            self.getQuit = kwargs.get('quit')
            
            self.background = xbmcgui.ControlImage( 70, 20, 1150, 630, 'http://s6.postimg.org/58jknrvtd/backgroundventana5.png')
            self.title = xbmcgui.ControlTextBox(140, 60, 1130, 50)
            self.quit = xbmcgui.ControlTextBox(145, 105, 1030, 45)
            self.plot = xbmcgui.ControlTextBox( 120, 150, 1056, 140 )
            self.thumbnail = xbmcgui.ControlImage( 813, 43, 390, 100, self.getThumbnail )
            self.fanart = xbmcgui.ControlImage( 120, 365, 1060, 250, self.getFanart )
            
            self.addControl(self.background)
            self.addControl(self.title)
            self.addControl(self.quit)
            self.addControl(self.plot)
            self.addControl(self.thumbnail)
            self.addControl(self.fanart)
            
            self.title.setText( self.getTitle )
            self.quit.setText( self.getQuit )
            try:
                self.plot.autoScroll(7000,6000,30000)
            except:
                import xbmc
                xbmc.executebuiltin('Notification([COLOR red][B]Actualiza Kodi a su última versión[/B][/COLOR], [COLOR skyblue]para mejor info[/COLOR],8000,"https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/kodi-icon.png")')
            self.plot.setText(  self.getPlot )
        
        def get(self):
            self.show()
        
        def onAction(self, action):
            if action == ACTION_SELECT_ITEM:
               self.close()


def info_capitulos(item):
    logger.info("pelisalacarta.bricocine trailer")
    url= item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    item.category = item.extra.split("|")[0]
    item.thumbnail = item.extra.split("|")[1]
    id = item.extra.split("|")[2]
    temp = item.extra.split("|")[3]
    epi = item.extra.split("|")[4]
    title = item.extra.split("|")[5]
    url="http://thetvdb.com/api/1D62F2F90030C444/series/"+item.extra.split("|")[0]+"/default/"+item.extra.split("|")[3]+"/"+item.extra.split("|")[4]+"/es.xml"
    if "/0" in url:
       url = url.replace("/0","/")
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    patron = '<Data>.*?<EpisodeName>([^<]+)</EpisodeName>.*?'
    patron += '<Overview>(.*?)</Overview>.*?'
        
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)==0 :
        title = bbcode_kodi2html("[COLOR red][B]LO SENTIMOS...[/B][/COLOR]")
        plot = "Este capitulo no tiene informacion..."
        plot = plot.replace(plot,bbcode_kodi2html("[COLOR yellow][B]"+plot+"[/B][/COLOR]"))
        image="http://s6.postimg.org/ub7pb76c1/noinfo.png"
        foto="http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
        quit = "Pulsa"+" [COLOR greenyellow][B]INTRO [/B][/COLOR]"+ "para quitar"
        
    else :
            
            
          for name_epi, info in matches:
              if "<filename>episodes" in data:
                  foto = scrapertools.get_match(data,'<Data>.*?<filename>(.*?)</filename>')
                  fanart = "http://thetvdb.com/banners/" + foto
              else:
                  fanart=item.extra.split("|")[1]
              plot = info
              plot = plot.replace(plot,bbcode_kodi2html("[COLOR pink][B]"+plot+"[/B][/COLOR]"))
              title = name_epi.upper()
              title = title.replace(title,bbcode_kodi2html("[COLOR bisque][B]"+title+"[/B][/COLOR]"))
              image=fanart
              foto= item.extra.split("|")[1]
              quit = "Pulsa"+" [COLOR darkviolet][B]INTRO [/B][/COLOR]"+ "para quitar"
    ventana = TextBox2(title=title, plot=plot, thumbnail=image, fanart=foto, quit=quit)
    ventana.doModal()

ACTION_SELECT_ITEM = 7
class TextBox2( xbmcgui.WindowDialog ):
        """ Create a skinned textbox window """
        def __init__( self, *args, **kwargs):
            self.getTitle = kwargs.get('title')
            self.getPlot = kwargs.get('plot')
            self.getThumbnail = kwargs.get('thumbnail')
            self.getFanart = kwargs.get('fanart')
            self.getQuit = kwargs.get('quit')
            
            self.background = xbmcgui.ControlImage( 70, 20, 1150, 630, 'http://s6.postimg.org/n3ph1uxn5/ventana.png')
            self.title = xbmcgui.ControlTextBox(120, 60, 430, 50)
            self.quit = xbmcgui.ControlTextBox(145, 105, 1030, 45)
            self.plot = xbmcgui.ControlTextBox( 120, 150, 1056, 100 )
            self.thumbnail = xbmcgui.ControlImage( 120, 300, 1056, 300, self.getThumbnail )
            self.fanart = xbmcgui.ControlImage( 780, 43, 390, 100, self.getFanart )
            
            self.addControl(self.background)
            self.addControl(self.title)
            self.addControl(self.quit)
            self.addControl(self.plot)
            self.addControl(self.thumbnail)
            self.addControl(self.fanart)
            
            self.title.setText( self.getTitle )
            self.quit.setText( self.getQuit )
            try:
                self.plot.autoScroll(7000,6000,30000)
            except:
                import xbmc
                xbmc.executebuiltin('Notification([COLOR red][B]Actualiza Kodi a su última versión[/B][/COLOR], [COLOR skyblue]para mejor info[/COLOR],8000,"https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/kodi-icon.png")')
            self.plot.setText(  self.getPlot )
        
        def get(self):
            self.show()
        
        def onAction(self, action):
            if action == ACTION_SELECT_ITEM:
               self.close()
