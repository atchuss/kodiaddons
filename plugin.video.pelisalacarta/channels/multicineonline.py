# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para sinluces
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re
import sys
import urllib

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.scrapertools import decodeHtmlentities as dhe

try:
    import xbmc
    import xbmcgui
except: pass


DEBUG = config.get_setting("debug")
host = "http://www.multicineonline.com"
Tmdb_key ="2e2160006592024ba87ccdf78c28f49f"


def mainlist(item):
    logger.info("pelisalacarta.multicineonline mainlist")
    itemlist = []
    title ="Estrenos"
    title = title.replace(title,"[COLOR skyblue]"+title+"[/COLOR]")
    itemlist.append( Item(channel=item.channel, title=title      , action="peliculas", url="http://www.multicineonline.com/estrenos-de-cine/page/1/", fanart="http://s6.postimg.org/kpdn6g1ht/sinlestfan2.jpg", thumbnail="http://s23.postimg.org/p1a2tyejv/sinlestthu.jpg"))

    title ="HD"
    title = title.replace(title,"[COLOR skyblue]"+title+"[/COLOR]")
    itemlist.append( Item(channel=item.channel, title=title      , action="peliculas", url="http://www.multicineonline.com/tag/hd/page/1/", fanart="http://s6.postimg.org/91jlbwccx/sinhdfan2.jpg", thumbnail="http://s12.postimg.org/d5w5ojuql/sinlhdth.jpg"))

    '''title ="Buscar"
    title = title.replace(title,"[COLOR skyblue]"+title+"[/COLOR]")
    itemlist.append( Item(channel=item.channel, title=title      , action="search", url="", fanart="http://s22.postimg.org/3tz2v05ap/sinlbufan.jpg", thumbnail="http://s30.postimg.org/jhmn0u4jl/sinlbusthub.jpg"))'''






    return itemlist
def search(item,texto):
    logger.info("pelisalacarta.multicineonline search")
    texto = texto.replace(" ","+")

    if "estrenos-de-cine" in item.url:
        item.url ="http://www.multicineonline.com/estrenos-de-cine/?s=%s" % (texto)
    elif "/tag/hd/" in item.url:
        item.url ="http://www.multicineonline.com/tag/hd/?s=%s" % (texto)
    else:
        item.url = "http://www.multicineonline.com/?s=%s" % (texto)
    try:
        return scraper(item)
    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

'''def buscador(item):
    logger.info("pelisalacarta.sinluces buscador")
    itemlist = []



    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    patron  = '<divclass="movie tooltip".*?<div class="imagen"> <img src="([^"]+)" '
    patron += 'alt="(.*?)\((.*?)\)".*?'
    patron += '<a href="([^"]+)"'
    patron += '<span class="icon-grade"></span>([^<]+)</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 and  not "Error 404" in data:
        itemlist.append( Item(channel=item.channel, title="[COLOR gold][B]No hay resultados...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/55zljwr4h/sinnoisethumb.png", fanart ="http://s6.postimg.org/avfu47xap/sinnoisefan.jpg",folder=False) )


    for scrapedthumbnail, scrapedtitle,scrapedyear, scrapedurl, scrapedrate in matches:


        scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR white]"+scrapedtitle+"[/COLOR]")


        itemlist.append( Item(channel=item.channel, action="fanart", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , extra=scrapedtitle, fanart="http://s30.postimg.org/4gugdsygx/sinlucesfan.jpg", folder=True) )

    return itemlist'''
def peliculas(item,paginacion=True):
    logger.info("pelisalacarta.multicineonline peliculas")
    itemlist = []

    title ="Listado"
    title = title.replace(title,"[COLOR skyblue]"+title+"[/COLOR]")
    itemlist.append( Item(channel=item.channel, title=title      , action="scraper", url=item.url, fanart="http://s6.postimg.org/mxrtns8lt/sinlucesfan2.jpg", thumbnail="http://s23.postimg.org/p1a2tyejv/sinlestthu.jpg", viewmode="movie"))
    title ="Buscar"
    title = title.replace(title,"[COLOR skyblue]"+title+"[/COLOR]")
    itemlist.append( Item(channel=item.channel, title=title      , action="search", url=item.url,extra= "search", fanart="http://s22.postimg.org/3tz2v05ap/sinlbufan.jpg", thumbnail="http://s30.postimg.org/jhmn0u4jl/sinlbusthub.jpg"))
    return itemlist
