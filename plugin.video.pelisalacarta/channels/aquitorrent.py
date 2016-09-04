# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import os
import re
import sys
import urllib2
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item


host = "http://www.aquitorrent.com/"

DEBUG = config.get_setting("debug")
def browser(url):
    import mechanize
    # Utilizamos Browser mechanize para saltar problemas con la busqueda en bing
    br = mechanize.Browser()
    # Browser options
    br.set_handle_equiv(False)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(False)
    br.set_handle_robots(False)
    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    
    # Want debugging messages?
    #br.set_debug_http(True)
    #br.set_debug_redirects(True)
    #br.set_debug_responses(True)
    
    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/7.1.7 Safari/537.85.16')]
    #br.addheaders =[('Cookie','SRCHD=D=4210979&AF=NOFORM; domain=.bing.com; expires=Wednesday, 09-Nov-06 23:12:40 GMT; MUIDB=36F71C46589F6EAD0BE714175C9F68FC; domain=www.bing.com;	expires=15 de enero de 2018 08:43:26 GMT+1')]
    # Open some site, let's pick a random one, the first that pops in mind
    r = br.open(url)
    response = r.read()
    if not ".ftrH,.ftrHd,.ftrD>" in response:
       print "proooxyy"
       r = br.open("http://anonymouse.org/cgi-bin/anon-www.cgi/"+url)
       response = r.read()
    return response


