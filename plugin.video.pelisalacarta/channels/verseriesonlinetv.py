# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import os
import re
import sys
import urllib
import urllib2

import xbmcgui

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.scrapertools import decodeHtmlentities as dhe


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
    r = br.open("http://anonymouse.org/cgi-bin/anon-www.cgi/"+url)
    response = r.read()
    if not ".ftrH,.ftrHd,.ftrD>" in response:
        print "proooxy"
        r = br.open("http://anonymouse.org/cgi-bin/anon-www.cgi/"+url)
        response = r.read()
    return response
'''def proxy(url):
    from lib import requests
    proxies = {"http": "40.76.53.46"}
    
    rsp = requests.get(url, proxies=proxies,stream=True)
    print rsp.raw._fp.fp._sock.getpeername()
    print rsp.content
    response = rsp.content
    return response'''


def mainlist(item):
    logger.info("pelisalacarta.bricocine mainlist")

    itemlist = []
    import xbmc
    ###Para musica(si hay) y borra customkeys
    if xbmc.Player().isPlaying():
       xbmc.executebuiltin('xbmc.PlayMedia(Stop)')
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    try:
        os.remove(KEYMAPDESTFILE)
        print "Custom Keyboard.xml borrado"
        os.remove(TESTPYDESTFILE)
        print "Testpy borrado"
        os.remove(REMOTEDESTFILE)
        print "Remote borrado"
        os.remove(APPCOMMANDDESTFILE)
        print "Appcommand borrado"
        xbmc.executebuiltin('Action(reloadkeymaps)')
    except Exception as inst:
        xbmc.executebuiltin('Action(reloadkeymaps)')
        print "No hay customs"
    
    itemlist.append( Item(channel=item.channel, title="[COLOR chartreuse][B]Series[/B][/COLOR]"         , action="scraper", url="http://www.verseriesonline.tv/series", thumbnail="http://s6.postimg.org/6hpa9tzgx/verseriesthumb.png", fanart="http://s6.postimg.org/71zpys3bl/verseriesfan2.jpg"))
    import xbmc
    if xbmc.Player().isPlaying():
       xbmc.executebuiltin('xbmc.PlayMedia(Stop)')
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    SEARCHDESTFILE= os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
    TRAILERDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "trailer.txt")
    try:
        os.remove(KEYMAPDESTFILE)
        print "Custom Keyboard.xml borrado"
        os.remove(TESTPYDESTFILE)
        print "Testpy borrado"
        os.remove(REMOTEDESTFILE)
        print "Remote borrado"
        os.remove(APPCOMMANDDESTFILE)
        print "Appcommand borrado"
        xbmc.executebuiltin('Action(reloadkeymaps)')
    except Exception as inst:
        xbmc.executebuiltin('Action(reloadkeymaps)')
        print "No hay customs"
    try:
        os.remove(SEARCHDESTFILE)
        print "Custom search.txt borrado"
    except:
        print "No hay search.txt"

    try:
        os.remove(TRAILERDESTFILE)
        print "Custom Trailer.txt borrado"
    except:
        print "No hay Trailer.txt"
    itemlist.append( Item(channel=item.channel, title="[COLOR chartreuse][B]Buscar[/B][/COLOR]"         , action="search", url="", thumbnail="http://s6.postimg.org/5gp1kpihd/verseriesbuscthumb.png", fanart="http://s6.postimg.org/7vgx54yq9/verseriesbuscfan.jpg", extra = "search"))
    

    return itemlist


def search(item,texto):
    logger.info("pelisalacarta.verseriesonlinetv search")
    texto = texto.replace(" ","+")
    item.url = "http://www.verseriesonline.tv/series?s=" + texto
   
    '''item.url = item.url.replace("+","-")
    data = dhe( scrapertools.cachePage(item.url) )
    
    if "<h1> <strong>Error 404</strong></h1>" in data:
        
        print "paaalmerin"
        import xbmc, time
        xbmc.executebuiltin( "XBMC.Action(back)" )
        xbmc.sleep(100)
        xbmc.executebuiltin('Notification([COLOR coral][B]Busqueda[/B][/COLOR], [COLOR green][B]'+'sin resultados'.upper()+'[/B][/COLOR],4000,"http://s6.postimg.org/j1bopgpu5/verserienobusqicon.png")')
    
    else:
        try:
           year = scrapertools.get_match(data,'<h1>.*?<span>\((.*?)\)</span></h1>')
           title_fan = scrapertools.get_match(data,'<h1>(.*?)<span>.*?</span></h1>').strip()
           item.title = title_fan
           trailer = title_fan + " " + year + " trailer"
           trailer = urllib.quote(trailer)
           item.title = item.title.replace(item.title,"[COLOR springgreen]"+item.title+"[/COLOR]")
           item.show = title_fan+"|"+year+"|"+trailer
        except:
           pass'''


    try:
        return scraper(item)
    # Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []


