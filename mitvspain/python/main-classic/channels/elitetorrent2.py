# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para elitetorrent2
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import os
import re
import sys
import urllib
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

HOST = 'http://www.elitetorrent2.net'

# LISTA PRINCIPAL #

def mainlist(item):
    
    logger.info()

    itemlist = []

    itemlist.append( Item(channel=item.channel, title="Novedades"    , action="novedades", url=HOST+"/pelicula/"))
    itemlist.append( Item(channel=item.channel, title="Año"    , action="year", url=HOST+"/lanzamiento/"))
    itemlist.append( Item(channel=item.channel, title="Buscar"    , action="search", url=HOST+"/?s="))
    
    return itemlist

# NOVEDADES #

def novedades(item):
    
    logger.info()

    itemlist = []

    data = httptools.downloadpage(item.url).data
    #data = scrapertools.cachePage(item.url)
    
    #**************************************
    
    # PATRON URL    
    patron = '<a href="(http://www.elitetorrent2.net/pelicula/[^"]+)">\w'
    # PATRON IMAGEN
    patron += '<img src="(.*?)"'
    # PATRON NOMBRE
    patron += '<h3>.*?>(.*?)</a>'
    # PATRON YEAR
    patron += '<span>(\d{4})</span>'
    
    #**************************************

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapurl, scrapimage, scraptitle, scrapyear in matches:
	url = urlparse.urljoin(HOST, scrapurl)
	image = urlparse.urljoin(HOST, scrapimage)
	title = scraptitle.strip()
	year = scrapyear
        itemlist.append( Item(channel=item.channel, action="pelicula", title=title, url=url, thumbnail=image, year=year, folder=False, viewmode="movie_with_plot") )    
'''
    # Extrae el paginador
    patron_next  = '<a class="arrow_pag" href="([^"]+)"><i class="icon-caret-right">'
    matches = re.compile(patron_next,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=item.channel, action="pelicula", title="Página siguiente >>" , url=scrapedurl , folder=True, viewmode="movie_with_plot") )

    return itemlist'''

# BUSQUEDA #

def year(item):
    
    logger.info()

    itemlist = []

    data = scrapertools.cachePage(item.url)

    # PATRON YEAR #
    patron = '>(\d{4})</a>'
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        itemlist.append( Item(channel=item.channel, action="pelicula", title=match, folder=True) )

    return itemlist

def search(item, texto):

    logger.info()
    texto = texto.replace(" ", "+")

    item.url = "http://www.elitetorrent2.net/?s=" + texto

    try:
        return getsearchlist(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
    return []

def getsearchlist(item):
    
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    # PATRON URL
    patron = '<div class="title"> <a href="(.*?)">'

    # PATRON IMAGE 
    patron = '<img src="(.*?)"'

    # PATRON NAME
    patron = 'alt="(.*?)"'

    # PATRON DESCRIPTION    
    patron += '<p>([^>]+)</p>'

    matches = scrapertools.find_multiple_matches(data, patron)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        title = scrapertools.remove_htmltags(scrapedtitle).decode('iso-8859-1').encode('utf8') + ' ' + scrapedinfo.decode('iso-8859-1').encode('utf8')
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url, urllib.quote(scrapedthumbnail))
        plot = scrapedplot
        logger.debug("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=item.channel, action="pelicula", title=title , url=url , thumbnail=thumbnail , plot=plot , folder=False, extra=extra) )

def pelicula(item):
    
    logger.info()
    itemlist = []

    # Descarga la página

    data = httptools.downloadpage(item.url).data
    #data = scrapertools.cachePage(item.url)

    # PATRON IMAGE
    patron =  '<div class="poster"> <img src="(.*?)"'
    # PATRON TITLE
    patron = 'alt="(.*?)">'
    # PATRON DESCRIPTION    
    patron += '<p>([^>]+)</p>'
    # PATRON YEAR
    patron += 'date">(.*?)<'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedthumbnail, scrapedtitle, scrapedplot, scrapedyear in matches:
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(HOST, scrapedthumbnail)
        plot = scrapedplot
        year = scrapedyear

        itemlist.append( Item(channel=item.channel, action="play", title=title , thumbnail=thumbnail , plot=plot , year=year,  folder=False) )

    return itemlist

def play(item):

    logger.info()

    itemlist = []

    data = scrapertools.cachePage(item.url)
    patron = '<a href="(.*?/links/.*?/)"'

# Scraped torrent
    url = scrapertools.find_single_match(data,patron)
    if url!="":
        itemlist.append( Item(channel=item.channel, action="play", server="torrent", title="[torrent]", folder=False) )

    return itemlist
