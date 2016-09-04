# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# ayuda - Videos de ayuda y tutoriales para pelisalacarta
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# contribuci?n de jurrabi
# ----------------------------------------------------------------------
import os

from channels import youtube_channel
from core import config
from core import logger
from core.item import Item
from platformcode import platformtools

if config.is_xbmc():
    import xbmc


def mainlist(item):
    logger.info("pelisalacarta.channels.ayuda mainlist")
    itemlist = []

    cuantos = 0

    if cuantos > 0:
        itemlist.append(Item(channel=item.channel,
                             action="tutoriales", title="Ver guías y tutoriales en vídeo"))
    else:
        itemlist.extend(tutoriales(item))

    itemlist.append(Item(channel=item.channel, action="", title="",
                         folder=False))

    if config.is_xbmc():
        #FIXME Al poner folder=False el log muestra: "WARNING: Attempt to use invalid handle -1"
        itemlist.append(Item(channel=item.channel,
                             action="force_creation_advancedsettings",
                             title="Crear fichero advancedsettings.xml optimizado", folder=True))
        cuantos += cuantos

    if config.is_xbmc():
        itemlist.append(Item(channel=item.channel,
                             action="recover_advancedsettings",
                             title="Restaurar advancedsettings.xml del backup", folder=False))
        cuantos += cuantos

    return itemlist


def tutoriales(item):
    playlists = youtube_channel.playlists(item, "tvalacarta")

    itemlist = []

    for playlist in playlists:
        if playlist.title == "Tutoriales de pelisalacarta":
            itemlist = youtube_channel.videos(playlist)

    return itemlist


def force_creation_advancedsettings(item):

    # Ruta del advancedsettings
    advancedsettings_kodi = xbmc.translatePath("special://userdata/advancedsettings.xml")
    advancedsettings_pelisalacarta = os.path.join(config.get_runtime_path(), "resources",
                                                  "advancedsettings.xml")
    fichero_backup = os.path.join(config.get_data_path(), "original_advancedsettings_backup.xml")

    # Archivos temporales para la modificacion de advancedsettings.xml:
    advancedsettings_same = os.path.join(config.get_data_path(), "same.txt")
    advancedsettings_trans = os.path.join(config.get_data_path(), "trans.txt")

    if os.path.exists(advancedsettings_kodi):
        logger.info("pelisalacarta.channels.ayuda La ruta de advanced settings del usuario existe!")

        if platformtools.dialog_yesno("pelisalacarta",
                                      "Esto modificara los ajustes avanzados de Kodi. ",
                                      "Deseas continuar?") == 1:

            # Backup del advancedsettings existente, antes de modificarlo.
            f_origen = open(advancedsettings_kodi)

            if not os.path.exists(fichero_backup):
                f_backup = open(fichero_backup, "w")
                
                for line in f_origen:
                    f_backup.write(line)
                
                f_backup.close()

            else:
                if platformtools.dialog_yesno("pelisalacarta",
                                              "Backup anterior encontrado. ",
                                              "Deseas sobreescribirlo?") == 1:
                    os.remove(fichero_backup)

                    f_backup = open(fichero_backup, "w")

                    for line in f_origen:
                        f_backup.write(line)

                    f_backup.close()

                    platformtools.dialog_notification("pelisalacarta",
                                                      "Backup terminado!")
                    logger.info("pelisalacarta.channels.ayuda Backup terminado!")
                else:
                    platformtools.dialog_notification("pelisalacarta",
                                                      "Backup no modificado")
                    logger.info("pelisalacarta.channels.ayuda Backup no modificado!")

            f_origen.close()

            # Edicion de advancedsettings.xml
            f_mod = open(os.path.join(advancedsettings_pelisalacarta))
            f_trans = open(os.path.join(advancedsettings_trans), "w")
            f_same = open(os.path.join(advancedsettings_same), "w")

            lines_seen = set()
            special_lines_seen = set()
            for line_mod in f_mod:
                
                f_orig = open(os.path.join(advancedsettings_kodi))

                if (line_mod.startswith(("<advancedsettings>",
                                         "</network>",
                                         "</advancedsettings>")) and line_mod
                        not in special_lines_seen):
                    f_same.write(line_mod)

                    if not line_mod.startswith("</network>"):
                        f_trans.write(line_mod)
                    
                    special_lines_seen.add(line_mod)

                for line_orig in f_orig:
                    if (line_orig.startswith(("<advancedsettings>",
                                              "</advancedsettings>")) and line_orig
                            not in special_lines_seen and line_orig not in
                            lines_seen):
                        lines_seen.add(line_orig)

                    if (line_orig == line_mod and line_orig not in lines_seen and
                            line_orig not in special_lines_seen):
                        line_same = line_orig
                        f_same.write(line_same)
                        lines_seen.add(line_orig)

                    if (not line_orig.startswith(("<autodetectpingtime>",
                                                  "<curlclienttimeout>",
                                                  "<curllowspeedtime>",
                                                  "<curlretries>",
                                                  "<disableipv6>",
                                                  "<cachemembuffersize>")) and
                            line_orig not in lines_seen and line_orig not in
                            special_lines_seen):

                        line_trans = line_orig

                        if line_orig.startswith("<network>"):
                            f_same.write(line_orig)
                        
                        f_trans.write(line_trans)
                        lines_seen.add(line_orig)

                f_orig.close()

            f_mod.close()
            f_trans.close()
            f_same.close()

            import filecmp
            if filecmp.cmp(advancedsettings_pelisalacarta, advancedsettings_same):
                platformtools.dialog_notification("pelisalacarta",
                                                  "advancessettings.xml estaba optimizado!")
            else:
                platformtools.dialog_notification("pelisalacarta",
                                                  "advancessettings.xml no estaba optimizado!")

            # Se vacia advancedsettings.xml
            open(os.path.join(advancedsettings_kodi)).close

            nospaces = False
            f_mod = open(os.path.join(advancedsettings_pelisalacarta))
            if filecmp.cmp(advancedsettings_pelisalacarta, advancedsettings_same):
                platformtools.dialog_ok("pelisalacarta",
                                        "advancessettings.xml estaba optimizado!",
                                        "(No sera editado)")
            else:
                platformtools.dialog_notification("pelisalacarta",
                                                  "modificando advancedsettings.xml...")
                f_trans = open(os.path.join(advancedsettings_trans))
                f_orig = open(os.path.join(advancedsettings_kodi), "w")

                for line_trans in f_trans:
                    if line_trans.startswith("<network>"):
                        for line_mod in f_mod:
                            if not line_mod.startswith(("<advancedsettings>",
                                                        "</network>",
                                                        "</advancedsettings>")):
                                f_orig.write(line_mod)
                    else:
                        if (line_trans.startswith("</advancedsettings>") or
                                nospaces):
                            line_trans = os.linesep.join([s for s in
                                                         line_trans.splitlines()
                                                         if s])
                            f_orig.write(line_trans)
                            nospaces = True
                        else:
                            f_orig.write(line_trans)

                if os.path.getsize(advancedsettings_same) == 0:
                    logger.info("UPSSS, ocurrio un error: same.txt esta vacio!")
                if os.path.getsize(advancedsettings_trans) == 0:
                    logger.info("UPSSS, ocurrio un error: trans.txt esta vacio!")
                    for line_mod in f_mod:
                        f_orig.write(line_mod)

                f_trans.close()
                f_orig.close()

                platformtools.dialog_ok("pelisalacarta",
                                        "Se ha modificado el fichero advancedsettings.xml",
                                        "con la configuración óptima para el streaming")
            f_mod.close()

            if os.path.exists(advancedsettings_same):
                logger.info("pelisalacarta.channels.ayuda Archivo de comparacion eliminado")
                os.remove(advancedsettings_same)
            if os.path.exists(advancedsettings_trans):
                logger.info("pelisalacarta.channels.ayuda Archivo de translacion eliminado")
                os.remove(advancedsettings_trans)
        else:
            platformtools.dialog_notification("pelisalacarta",
                                              "Operacion cancelada por el usuario")

    else:
        # Si no hay advancedsettings.xml se copia el advancedsettings.xml desde el directorio
        # resources al userdata.
        f_optimo = open(advancedsettings_pelisalacarta)
        f_original = open(advancedsettings_kodi, "w")

        for line in f_optimo:
            f_original.write(line)
        
        f_optimo.close()
        f_original.close()

        platformtools.dialog_ok("pelisalacarta",
                                "Se ha creado un fichero advancedsettings.xml",
                                "con la configuración óptima para streaming")

    logger.info("pelisalacarta.channels.ayuda 'force_creation_advancedsettings' method finnished")

    return []