def scraper(item):
    logger.info("pelisalacarta.verseriesonlinetv scraper")
    itemlist = []
    ###Borra customkeys
    import xbmc
    if xbmc.Player().isPlaying():
       xbmc.executebuiltin('xbmc.PlayMedia(Stop)')
    
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    TRAILERDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "trailer.txt")
    try:
        os.remove(KEYMAPDESTFILE)
        print "Custom Keyboard.xml borrado"
        os.remove(TESTPYDESTFILE)
        print "Testpy borrado"
        os.remove(REMOTEDESTFILE)
        print "Remote borrado"
        os.remove(APPCOMMANDDESTFILE)
        print "App borrado"
        xbmc.executebuiltin('Action(reloadkeymaps)')
    except Exception as inst:
        xbmc.executebuiltin('Action(reloadkeymaps)')
        print "No hay customs"

    try:
        os.remove(TRAILERDESTFILE)
        print "Trailer.txt borrado"
    except:
        print "No hay Trailer.txt"

    # Descarga la página
    data = dhe( scrapertools.cachePage(item.url) )

    patron = '<li class="item">.*?<a class="poster" href="([^"]+)".*?<img src="([^"]+)" alt="([^<]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title_fan = scrapedtitle.strip()
        
        #Busqueda del año y puntuacion
        urlyear =scrapedurl
        data2 =  scrapertools.cachePage( scrapedurl )
        year= scrapertools.get_match(data2,'<h1>.*?<span>\((.*?)\)</span></h1>')
        points= scrapertools.get_match(data2,'<div class="number">.*?<b>(.*?)</b>')
        if points=="":
           points = "No puntuada"
        trailer = title_fan + " " + year + " trailer"
        trailer = urllib.quote(trailer)
        scrapedtitle = scrapedtitle + " ("+"[COLOR orange][B]"+points+"[/B][/COLOR]"+ ")"
        show = title_fan+"|"+year+"|"+trailer
                                       
        scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR springgreen]"+scrapedtitle+"[/COLOR]")
        itemlist.append( Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action= "fanart" , thumbnail=scrapedthumbnail, fanart="http://s6.postimg.org/8pyvdfh75/verseriesfan.jpg", show= show, plot= title_fan, folder=True) )

    
    ## Paginación
    #<span class='current'>1</span><a href='http://www.bricocine.com/c/hd-microhd/page/2/'
    
    # Si falla no muestra ">> Página siguiente"
    try:

        next_page = scrapertools.get_match(data,"<span class='current'>\d+</span><a class=\"page larger\" href=\"([^\"]+)\"")
        
        title= "[COLOR floralwhite]Pagina siguiente>>[/COLOR]"
        itemlist.append( Item(channel=item.channel, title=title, url=next_page, action="scraper", fanart="http://s6.postimg.org/8pyvdfh75/verseriesfan.jpg", thumbnail="http://virtualmarketingpro.com/app/webroot/img/vmp/arrows/Green%20Arrow%20(26).png", folder=True) )
    except: pass


    return itemlist



