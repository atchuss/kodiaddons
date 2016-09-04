# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para peliculasdk
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

try:
    import xbmc
    import xbmcgui
except: pass


DEBUG = config.get_setting("debug")
host = "http://www.peliculasdk.com/"
Tmdb_key ="2e2160006592024ba87ccdf78c28f49f"


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

def mainlist(item):
    logger.info("pelisalacarta.peliculasdk mainlist")
    itemlist = []
    title ="Estrenos"
    title = title.replace(title,bbcode_kodi2html("[COLOR orange]"+title+"[/COLOR]"))
    itemlist.append( Item(channel=item.channel, title=title      , action="peliculas", url="http://www.peliculasdk.com/ver/estrenos", fanart="http://s24.postimg.org/z6ulldcph/pdkesfan.jpg", thumbnail="http://s16.postimg.org/st4x601d1/pdkesth.jpg"))
    title ="PelisHd"
    title = title.replace(title,bbcode_kodi2html("[COLOR orange]"+title+"[/COLOR]"))
    itemlist.append( Item(channel=item.channel, title=title     , action="peliculas", url="http://www.peliculasdk.com/calidad/HD-720/", fanart="http://s18.postimg.org/wzqonq3w9/pdkhdfan.jpg", thumbnail="http://s8.postimg.org/nn5669ln9/pdkhdthu.jpg"))
    title ="Pelis HD-Rip"
    title = title.replace(title,bbcode_kodi2html("[COLOR orange]"+title+"[/COLOR]"))
    itemlist.append( Item(channel=item.channel, title=title      , action="peliculas", url="http://www.peliculasdk.com/calidad/HD-320", fanart="http://s7.postimg.org/3pmnrnu7f/pdkripfan.jpg", thumbnail="http://s12.postimg.org/r7re8fie5/pdkhdripthub.jpg"))
    title ="Pelis Audio español"
    title = title.replace(title,bbcode_kodi2html("[COLOR orange]"+title+"[/COLOR]"))
    itemlist.append( Item(channel=item.channel, title=title     , action="peliculas", url="http://www.peliculasdk.com/idioma/Espanol/", fanart="http://s11.postimg.org/65t7bxlzn/pdkespfan.jpg", thumbnail="http://s13.postimg.org/sh1034ign/pdkhsphtub.jpg"))
    title ="Buscar..."
    title = title.replace(title,bbcode_kodi2html("[COLOR orange]"+title+"[/COLOR]"))
    itemlist.append( Item(channel=item.channel, title=title      , action="search", url="http://www.peliculasdk.com/calidad/HD-720/", fanart="http://s14.postimg.org/ceqajaw2p/pdkbusfan.jpg", thumbnail="http://s13.postimg.org/o85gsftyv/pdkbusthub.jpg"))
    

    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.peliculasdk search")
    texto = texto.replace(" ","+")
    
    item.url = "http://www.peliculasdk.com/index.php?s=%s&x=0&y=0" % (texto)
    
    try:
        return buscador(item)
    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def buscador(item):
    logger.info("pelisalacarta.peliculasdk buscador")
    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)


    patron = '<div class="karatula".*?'
    patron += 'src="([^"]+)".*?'
    patron += '<div class="tisearch"><a href="([^"]+)">'
    patron += '([^<]+)<.*?'
    patron += 'Audio:(.*?)</a>.*?'
    patron += 'Género:(.*?)</a>.*?'
    patron += 'Calidad:(.*?),'
    

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 :
        itemlist.append( Item(channel=item.channel, title=bbcode_kodi2html("[COLOR gold][B]Sin resultados...[/B][/COLOR]"), thumbnail ="http://s6.postimg.org/t8gfes7rl/pdknoisethumb.png", fanart ="http://s6.postimg.org/oy1rj72oh/pdknoisefan.jpg",folder=False) )

    for scrapedthumbnail,scrapedurl, scrapedtitle,  scrapedlenguaje, scrapedgenero, scrapedcalidad in matches:
        scrapedcalidad = re.sub(r"<a href.*?>|</a>|</span>","",scrapedcalidad).strip()
        scrapedlenguaje = re.sub(r"<a href.*?>|</a>|</span>","",scrapedlenguaje).strip()
        
        if not "Adultos" in scrapedgenero and not "Adultos" in scrapedlenguaje and not "Adultos" in scrapedcalidad:
           scrapedcalidad = scrapedcalidad.replace(scrapedcalidad,bbcode_kodi2html("[COLOR orange]"+scrapedcalidad+"[/COLOR]"))
           scrapedlenguaje = scrapedlenguaje.replace(scrapedlenguaje,bbcode_kodi2html("[COLOR orange]"+scrapedlenguaje+"[/COLOR]"))
           try:
               yeartrailer = scrapertools.get_match(scrapedtitle,'\((.*?)\)')
           except:
               yeartrailer = ""
           try:
               titletrailer= scrapertools.get_match(scrapedtitle,'(.*?)\(')
           except:
               titletrailer=""
           trailer = titletrailer + yeartrailer + "trailer"
           trailer = urllib.quote(trailer)
           scrapedtitle = scrapedtitle + "-(Idioma: " + scrapedlenguaje + ")" + "-(Calidad: " + scrapedcalidad +")"
           scrapedtitle = scrapedtitle.replace(scrapedtitle,bbcode_kodi2html("[COLOR white]"+scrapedtitle+"[/COLOR]"))
           itemlist.append( Item(channel=item.channel, title =scrapedtitle , url=scrapedurl, action="fanart", thumbnail=scrapedthumbnail,plot = trailer, fanart="http://s18.postimg.org/h9kb22mnt/pdkfanart.jpg", folder=True) )
    try:
        next_page = scrapertools.get_match(data,'<span class="current">.*?<a href="(.*?)".*?>Siguiente &raquo;</a></div>')


        title ="siguiente>>"
        title = title.replace(title,bbcode_kodi2html("[COLOR red]"+title+"[/COLOR]"))
        itemlist.append( Item(channel=item.channel, action="buscador", title=title , url=next_page , thumbnail="http://s6.postimg.org/uej03x4r5/bricoflecha.png", fanart="http://s18.postimg.org/h9kb22mnt/pdkfanart.jpg",  folder=True) )
    except: pass

    return itemlist




