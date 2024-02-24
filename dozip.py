# -*- coding: utf-8 -*-
import zlib,os,dropbox,sys
import sqlite3,base64
from shutil import copyfile

def encode(string):
   #key = 'sYti87g4Ut0_z'   # --> el bueno
    key = 'sYzi87g4Ut0-z'  #micine
    encoded_chars = []
    for i in xrange(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return base64.urlsafe_b64encode(encoded_string)

path = os.path.dirname(os.path.abspath(__file__))

print('1. Aumenta el número de versión'.decode('utf-8'))

conn = sqlite3.connect("%s/base.db" %path)
cur = conn.cursor()
cur.execute("Select version from version")
vrs = cur.fetchone()
vrs = vrs[0] + 1
#cur.execute("select faffid from pelis group by faffid having faffid>0;")
cur.execute("select faffid from pelis where faffid>0 group by faffid;")
rows = cur.fetchall()
cnt = len(rows)
cur.execute("select faffid from pelis where faffid<0;")
rows = cur.fetchall()
cnt += len(rows)
print '   -- Version %s --' %(str(vrs))
cur.execute("update version set version=?", (vrs,))
conn.commit()
import datetime
anno = datetime.datetime.now().year
#cur.execute("SELECT faffid FROM pelis where anno>=? group by faffid having repe=0 order by min(id) DESC LIMIT(100);", (anno-1,))
cur.execute("SELECT faffid FROM pelis where anno>=? group by faffid order by min(id) DESC LIMIT(100);", (anno-1,))
orden1 = cur.fetchall()
#cur.execute("SELECT faffid FROM pelis where anno<? group by faffid having repe=0 order by min(id) DESC LIMIT(100);", (anno-1,))
cur.execute("SELECT faffid FROM pelis where anno<? group by faffid order by min(id) DESC LIMIT(100);", (anno-1,))
orden2 = cur.fetchall()
conn.close()

#sys.exit(0)

print('2. Crea el archivo de versión'.decode('utf-8'))

f = open('%s/base.max' %path, 'w+')
f.write(str(vrs))
f.close()

print('3. Borra base temporal si existe')

try:
    os.remove("%s/basetmp.db" %path)
except:
    pass

print('4. Copia la base a una temporal')

copyfile("%s/base.db" %path, "%s/basetmp.db" %path)

conn = sqlite3.connect("%s/basetmp.db" %path)
conn.text_factory = str
cur = conn.cursor()

print('5. Pone pelis más vistas'.decode('utf-8'))
cur.execute('CREATE INDEX faffid_idx ON pelis (faffid);')
cur.execute("select faffid,sum(vta) from pelis group by faffid order by sum(vta) DESC;")
rows = cur.fetchall()
cur.execute("update pelis set vta=0 where id>0;")
dmax=0
for row in rows:
    faf=row[0]
    num=row[1]
    cur.execute("update pelis set vta=? where faffid=?;", (num,faf))
    conn.commit()
    dmax+=1
    if dmax==100:
        break
cur.execute('DROP INDEX faffid_idx;')

print('6. Borra de la base temporal las pelis repetidas')

cur.execute('pragma foreign_keys = ON;')
cur.execute("update pelis set HD='' where HD is null;")
cur.execute("update pelis set img2=img1 where (img2 is null) and (img1<>'*');")

if 'sc' == 'zz':
    #-------------------------------
    cur.execute("Delete from pelis where server='1f' or server='zz' or server='cp' or cole='19889' or cole='20003' or user='trivianita';")
    cur.execute("Delete from pelis where server='dk' and (gb=28 or gb=33 or gb=68);")
    cur.execute("Delete from pelis where (peli is null) or (peli='');")
    conn.commit()
    # Cambiar sc por dk
    cur.execute("select faffid from pelis where HD='' group by faffid having count(faffid)>1;")
    rows = cur.fetchall()
    for row in rows:
        faf = row[0]
        cur.execute("select id from pelis where faffid=? and server='sc' and repe=0 and HD='';", (faf,))
        rw1 = cur.fetchone()
        if rw1:
            id1 = rw1[0]
            cur.execute("select id,user,cole,peli from pelis where faffid=? and server='dk' and HD='';", (faf,))
            rw2 = cur.fetchone()
            if rw2:
                id2 = rw2[0]
                user = rw2[1]
                cole = rw2[2]
                peli = rw2[3]
                cur.execute("update pelis set server='zz' where id=?;", (id2,))
                cur.execute("update pelis set server='dk',user=?,cole=?,peli=? where id=?;", (user,cole,peli,id1,))
                conn.commit()

#Mientra no funcione StreamCloud
#cur.execute("Delete from pelis where server='sc' and HD='' and length(peli)<>16;")
#-------------------------------

# Streamcloud caído
cur.execute("Delete from pelis where (url is null) or (url='');")

# Mientras siga caído Diskokosmiko
cur.execute("Delete from pelis where server='dk' and url is null;")
cur.execute("Delete from pelis where server='kb' and url is null;")
cur.execute("Delete from pelis where repe=1 or server='1f' or server='zz' or server='cp' or cole='19889' or cole='20003' or user='trivianita';")
cur.execute("Delete from pelis where user='BORRADA' and url is null;")
cur.execute("Delete from pelis where server='dk' and (gb=28 or gb=33 or gb=68) and url is null;")
cur.execute("Delete from pelis where ((peli is null) or (peli='')) and url is null;")
cur.execute("update pelis set img1=null where img1='-';")
cur.execute("update pelis set pais='EEUU' where pais='Estados Unidos';")
cur.execute("update pelis set CS=null;")

# Cierre del addon
# cur.execute("Delete from pelact;")
# cur.execute("Delete from pelgen;")
# cur.execute("Delete from pelgru;")
# cur.execute("Delete from peltem;")
# cur.execute("update pelis set nombre='*** No disponible ***',sinopsis=null,anno=null,director=null,pais=null,img1=null,img2=null;")
# cur.execute("update version set pdata=null,ubi=null;")

conn.commit()

# cur.execute("select faffid from pelis where faffid>0 group by faffid;")
# rows = cur.fetchall()
# cnt = len(rows)
# cur.execute("select faffid from pelis where faffid<0;")
# rows = cur.fetchall()
# cnt += len(rows)

cur.execute("select faffid from pelis group by faffid;")
rows = cur.fetchall()
cnt = len(rows)
tot = '   -- %s películas --' %cnt
print(tot.decode('utf-8'))

print('7. Crea y rellena la tabla de Series')
cur.execute("create table 'Series' ('id' INTEGER PRIMARY KEY, 'lista' TEXT);")
lds = ''
for p, d, f in os.walk('M:/Series'):
    d.sort()
    f.sort()
    for file in f:
        file2 = file.lower()
        if (file2.endswith('.mkv') or file2.endswith('.mp4') or file2.endswith('.avi')):
            url = os.path.join(p, file)
            url = url.replace('/','\\')
            lds += url.decode('cp1252') + '\n'
lds = lds.replace('-B.mkv','',)
cur.execute("INSERT INTO Series(id,lista) VALUES (?,?);", (1,lds))
conn.commit()

print('8. Pone orden de entrada')
cur.execute('update pelis set pais="EEUU" where (pais is null) or (pais="");')
cur.execute('update pelis set repe=1;')
cur.execute('update pelis set repe=0 where pais="España";')
cur.execute("update pelis set gb=null;")
conn.commit()
num=0
for row in orden1:
    faf = row[0]
    num+=1
    cur.execute("update pelis set gb=? where faffid=?;", (num,faf))
conn.commit()
for row in orden2:
    faf = row[0]
    num+=1
    cur.execute("update pelis set gb=? where faffid=?;", (num,faf))
conn.commit()
#cur.execute('ALTER TABLE pelis ADD COLUMN gb2 integer default 0;')
#cur.execute("SELECT faffid FROM pelis where (HD='S' or HD='3D') group by faffid order by min(id) DESC LIMIT(100);")
#orden3 = cur.fetchall()
#num=0
#for row in orden3:
#    faf = row[0]
#    num+=1
#    cur.execute("update pelis set gb2=? where (HD='S' or HD='3D') and faffid=?;", (num,faf))
#conn.commit()

print('9. Pasa los usuarios y enlaces a base64')
cur.execute("update pelis set user=null where user='';")
cur.execute("update pelis set cole=null where cole='';")
conn.commit()
cur.execute("select id,peli,user,cole from pelis;")
rows = cur.fetchall()
for row in rows:
    pid=row[0]
    pel=row[1]
    if (pel == None) or (pel == ''):
        pel="0"
    pel=encode(pel)
    usr=row[2]
    cole=row[3]
    if cole == None:
        from random import randint
        cole = randint(1234,8765)
    if (usr == None) or (usr == ''):
        usr = 'Alahuaje'
    cole=encode(str(cole))
    usr=encode(usr)
    cur.execute("update pelis set peli=?,user=?,cole=? where id=?;", (pel,usr,cole,pid))

conn.commit()
conn.close()

print('10. Compacta la base de datos temporal')

conn = sqlite3.connect("%s/basetmp.db" %path)
conn.execute("VACUUM")
conn.close()

print('11. Comprime la base de datos')

f = open('%s/basetmp.db' %path,'rb')
data = f.read()
f.close()
l1 = len(data)
data = zlib.compress(data,9)
l2 = len(data)
print '   - %s - %s' %(l1,l2)
f = open('%s/bass.cmp' %path,'wb')
f.write(data)
f.close()

a=raw_input("Pressione ENTER para salir")