def fanart(item):
    #Vamos a sacar todos los fanarts y arts posibles
    logger.info("pelisalacarta.verseriesonlinetv fanart")
    itemlist = []
    url = item.url
    data = dhe( scrapertools.cachePage(item.url) )
    data = re.sub(r"\n|\r|\t|\s{2}|\(.*?\)|\[.*?\]|&nbsp;","",data)
    
    import xbmc
        
    SEARCHDESTFILE= os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    TRAILERDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "trailer.txt")
        
           
    title= item.show.split("|")[0].decode('utf8').encode('latin1')
    item.title = re.sub(r"\(.*?\)","",item.title)
    year = item.show.split("|")[1]
    trailer = item.show.split("|")[2]
    '''title = title.replace ("&","y")
    if "Contraataque" in title:
        title = "strike back"
    if title == "Hope":
        title = "Raising hope"
    if title == "Invisibles":
        title = "The whispers"
    if title == "La Batalla del Agua Pesada":
        title ="Kampen om tungtvannet"
    if title == "Familia de acogida":
        title ="the foster"
    if title == "Brotherhood":
        title =title+" "+"comedy"
    if title == "   ":
        title =title+" "+"2011"
    if title == "Las Palomas de Judea":
        title ="the dovekeepers"
    plot = title
    title= title.replace('á','a')
    title= title.replace('Á','A')
    title= title.replace('é','e')
    title= title.replace('í','i')
    title= title.replace('ó','o')
    title= title.replace('ú','u')
    title= title.replace('ñ','n')
    title_tunes = title_tunes.replace("&#39;","")'''
        
        
    title_tunes= (translate(title,"en"))
    ###Prepara customkeys
    import xbmc
    if not xbmc.Player().isPlaying() and not os.path.exists ( TRAILERDESTFILE ):
            
        TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
        KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
        REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
        APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
        try:
            os.remove(KEYMAPDESTFILE)
            print "Custom Keyboard.xml borrado"
            os.remove(TESTPYDESTFILE)
            print "Testpy borrado"
            os.remove(REMOTEDESTFILE)
            print "Remote borrado"
            os.remove(APPCOMMANDDESTFILE)
            print "Appcommand borrado"
            xbmc.executebuiltin('Action(reloadkeymaps)')
        except Exception as inst:
            xbmc.executebuiltin('Action(reloadkeymaps)')
            print "No hay customs"

            try:
                ###Busca música serie y caraga customkey. En la vuelta evita busqueda si ya suena música
                url_bing ="http://www.bing.com/search?q=%s+theme+song+site:televisiontunes.com" % title_tunes.replace(' ', '+')
                    #Llamamos al browser de mechanize. Se reitera en todas las busquedas bing
                data = browser (url_bing)
                '''if "z{a:1}"in data:
                    data = proxy(url_bing)'''
                try:
                    subdata_tvt = scrapertools.get_match(data,'<li class="b_algo">(.*?)h="ID')
                except:
                    pass
                try:
                    url_tvt = scrapertools.get_match(subdata_tvt,'<a href="(.*?)"')
                except:
                    url_tvt = ""
                        
                if "-theme-songs.html" in url_tvt:
                    url_tvt = ""
                if "http://m.televisiontunes" in url_tvt:
                    url_tvt= url_tvt.replace ("http://m.televisiontunes","http://televisiontunes")
                                                                        
                data = scrapertools.cachePage( url_tvt )
                song = scrapertools.get_match(data,'<form name="song_name_form">.*?type="hidden" value="(.*?)"')
                song = song.replace (" ","%20")
                print song
                xbmc.executebuiltin('xbmc.PlayMedia('+song+')')
                import xbmc, time
                TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
                urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/test.py", TESTPYDESTFILE )
                KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
        
                urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customkey.xml", KEYMAPDESTFILE )
                REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
                urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/remote.xml", REMOTEDESTFILE )
                APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
                urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customapp.xml", APPCOMMANDDESTFILE )
                
                xbmc.executebuiltin('Action(reloadkeymaps)')
              
            except:
                pass
    try:
        os.remove(TRAILERDESTFILE)
        print "Trailer.txt borrado"
    except:
        print "No hay Trailer.txt"
        
    if os.path.exists ( SEARCHDESTFILE ):
        try:
            os.remove(KEYMAPDESTFILE)
            print "Custom Keyboard.xml borrado"
            os.remove(TESTPYDESTFILE)
            print "Testpy borrado"
            os.remove(REMOTEDESTFILE)
            print "Remote borrado"
            os.remove(APPCOMMANDDESTFILE)
            print "Appcommand borrado"
            os.remove(SEARCHDESTFILE)
            print "search.txt borrado"
            xbmc.executebuiltin('Action(reloadkeymaps)')
        except Exception as inst:
            xbmc.executebuiltin('Action(reloadkeymaps)')
            print "No hay customs"

    #Busqueda bing de Imdb serie id
    url_imdb = "http://www.bing.com/search?q=%s+%s+tv+series+site:imdb.com" % (title.replace(' ', '+'),  year)
    print url_imdb
    data = browser (url_imdb)
    '''if "z{a:1}"in data:
       data = proxy(url_imdb)'''
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
    print matches
    if len(matches)== 0:
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
                    extra= "http://s6.postimg.org/nwekf82xd/verseriesinopsis5.png"
                    fanart_info = "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg"
                    fanart_trailer = "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg"
                    category= ""
                    show = title+"|"+year+"|"+"http://s6.postimg.org/xyor47sgh/verseriesnofan7.jpg"+"|"+trailer
                    itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="temporadas", thumbnail=item.thumbnail, fanart="http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg" ,extra=extra, category= category,  show=show ,plot=plot, folder=True) )
        
       else:
            title= title.replace(" ","%20")
            url_tvdb="http://thetvdb.com/api/GetSeries.php?seriesname=" + title + "&language=es"
            data = scrapertools.cachePage(url_tvdb)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
            patron = '<Data><Series><seriesid>([^<]+)</seriesid>.*?<Overview>(.*?)</Overview>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            if len(matches) == 0:
                plot = ""
                postertvdb = item.thumbnail
                extra= "http://s6.postimg.org/nwekf82xd/verseriesinopsis5.png"
                show = title+"|"+year+"|"+"http://s6.postimg.org/xyor47sgh/verseriesnofan7.jpg"+"|"+trailer
                fanart_info = "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg"
                fanart_trailer = "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg"
                category= ""
                itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="temporadas", thumbnail=item.thumbnail, fanart="http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg" ,extra=extra, category= category,  show=show ,plot= plot, folder=True) )

    #fanarts
        
    for id , info in matches:
        try:
          info = (translate(info,"es"))
        except:
          pass

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
            extra="http://s6.postimg.org/nwekf82xd/verseriesinopsis5.png"
            show = title+"|"+year+"|"+"http://s6.postimg.org/xyor47sgh/verseriesnofan7.jpg"
            fanart_info = "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg"
            fanart_trailer = "http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg"
            itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="temporadas", thumbnail=postertvdb, fanart="http://s6.postimg.org/qcbsfbvm9/verseriesnofan2.jpg"  ,category = category, extra=extra, show=show,folder=True) )

        for fan in matches:
            fanart="http://thetvdb.com/banners/" + fan
            fanart_1= fanart
            patron= '<Banners><Banner>.*?<BannerPath>.*?</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>.*?</Banner><Banner>.*?<BannerPath>(.*?)</BannerPath>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            if len(matches)==0:
                fanart_info= fanart_1
                fanart_trailer = fanaer_1
                fanart_2 = fanart_1
                show = title+"|"+year+"|"+fanart_1
                extra=postertvdb
                itemlist.append( Item(channel=item.channel, title=item.title, url=item.url, action="temporadas", thumbnail=postertvdb, fanart=item.extra  ,category = category, extra=extra, show=show,folder=True) )
            for fanart_info, fanart_trailer, fanart_2 in matches:
                fanart_info = "http://thetvdb.com/banners/" + fanart_info
                fanart_trailer = "http://thetvdb.com/banners/" + fanart_trailer
                fanart_2 = "http://thetvdb.com/banners/" + fanart_2
                        


        #Busqueda de todos loas arts posibles
        for id in matches:
            url_fanartv ="http://webservice.fanart.tv/v3/tv/"+id_serie+"?api_key=dffe90fba4d02c199ae7a9e71330c987"
            data = scrapertools.cachePage(url_fanartv)
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
                item.thumbnail = postertvdb
                if '"hdtvlogo"' in data:
                    if "showbackground" in data:
                            
                        if '"hdclearart"' in data:
                            thumbnail = hdtvlogo
                            extra=  hdtvclear
                            show = title+"|"+year+"|"+fanart_2+"|"+trailer
                        else:
                            thumbnail = hdtvlogo
                            extra= thumbnail
                            show = title+"|"+year+"|"+fanart_2+"|"+trailer
                        itemlist.append( Item(channel=item.channel, title = item.title , action="temporadas", url=item.url, server="torrent", thumbnail=thumbnail , fanart=fanart_1, category=category, extra=extra, show=show, folder=True) )
                        
                        
                    else:
                        if '"hdclearart"' in data:
                            thumbnail= hdtvlogo
                            extra= hdtvclear
                            show = title+"|"+year+"|"+fanart_2+"|"+trailer
                        else:
                            thumbnail= hdtvlogo
                            extra= thumbnail
                            show = title+"|"+year+"|"+fanart_2+"|"+trailer
                            
                        itemlist.append( Item(channel=item.channel, title = item.title , action="temporadas", url=item.url, thumbnail=thumbnail , fanart=fanart_1, extra=extra, show=show,  category= category, folder=True) )
                else:
                    extra=  "http://s6.postimg.org/nwekf82xd/verseriesinopsis5.png"
                    show = title+"|"+year+"|"+fanart_2+"|"+trailer
                    itemlist.append( Item(channel=item.channel, title = item.title , action="temporadas", url=item.url, server="torrent", thumbnail=item.thumbnail , fanart=fanart_1, extra=extra, show=show, category = category, folder=True) )
                                                
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
                        show = title+"|"+year+"|"+fanart_2+"|"+trailer
                        itemlist.append( Item(channel=item.channel, title = item.title , action="temporadas", url=item.url, server="torrent", thumbnail=thumbnail , fanart=fanart_1, extra=extra,show=show, category= category, folder=True) )
                    else:
                        extra= clear
                        show = title+"|"+year+"|"+fanart_2+"|"+trailer
                        itemlist.append( Item(channel=item.channel, title = item.title , action="temporadas", url=item.url, server="torrent", thumbnail=thumbnail , fanart=fanart_1, extra=extra,show=show, category= category, folder=True) )
                                                                                                                        
                if "showbackground" in data:
                    
                    if '"clearart"' in data:
                        clear=scrapertools.get_match(data,'"clearart":.*?"url": "([^"]+)"')
                        extra=clear
                        show = title+"|"+year+"|"+fanart_2+"|"+trailer
                    else:
                        extra=logo
                        show = title+"|"+year+"|"+fanart_2+"|"+trailer
                        itemlist.append( Item(channel=item.channel, title = item.title , action="temporadas", url=item.url, server="torrent", thumbnail=thumbnail , fanart=fanart_1, extra=extra,show=show,  category = category, folder=True) )
                                                                                                                                                            
                if not '"clearart"' in data and not '"showbackground"' in data:
                        if '"hdclearart"' in data:
                            extra= hdtvclear
                            show = title+"|"+year+"|"+fanart_2+"|"+trailer
                        else:
                            extra= thumbnail
                            show = title+"|"+year+"|"+fanart_2+"|"+trailer
                        itemlist.append( Item(channel=item.channel, title = item.title , action="temporadas", url=item.url, server="torrent", thumbnail=thumbnail , fanart=fanart_1, extra=extra,show=show , category = category, folder=True) )
    
    ####Info item. Se añade item.show.split("|")[0] and item.extra != "Series" para salvar el error de cuando una serie no está perfectamente tipificada como tal en Bricocine
    title ="Info"
    title = title.replace(title,"[COLOR seagreen]"+title+"[/COLOR]")
    
    
    if '"tvposter"' in data:
        thumbnail= tvposter
    else:
        thumbnail = postertvdb
        
    if "tvbanner" in data:
        category = tvbanner
    else:
        category = show.split("|")[2]


    itemlist.append( Item(channel=item.channel, action="info" , title=title , url=item.url, thumbnail=thumbnail, fanart=fanart_info, show= show, extra= extra, category= category,plot =plot, folder=False ))
    ####Trailer item
    title= "[COLOR greenyellow]Trailer[/COLOR]"
    
    if '"tvthumb"' in data:
        thumbnail = tvthumb
    else:
        thumbnail = postertvdb
    if '"tvbanner"' in data:
        extra= tvbanner
    elif '"tvthumb"' in data:
            extra = tvthumb
    else:
        extra = item.thumbnail

    itemlist.append( Item(channel=item.channel, action="trailer", title=title , url=item.url , thumbnail=thumbnail , fulltitle = item.title , fanart=fanart_trailer, extra=extra, show=trailer, folder=True) )
    return itemlist