def peliculas(item):
    logger.info("pelisalacarta.peliculasdk peliculas")
    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|&#.*?;","",data)
    
    
    


    patron = 'style="position:relative;"> '
    patron += '<a href="([^"]+)" '
    patron += 'title="([^<]+)">'
    patron += '<img src="([^"]+)".*?'
    patron += 'Audio:(.*?)</br>.*?'
    patron += 'Calidad:(.*?)</br>.*?'
    patron +='Género:.*?tag">(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)


    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedlenguaje, scrapedcalidad , scrapedgenero in matches:
        scrapedcalidad = re.sub(r"<a href.*?>|</a>","",scrapedcalidad).strip()
        scrapedlenguaje = re.sub(r"<a href.*?>|</a>","",scrapedlenguaje).strip()
        scrapedcalidad = scrapedcalidad.replace(scrapedcalidad,bbcode_kodi2html("[COLOR orange]"+scrapedcalidad+"[/COLOR]"))
        
       
        if not "Adultos" in scrapedgenero and not "Adultos" in scrapedlenguaje and not "Adultos" in scrapedcalidad:
        
           scrapedlenguaje = scrapedlenguaje.replace(scrapedlenguaje,bbcode_kodi2html("[COLOR orange]"+scrapedlenguaje+"[/COLOR]"))
           try:
              yeartrailer = scrapertools.get_match(scrapedtitle,'\((.*?)\)')
           except:
              yeartrailer = ""
           try:
              titletrailer= scrapertools.get_match(scrapedtitle,'(.*?)\(')
           except:
              titletrailer=""
           trailer = titletrailer + yeartrailer + "trailer"
           trailer = urllib.quote(trailer)
          
           scrapedtitle = scrapedtitle + "-(Idioma: " + scrapedlenguaje + ")" + "-(Calidad: " + scrapedcalidad +")"
           scrapedtitle = scrapedtitle.replace(scrapedtitle,bbcode_kodi2html("[COLOR white]"+scrapedtitle+"[/COLOR]"))
           
           itemlist.append( Item(channel=item.channel, title =scrapedtitle , url=scrapedurl, action="fanart", thumbnail=scrapedthumbnail,plot = trailer, fanart="http://s18.postimg.org/h9kb22mnt/pdkfanart.jpg", folder=True) )
    ## Paginación
    
    next_page = scrapertools.get_match(data,'<span class="current">.*?<a href="(.*?)".*?>Siguiente &raquo;</a></div>')
    
    title ="siguiente>>"
    title = title.replace(title,bbcode_kodi2html("[COLOR red]"+title+"[/COLOR]"))
    itemlist.append( Item(channel=item.channel, action="peliculas", title=title , url=next_page , thumbnail="http://s6.postimg.org/uej03x4r5/bricoflecha.png", fanart="http://s18.postimg.org/h9kb22mnt/pdkfanart.jpg",  folder=True) )
    

    return itemlist

