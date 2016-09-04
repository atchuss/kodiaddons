#!/usr/bin/env python
# -*- coding: utf-8 -*-

from resources.lib.modules.addon import Addon
from resources.lib.modules import control,client,webutils,convert
import re,sys,os,urlparse,xbmcgui,xbmcplugin

addon = Addon('plugin.video.laliga', sys.argv)
addon_handle = int(sys.argv[1])

if not os.path.exists(control.dataPath):
    os.mkdir(control.dataPath)

AddonPath = addon.get_path()
IconPath = os.path.join(AddonPath , "resources/media/")
fanart = os.path.join(AddonPath + "/fanart.jpg")

def icon_path(filename):
    if 'http://' in filename:
        return filename
    return os.path.join(IconPath, filename)

class info():
    def __init__(self):
        self.mode = 'laliga'
        self.name = 'La Liga'
        self.icon = icon_path('logo.png')
        self.ico2 = icon_path('atm.png')
        self.icsg = icon_path('log2.png')
        self.icpr = icon_path('premier.png')
        self.icit = icon_path('italia.png')
        self.ical = icon_path('bundes.png')
        self.icfr = icon_path('french.png')
        self.iccl = icon_path('ucl.png')
        self.icel = icon_path('uel.png')
        self.icop = icon_path('copa.png')
        self.icfw = icon_path('fwc.png')
        self.categorized = False
        self.paginated = False
        self.multilink = True