def temporadas(item):
    logger.info("pelisalacarta.verseriesonlinetv temporadas")
    
    itemlist = []
    ###Ubicacion Customkey
    import xbmc
    SEARCHDESTFILE= os.path.join(xbmc.translatePath('special://userdata/keymaps'), "search.txt")
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
    REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    ###Carga Customkey en Finvideos cuando se trata de una busqueda
    if  xbmc.Player().isPlaying():
        if not os.path.exists ( TESTPYDESTFILE ):
           import xbmc
           urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/search.txt", SEARCHDESTFILE )
           urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/test.py", TESTPYDESTFILE )
           urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customkey.xml", KEYMAPDESTFILE )
           urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/remote.xml", REMOTEDESTFILE )
           urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customapp.xml", APPCOMMANDDESTFILE )
                                    
           xbmc.executebuiltin('Action(reloadkeymaps)')

    data = dhe( scrapertools.cachePage(item.url) )
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    ###Borra Customkey cuando no hay música
    import xbmc
    if not xbmc.Player().isPlaying():
        TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
        KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
        REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
        APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
        try:
            os.remove(KEYMAPDESTFILE)
            print "Custom Keyboard.xml borrado"
            os.remove(TESTPYDESTFILE)
            print "Testpy borrado"
            os.remove(REMOTEDESTFILE)
            print "Remote borrado"
            os.remove(APPCOMMANDDESTFILE)
            print "Appcommand borrado"
            xbmc.executebuiltin('Action(reloadkeymaps)')
        except Exception as inst:
            xbmc.executebuiltin('Action(reloadkeymaps)')
            print "No hay customs"
    if "Temporada 0" in data:
         bloque_temporadas = 'Temporada 0.*?(<h3 class="three fourths col-xs-12 pad0">.*?<div class="col-md-4 padl0">)'
         matchestemporadas = re.compile(bloque_temporadas,re.DOTALL).findall(data)
         
         for bloque_temporadas in matchestemporadas:
             patron = '<h3 class="three fourths col-xs-12 pad0">.*?href="([^"]+)" title="([^<]+)"'
             matches = re.compile(patron,re.DOTALL).findall(bloque_temporadas)

    else:
        patron = '<h3 class="three fourths col-xs-12 pad0">.*?href="([^"]+)" title="([^<]+)"'
        matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)==0 :
       itemlist.append( Item(channel=item.channel, title="[COLOR gold][B]No hay resultados...[/B][/COLOR]", thumbnail ="http://s6.postimg.org/fay99h9ox/briconoisethumb.png", fanart ="http://pic.raise5.com/user_pictures/user-1423992581-237429.jpg",folder=False) )
    for scrapedurl, scrapedtitle in matches:
        ###Busqueda poster temporada tmdb
        scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR springgreen]"+scrapedtitle+"[/COLOR]")
        temporada = scrapertools.get_match(scrapedtitle,'Temporada (\d+)')
        scrapedtitle = scrapedtitle.replace("Temporada","[COLOR darkorange]Temporada[/COLOR]")
        title = item.show.split("|")[0]
        year = item.show.split("|")[1]
        trailer = item.show.split("|")[3]
        
        if ":" in title:
            try:
                title = title.replace(" ","%20")
                url_tmdb="http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query="+ title+"&year="+year+"&language=es&include_adult=false"
                data = scrapertools.cachePage(url_tmdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                id_tmdb = scrapertools.get_match(data,'page":1.*?,"id":(.*?),"')
            except:
                try:
                    title= re.sub(r"(:.*)","",title)
                    title = title.replace(" ","%20")
                    url_tmdb="http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query="+ title+"&year="+year+"&language=es&include_adult=false"
                    data = scrapertools.cachePage(url_tmdb)
                    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                    id_tmdb = scrapertools.get_match(data,'page":1.*?,"id":(.*?),"')
                except:
                    thumbnail= item.thumbnail
                    fanart = item.fanart
                    id_tmdb =""
        else:
            try:
                title = title.replace(" ","%20")
                url_tmdb="http://api.themoviedb.org/3/search/tv?api_key=2e2160006592024ba87ccdf78c28f49f&query="+ title+"&year="+year+"&language=es&include_adult=false"
                data = scrapertools.cachePage(url_tmdb)
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
                id_tmdb = scrapertools.get_match(data,'page":1.*?,"id":(.*?),"')
            except:
                thumbnail= item.thumbnail
                fanart = item.fanart
                id_tmdb =""
        ###Teniendo (o no) el id Tmdb busca imagen
        urltmdb_images = "https://api.themoviedb.org/3/tv/"+id_tmdb+"?api_key=2e2160006592024ba87ccdf78c28f49f"
        data = scrapertools.cachePage(urltmdb_images)
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        try:
            backdrop=scrapertools.get_match(data,'"backdrop_path":"(.*?)"')
            fanart_3 = "https://image.tmdb.org/t/p/original" + backdrop
            fanart=fanart_3
        except:
            fanart_3= item.fanart
            fanart = fanart_3

        ###Busca poster de temporada Tmdb
        urltmdb_temp= "http://api.themoviedb.org/3/tv/"+id_tmdb+"/season/"+temporada+"/images?api_key=2e2160006592024ba87ccdf78c28f49f"
        data = scrapertools.cachePage( urltmdb_temp )
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        patron = '{"id".*?"file_path":"(.*?)","height"'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches) == 0:
            thumbnail= item.thumbnail
        for temp in matches:
            thumbnail= "https://image.tmdb.org/t/p/original"+ temp
        ####Busca el fanart para el item info####
        urltmdb_faninfo ="http://api.themoviedb.org/3/tv/"+id_tmdb+"/images?api_key=2e2160006592024ba87ccdf78c28f49f1"
        data = scrapertools.cachePage( urltmdb_faninfo )
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
        patron = '{"backdrops".*?"file_path":".*?","height".*?"file_path":"(.*?)",'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches) == 0:
            fanart = item.fanart
        for fanart_4 in matches:
            fanart= "https://image.tmdb.org/t/p/original" + fanart_4

        show = fanart_3+"|"+fanart+"|"+id_tmdb+"|"+temporada+"|"+trailer
        if "verseriesnofan7.jpg" in item.show.split("|")[2]:
            fanart = item.fanart
        else:
            fanart = item.show.split("|")[2]

        itemlist.append( Item(channel=item.channel, title=scrapedtitle, action="capitulos", url=scrapedurl, thumbnail =thumbnail, fanart =fanart,show = show, extra= item.extra,category = item.category, folder=True) )

    return itemlist