def fanart(item):
    logger.info("pelisalacarta.peliculasdk fanart")
    itemlist = []
    url = item.url
    
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    title= scrapertools.get_match(data,'<title>Ver Película(.*?) \(')
    title= re.sub(r"3D|SBS|-|","",title)
    title= title.replace('á','a')
    title= title.replace('Á','A')
    title= title.replace('é','e')
    title= title.replace('í','i')
    title= title.replace('ó','o')
    title= title.replace('ú','u')
    title= title.replace('ñ','n')
    title= title.replace('Crepusculo','Twilight')
    title= title.replace(' ','%20')
    url="http://api.themoviedb.org/3/search/movie?api_key="+Tmdb_key+"&query=" + title + "&language=es&include_adult=false"
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
        itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart=item.thumbnail ,extra=extra, show=show, category= category, folder=True) )
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
                    itemlist.append( Item(channel=item.channel, title = item.title , action="findvideos", url=item.url, server="torrent", thumbnail=logo, fanart=item.extra,category= category, extra=extra,show=show ,  folder=True) )

    title ="Info"
   
    if posterdb == item.thumbnail:
       if '"movieposter"' in data:
           thumbnail= poster
       else:
           thumbnail = item.thumbnail
    else:
        thumbnail = posterdb



    

    title = title.replace(title,bbcode_kodi2html("[COLOR skyblue]"+title+"[/COLOR]"))
    itemlist.append( Item(channel=item.channel, action="info" , title=title , url=item.url, thumbnail=posterdb, fanart=fanart_info, extra = extra, show = show,folder=False ))

    title= bbcode_kodi2html("[COLOR crimson]Trailer[/COLOR]")
    
    if len(item.extra)==0:
        fanart=item.thumbnail
    else:
        fanart = item.extra



    if '"moviethumb"' in data:
        thumbnail = thumb
    else:
        thumbnail = posterdb

    if '"moviebanner"' in data:
        extra= banner
    else:
        if 'hdmovieclearart"' in data:
            extra = clear
        
        else:
            extra = posterdb



    itemlist.append( Item(channel=item.channel, action="trailer", title=title , url=item.url , thumbnail=thumbnail , fulltitle = item.title , fanart=fanart_trailer, extra=extra, plot = item.plot,folder=True) )


    return itemlist