def scraper(item,paginacion=True):
    logger.info("pelisalacarta.sinluces peliculas")
    itemlist = []

    # Descarga la página
    data = dhe( scrapertools.cachePage(item.url) )
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)

    patron = '<divclass="movie tooltip".*?title="(.*?)".*?<div class="imagen"> <img src="([^"]+)" '
    patron += 'alt="(.*?)\((.*?)\)".*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<span class="icon-grade"></span>([^<]+)</div>'


    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 and  not "Error 404" in data:
        itemlist.append( Item(channel=item.channel, title="[COLOR gold][B]No hay resultados...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/55zljwr4h/sinnoisethumb.png", fanart ="http://s6.postimg.org/avfu47xap/sinnoisefan.jpg",folder=False) )


    for scrapedidioma, scrapedthumbnail, scrapedtitle, scrapedyear, scrapedurl, scrapedrate in matches:
        title_fan = scrapedtitle.strip()
        title_fan = re.sub(r'/.*','',title_fan)
        scrapedrate=scrapedrate.strip()
        if "N/A" in scrapedrate:
           scrapedrate = "Sin puntuación"
        if "castellano" in scrapedidioma:
            scrapedidioma= "[COLOR deepskyblue][B](Castellano) [/B][/COLOR]"
        elif "Subtitulada" in scrapedidioma:
            scrapedidioma = "[COLOR deepskyblue][B](Subtitulada) [/B][/COLOR]"
        else:
            scrapedidioma = "[COLOR deepskyblue][B](Latino) [/B][/COLOR]"
        scrapedrate = scrapedrate.replace(scrapedrate,"[COLOR blue][B]("+scrapedrate+")[/B][/COLOR]")
        scrapedtitle = scrapedtitle + scrapedidioma + scrapedrate
        scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR white]"+scrapedtitle+"[/COLOR]")
        trailer = title_fan + " " + scrapedyear + " trailer"
        trailer = urllib.quote(trailer)

        extra = title_fan+"|"+scrapedyear+"|"+trailer
        itemlist.append( Item(channel=item.channel, action="fanart", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , extra= extra,  fanart="http://s6.postimg.org/mxrtns8lt/sinlucesfan2.jpg") )




    # Extrae el paginador
    ## Paginación
    try:
       if  "Error 404" in data:
            itemlist.append( Item(channel=item.channel, title="[COLOR gold][B]No hay mas paginas...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/55zljwr4h/sinnoisethumb.png", fanart ="http://s6.postimg.org/avfu47xap/sinnoisefan.jpg",folder=False) )
       else:
           current_page_number = int(scrapertools.get_match(item.url,'page/(\d+)'))
           item.url = re.sub(r"page/\d+","page/{0}",item.url)

           next_page_number = current_page_number +1
           next_page = item.url.format(next_page_number)

           title= "[COLOR skyblue]Pagina siguiente>>[/COLOR]"
           if  not "Error 404" in data:
              itemlist.append( Item(channel=item.channel, title=title, url=next_page, fanart="http://s30.postimg.org/4gugdsygx/sinlucesfan.jpg", thumbnail="http://s16.postimg.org/lvzzttkol/pelisvkflecha.png", action="scraper", folder=True, viewmode="movie") )
    except:
         pass

    return itemlist