def capitulos(item):
    logger.info("pelisalacarta.verseriesonlinetv capitulos")
    itemlist = []
    ###Borra Customkey si no hay música
    import xbmc
    xbmc.executebuiltin('Action(reloadkeymaps)')
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    if not xbmc.Player().isPlaying() and os.path.exists ( TESTPYDESTFILE ):
        TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
        KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
        REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
        APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
        try:
            os.remove(KEYMAPDESTFILE)
            print "Custom Keyboard.xml borrado"
            os.remove(TESTPYDESTFILE)
            print "Testpy borrado"
            os.remove(REMOTEDESTFILE)
            print "Remote borrado"
            os.remove(APPCOMMANDDESTFILE)
            print "Appcommand borrado"
            xbmc.executebuiltin('Action(reloadkeymaps)')
        except Exception as inst:
            xbmc.executebuiltin('Action(reloadkeymaps)')
            print "No hay customs"
    
   
    data = dhe( scrapertools.cachePage(item.url) )
    patron = '<div class="item_episodio col-xs-3 ">.*?href="([^"]+)" title="([^<]+)".*?<img src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)==0 :
        itemlist.append( Item(channel=item.channel, title="[COLOR coral][B]"+"no hay capítulos...".upper()+"[/B][/COLOR]", thumbnail ="http://s6.postimg.org/wa269heq9/verseriesnohaythumb.png", fanart ="http://s6.postimg.org/4nzeosvdd/verseriesnothingfan.jpg",folder=False) )
    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = re.sub(r"(.*?Temporada \d+)","",scrapedtitle).strip()
        capitulo = re.sub(r"Capitulo","",scrapedtitle).strip()
        scrapedtitle = scrapedtitle.replace(scrapedtitle,"[COLOR limegreen]"+scrapedtitle+"[/COLOR]")
        extra =item.extra+"|"+capitulo
        
        itemlist.append( Item(channel=item.channel, title = scrapedtitle , action="findvideos", url=scrapedurl,  thumbnail=scrapedthumbnail, fanart=item.show.split("|")[0], show = item.show, extra= extra,category= item.category,folder=True) )
        title ="Info"
        title = title.replace(title,"[COLOR darkseagreen]"+title+"[/COLOR]")
        itemlist.append( Item(channel=item.channel, action="info_capitulos" , title=title , url=item.url, thumbnail=scrapedthumbnail, fanart=item.show.split("|")[0], extra = extra, show = item.show, category = item.category, folder=False ))
        


    return itemlist