def findvideos(item):
    logger.info("pelisalacarta.peliculasdk findvideos")
    
    itemlist = []
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"<!--.*?-->","",data)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    
    
    servers_data_list = {}
    
    patron = '<div id="tab\d+" class="tab_content"><script type="text/rocketscript">(\w+)\("([^"]+)"\)</script></div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    if len(matches)==0:
        patron = '<div id="tab\d+" class="tab_content"><script>(\w+)\("([^"]+)"\)</script></div>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        print matches
    
    for server, id in matches:
        
        
        scrapedplot = scrapertools.get_match(data,'<span class="clms">(.*?)</div></div>')
        plotformat = re.compile('(.*?:) </span>',re.DOTALL).findall(scrapedplot)
        scrapedplot = scrapedplot.replace(scrapedplot,bbcode_kodi2html("[COLOR white]"+scrapedplot+"[/COLOR]"))
        
        for plot in plotformat:
            scrapedplot = scrapedplot.replace(plot,bbcode_kodi2html("[COLOR red][B]"+plot+"[/B][/COLOR]"))
        scrapedplot = scrapedplot.replace("</span>","[CR]")
        scrapedplot = scrapedplot.replace(":","")
        servers_data_list.update({server:id})

    
    url = "http://www.peliculasdk.com/Js/videos.js"
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    data = data.replace ('<iframe width="100%" height="400" scrolling="no" frameborder="0"','')

    patron = 'function (\w+)\(id\).*?'
    patron+= '"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for server, url in matches:
        
        '''if  "carajo" in manolo:
            print "tu viejaaaa"
            import xbmc, time
                    
            timeout = time.time()+1
            while time.time()< timeout:
                  xbmc.executebuiltin( "Action(back)" )
                  time.sleep(1)
                                    
                                    
            xbmc.executebuiltin('Notification([COLOR crimson][B]Video[/B][/COLOR], [COLOR yellow][B]'+'No compatible'.upper()+'[/B][/COLOR],4000,"http://s29.postimg.org/wzw749oon/pldklog.jpg")')
                      
            break'''
        if server in servers_data_list:
            video_url = re.sub(r"embed\-|\-630x400\.html","",url)
            video_url = video_url.replace("'+codigo+'",servers_data_list[server])
            servertitle = scrapertools.get_match(video_url,'http://(.*?)/')
            servertitle = servertitle.replace(servertitle,bbcode_kodi2html("[COLOR red]"+servertitle+"[/COLOR]"))
            servertitle = servertitle.replace("embed.","")
            servertitle = servertitle.replace("player.","")
            servertitle = servertitle.replace("api.video.","")
            servertitle = servertitle.replace("hqq.tv","netu.tv")
            title = bbcode_kodi2html("[COLOR orange]Ver en --[/COLOR]") + servertitle
            itemlist.append( Item(channel=item.channel, title =title , url=video_url, action="play", thumbnail=item.category, plot=scrapedplot, fanart=item.show ) )
         
           
           


    return itemlist


def play(item):
    logger.info("pelisalacarta.bricocine findvideos")
    
    itemlist = servertools.find_video_items(data=item.url)
    data = scrapertools.cache_page(item.url)
    
    
    
    listavideos = servertools.findvideos(data)
    
    for video in listavideos:
        videotitle = scrapertools.unescape(video[0])
        url =item.url
        server = video[2]
        
        #xbmctools.addnewvideo( item.channel , "play" , category , server ,  , url , thumbnail , plot )
        itemlist.append( Item(channel=item.channel, action="play", server=server, title="Trailer - " + videotitle  , url=url , thumbnail=item.thumbnail , plot=item.plot , fulltitle = item.title , fanart="http://s23.postimg.org/84vkeq863/movietrailers.jpg", folder=False) )
    
    
   

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
        itemlist.append( Item(channel=item.channel, title=bbcode_kodi2html("[COLOR gold][B]No hay Trailer[/B][/COLOR]"), thumbnail ="http://s6.postimg.org/jp5jx97ip/bityoucancel.png", fanart ="http://s6.postimg.org/vfjhen0b5/bityounieve.jpg",folder=False) )
    
    for scrapedurl, scrapedtitle in matches:
        
        scrapedurl = "https://www.youtube.com/watch"+scrapedurl
        scrapedtitle = scrapertools.decodeHtmlentities( scrapedtitle )
        scrapedtitle=scrapedtitle.replace(scrapedtitle,bbcode_kodi2html("[COLOR khaki][B]"+scrapedtitle+"[/B][/COLOR]"))
        itemlist.append( Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, server="youtube", fanart="http://static1.squarespace.com/static/5502c970e4b0cec330247c32/t/5517212ee4b07ea6d281c891/1427579186693/Movie+Trailers+and+promos.JPG?format=1500w", thumbnail=item.extra, action="play", folder=False) )
    
    return itemlist