def fanart(item):
    logger.info("pelisalacarta.multicineonline fanart")
    itemlist = []
    url = item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    year = item.extra.split("|")[1]
    title = item.extra.split("|")[0]
    trailer = item.extra.split("|")[2]
    title_info = title
    item.title  = title
    item.title = item.title.replace(item.title,"[COLOR deepskyblue][B]"+item.title+"[/B][/COLOR]")
    title= re.sub(r"3D|SBS|-|\(.*?\)","",title)
    title= title.replace('Ver','')
    title= title.replace('Online','')
    title= title.replace('Gratis','')
    title= title.replace(' ','%20')
    url="http://api.themoviedb.org/3/search/movie?api_key="+Tmdb_key+"&query=" + title + "&language=es&include_adult=false"
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    patron = '"page":1.*?,"id":(.*?),.*?"backdrop_path":"\\\(.*?)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)==0:
        extra="http://s6.postimg.org/ook1gr4wh/sinsinopsis.png"
        show= "http://s6.postimg.org/mxrtns8lt/sinlucesfan2.jpg"
        posterdb = item.thumbnail
        fanart_info = "http://s6.postimg.org/mxrtns8lt/sinlucesfan2.jpg"
        fanart_trailer = "http://s6.postimg.org/mxrtns8lt/sinlucesfan2.jpg"
        category= item.thumbnail
        itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart="http://s6.postimg.org/mxrtns8lt/sinlucesfan2.jpg" ,extra=extra, show=show, category= category, folder=True) )
    else:
        for id, fan in matches:
            try:
                posterdb = scrapertools.get_match(data,'"page":1,.*?"poster_path":"\\\(.*?)"')
                posterdb =  "https://image.tmdb.org/t/p/original" + posterdb
            except:
                posterdb = item.thumbnail
            fanart="https://image.tmdb.org/t/p/original" + fan
            item.extra= fanart
            url ="http://api.themoviedb.org/3/movie/"+id+"/images?api_key="+Tmdb_key
            data = scrapertools.cachePage( url )
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

            #fanart_2 y arts

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
                itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=posterdb, fanart=item.extra,  extra=extra, show=show, category= category, folder=True) )
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
                      itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=logo, fanart=item.extra, extra=extra,show=show, category= category, folder=True) )
                 else:
                      extra= clear
                      show=fanart_2
                      if '"moviedisc"' in data:
                          category = disc
                      else:
                          category = clear
                      itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=logo, fanart=item.extra, extra=extra,show=show, category= category, folder=True) )

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
                       itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=logo, fanart=item.extra, extra=extra,show=show, category= category,  folder=True) )

            if not '"hdmovieclearart"' in data and not '"moviebackground"' in data:
                     extra= logo
                     show=  fanart_2
                     if '"moviedisc"' in data:
                          category= disc
                     else:
                          category= item.extra
                     itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=logo, fanart=fanart_info,category= category, extra=extra,show=show ,  folder=True) )

    title ="[COLOR rosybrown]Info[/COLOR]"

    if posterdb == item.thumbnail:
        if '"movieposter"' in data:
            thumbnail= poster
        else:
            thumbnail = item.thumbnail
    else:
        thumbnail = posterdb

    itemlist.append( Item(channel=item.channel, action="info" , title=title , url=item.url, thumbnail=posterdb,  fanart=fanart_info, extra = extra, show = show, plot = title_info +" "+"("+ year+")", folder=False ))

    title= "[COLOR royalblue]Trailer[/COLOR]"


    if '"moviebanner"' in data:
        thumbnail = banner
    else:
        thumbnail = posterdb

    if '"moviedisc"' in data:
        extra= disc
    else:
       if 'hdmovieclearart"' in data:
           extra = clear

       else:
           extra = posterdb



    itemlist.append( Item(channel=item.channel, action="trailer", title=title , url=item.url , thumbnail=thumbnail , fulltitle = item.title , fanart=fanart_trailer, extra=extra, show= trailer,folder=True) )

    return itemlist