def findvideos(item):
    logger.info("pelisalacarta.verseriesonlinetv findvideos")
    itemlist = []
    ###Borra Customkey si no hay música
    import xbmc
    xbmc.executebuiltin('Action(reloadkeymaps)')
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    if not xbmc.Player().isPlaying() and os.path.exists ( TESTPYDESTFILE ):
        TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
        KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customkey.xml")
        REMOTEDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remote.xml")
        APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
        try:
            os.remove(KEYMAPDESTFILE)
            print "Custom Keyboard.xml borrado"
            os.remove(TESTPYDESTFILE)
            print "Testpy borrado"
            os.remove(REMOTEDESTFILE)
            print "Remote borrado"
            os.remove(APPCOMMANDDESTFILE)
            print "Appcommand borrado"
            xbmc.executebuiltin('Action(reloadkeymaps)')
        except Exception as inst:
            xbmc.executebuiltin('Action(reloadkeymaps)')
            print "No hay customs"
    data = scrapertools.cachePage(item.url)
    
    patron = '<td><a href="([^"]+)".*?<img src="([^"]+)" title="([^<]+)" .*?<td>([^<]+)</td>.*?<td>([^<]+)</td>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    print matches
    for scrapedurl, scrapedthumbnail,scrapedserver,scrapedidioma,scrapedcalidad in matches:
        
        server = scrapertools.get_match(scrapedserver,'(.*?)[.]')
        icon_server = os.path.join( config.get_runtime_path() , "resources" , "images" , "servers" , "server_"+server+".png" )
        icon_server= re.sub(r"tv|com|net|","",icon_server)
        icon_server = icon_server.replace('streamin','streaminto')
        icon_server = icon_server.replace('ul','uploadedto')
        
        if not os.path.exists(icon_server):
            icon_server = scrapedthumbnail

        scrapedserver= scrapedserver.replace(scrapedserver,"[COLOR darkorange][B]"+"["+scrapedserver+"]"+"[/B][/COLOR]")
        scrapedidioma=scrapedidioma.replace(scrapedidioma,"[COLOR lawngreen][B]"+"--"+scrapedidioma+"--"+"[/B][/COLOR]")
        scrapedcalidad=scrapedcalidad.replace(scrapedcalidad,"[COLOR floralwhite][B]"+scrapedcalidad+"[/B][/COLOR]")
        
        title = scrapedserver + scrapedidioma+scrapedcalidad
        itemlist.append( Item(channel=item.channel, title = title , action="play", url=scrapedurl,  thumbnail=icon_server, fanart=item.show.split("|")[1], extra = item.thumbnail, folder=True) )
    

    
    return itemlist
def play(item):
    logger.info("pelisalacarta.verseriesonlinetv play")
    import xbmc
    xbmc.executebuiltin('Action(reloadkeymaps)')

    itemlist = servertools.find_video_items(data=item.url)
    
    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.thumbnail = item.extra
        videoitem.extra = item.extra
        videoitem.channel = item.channel

    return itemlist