def recover_advancedsettings(item):
    logger.info("pelisalacarta.channels.ayuda recover_advancedsettings")

    fichero_backup = os.path.join(config.get_data_path(),
                                  "original_advancedsettings_backup.xml")
    advancedsettings_kodi = xbmc.translatePath("special://userdata/advancedsettings.xml")

    if platformtools.dialog_yesno("pelisalacarta",
                                  "Deseas restaurar el backup de advancedsettings.xml?") == 1:
        if os.path.exists(fichero_backup):
            logger.info("pelisalacarta.channels.ayuda Existe un backup de advancedsettings.xml")
            
            f_backup = open(fichero_backup)
            f_original = open(advancedsettings_kodi, "w")
            
            for line in f_backup:
                f_original.write(line)
            
            f_backup.close()
            f_original.close()

            platformtools.dialog_ok("pelislacarta",
                                    "Backup restaurado correctamente")

        else:
            logger.info("pelisalacarta.channels.ayuda No hay ningun backup disponible")
            if platformtools.dialog_yesno("pelisalacarta",
                                          "No hay ningun backup disponible."
                                          "Deseas crearlo?") == 1:
                f_origen = open(advancedsettings_kodi)
                f_backup = open(fichero_backup, "w")

                for line in f_origen:
                    f_backup.write(line)

                f_origen.close()
                f_backup.close()

                platformtools.dialog_notification("pelisalacarta", "Backup hecho!")
                logger.info("pelisalacarta.channels.ayuda Backup terminado!")
            else:
                platformtools.dialog_notification("pelisalacarta", "Backup no hecho!")
                logger.info("pelisalacarta.channels.ayuda Backup no hecho!")

    else:
        platformtools.dialog_notification("pelisalacarta",
                                          "Operacion cancelada por el usuario")
        logger.info("pelisalacarta.channels.ayuda Optimizacion de adavancedsettings.xml cancelada!")

    return []