def findvideos(item):
    logger.info("pelisalacarta.multicineonline findvideos")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)




    #extra enlaces


    patron= '<div class="play-c">(.*?)<div class="datos">'

    matches = re.compile(patron,re.DOTALL).findall(data)

    if len(matches)==0:
        itemlist.append( Item(channel=item.channel, title="[COLOR orange][B]Sin servidores para Pelisalacarta...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/55zljwr4h/sinnoisethumb.png", fanart ="http://s6.postimg.org/avfu47xap/sinnoisefan.jpg",folder=False) )

    for bloque_enlaces_idiomas in matches:
        patronenlaces= '<div id="play-(.*?)".*?src="([^"]+)"'
        matchesenlaces = re.compile(patronenlaces,re.DOTALL).findall(bloque_enlaces_idiomas)
        patronidiomas= '<a href="#play-(.*?)">([^<]+)'
        matchesidiomas = re.compile(patronidiomas,re.DOTALL).findall(bloque_enlaces_idiomas)
        for numero, scrapedurl in matchesenlaces:
            url=scrapedurl
            for numero2, idiomas in matchesidiomas:
                if numero == numero2:
                   title = idiomas
                   idiomas= re.sub(r"[0-9]","",idiomas)
                   listavideos = servertools.findvideos(url)
                   for video in listavideos:

                      #idiomas = idiomas.replace(idiomas,"[COLOR white]"+idiomas+"[/COLOR]")
                       videotitle = scrapertools.unescape(video[0]) #+"-"+idiomas
                       url = video[1]
                       server = video[2]
                       videotitle = videotitle.replace(videotitle,"[COLOR skyblue]"+videotitle+"[/COLOR]")
                       title_first="[COLOR gold]Ver en--[/COLOR]"
                       title= title_first + videotitle
                       if "sinopsis" in item.extra:
                          item.extra = item.thumbnail
                       itemlist.append( Item(channel=item.channel, action="play", server=server, title=title , url=url , thumbnail=item.extra , fulltitle = item.title , fanart = item.show, folder=False) )


        #otro patronenlaces
        patronenlaces= '<div id="play-(.*?)".*?src=\'([^\']+)\''
        matchesenlaces = re.compile(patronenlaces,re.DOTALL).findall(bloque_enlaces_idiomas)
        patronidiomas= '<a href="#play-(.*?)">([^<]+)'
        matchesidiomas = re.compile(patronidiomas,re.DOTALL).findall(bloque_enlaces_idiomas)
        for numero, url in matchesenlaces:
            pepe=url
            for numero2, idiomas in matchesidiomas:
                if numero == numero2:
                   title = idiomas
                   idiomas= re.sub(r"[0-9]","",idiomas)
                   listavideos = servertools.findvideos(pepe)
                   for video in listavideos:

                       #idiomas = idiomas.replace(idiomas,"[COLOR white]"+idiomas+"[/COLOR]")
                       videotitle = scrapertools.unescape(video[0]) #+"-"+idiomas
                       url = video[1]
                       server = video[2]
                       videotitle = videotitle.replace(videotitle,"[COLOR skyblue]"+videotitle+"[/COLOR]")
                       title_first="[COLOR gold]Ver en--[/COLOR]"
                       title= title_first + videotitle
                       if "sinopsis" in item.extra:
                           item.extra = item.thumbnail
                       itemlist.append( Item(channel=item.channel, action="play", server=server, title=title , url=url , thumbnail=item.extra , fulltitle = item.title , fanart = item.show, folder=False) )


        patron = '<em>opción \d+, ([^<]+)</em>.*?'
        # Datos que contienen los enlaces para sacarlos con servertools.findvideos
        patron+= '<div class="contenedor_tab">(.*?)<div style="clear:both;">'
        matches = re.compile(patron,re.DOTALL).findall(data)

        for idioma, datosEnlaces in matches:

            listavideos = servertools.findvideos(datosEnlaces)


            for video in listavideos:
                videotitle = scrapertools.unescape(video[0])+"-"+idioma
                url = video[1]
                server = video[2]
                videotitle = videotitle.replace(videotitle,"[COLOR skyblue]"+videotitle+"[/COLOR]")
                title_first="[COLOR gold]Ver en--[/COLOR]"
                title= title_first + videotitle
                idioma = idioma.replace(idioma,"[COLOR white]"+idioma+"[/COLOR]")
                if "sinopsis" in item.extra:
                    item.extra = item.thumbnail
                itemlist.append( Item(channel=item.channel, action="play", server=server, title=title , url=url , thumbnail=item.extra , fulltitle = item.title , fanart = item.show, folder=False) )









    return itemlist

def trailer(item):
    logger.info("pelisalacarta.multicineonline trailer")
    itemlist = []

    youtube_trailer = "https://www.youtube.com/results?search_query=" + item.show + "español"


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
        scrapedtitle=scrapedtitle.replace(scrapedtitle,"[COLOR khaki][B]"+scrapedtitle+"[/B][/COLOR]")
        itemlist.append( Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, server="youtube", fanart="http://static1.squarespace.com/static/5502c970e4b0cec330247c32/t/5517212ee4b07ea6d281c891/1427579186693/Movie+Trailers+and+promos.JPG?format=1500w", thumbnail=item.extra, action="play", folder=False) )
    
    return itemlist