def trailer(item):
    
    logger.info("pelisalacarta.verseriesonlinetv trailer")
    itemlist = []
    ###Crea archivo control trailer.txt para evitar la recarga de la música cuando se vuelve de trailer
    import xbmc
    xbmc.executebuiltin('Action(reloadkeymaps)')
    TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
    if os.path.exists ( TESTPYDESTFILE ):
        TRAILERDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "trailer.txt")
        urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/trailer.txt", TRAILERDESTFILE )
    youtube_trailer = "https://www.youtube.com/results?search_query=tv+show" + item.show + "español"
    
    data = scrapertools.cache_page(youtube_trailer)
    
    patron = '<a href="/watch?(.*?)".*?'
    patron += 'title="([^"]+)"'
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)==0 :
        itemlist.append( Item(channel=item.channel, title="[COLOR salmon][B]No hay Trailer[/B][/COLOR]", thumbnail ="http://s6.postimg.org/jp5jx97ip/bityoucancel.png", fanart ="http://s6.postimg.org/k2gzbpd5d/Movie_Trailer_poster.jpg",folder=False) )
    
    for scrapedurl, scrapedtitle in matches:
        
        scrapedurl = "https://www.youtube.com/watch"+scrapedurl
        scrapedtitle = scrapertools.decodeHtmlentities( scrapedtitle )
        scrapedtitle=scrapedtitle.replace(scrapedtitle,"[COLOR lightsalmon][B]"+scrapedtitle+"[/B][/COLOR]")
        itemlist.append( Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, server="youtube", fanart="http://s6.postimg.org/k2gzbpd5d/Movie_Trailer_poster.jpg", thumbnail=item.extra, action="play", folder=False) )
    return itemlist

def info(item):
    
    logger.info("pelisalacarta.verseriesonlinetv info")
    url=item.url
    data = dhe( scrapertools.cachePage(item.url) )
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    ###Se prepara el Customkey para no permitir el forcerefresh y evitar conflicto con info
    import xbmc
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    try:
        os.remove(APPCOMMANDDESTFILE)
    except:
        pass
    patron ='<div class="sinopsis">.*?</b>(.*?)</div>'
      
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)==0 :
        title = "[COLOR red][B]LO SENTIMOS...[/B][/COLOR]"
        plot = "Esta serie no tiene informacion..."
        plot = plot.replace(plot,"[COLOR yellow][B]"+plot+"[/B][/COLOR]")
        photo="http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
        foto ="http://s6.postimg.org/ub7pb76c1/noinfo.png"
        info =""
        quit = "Pulsa"+" [COLOR greenyellow][B]INTRO [/B][/COLOR]"+ "para quitar"
    for plot in matches:
        if plot == " . Aquí podrán encontrar la información de toda la serie incluyendo sus temporadas y episodios." :
             plot =item.plot
        plot_title = "Sinopsis" + "[CR]"
        plot_title = plot_title.replace(plot_title,"[COLOR chocolate]"+plot_title+"[/COLOR]")
        plot= plot_title + plot
        plot = plot.replace(plot,"[COLOR white][B]"+plot+"[/B][/COLOR]")
        plot = re.sub(r'div class=".*?">','',plot)
        plot = plot.replace("div>","")
        plot = plot.replace('div class="margin_20b">','')
        plot = plot.replace('div class="post-entry">','')
        plot = plot.replace('p style="text-align: left;">','')
        title = item.title
        title = title.replace(title,"[COLOR sandybrown][B]"+title+"[/B][/COLOR]")
          
        try:
            info = scrapertools.get_match(data,'<div id="informacion" class="tab-pane active">(.*?)<h2>Sinopsis</h2>')
            info= re.sub(r"<p><span class=.*?>|</span>|<a href=.*?>|</a>|,","",info)
            info = info.replace("<span class=\"ab\">"," : ")
            info = info.replace("</p>"," -")
        
        
        except IndexError :
            info = "No hay info extra..."


        infoformat = re.compile('(.*?:).*?-',re.DOTALL).findall(info)


        for head in infoformat:
            
            info= info.replace(head,"[COLOR green][B]"+head+"[/B][/COLOR]")
            info= info.replace(info,"[COLOR orange]"+info+"[/COLOR]")
            info = re.sub(r"-"," ",info)

        photo= item.extra
        foto = item.category
        quit = "Pulsa"+" [COLOR greenyellow][B]INTRO [/B][/COLOR]"+ "para quitar"
        ###Se carga Customkey no atras
        NOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "noback.xml")
        REMOTENOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remotenoback.xml")
        APPNOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "appnoback.xml")
        urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/noback.xml", NOBACKDESTFILE )
        urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/remotenoback.xml", REMOTENOBACKDESTFILE)
        urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/appnoback.xml", APPNOBACKDESTFILE )
        xbmc.executebuiltin('Action(reloadkeymaps)')
    


    ventana2 = TextBox1(title=title, plot=plot, info= info, thumbnail=photo, fanart=foto, quit= quit)
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
               xbmc.executebuiltin('Notification([COLOR red][B]Actualiza Kodi a su última versión[/B][/COLOR], [COLOR skyblue]para mejor info[/COLOR],8000,"https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/kodi-icon.png")')
            self.plot.setText(  self.getPlot )
            self.info.addLabel(self.getInfo)
            
        def get(self):
            
            self.show()
            
        def onAction(self, action):
            if action == ACTION_SELECT_ITEM or action == ACTION_GESTURE_SWIPE_LEFT:
               ###Se vuelven a cargar Customkey al salir de info
               import os, sys
               import xbmc
               APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
               NOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "noback.xml")
               REMOTENOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remotenoback.xml")
               APPNOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "appnoback.xml")
               TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
               try:
                   os.remove(NOBACKDESTFILE)
                   os.remove(REMOTENOBACKDESTFILE)
                   os.remove(APPNOBACKDESTFILE)
                   if os.path.exists ( TESTPYDESTFILE ):
                      urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customapp.xml", APPCOMMANDDESTFILE )
                   xbmc.executebuiltin('Action(reloadkeymaps)')
               except:
                  pass
               self.close()


