# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# MiTvSpain - XBMC Plugin
# Conector para Vimeo

# ------------------------------------------------------------

import re

from core import httptools
from core import logger
from core import scrapertools


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

	video_urls = []
	
    headers = [['User-Agent', 'Mozilla/5.0']]
    if "|" in page_url:
        page_url, referer = page_url.split("|", 1)
        headers.append(['Referer', referer])

    if not page_url.endswith("/config"):
    page_url = scrapertools.find_single_match(page_url, ".*?video/[0-9]+")

    data = httptools.downloadpage(page_url, headers = headers).data
    logger.info("Intel11 %s" %data)
    patron  = 'mime":"([^"]+)"'
    patron += '.*?url":"([^"]+)"'
    patron += '.*?quality":"([^"]+)"'
    match = scrapertools.find_multiple_matches(data, patron)
   for mime, media_url, calidad in match:
        title = "%s (%s) [vimeo]" % (mime.replace("video/", "."), calidad)
        video_urls.append([title, media_url, int(calidad.replace("p",""))])
    video_urls.sort(key=lambda x: x[2])
    
    for video_url in video_urls:
        video_url[2] = 0
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    referer = ""
    if "|" in text:
        referer = "|" + text.split("|", 1)[1]
    # http://player.vimeo.com/video/17555432?title=0&amp;byline=0&amp;portrait=0
    # http://vimeo.com/17555432
    patronvideos = '(?:vimeo.com/|player.vimeo.com/video/)([0-9]+)'
    logger.info("#" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for match in matches:
        titulo = "[vimeo]"
        url = "https://player.vimeo.com/video/%s/config%s" % (match, referer)
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'vimeo'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
