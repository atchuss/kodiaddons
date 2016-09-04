# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Pepecine
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import ast
import re
import sys
import urlparse

from core import config
from core import jsontools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

__url_base__ = "http://pepecine.com"
fanart_host = "https://d12.usercdn.com/i/02278/u875vjx9c0xs.png"


def mainlist(item):
    logger.info("[pepecine.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=item.channel, action="listado", title="Películas",
                          text_color="0xFFEB7600", text_blod=True, extra="movie", fanart=fanart_host,
                          url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=movie&offset=0&limit=30"),
                          thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/movies.png"))
    itemlist.append( Item(channel=item.channel, action="sub_filtrar", title="     Filtrar películas por género",
                          text_color="0xFFEB7600", extra="movie", fanart=fanart_host,
                          url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=movie&offset=0&limit=30"),
                          thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/movies_filtrar.png"))
    itemlist.append( Item(channel=item.channel, action="search", title="     Buscar películas por título",
                          text_color="0xFFEB7600", extra="movie", fanart=fanart_host,
                          url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=movie&offset=0&limit=30"),
                          thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/movies_buscar.png"))
    
    itemlist.append( Item(channel=item.channel, action="listado", title="Series",
                          text_color="0xFFEB7600", text_blod=True, extra="series", fanart=fanart_host,
                          url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=series&offset=0&limit=30"),
                          thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/tv.png"))
    itemlist.append( Item(channel=item.channel, action="sub_filtrar", title="     Filtrar series por género",
                          text_color="0xFFEB7600", extra="series", fanart=fanart_host,
                          url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=series&offset=0&limit=30"),
                          thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/tv_filtrar.png"))
    itemlist.append( Item(channel=item.channel, action="search", title="     Buscar series por título",
                          text_color="0xFFEB7600", extra="series", fanart=fanart_host,
                          url=urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=series&offset=0&limit=30"),
                          thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/tv_buscar.png"))
    itemlist.append( Item(channel=item.channel, action="listado", title="     Ultimos capítulos actualizados",
                          text_color="0xFFEB7600", extra="series_novedades", fanart=fanart_host,
                          url=urlparse.urljoin(__url_base__,"plugins/combined_json.php?&offset=0&limit=30&type=series"),
                          thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/channels/pepecine/tv.png"))
    
    #itemlist.append( Item( channel=item.channel, action="test", title="Test", url="http://pepecine.com/series-online/8763-breaking-bad/seasons/1/episodes/7", extra="series", fanart=fanart_host ) )
    return itemlist
 
def sub_filtrar(item):
    logger.info("[pepecine.py] sub_filtrar")
    itemlist=[]
    generos=("acción","animación","aventura","ciencia ficción","comedia","crimen",
             "documental","drama","familia","fantasía","guerra","historia","misterio",
             "música","musical","romance","terror","thriller","western")
    thumbnail=('https://d12.usercdn.com/i/02278/spvnq8hghtok.jpg',
               'https://d12.usercdn.com/i/02278/olhbpe7phjas.jpg',
               'https://d12.usercdn.com/i/02278/8xm23q2vewtt.jpg',
               'https://d12.usercdn.com/i/02278/o4vuvd7q4bau.jpg',
               'https://d12.usercdn.com/i/02278/v7xq7k9bj3dh.jpg',
               'https://d12.usercdn.com/i/02278/yo5uj9ff7jmg.jpg',
               'https://d12.usercdn.com/i/02278/ipeodwh6vw6t.jpg',
               'https://d12.usercdn.com/i/02278/0c0ra1wb11ro.jpg',
               'https://d12.usercdn.com/i/02278/zn85t6f2oxdv.jpg',
               'https://d12.usercdn.com/i/02278/ipk94gsdqzwa.jpg',
               'https://d12.usercdn.com/i/02278/z5hsi6fr4yri.jpg',
               'https://d12.usercdn.com/i/02278/nq0jvyp7vlb9.jpg',
               'https://d12.usercdn.com/i/02278/tkbe7p3rjmps.jpg',
               'https://d12.usercdn.com/i/02278/is60ge4zv1ve.jpg',
               'https://d12.usercdn.com/i/02278/86ubk310hgn8.jpg',
               'https://d12.usercdn.com/i/02278/ph1gfpgtljf7.jpg',
               'https://d12.usercdn.com/i/02278/bzp3t2edgorg.jpg',
               'https://d12.usercdn.com/i/02278/31i1xkd8m30b.jpg',
               'https://d12.usercdn.com/i/02278/af05ulgs20uf.jpg')

    for g, t in zip(generos,thumbnail):
        url=item.url + "&genre=" + g
        itemlist.append( Item(channel=item.channel, action="listado", text_color="0xFFEB7600",
                              title= g.capitalize(),url=url,extra=item.extra,thumbnail=t,fanart=fanart_host) )
   
    return itemlist 

def search(item,texto):
    logger.info("[pepecine.py] search:" + texto)
    item.url = item.url + "&query=" + texto
    try:
        return listado(item) 
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def newest(categoria):
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = urlparse.urljoin(__url_base__,"plugins/last_update_links.php?type=movie&offset=0&limit=30")
            item.extra = "movie"

        elif categoria == 'infantiles':
            item.url = urlparse.urljoin(__url_base__, "plugins/last_update_links.php?type=movie&offset=0&limit=30&genre=Animación")
            item.extra = "movie"

        elif categoria == 'series':
            item.url = urlparse.urljoin(__url_base__,"plugins/combined_json.php?&offset=0&limit=30&type=series")
            item.extra="series_novedades"

        else:
            return []

        itemlist = listado(item)
        if itemlist[-1].action == "listado":
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

def listado(item):
    #import json
    logger.info("[pepecine.py] listado")
    itemlist = []
    
    try:
        data_dict = jsontools.load_json(scrapertools.cache_page(item.url))
    except:
        return itemlist # Devolvemos lista vacia
        
    offset= scrapertools.get_match(item.url,'offset=(\d*)')
    limit= scrapertools.get_match(item.url,'limit=(\d*)')
       
    for i in data_dict["result"]:
        infoLabels={}
        idioma =''
        
        if item.extra=="movie":
            action="get_movie"
            title= i["title"] + ' (' + i['year'] + ')'
            url= urlparse.urljoin(__url_base__,"peliculas-online/" + str(i["id"])) #+"-"+i["title"]).lower().replace(" ","-")))
        elif item.extra=="series": 
            action="get_temporadas"
            title= i["title"]
            infoLabels['tvshowtitle']= i["title"]
            url= urlparse.urljoin(__url_base__,"series-online/" + str(i["id"])) #+"-"+i["title"]).lower().replace(" ","-")))
        else: #item.extra=="series_novedades": 
            action="get_only_episodio"
            infoLabels['season']=i['season']
            infoLabels['episode']=i['episode'].zfill(2)
            item.extra=infoLabels["season"] + "x" + infoLabels["episode"]
            infoLabels['tvshowtitle']= i["title"]
            flag= scrapertools.find_single_match(i["label"],'(\s*\<img src=.*\>)')
            idioma=i["label"].replace(flag,"")
            title=i["title"] + ' '  + item.extra + ' (' + idioma + ')'
            url= urlparse.urljoin(__url_base__,"series-online/" + str(i["id"])) #+"-"+i["title"]).lower().replace(" ","-"))) 
        
        if i.has_key("poster") and i["poster"]: 
            thumbnail=re.compile("/w\d{3}/").sub("/w500/",i["poster"])
        else:
            thumbnail= item.thumbnail
        if i.has_key("background") and i["background"]: 
            fanart= i["background"]
        else:
            fanart= item.fanart
        
        # Rellenamos el diccionario de infoLabels
        infoLabels['title_id']=i['id'] # title_id: identificador de la pelicula/serie en pepecine.com
        infoLabels['titleraw']= i["title"] # titleraw: titulo de la pelicula/serie sin formato
        if i['genre']: infoLabels['genre']=i['genre']
        if i['year']: infoLabels['year']=i['year']
        if i['tagline']: infoLabels['plotoutline']=i['tagline']
        if i['plot']: 
            infoLabels['plot']=i['plot']
        else:
            infoLabels['plot']=""
        if i['runtime']: infoLabels['duration']=int(i['runtime'])*60
        if i['imdb_rating']:
            infoLabels['rating']=i['imdb_rating']
        elif i['tmdb_rating']:
            infoLabels['rating']=i['tmdb_rating']


        newItem = Item(channel=item.channel, action=action, title=title, url=url, extra=item.extra,
                         fanart=fanart, thumbnail=thumbnail, viewmode="movie_with_plot",
                         language=idioma, text_color="0xFFFFCE9C", infoLabels=infoLabels)
        newItem.year=i['year']
        newItem.contentTitle=i['title']
        if 'season' in infoLabels and infoLabels['season']:
            newItem.contentSeason = infoLabels['season']
        if 'episode' in infoLabels and infoLabels['episode']:
            newItem.contentEpisodeNumber = infoLabels['episode']
        itemlist.append(newItem)
    
    # Paginacion
    if int(data_dict["total_results"]) == int(limit):
        url=item.url.replace('offset='+offset,'offset='+ str(int(offset)+ int(limit)))
        itemlist.append( Item( channel=item.channel, action="listado", text_color="0xFF994D00",
                               title=">> Pagina siguiente >>", thumbnail=item.thumbnail,
                               url=url, extra=item.extra, fanart=fanart_host) )
    
    return itemlist      
              
def get_movie(item):
    logger.info("[pepecine.py] get_movie")
    itemlist = []

    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))
    patron ='vars.title =(.*?)};'
    try:
        data_dict= jsontools.load_json(scrapertools.get_match(data,patron) +'}')
    except:
        return itemlist # Devolvemos lista vacia
    
    infoLabels=item.infoLabels
    if data_dict.has_key("actor"):
        cast=[]
        rol=[]
        for actor in data_dict["actor"]:
            cast.append(actor['name'])
            rol.append(actor['pivot']['char_name'])
        infoLabels['cast'] = cast
        infoLabels['castandrole'] = zip(cast,rol)
        
    if data_dict.has_key("writer"):
        writers_list=[]
        for writer in data_dict["writer"]:
            writers_list.append(writer['name'])
        infoLabels['writer'] = ", ".join(writers_list )
        
    if data_dict.has_key("director"):    
        director_list=[]
        for director in data_dict["director"]:
            director_list.append(director['name'])    
        infoLabels['director'] = ", ".join(director_list )
    

    item.infoLabels= infoLabels
    item.url=str(data_dict["link"])
    
    return findvideos (item)
    
def get_temporadas(item):
    logger.info("[pepecine.py] get_temporadas")
    itemlist = []
    infoLabels = {}
    
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))
    patron ='vars.title =(.*?)};'
    try:
        data_dict= jsontools.load_json(scrapertools.get_match(data,patron) +'}')
    except:
        return itemlist # Devolvemos lista vacia
    
    if item.extra == "serie_add":
        item.extra=str(data_dict['tmdb_id'])
        item.url=str(data_dict["link"])
        infoLabels['titleraw'] = data_dict["title"]
        infoLabels['tvshowtitle'] = data_dict["title"]
        infoLabels['title_id'] = data_dict['id']
        item.infoLabels = infoLabels
        itemlist= get_episodios(item)
    else:
        infoLabels = item.infoLabels
        if data_dict.has_key("actor"):
            cast=[]
            rol=[]
            for actor in data_dict["actor"]:
                cast.append(actor['name'])
                rol.append(actor['pivot']['char_name'])
            infoLabels['cast'] = cast
            infoLabels['castandrole'] = zip(cast,rol)
            
        if data_dict.has_key("writer"):    
            writers_list=[]
            for writer in data_dict["writer"]:
                writers_list.append(writer['name'])
            infoLabels['writer'] = ", ".join(writers_list )
        
        if data_dict.has_key("director"):  
            director_list=[]
            for director in data_dict["director"]:
                director_list.append(director['name'])    
            infoLabels['director'] = ", ".join(director_list )
    
        if len(data_dict["season"]) == 1: 
            # Si solo hay una temporada ...
            item.extra=str(data_dict['tmdb_id'])
            item.url=str(data_dict["link"])
            item.infoLabels = infoLabels
            itemlist= get_episodios(item)
        else: #... o si hay mas de una temporada y queremos el listado por temporada...
            item.extra=str(data_dict['tmdb_id'])
            data_dict["season"].sort(key=lambda x:(x['number'])) # ordenamos por numero de temporada
            for season in data_dict["season"]:
                url= filter(lambda l: l["season"]== season['number'],data_dict["link"]) #filtramos enlaces por temporada
                if url:
                    if season['overview']: infoLabels['plot']=season['overview']
                    if season['number']: infoLabels['season']=season['number']
                    if season["poster"]: item.thumbnail=re.compile("/w\d{3}/").sub("/w500/",season["poster"])
                    if season["release_date"]: infoLabels['premiered']= season['release_date']

                    item.infoLabels = infoLabels
                    title=item.title + ' ' + season["title"].lower().replace('season','temporada').capitalize()
                    
                    itemlist.append( Item( channel=item.channel, action="get_episodios", title=title, url=str(url),
                                           extra=item.extra, fanart=item.fanart, text_color="0xFFFFCE9C",
                                           thumbnail=item.thumbnail, viewmode="movie_with_plot",
                                           infoLabels=item.infoLabels) )
            
            if config.get_library_support() and itemlist:
                url= urlparse.urljoin(__url_base__,"series-online/" + str(data_dict['id']))
                itemlist.append( Item(channel=item.channel,
                                      title="Añadir esta serie a la biblioteca", url=url,
                                      action="add_serie_to_library", extra='episodios###serie_add',
                                      show= data_dict["title"], text_color="0xFFe5ffcc",
                                      thumbnail = 'https://d5.usercdn.com/dl/i/02360/a99fzwbqdaen.png'))

    return itemlist      

def get_only_episodio(item):
    logger.info("[pepecine.py] get_only_episodio")
    itemlist = []
    plot={}
    
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)","",scrapertools.cache_page(item.url))
    patron ='vars.title =(.*?)};'
    try:
        data_dict= jsontools.load_json(scrapertools.get_match(data,patron) +'}')
    except:
        return itemlist # Devolvemos lista vacia
        
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(id_Tmdb= data_dict['tmdb_id'],tipo="tv")
    except:
        pass

    infoLabels = item.infoLabels
    cast=[]
    rol=[]
    for actor in data_dict["actor"]:
        cast.append(actor['name'])
        rol.append(actor['pivot']['char_name'])
    
    writers_list=[]
    for writer in data_dict["writer"]:
        writers_list.append(writer['name'])
        
    director_list=[]
    for director in data_dict["director"]:
        director_list.append(director['name'])    
    
    infoLabels['cast'] = cast
    infoLabels['castandrole'] = zip(cast,rol)
    infoLabels['writer'] = ", ".join(writers_list )
    infoLabels['director'] = ", ".join(director_list )
    infoLabels['season'], infoLabels['episode']= item.extra.split('x')
    try:
        # añadimos sinopsis e imagenes del capitulo
        datos_tmdb=oTmdb.get_episodio(temporada= infoLabels['season'],capitulo= infoLabels['episode'])
        if datos_tmdb["episodio_sinopsis"] !="": infoLabels['plot']= datos_tmdb["episodio_sinopsis"]
        if datos_tmdb["episodio_imagen"] !="": item.thumbnail= datos_tmdb["episodio_imagen"]
        #if datos_tmdb["episodio_titulo"] !="": title = title + " [COLOR 0xFFFFE6CC]" + datos_tmdb["episodio_titulo"].replace('\t','') + "[/COLOR]"
    except:
            pass
    
    def cap(l): 
        try:
            temporada_link = int(l["season"])
            capitulo_link = int(l['episode'])
        except:
            return False
        return True if temporada_link== int(infoLabels['season'])  and capitulo_link == int(infoLabels['episode']) else False    
    item.url= str(filter(cap, data_dict["link"])) #filtramos enlaces por capitulo

    item.infoLabels = infoLabels
    item.extra=str(data_dict['tmdb_id'])
    
    return findvideos(item)

def get_episodios(item):
    logger.info("[pepecine.py] get_episodios")
    itemlist = []
    plot={}
    
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(id_Tmdb= item.extra,tipo="tv")
    except:
        pass

    infoLabels = item.infoLabels

    lista_links=ast.literal_eval(item.url) 
    # Agrupar enlaces por episodios  temXcap
    temXcap_dict={}
    for link in lista_links:
        title_id = link['title_id']
        try:
            season = str(int(link['season']))
            episode = str(int(link['episode'])).zfill(2)
        except:
            continue
        id= season + "x" + episode
        if temXcap_dict.has_key(id):
            l= temXcap_dict[id]
            l.append(link)
            temXcap_dict[id]= l
        else:
            temXcap_dict[id]= [link]
            
    # Ordenar lista de enlaces por temporada y capitulo
    temXcap_list=temXcap_dict.items()
    temXcap_list.sort(key=lambda x: (int(x[0].split("x")[0]),int(x[0].split("x")[1])))
    for episodio in temXcap_list:
        title= infoLabels['titleraw'] + ' (' + episodio[0] + ')'
        infoLabels['season'], infoLabels['episode']=  episodio[0].split('x')
        try:
            # añadimos sinopsis e imagenes para cada capitulo
            datos_tmdb=oTmdb.get_episodio(temporada= infoLabels['season'],capitulo= infoLabels['episode'])
            if datos_tmdb["episodio_sinopsis"] !="": infoLabels['plot']= datos_tmdb["episodio_sinopsis"]
            if datos_tmdb["episodio_imagen"] !="": item.thumbnail= datos_tmdb["episodio_imagen"]
            if datos_tmdb["episodio_titulo"] !="": title = title + " " + datos_tmdb["episodio_titulo"].replace('\t','')
        except:
                pass

        itemlist.append( Item( channel=item.channel, action="findvideos", title=title, url=str(episodio[1]),
                               extra=item.extra, show=infoLabels['tvshowtitle'], fanart=item.fanart,
                               infoLabels = infoLabels,
                               thumbnail=item.thumbnail, viewmode="movie_with_plot", text_color="0xFFFFCE9C") )
    
    if config.get_library_support() and itemlist:
        url= urlparse.urljoin(__url_base__,"series-online/" + str(title_id))
        #url= urlparse.urljoin(__url_base__,"series-online/" + (str(infoLabels['title_id']) +"-"+ infoLabels['titleraw']))
        itemlist.append( Item(channel=item.channel, title="Añadir esta serie a la biblioteca", url=url,
                              text_color="0xFFe5ffcc", action="add_serie_to_library", extra='episodios###serie_add',
                              show= infoLabels['tvshowtitle'],
                              thumbnail = 'https://d5.usercdn.com/dl/i/02360/a99fzwbqdaen.png'))

    
    return itemlist
       
def findvideos(item):
    logger.info("[pepecine.py] findvideos")
    itemlist = []
 
    
    for link in ast.literal_eval(item.url):
        url= link["url"]
        flag= scrapertools.find_single_match(link["label"],'(\s*\<img src=.*\>)')
        idioma=link["label"].replace(flag,"")
        calidad=(' [' +link["quality"]+ ']') if link["quality"] !="?" else ""
        video= find_videos(link["url"])
    
        if video["servidor"]!="":
            servidor=video["servidor"]
            url=video["url"]
            title= "Ver en " + servidor.capitalize() + calidad + ' (' + idioma + ')'
            itemlist.append( Item(channel=item.channel, action="play", viewmode="list", server=servidor, title=title,
                                  text_color="0xFF994D00",thumbnail=item.thumbnail, fanart= item.fanart,
                                  plot= item.plot, url=url, folder=False) )
            
    return itemlist
    
def find_videos(url):
    #logger.info("[pepecine.py] find_videos") 
    ret = {'titulo':"",
           'url':"",
           'servidor':""}
    
    # Ejecuta el find_videos en cada servidor hasta que encuentra una coicidencia
    lista_servers = servertools.get_servers_list()
    for serverid in lista_servers:
        try:
            servers_module = __import__("servers."+serverid)
            server_module = getattr(servers_module,serverid)
            devuelve= server_module.find_videos(url)
            
            if devuelve:
                ret["titulo"]=devuelve[0][0]
                ret["url"]=devuelve[0][1]
                ret["servidor"]=devuelve[0][2]
                # reordenar el listado, es probable q el proximo enlace sea del mismo servidor
                lista_servers.remove(serverid)
                lista_servers.insert(0,serverid)
                break
           
        except ImportError:
            logger.info("No existe conector para #"+serverid+"#")
            #import traceback
            #logger.info(traceback.format_exc())
        except:
            logger.info("Error en el conector #"+serverid+"#")
            import traceback
            logger.info(traceback.format_exc())
    
    return ret
    
    pass
    
def episodios(item):
    # Necesario para las actualizaciones automaticas
    return get_temporadas(Item(url=item.url, show=item.show, extra= "serie_add"))