def info(item):
    logger.info("pelisalacarta.multicineonline trailer")
    url=item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    title= item.plot
    title = re.sub(r"-.*","",title)
    title = title.title()
    title = title.replace(title,"[COLOR aqua][B]"+title+"[/B][/COLOR]")
    try:
        plot = scrapertools.get_match(data,'<h2>Sinopsis.*?<p>([^<]+).*?</p>')
        plot = plot.replace(plot,"[COLOR white][B]"+plot+"[/B][/COLOR]")
   
        plot = plot.replace("</span>","[CR]")
        plot = plot.replace("</i>","")
        plot = plot.replace("&#8220","")
        plot = plot.replace("<b>","")
        plot = plot.replace("</b>","")
        plot = plot.replace(" &#8203;&#8203;","")
        plot = plot.replace("&#8230","")
        plot = plot.replace("</div> </div> <div class='clear'>","")
        plot = plot.replace("</div><div><span><i class='icon icon-ok'>","[CR]")
    except:
        title ="[COLOR red][B]LO SENTIMOS...[/B][/COLOR]"
        plot = "Esta Pelicula no tiene informacion..."
        plot = plot.replace(plot,"[COLOR yellow][B]"+plot+"[/B][/COLOR]")
        photo="http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
        foto ="http://s6.postimg.org/ub7pb76c1/noinfo.png"
        info =""
        quit = "Pulsa"+" [COLOR orangered][B]INTRO [/B][/COLOR]"+ "para quitar"
    try:
        scrapedinfo = scrapertools.get_match(data,'<b class="icon-bullhorn">(.*?)>Sinopsis</a>')
        scrapedinfo = re.sub(r'</b> <a href="http.*?director.*?" rel="tag">','Director: ',scrapedinfo)
        scrapedinfo = re.sub(r'<a href=.*?actor.*?" rel="tag">','Reparto: ',scrapedinfo)
        scrapedinfo = re.sub(r'</a>, Reparto:',',',scrapedinfo)
        scrapedinfo = re.sub(r'<b class="icon-check"></b>','Año: ',scrapedinfo)
        scrapedinfo = re.sub(r'<b class="icon-trophy">','Premios: ',scrapedinfo)
        scrapedinfo = re.sub(r'</a></p></div><div class="xmll"><p class="xcsd">|<b class="icon-star">|</b>|</p></div><div class="xmll"><p class="xcsd">|</p></div><div class="xmll"><p class="tsll xcsd"><b class="icon-info-circle"></b> <a href="#dato-2"','-',scrapedinfo)
        
        infoformat = re.compile('(.*?:).*?-',re.DOTALL).findall(scrapedinfo)
        
        for info  in infoformat:
            scrapedinfo= scrapedinfo.replace(info,"[COLOR aqua][B]"+info+"[/B][/COLOR]")
            scrapedinfo= scrapedinfo.replace(scrapedinfo,"[COLOR bisque]"+scrapedinfo+"[/COLOR]")
        
        
        info = scrapedinfo
        info = info.replace("---","")
        info = info.replace("-"," ")
    except:
        info = "[COLOR skyblue][B]Sin informacion adicional...[/B][/COLOR]"
    foto = item.show
    photo= item.extra
    quit = "Pulsa"+" [COLOR blue][B]INTRO [/B][/COLOR]"+ "para quitar"
    ventana2 = TextBox1(title=title, plot=plot, info=info, thumbnail=photo, fanart=foto, quit= quit)
    ventana2.doModal()

ACTION_SELECT_ITEM = 7
class TextBox1( xbmcgui.WindowDialog ):
        """ Create a skinned textbox window """
        def __init__( self, *args, **kwargs):
            
            self.getTitle = kwargs.get('title')
            self.getPlot = kwargs.get('plot')
            self.getInfo = kwargs.get('info')
            self.getThumbnail = kwargs.get('thumbnail')
            self.getFanart = kwargs.get('fanart')
            self.getQuit = kwargs.get('quit')
            
            self.background = xbmcgui.ControlImage( 70, 20, 1150, 630, 'http://s6.postimg.org/58jknrvtd/backgroundventana5.png')
            self.title = xbmcgui.ControlTextBox(140, 60, 1130, 50)
            self.quit = xbmcgui.ControlTextBox(145, 90, 1030, 45)
            self.plot = xbmcgui.ControlTextBox( 120, 150, 1056, 140 )
            self.info = xbmcgui.ControlFadeLabel(120, 310, 1056, 100)
            self.thumbnail = xbmcgui.ControlImage( 813, 43, 390, 100, self.getThumbnail )
            self.fanart = xbmcgui.ControlImage( 120, 365, 1060, 250, self.getFanart )
            
            self.addControl(self.background)
            self.addControl(self.title)
            self.addControl(self.quit)
            self.addControl(self.plot)
            self.addControl(self.thumbnail)
            self.addControl(self.fanart)
            self.addControl(self.info)
            
            self.title.setText( self.getTitle )
            self.quit.setText( self.getQuit )
            try:
                self.plot.autoScroll(7000,6000,30000)
            except:
                print "Actualice a la ultima version de kodi para mejor info"
                import xbmc
                xbmc.executebuiltin('Notification(bbcode_kodi2html([COLOR red][B]Actualiza Kodi a su última versión[/B][/COLOR]), bbcode_kodi2html([COLOR skyblue]para mejor info[/COLOR]),8000,"https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/kodi-icon.png")')
            self.plot.setText(  self.getPlot )
            self.info.addLabel(self.getInfo)
        
        def get(self):
            self.show()
        
        def onAction(self, action):
            if action == ACTION_SELECT_ITEM:
                self.close()