def mainlist(item):
    logger.info("pelisalacarta.aquitorrent mainlist")

    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Peliculas"      , action="peliculas", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=PELICULAS", thumbnail="http://imgc.allpostersimages.com/images/P-473-488-90/37/3710/L3YAF00Z/posters/conrad-knutsen-cinema.jpg", fanart="http://s6.postimg.org/m8dipognl/aquitorrentfanart2.jpg"))
    itemlist.append( Item(channel=item.channel, action="peliculas", title="Series", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=SERIES", thumbnail="http://s6.postimg.org/nbxn1n1ap/aquitserielogo.jpg", fanart="http://s6.postimg.org/x6os7v58x/aquitorretseries.jpg"))
    itemlist.append( Item(channel=item.channel, action="peliculas", title="Películas HD", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=Peliculas%20HD", thumbnail="http://s6.postimg.org/4uymx2vyp/aquithdlogo.jpg", fanart="http://s6.postimg.org/umxqri72p/aquitphd3.jpg"))
    itemlist.append( Item(channel=item.channel, action="peliculas", title="Películas 3D", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=PELICULAS%203D", thumbnail="http://s6.postimg.org/53rm99jdd/aquit3dlogo.jpg", fanart="http://s6.postimg.org/9i03l3txt/aquit3d.jpg"))
    itemlist.append( Item(channel=item.channel, action="peliculas", title="Películas V.O.S.", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=PELICULAS%20V.O.S.", thumbnail="http://s6.postimg.org/fofbx2s0h/aquitvostub2.jpg", fanart="http://s6.postimg.org/wss1m0aj5/aquitvos.jpg"))
    itemlist.append( Item(channel=item.channel, action="peliculas", title="Docus y TV", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=Docus%20y%20TV",  thumbnail="http://s6.postimg.org/5mnir1w0h/tv_docaquit.jpg", fanart="http://s6.postimg.org/5lrd2uyc1/aquitdoctv3_an.jpg"))
    itemlist.append( Item(channel=item.channel, action="peliculas", title="Clásicos Disney", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=CLASICOS%20DISNEY", thumbnail="http://s6.postimg.org/87xosbas1/Walt_Disney.jpg", fanart="http://s6.postimg.org/5m0jucd3l/aquitwalt.jpg"))
    itemlist.append( Item(channel=item.channel, action="peliculas", title="F1 2014", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=F1%202014", thumbnail="http://s6.postimg.org/42vyxvrrl/aquitf1tub.png", fanart="http://s6.postimg.org/sbqhvuhjl/aquitf1f.jpg"))
    itemlist.append( Item(channel=item.channel, action="peliculas", title="MotoGP 2014", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=MotoGP%202014", thumbnail="http://s6.postimg.org/flquwhyz5/aquit_Moto_GP_Logo.jpg", fanart="http://s6.postimg.org/sv06iuyc1/aquitmgpf2.jpg"))
    itemlist.append( Item(channel=item.channel, action="peliculas", title="Mundial 2014", url="http://www.aquitorrent.com/torr.asp?pagina=1&tipo=Mundial%202014", thumbnail="http://s6.postimg.org/sgyuj9e8h/aquitmundial_TUB.png", fanart="http://s6.postimg.org/7vk2rcwnl/aquitmundiall.jpg"))
    itemlist.append( Item(channel=item.channel, action="search", title="Buscar...", url="", thumbnail="http://s6.postimg.org/gninw2o9d/searchaquittub.jpg", fanart="http://s6.postimg.org/b4kpslglt/searchaquit.jpg"))
    
    

    return itemlist


                

def search(item,texto):
    logger.info("[pelisalacarta.aquitorrent search texto="+texto)
    
    item.url = "http://www.aquitorrent.com/buscar.asp?q=%s" % (texto)
    try:
        
        return buscador(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []


def buscador(item):
    logger.info("pelisalacarta.aquitorrent buscador")
    
    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    #quitamos los titulos de los href en enlaces<
    data = re.sub(r'&/[^"]+">','">',data)

    patron = '<h2 class="post-title entry-title">.*?'
    patron += '<a href=".([^"]+)".*?>'
    patron += '([^<]+)</a>.*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<b>([^"]+)</b>'
    
    
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 :
        itemlist.append( Item(channel=item.channel, title="[COLOR gold][B]No hay resultados...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/t48ttay4x/aquitnoisethumb.png", fanart ="http://s6.postimg.org/4wjnb0ksx/aquitonoisefan.jpg",folder=False) )
    
    
    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedinfo in matches:
        if "Serie" in scrapedurl:
            title_fan = scrapertools.get_match(scrapedtitle,'(.*?)-')
            title_fan = title_fan.strip()
        else:
            title_fan = scrapedtitle.strip()
        scrapedinfo = scrapedinfo.replace("<br>","-")
        scrapedinfo = scrapedinfo.replace(scrapedinfo,"[COLOR green]"+scrapedinfo+"[/COLOR]")
        scrapedtitle= scrapedtitle.replace(scrapedtitle,"[COLOR white]"+scrapedtitle+"[/COLOR]")
        scrapedtitle = scrapedtitle + " (" + scrapedinfo + ")"
        # Arregla la url y thumbnail
        #scrapedurl = fix_url(scrapedurl)
        scrapedthumbnail = fix_url(scrapedthumbnail)
        
        
        if "tipo=Docus" in item.url or "tipo=F1" in item.url or "tipo=MotoGP" in item.url or "tipo=Mundia" in item.url:
            action= "findvideos"
        else:
            action = "fanart"
        extra = title_fan
        itemlist.append( Item(channel=item.channel, title =scrapedtitle , url= urlparse.urljoin(host, scrapedurl), action=action, fanart="http://s9.postimg.org/lmwhrdl7z/aquitfanart.jpg", extra=extra,thumbnail=scrapedthumbnail) )

    return itemlist


def peliculas(item):
    logger.info("pelisalacarta.aquitorrent peliculas")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    #quitamos los titulos de los href en enlaces<
    data = re.sub(r'&/[^"]+">','">',data)
    
    
    patron = '<div class="sompret-image">'
    patron += '<a href=".([^"]+)".*?>'
    patron += '<img src="([^"]+)".*?'
    patron += 'title="(.*?) -.*?'
    patron += '<div class="sompret-header">(.*?)</div>.*?'
    patron += '<b>([^"]+)</b>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 :
        itemlist.append( Item(channel=item.channel, title="[COLOR gold][B]No hay resultados...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/t48ttay4x/aquitnoisethumb.png", fanart ="http://s6.postimg.org/4wjnb0ksx/aquitonoisefan.jpg",folder=False) )
    
   
    for scrapedurl, scrapedthumbnail, scrapedtitle,scrapedinfoserie, scrapedinfo in matches:
        title_fan = scrapedtitle.strip()
        scrapedinfo = scrapedinfo.replace("<br>","-")
        scrapedinfo = scrapedinfo.replace(scrapedinfo,"[COLOR green]"+scrapedinfo+"[/COLOR]")
        scrapedtitle= scrapedtitle.replace(scrapedtitle,"[COLOR white]"+scrapedtitle+"[/COLOR]")
        if "tipo=SERIES" in item.url:
            scrapedinfoserie= scrapertools.get_match(scrapedinfoserie,'.*?-(.*)')
            scrapedinfoserie = scrapedinfoserie.replace(scrapedinfoserie,"[COLOR yellow]"+scrapedinfoserie+"[/COLOR]")
            scrapedtitle =scrapedtitle + " " + scrapedinfoserie + " " + " (" + scrapedinfo + ")"
        else:
            scrapedtitle = scrapedtitle + " (" + scrapedinfo + ")"
        # Arregla la url y thumbnail
        #scrapedurl = fix_url(scrapedurl)
        scrapedthumbnail = fix_url(scrapedthumbnail)
        
        if "tipo=Docus" in item.url or "tipo=F1" in item.url or "tipo=MotoGP" in item.url or "tipo=Mundia" in item.url:
            action= "findvideos"
        else:
            action = "fanart"

        extra = title_fan
        itemlist.append( Item(channel=item.channel, title =scrapedtitle , url=urlparse.urljoin(host, scrapedurl), action=action, fanart="http://s9.postimg.org/lmwhrdl7z/aquitfanart.jpg", extra = extra, thumbnail=scrapedthumbnail) )
        #itemlist.append( Item(channel=item.channel, title =scrapedtitle , url='acestream://e54e3095b406b870e4380312810160971de37196', action=action, fanart="http://s9.postimg.org/lmwhrdl7z/aquitfanart.jpg", extra = extra, thumbnail=scrapedthumbnail) )

    ## Paginación
    pagina = int(scrapertools.get_match(item.url,"pagina=(\d+)"))+1
    pagina = "pagina=%s" % (pagina)
    next_page = re.sub(r"pagina=\d+", pagina, item.url)
    title= "[COLOR green]Pagina siguiente>>[/COLOR]"
    if pagina in data:
        itemlist.append( Item(channel=item.channel, title=title, url=next_page, fanart="http://s9.postimg.org/lmwhrdl7z/aquitfanart.jpg", thumbnail="http://s6.postimg.org/4hpbrb13l/texflecha2.png",
            action="peliculas", folder=True) )


    
    return itemlist

def fanart(item):
    logger.info("pelisalacarta.aquitorrent fanart")
    itemlist = []
    url = item.url
    data = scrapertools.cache_page(url)
    data = re.sub(r"\n|\r|\t|\s{2}|\(.*?\)|&nbsp;","",data)
    title = item.extra
    
    
    

    year=""
    item.title = re.sub(r"-|\(.*?\)|\d+x\d+","",item.title)
    if not "Series" in item.url:
        urlyear = item.url
        data = scrapertools.cache_page(urlyear)
        try:
            year =scrapertools.get_match(data,'<span style="text-align: justify;">.*?Año.*?(\d\d\d\d)')
        except:
            year = ""
        try:
            
            if "CLASICOS-DISNEY" in item.url:
                title = title + " "+"Disney"
            try:
                ###Busqueda en Tmdb la peli por titulo y año
                title_tmdb = title.replace(" ","%20")
                url_tmdb="http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title_tmdb +"&year="+year+"&language=es&include_adult=false"
                
                data = scrapertools.cachePage(url_tmdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                id = scrapertools.get_match(data,'"page":1.*?,"id":(.*?),')
            
            except:
                if ":" in title or "(" in title:
                    title_tmdb = title.replace(" ","%20")
                    url_tmdb="http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title_tmdb +"&year="+year+"&language=es&include_adult=false"
                    data = scrapertools.cachePage(url_tmdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                    id = scrapertools.get_match(data,'"page":1.*?,"id":(.*?),')
                    
                else:
                    title_tmdb = title.replace(" ","%20")
                    title_tmdb= re.sub(r"(:.*)|\(.*?\)","",title_tmdb)
                    url_tmdb="http://api.themoviedb.org/3/search/movie?api_key=2e2160006592024ba87ccdf78c28f49f&query=" + title_tmdb +"&year="+year+"&language=es&include_adult=false"
                    data = scrapertools.cachePage(url_tmdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                    id = scrapertools.get_match(data,'"page":1.*?,"id":(.*?),')



        except:
            ###Si no hay coincidencia realiza busqueda por bing del id Imdb
            urlbing_imdb = "http://www.bing.com/search?q=%s+%s+site:imdb.com" % (title.replace(' ', '+'),  year)
            data = browser (urlbing_imdb)
            
            try:
                subdata_imdb = scrapertools.get_match(data,'<li class="b_algo">(.*?)h="ID')
            except:
              pass
            
            try:
                url_imdb = scrapertools.get_match(subdata_imdb,'<a href="([^"]+)"')
        
            except:
                pass
            try:
                id_imdb = scrapertools.get_match(url_imdb,'.*?www.imdb.com/.*?/(.*?)/')
            except:
                pass
            try:
                ###Busca id Tmdb mediante el id de Imdb
                urltmdb_remote ="https://api.themoviedb.org/3/find/"+id_imdb+"?external_source=imdb_id&api_key=2e2160006592024ba87ccdf78c28f49f&language=es&include_adult=false"
                data = scrapertools.cachePage(urltmdb_remote)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                id = scrapertools.get_match(data,'"movie_results".*?,"id":(\d+)')
                
            except:
                id = ""
                 
        
        ###Llegados aqui ya tenemos(o no) el id(Tmdb);Busca fanart_1
        urltmdb_fan1 ="http://api.themoviedb.org/3/movie/"+id+"?api_key=2e2160006592024ba87ccdf78c28f49f"
        data = scrapertools.cachePage( urltmdb_fan1 )
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        patron = '"adult".*?"backdrop_path":"(.*?)"'
        matches = re.compile(patron,re.DOTALL).findall(data)
        try:
            ###Prueba poster de Tmdb
            posterdb = scrapertools.get_match(data,'"adult".*?"poster_path":"(.*?)"')
            posterdb =  "https://image.tmdb.org/t/p/original" + posterdb
        except:
            posterdb = item.thumbnail
    
        if len(matches)==0:
            fanart_info = item.fanart
            fanart= item.fanart
            fanart_2 = item.fanart
            itemlist.append( Item(channel=item.channel, title =item.title, url=item.url, action="findvideos", thumbnail=posterdb, fanart=fanart ,extra= fanart_2, folder=True) )
        for fan in matches:
    
            fanart="https://image.tmdb.org/t/p/original" + fan
            fanart_1= fanart
            
            ###Busca fanart para info, fanart para trailer y fanart_2(finvideos) en Tmdb
            urltmdb_images ="http://api.themoviedb.org/3/movie/"+id+"/images?api_key=2e2160006592024ba87ccdf78c28f49f"
            data = scrapertools.cachePage(urltmdb_images)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
            
            patron = '"backdrops".*?"file_path":".*?",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)"'
            matches = re.compile(patron,re.DOTALL).findall(data)
            
            if len(matches) == 0:
                patron = '"backdrops".*?"file_path":"(.*?)",.*?"file_path":"(.*?)",.*?"file_path":"(.*?)"'
                matches = re.compile(patron,re.DOTALL).findall(data)
                if len(matches) == 0:
                    fanart_info = fanart_1
                    fanart_trailer = fanart_1
                    fanart_2 = fanart_1
                    category =""
            for fanart_info, fanart_trailer, fanart_2 in matches:
                fanart_info = "https://image.tmdb.org/t/p/original" + fanart_info
                fanart_trailer = "https://image.tmdb.org/t/p/original" + fanart_trailer
                fanart_2 = "https://image.tmdb.org/t/p/original" + fanart_2
                category = ""
                
                if fanart_info == fanart:
                    ###Busca fanart_info en Imdb si coincide con fanart
                    try:
                        url_imdbphoto = "http://www.imdb.com/title/"+id_imdb+"/mediaindex"
                        photo_imdb= scrapertools.get_match(url_imdbphoto,'<div class="media_index_thumb_list".*?src="([^"]+)"')
                        photo_imdb = photo_imdb.replace("@._V1_UY100_CR25,0,100,100_AL_.jpg","@._V1_SX1280_SY720_.jpg")
                        fanart_info = photo_imdb
                    except:
                        fanart_info = fanart_2
            itemlist.append( Item(channel=item.channel, title =item.title, url=item.url, action="findvideos", thumbnail=posterdb, fanart=fanart_1 ,extra= fanart_2, folder=True) )



    else:
        urlyear = item.url
        data = scrapertools.cache_page(urlyear)
        try:
            year =scrapertools.get_match(data,'<span style="text-align: justify;">.*?Año.*?(\d\d\d\d)')
        except:
              try:
                 year =scrapertools.get_match(data,'SINOPSIS.*? \((\d\d\d\d)')
              except:
                 year = ""
        #Busqueda bing de Imdb serie id
        url_imdb = "http://www.bing.com/search?q=%s+%s+tv+series+site:imdb.com" % (title.replace(' ', '+'),  year)
        data = browser (url_imdb)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        
        try:
            subdata_imdb = scrapertools.get_match(data,'<li class="b_algo">(.*?)h="ID')
        except:
            pass
        try:
            imdb_id = scrapertools.get_match(subdata_imdb,'<a href=.*?http.*?imdb.com/title/(.*?)/.*?"')
        except:
            imdb_id = ""
        ### Busca id de tvdb mediante imdb id
        urltvdb_remote="http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid="+imdb_id+"&language=es"
        data = scrapertools.cachePage(urltvdb_remote)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        patron = '<Data><Series><seriesid>([^<]+)</seriesid>.*?<Overview>(.*?)</Overview>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        
        if len(matches)== 0:
            print "gooooooo"
            ###Si no hay coincidencia busca en tvdb directamente
            if ":" in title or "(" in title:
                title= title.replace(" ","%20")
                url_tvdb="http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
                data = scrapertools.cachePage(url_tvdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                patron = '<Data><Series><seriesid>([^<]+)</seriesid>.*?<Overview>(.*?)</Overview>'
                matches = re.compile(patron,re.DOTALL).findall(data)
                if len(matches)== 0:
                    title= re.sub(r"(:.*)|\(.*?\)","",title)
                    title= title.replace(" ","%20")
                    url_tvdb="http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
                    data = scrapertools.cachePage(url_tvdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                    patron = '<Data><Series><seriesid>([^<]+)</seriesid>.*?<Overview>(.*?)</Overview>'
                    matches = re.compile(patron,re.DOTALL).findall(data)
                        
                    if len(matches) == 0:
                        plot = ""
                        postertvdb = item.thumbnail
                        extra= "http://s6.postimg.org/rv2mu3pap/bityouthsinopsis2.png"
                        fanart_info = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                        fanart_trailer = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                        category= ""
                        show = title+"|"+year+"|"+"http://s6.postimg.org/mh3umjzkh/bityouthnofanventanuco.jpg"
                        itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="finvideos", thumbnail=item.thumbnail, fanart="http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg" ,extra=extra, category= category,  show=show ,plot=plot, folder=True) )
        
            else:
                title= title.replace(" ","%20")
                url_tvdb="http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
                data = scrapertools.cachePage(url_tvdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                patron = '<Data><Series><seriesid>([^<]+)</seriesid>.*?<Overview>(.*?)</Overview>'
                print "perroooo"
                print patron
                matches = re.compile(patron,re.DOTALL).findall(data)
                print matches
                if len(matches) == 0:
                    plot = ""
                    postertvdb = item.thumbnail
                    extra= "http://s6.postimg.org/rv2mu3pap/bityouthsinopsis2.png"
                    show = title+"|"+year+"|"+"http://s6.postimg.org/mh3umjzkh/bityouthnofanventanuco.jpg"
                    fanart_info = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                    fanart_trailer = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                    category= ""
                    itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="findvideos", thumbnail=item.thumbnail, fanart="http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg" ,extra=extra, category= category,  show=show ,plot= plot, folder=True) )
        #fanart
        for  id, info in matches:
            
            category = id
            plot = info
            id_serie = id
            
            url ="http://thetvdb.com/api/1D62F2F90030C444/series/"+id_serie+"/banners.xml"
            
            data = scrapertools.cachePage(url)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
            patron = '<Banners><Banner>.*?<VignettePath>(.*?)</VignettePath>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            try:
                postertvdb = scrapertools.get_match(data,'<Banners><Banner>.*?<BannerPath>posters/(.*?)</BannerPath>')
                postertvdb =  "http://thetvdb.com/banners/_cache/posters/" + postertvdb
            except:
                postertvdb = item.thumbnail
                                
            if len(matches)==0:
                extra="http://s6.postimg.org/rv2mu3pap/bityouthsinopsis2.png"
                show = title+"|"+year+"|"+"http://s6.postimg.org/mh3umjzkh/bityouthnofanventanuco.jpg"
                fanart_info = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                fanart_trailer = "http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"
                itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="findvideos", thumbnail=postertvdb, fanart="http://s6.postimg.org/6ucl96lsh/bityouthnofan.jpg"  ,category = category, extra=extra, show=show,folder=True) )
                                                        
            for fan in matches:
                fanart="http://thetvdb.com/banners/" + fan
                fanart_1= fanart
                patron= '<Banners><Banner>.*?<BannerPath>.*?</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>'
                matches = re.compile(patron,re.DOTALL).findall(data)
                if len(matches)==0:
                   fanart_info= fanart_1
                   fanart_trailer = fanart_1
                   fanart_2 = fanart_1
                   show = title+"|"+year+"|"+fanart_1
                   extra=postertvdb
                   itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="findvideos", thumbnail=postertvdb, fanart=fanart_1  ,category = category, extra=extra, show=show,folder=True) )
                for fanart_info, fanart_trailer, fanart_2 in matches:
                    fanart_info = "http://thetvdb.com/banners/" + fanart_info
                    fanart_trailer = "http://thetvdb.com/banners/" + fanart_trailer
                    fanart_2 = "http://thetvdb.com/banners/" + fanart_2
                
                    itemlist.append( Item(channel=item.channel, title =item.title, url=item.url, action="findvideos", thumbnail=postertvdb, fanart=fanart_1 , extra= fanart_2,folder=True) )
    title ="Info"
    title = title.replace(title,"[COLOR skyblue][B]"+title+"[/B][/COLOR]")
    if "Series" in item.url:
        thumbnail = postertvdb
    else:
        thumbnail = posterdb

    itemlist.append( Item(channel=item.channel, action="info" , title=title , url=item.url, thumbnail=thumbnail, fanart=fanart_info , folder=False ))

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.aquitorrent findvideos")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    # Torrent en zip
    patron = '<h1 class="post-title entry-title">([^<]+)</h1>.*?</b><br><br>.*?'
    patron+= 'href="(.*?\.zip)".*?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)>0:
        for scrapedtitle, scrapedzip in matches:
            # Arregla la url y extrae el torrent
            scrapedtorrent = unzip(fix_url(scrapedzip))
            
            itemlist.append( Item(channel=item.channel, title =item.title+"[COLOR red][B] [magnet][/B][/COLOR]" , url=scrapedtorrent,  action="play", server="torrent", thumbnail=item.thumbnail, fanart=item.extra , folder=False) )


    #Vamos con el normal

    patron = '<h1 class="post-title entry-title">([^<]+)</h1>.*?'
    patron+= 'href="(magnet[^"]+)".*?'


    
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedtitle, scrapedmagnet in matches:
        if "Docus" in item.url or "F1" in item.url or "MotoGP" in item.url or "Mundia" in item.url:
            fanart= item.fanart
        else:
            fanart = item.extra
        title_tag="[COLOR yellow][B]Ver--[/B][/COLOR]"
        item.title=item.title.strip()
        itemlist.append( Item(channel=item.channel, title =title_tag+item.title+"[COLOR red][B] [magnet][/B][/COLOR]" , url=scrapedmagnet,  action="play", server="torrent", thumbnail=item.thumbnail, fanart=fanart , folder=False) )
    
    #nueva variacion
    if len(itemlist) == 0:
       patron = '<h1 class="post-title entry-title">([^<]+)</h1>.*?<br><br>.*?'
       patron+= 'href="([^"]+)".*?'
       
       matches = re.compile(patron,re.DOTALL).findall(data)
    
       for scrapedtitle, scrapedtorrent in matches:
           itemlist.append( Item(channel=item.channel, title =scrapedtitle+"[COLOR green][B] [magnet][/B][/COLOR]", url=scrapedtorrent, action="play", server="torrent", thumbnail=item.thumbnail, fanart=item.extra , folder=False) )


    
    return itemlist


def fix_url(url):
    if url.startswith("/"):
        url = url[1:]
        if not url.startswith("http://"):
            url = host+url
    return url

def unzip(url):
    import zipfile
    itemlist=   []
    # Path para guardar el zip como tem.zip los .torrent extraidos del zip
    torrents_path = config.get_library_path()+'/torrents'
    
    if not os.path.exists(torrents_path):
        os.mkdir(torrents_path)

    ## http://stackoverflow.com/questions/4028697/how-do-i-download-a-zip-file-in-python-using-urllib2
    # Open the url
    try:
        f = urllib2.urlopen(url)
        with open( torrents_path+"/temp.zip", "wb") as local_file:
            local_file.write(f.read())
        
        # Open our local file for writing
        fh = open(torrents_path+"/temp.zip", 'rb')
        z = zipfile.ZipFile(fh)
        for name in z.namelist():
            z.extract(name, torrents_path)
        fh.close()

    #handle errors
    except urllib2.HTTPError, e:
        print "HTTP Error:", e.code, url
    except urllib2.URLError, e:
        print "URL Error:", e.reason, url
    try:
       torrent = "file:///"+torrents_path+"/"+name
    except:
        import xbmc, time
        xbmc.executebuiltin( "XBMC.Action(back)" )
        xbmc.sleep(100)
        xbmc.executebuiltin('Notification([COLOR yellow][B]Torrent temporalmente[/B][/COLOR], [COLOR green][B]'+'no disponible'.upper()+'[/B][/COLOR],5000,"http://s6.postimg.org/kta7oe8y9/aquitorrentlogo.png")')

    if not torrents_path.startswith("/"):
        torrents_path = "/"+torrents_path
    try:
       torrent = "file://"+torrents_path+"/"+name

       return torrent
    except:
       return itemlist

def info(item):
    logger.info("pelisalacarta.aquitorrents info")
    
    url=item.url
    data = scrapertools.cachePage(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    title= scrapertools.get_match(data,'<h1 class="post-title entry-title">([^<]+)</h1>')
    title = title.replace(title,"[COLOR aqua][B]"+title+"[/B][/COLOR]")
    
    if "DISNEY" in item.url or "Series" in item.url or "PELICULAS-3D" in item.url or "PELICULAS-VOS" in item.url:
        scrapedplot = scrapertools.get_match(data,'<span style="text-align: justify;">(.*)</span></div>')
        plotformat = re.compile('(.*?:).*?<br />',re.DOTALL).findall(scrapedplot)
        # Reemplaza las etiquetas con etiquetas formateadas con color azul y negrita
        for plot in plotformat:
            scrapedplot = scrapedplot.replace(plot,"[COLOR green][B]"+plot+"[/B][/COLOR]")
            plot = plot.replace(plot,"[COLOR white]"+plot+"[/COLOR]")
        
        # reemplaza los <br /> por saltos de línea del xbmc
        scrapedplot = scrapedplot.replace("<br />","[CR]")
        # codifica el texto en utf-8 para que se puedan ver las tíldes y eñes
        scrapedplot= scrapedplot.replace('á','a')
        scrapedplot= scrapedplot.replace('Á','A')
        scrapedplot= scrapedplot.replace('é','e')
        scrapedplot= scrapedplot.replace('í','i')
        scrapedplot= scrapedplot.replace('ó','o')
        scrapedplot= scrapedplot.replace('ú','u')
        scrapedplot= scrapedplot.replace('ñ','n')
        fanart="http://s11.postimg.org/qu66qpjz7/zentorrentsfanart.jpg"
        tbd = TextBox("DialogTextViewer.xml", os.getcwd(), "Default")
        tbd.ask(title, scrapedplot,fanart)
        del tbd
        return
    else:
        if "PELICULAS" in item.url or "peliculas" in item.url:
            scrapedplot = scrapertools.get_match(data,'<br><br>>(.*)<br><br><img')
            plotformat = re.compile('(.*?:).*?<br />',re.DOTALL).findall(scrapedplot)
            # Reemplaza las etiquetas con etiquetas formateadas con color azul y negrita
            for plot in plotformat:
                scrapedplot = scrapedplot.replace(plot,"[COLOR green][B]"+plot+"[/B][/COLOR]")
                plot = plot.replace(plot,"[COLOR white]"+plot+"[/COLOR]")
            # reemplaza los <br /> por saltos de línea del xbmc
            scrapedplot = scrapedplot.replace("<br />","[CR]")
            # codifica el texto en utf-8 para que se puedan ver las tíldes y eñes
            scrapedplot= scrapedplot.replace('á','a')
            scrapedplot= scrapedplot.replace('Á','A')
            scrapedplot= scrapedplot.replace('é','e')
            scrapedplot= scrapedplot.replace('í','i')
            scrapedplot= scrapedplot.replace('ó','o')
            scrapedplot= scrapedplot.replace('ú','u')
            scrapedplot= scrapedplot.replace('ñ','n')
            fanart="http://s11.postimg.org/qu66qpjz7/zentorrentsfanart.jpg"
            tbd = TextBox("DialogTextViewer.xml", os.getcwd(), "Default")
            tbd.ask(title, scrapedplot,fanart)
            del tbd
            return
        else:
            scrapedplot = scrapertools.get_match(data,'<span style="text-align: justify;">(.*)</span></div>')
            plotformat = re.compile('(.*?:).*?<br />',re.DOTALL).findall(scrapedplot)
            # Reemplaza las etiquetas con etiquetas formateadas con color azul y negrita
            for plot in plotformat:
                scrapedplot = scrapedplot.replace(plot,"[COLOR green][B]"+plot+"[/B][/COLOR]")
                plot = plot.replace(plot,"[COLOR white]"+plot+"[/COLOR]")
            # reemplaza los <br /> por saltos de línea del xbmc
            scrapedplot = scrapedplot.replace("<br />","[CR]")
            # codifica el texto en utf-8 para que se puedan ver las tíldes y eñes
            scrapedplot= scrapedplot.replace('á','a')
            scrapedplot= scrapedplot.replace('Á','A')
            scrapedplot= scrapedplot.replace('é','e')
            scrapedplot= scrapedplot.replace('í','i')
            scrapedplot= scrapedplot.replace('ó','o')
            scrapedplot= scrapedplot.replace('ú','u')
            scrapedplot= scrapedplot.replace('ñ','n')
            fanart="http://s11.postimg.org/qu66qpjz7/zentorrentsfanart.jpg"
            tbd = TextBox("DialogTextViewer.xml", os.getcwd(), "Default")
            tbd.ask(title, scrapedplot,fanart)
            del tbd
            return




try:
    import xbmc, xbmcgui
    class TextBox( xbmcgui.WindowXMLDialog ):
        """ Create a skinned textbox window """
        def __init__( self, *args, **kwargs):
            
            pass
        
        def onInit( self ):
            try:
                self.getControl( 5 ).setText( self.text )
                self.getControl( 1 ).setLabel( self.title )
            except: pass
        
        def onClick( self, controlId ):
            pass
        
        def onFocus( self, controlId ):
            pass
        
        def onAction( self, action ):
            self.close()
        
        def ask(self, title, text, image ):
            self.title = title
            self.text = text
            self.doModal()

except:
    pass