class main():
    def __init__(self):
        self.base = 'http://arenavision.in'
        self.headers = { "Cookie" : "beget=begetok; has_js=1;" }

    def links(self,url,tit):
        links = re.findall('(\d+.+?)\[(.+?)\]',url)
        links=self.__prepare_links(links,tit)
        return links

    def channels(self):
        
        result = client.request('http://arenavision.in/agenda', headers=self.headers)
        table = client.parseDOM(result,'table',attrs={'style':'width: 100%; float: left'})[0]
        rows = client.parseDOM(table,'tr')
        events = self.__prepare_events(rows)
        return events

    @staticmethod
    def convert_time(time,date):
        li = time.split(':')
        li2 = date.split('/')
        hour,minute = li[0],li[1]
        day,month,year = li2[0],li2[1],li2[2]
        import datetime
        from resources.lib.modules import pytzimp
        d = pytzimp.timezone(str(pytzimp.timezone('Europe/Ljubljana'))).localize(datetime.datetime(int(year), int(month), int(day), hour=int(hour), minute=int(minute)))
        timezona = control.setting('timezone_new')
        my_location = pytzimp.timezone(pytzimp.all_timezones[int(timezona)])
        convertido = d.astimezone(my_location)
        fmt = "%A, %d de %B de %Y"
        fm2 = "%H:%M"
        fch = convertido.strftime(fmt)
        hor = convertido.strftime(fm2)
        fch = fch.replace('January','Enero')
        fch = fch.replace('February','Febrero')
        fch = fch.replace('March','Marzo')
        fch = fch.replace('April','Abril')
        fch = fch.replace('May','Mayo')
        fch = fch.replace('June','Junio')
        fch = fch.replace('July','Julio')
        fch = fch.replace('August','Agosto')
        fch = fch.replace('September','Septiembre')
        fch = fch.replace('October','Octubre')
        fch = fch.replace('November','Noviembre')
        fch = fch.replace('December','Diciembre')
        fch = fch.replace('Monday','Lunes')
        fch = fch.replace('Tuesday','Martes')
        fch = fch.replace('Wednesday','Miércoles')
        fch = fch.replace('Thursday','Jueves')
        fch = fch.replace('Friday','Viernes')
        fch = fch.replace('Saturday','Sábado')
        fch = fch.replace('Sunday','Domingo')
        return hor,fch

    def __prepare_events(self,events):
        new = []
        events.pop(0)
        date_old = ''
        time = ''
        sport = ''
        competition = ''
        for event in events:
            items = client.parseDOM(event,'td')
            i = 0
            for item in items:

                if i==0:
                    date = item
                elif i==1:
                    time = item.replace('CET','').strip()
                elif i==2:
                    sport = item
                elif i==3:
                    competition = item
                elif i==4:
                    event = webutils.remove_tags(item)
                elif i==5:
                    url = item

                i += 1
            try:
                time, date = self.convert_time(time,date)
                sport = '%s - %s'%(sport,competition)
                event = re.sub('\s+',' ',event)
                title = '[COLOR orange](%s)[/COLOR] (%s) [B]%s[/B]'%(time,sport,convert.unescape(event))
                title2 = '[COLOR orange]%s[/COLOR]  [B]%s[/B]'%(time,convert.unescape(event))
                atm = 'ATLETICO MADRID'
                atmb = 'ATLETICO DE MADRID'
                lig = 'SPANISH LALIGA)'
                lg2 = 'SPANISH LALIGA2'
                prm = 'PREMIER LEAGUE'
                fra = 'FRENCH LIGUE1'
                ale = 'BUNDESLIGA'
                ita = 'ITALIA SERIE A'
                ucl = 'UEFA CHAMPIONS LEAGUE'
                uel = 'UEFA EUROPA LEAGUE'
                cop = 'COPA DEL REY'
                fwc = 'FIFA WORLD CUP'
                title2 = title2.replace(atm,atmb)
                primera = addon.get_setting('primera')
                segunda = addon.get_setting('segunda')
                premier = addon.get_setting('premier')
                francia = addon.get_setting('francia')
                italia = addon.get_setting('italia')
                alemania = addon.get_setting('alemania')
                champions = addon.get_setting('champions')
                eurleague = addon.get_setting('eurleague')
                copa = addon.get_setting('copa')
                fwcup = addon.get_setting('fwcup')
                if segunda=='false' and premier=='false' and francia=='false' and italia=='false' and alemania=='false' and champions=='false' and eurleague=='false' and copa=='false':
                    primera='true'
                if (title.find(atm)!=-1 or title.find(atmb)!=-1) and (primera=='true'):
                    if date != date_old:
                        date_old = date
                        new.append(('x','[COLOR yellow]%s[/COLOR]'%date, info().icon))
                    title = title.encode('utf-8')
                    title2 = title2.replace('[B]','[B][COLOR tomato]')
                    title2 = title2.replace('[/B]','[/COLOR][/B]')
                    new.append((url,title2, info().ico2))
                elif title.find(lig)!=-1 and primera=='true':
                    if date != date_old:
                        date_old = date
                        new.append(('x','[COLOR yellow]%s[/COLOR]'%date, info().icon))
                    title = title.encode('utf-8')
                    new.append((url,title2, info().icon))
                elif title.find(lg2)!=-1 and segunda=='true':
                    if date != date_old:
                        date_old = date
                        new.append(('x','[COLOR yellow]%s[/COLOR]'%date, info().icon))
                    title = title.encode('utf-8')
                    new.append((url,title2, info().icsg))
                elif title.find(prm)!=-1 and premier=='true':
                    if date != date_old:
                        date_old = date
                        new.append(('x','[COLOR yellow]%s[/COLOR]'%date, info().icon))
                    title = title.encode('utf-8')
                    new.append((url,title2, info().icpr))
                elif title.find(fra)!=-1 and francia=='true':
                    if date != date_old:
                        date_old = date
                        new.append(('x','[COLOR yellow]%s[/COLOR]'%date, info().icon))
                    title = title.encode('utf-8')
                    new.append((url,title2, info().icfr))
                elif title.find(ita)!=-1 and italia=='true':
                    if date != date_old:
                        date_old = date
                        new.append(('x','[COLOR yellow]%s[/COLOR]'%date, info().icon))
                    title = title.encode('utf-8')
                    new.append((url,title2, info().icit))
                elif title.find(ale)!=-1 and alemania=='true':
                    if date != date_old:
                        date_old = date
                        new.append(('x','[COLOR yellow]%s[/COLOR]'%date, info().icon))
                    title = title.encode('utf-8')
                    new.append((url,title2, info().ical))
                elif title.find(ucl)!=-1 and champions=='true':
                    if date != date_old:
                        date_old = date
                        new.append(('x','[COLOR yellow]%s[/COLOR]'%date, info().icon))
                    title = title.encode('utf-8')
                    new.append((url,title2, info().iccl))
                elif title.find(uel)!=-1 and eurleague=='true':
                    if date != date_old:
                        date_old = date
                        new.append(('x','[COLOR yellow]%s[/COLOR]'%date, info().icon))
                    title = title.encode('utf-8')
                    new.append((url,title2, info().icel))
                elif title.find(cop)!=-1 and copa=='true':
                    if date != date_old:
                        date_old = date
                        new.append(('x','[COLOR yellow]%s[/COLOR]'%date, info().icon))
                    title = title.encode('utf-8')
                    new.append((url,title2, info().icop))
                elif title.find(fwc)!=-1 and fwcup=='true':
                    if date != date_old:
                        date_old = date
                        new.append(('x','[COLOR yellow]%s[/COLOR]'%date, info().icon))
                    title = title.encode('utf-8')
                    if title2.find('SPAIN')!=-1:
                        title2 = title2.replace('SPAIN','[COLOR red]ES[COLOR yellow]PA[/COLOR]ÑA[/COLOR]'.decode('utf-8'))
                    new.append((url,title2, info().icfw))

            except:
                pass
        
        return new

    def __prepare_links(self,links,tit):
        new=[]
        spc=[]
        ace=[]
        tit = re.sub('\[.+?\]','',tit)
        ace.append(('x','[COLOR gold]' + tit[7:].replace('-',' [COLOR orange]vs[/COLOR] ') + '[/COLOR]'))
        for link in links:
            lang = link[1]
            urls = link[0].split('-')
            for u in urls:
                title = '[B]• AV%s[/B] [%s]'%(u.replace(' ',''),lang)
                #title = " ".join(title.split())
                url = 'http://arenavision.in/av' + u
                if title.find('AVS')==-1:
                    new.append((url,title))
                else:
                    spc.append((url,title))
        if new!=[]:
            ace.append(('x','[COLOR darkkhaki]AceStream[/COLOR]'))
        new = ace + new
        if spc!=[]:
            new.append(('x','[COLOR darkkhaki]Sopcast[/COLOR]'))
            new = new + spc
        return new

    def resolve(self,url):
        import liveresolver
        return liveresolver.resolve(url,cache_timeout=0)

    def doit(self):
        for event in self.channels():
            addon.add_item({'mode': 'get_p2p_event', 'url': event[0],'site':info().mode , 'title':event[1], 'img': event[2]}, {'title': event[1]}, img=event[2], fanart=fanart,is_folder=True)

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)

if mode is None:
    principal = main()
    principal.doit()
    addon.end_of_directory()

elif mode[0]=='get_p2p_event':
    url = args['url'][0]
    if url != 'x':
        title = args['title'][0]
        site = args['site'][0]
        img = args['img'][0]
        info = info()
        source = main()
        events = source.links(url,title)
        for event in events:
            addon.add_video_item({'mode': 'play_p2p', 'url': event[0],'title':title, 'img': img, 'site':site}, {'title': event[1]}, img=img, fanart=fanart)
        addon.end_of_directory()

elif mode[0] == 'play_p2p':
    url = args['url'][0]
    title = args['title'][0]
    img = args['img'][0]
    site = args['site'][0]
    source = main()
    resolved = source.resolve(url)
    li = xbmcgui.ListItem(title, path=resolved)
    li.setThumbnailImage(img)
    li.setLabel(title)
    handle = int(sys.argv[1])
    if handle > -1:
        xbmcplugin.endOfDirectory(handle, True, False, False)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)