def info(item):
    logger.info("pelisalacarta.zentorrents info")
    
    url=item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    title= scrapertools.get_match(data,'<title>Ver Película(.*?) \(')
    title = title.replace(title,bbcode_kodi2html("[COLOR orange][B]"+title+"[/B][/COLOR]"))
    try:
        plot = scrapertools.get_match(data,'<span class="clms">Sinopsis: </span>(.*?)</div>')
        plot = plot.replace(plot,bbcode_kodi2html("[COLOR white][B]"+plot+"[/B][/COLOR]"))
    except :
        title = bbcode_kodi2html("[COLOR red][B]LO SENTIMOS...[/B][/COLOR]")
        plot = "Esta Pelicula no tiene informacion..."
        plot = plot.replace(plot,bbcode_kodi2html("[COLOR yellow][B]"+plot+"[/B][/COLOR]"))
        photo="http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
        foto ="http://s6.postimg.org/ub7pb76c1/noinfo.png"
        info =""
        quit = "Pulsa"+bbcode_kodi2html(" [COLOR orangered][B]INTRO [/B][/COLOR]"+ "para quitar")
    try:
        scrapedinfo= scrapertools.get_match(data,'<div class="infopeli">(.*?)<table class="ventana2" border="0">')
    
        infoformat = re.compile('(.*?:) .*?<br/>',re.DOTALL).findall(scrapedinfo)
        for info in infoformat:
           scrapedinfo= scrapedinfo.replace(info,bbcode_kodi2html("[COLOR orange][B]"+info+"[/B][/COLOR]"))
           info= scrapedinfo.replace(info,bbcode_kodi2html("[COLOR white][B]"+info+"[/B][/COLOR]"))
           info = scrapedinfo
           info = re.sub(r'<a href=".*?">|<span>|</a>|</div></td></tr></table>|<span class=".*?".*?>|<a><img src=".*?"/>','',scrapedinfo)
           info = info.replace("</span><br/>"," ")
           info = info.replace("</span>"," ")
           info = info.replace("<br/>","  ")
           info = info.replace("</B>","")
           info = info.replace("Calificación IMDb:",bbcode_kodi2html("[COLOR orange][B]Calificación IMDb:[/B][/COLOR]"))
           info = info.replace("Calificación IMDb:[/B]","Calificación IMDb:")
           info = info.replace("Premios:",bbcode_kodi2html("[COLOR orange][B]Premios:[/B][/COLOR]"))
    except:
         info = bbcode_kodi2html("[COLOR red][B]Sin informacion adicional...[/B][/COLOR]")
    info = info
    foto = item.show
    photo= item.extra
    quit = "Pulsa"+bbcode_kodi2html(" [COLOR orangered][B]INTRO [/B][/COLOR]"+ "para quitar")


    ventana2 = TextBox1(title=title, plot=plot, info=info, thumbnail=photo, fanart=foto, quit= quit)
    ventana2.doModal()
ACTION_GESTURE_SWIPE_LEFT = 511
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
            if action == ACTION_SELECT_ITEM or action == ACTION_GESTURE_SWIPE_LEFT:
               self.close()