def info_capitulos(item):

    logger.info("pelisalacarta.verseriesonlinetv trailer")
    import xbmc
    APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
    try:
       os.remove(APPCOMMANDDESTFILE)
    except:
       pass
    url= item.url
    data = dhe( scrapertools.cachePage(item.url) )
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    
    capitulo =item.extra.split("|")[1]
    temporada = item.show.split("|")[3]
    id_tvdb = item.category
    
    url="http://thetvdb.com/api/1D62F2F90030C444/series/"+item.category+"/default/"+temporada+"/"+capitulo+"/es.xml"
    data = scrapertools.cache_page(url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;","",data)
    patron = '<Data>.*?<EpisodeName>([^<]+)</EpisodeName>.*?'
    patron += '<Overview>(.*?)</Overview>.*?'
        
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)==0 :
        title = "[COLOR orange][B]LO SENTIMOS...[/B][/COLOR]"
        plot = "Este capitulo no tiene informacion..."
        plot = plot.replace(plot,"[COLOR yellow][B]"+plot+"[/B][/COLOR]")
        image="http://s6.postimg.org/ub7pb76c1/noinfo.png"
        foto="http://s6.postimg.org/nm3gk1xox/noinfosup2.png"
        quit = "Pulsa"+" [COLOR greenyellow][B]INTRO [/B][/COLOR]"+ "para quitar"
    else :


        for name_epi, info in matches:
            if "<filename>episodes" in data:
               foto = scrapertools.get_match(data,'<Data>.*?<filename>(.*?)</filename>')
               fanart = "http://thetvdb.com/banners/" + foto
            else:
                fanart=item.show.split("|")[1]
                if item.show.split("|")[1] == item.thumbnail:
                   fanart = "http://s6.postimg.org/4asrg755b/bricotvshows2.png"
            
            plot = info
            plot = (translate(plot,"es"))
            plot = plot.replace(plot,"[COLOR yellow][B]"+plot+"[/B][/COLOR]")
            title = name_epi.upper()
            title = title.replace(title,"[COLOR sandybrown][B]"+title+"[/B][/COLOR]")
            image=fanart
            foto= item.extra.split("|")[0]
            '''if not ".png" in item.show.split("|")[1] :
               foto ="http://s6.postimg.org/6flcihb69/brico1sinopsis.png"'''
            quit = "Pulsa"+" [COLOR greenyellow][B]INTRO [/B][/COLOR]"+ "para quitar"
            NOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "noback.xml")
            REMOTENOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remotenoback.xml")
            APPNOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "appnoback.xml")
            TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
            urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/noback.xml", NOBACKDESTFILE )
            urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/remotenoback.xml", REMOTENOBACKDESTFILE)
            urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/appnoback.xml", APPNOBACKDESTFILE )
            xbmc.executebuiltin('Action(reloadkeymaps)')
    ventana = TextBox2(title=title, plot=plot, thumbnail=image, fanart=foto, quit= quit)
    ventana.doModal()


ACTION_GESTURE_SWIPE_LEFT = 511
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
            self.quit = xbmcgui.ControlTextBox(145, 90, 1030, 45)
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
                print "Actualice a la ultima version de kodi para mejor info"
                import xbmc
                xbmc.executebuiltin('Notification([COLOR red][B]Actualiza Kodi a su última versión[/B][/COLOR], [COLOR skyblue]para mejor info[/COLOR],8000,"https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/kodi-icon.png")')
            self.plot.setText(  self.getPlot )
        
        def get(self):
            self.show()
        
        def onAction(self, action):
            if action == ACTION_SELECT_ITEM or action == ACTION_GESTURE_SWIPE_LEFT:
               import os, sys
               import xbmc
               APPCOMMANDDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "customapp.xml")
               NOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "noback.xml")
               REMOTENOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "remotenoback.xml")
               APPNOBACKDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "appnoback.xml")
               TESTPYDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "test.py")
               try:
                   os.remove(NOBACKDESTFILE)
                   os.remove(REMOTENOBACKDESTFILE)
                   os.remove(APPNOBACKDESTFILE)
                   if os.path.exists ( TESTPYDESTFILE ):
                      urllib.urlretrieve ("https://raw.githubusercontent.com/neno1978/script.palc.forcerefresh/master/Bricocine/customapp.xml", APPCOMMANDDESTFILE )
                   xbmc.executebuiltin('Action(reloadkeymaps)')
               except:
                   xbmc.executebuiltin('Action(reloadkeymaps)')
               self.close()


def translate(to_translate, to_langage="auto", langage="auto"):
    '''Return the translation using google translate
        you must shortcut the langage you define (French = fr, English = en, Spanish = es, etc...)
        if you don't define anything it will detect it or use english by default
        Example:
        print(translate("salut tu vas bien?", "en"))
        hello you alright?'''
    agents = {'User-Agent':"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
    before_trans = 'class="t0">'
    link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (to_langage, langage, to_translate.replace(" ", "+"))
    request = urllib2.Request(link, headers=agents)
    page = urllib2.urlopen(request).read()
    result = page[page.find(before_trans)+len(before_trans):]
    result = result.split("<")[0]
    return result

if __name__ == '__main__':
    to_translate = 'Hola como estas?'
    print("%s >> %s" % (to_translate, translate(to_translate)))
    print("%s >> %s" % (to_translate, translate(to_translate, 'fr')))
#should print Hola como estas >> Hello how are you
#and Hola como estas? >> Bonjour comment allez-vous?








