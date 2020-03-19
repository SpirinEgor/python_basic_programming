import sqlite3
import re
from types import SimpleNamespace

base_url = 'https://fanfox.net'
volume_re = re.compile(r'v(\d)+')
chapter_re = re.compile(r'c(\d)+')

def get_links(data):
    catalog_url = base_url + '/directory/?news'

    data.driver.get(catalog_url)

    pager = data.driver.find_element_by_class_name('pager-list-left')
    pages = pager.find_elements_by_tag_name('a')
    last_page = int(pages[-2].text)

    for i in range(1, last_page + 1):
        page_link = '/directory/' + str(i) + '.html?news'
        data.driver.get(base_url + page_link)
        manga_list = data.driver.find_element_by_class_name('manga-list-1-list')

        def build_info(elem):
            a = elem.find_element_by_tag_name('a')

            info = SimpleNamespace()

            info.title = a.get_attribute('title')
            info.link = a.get_attribute('href')
            info.cover = a.find_element_by_tag_name('img').get_attribute('src')

            return info

        elems = list(map(build_info, manga_list.find_elements_by_tag_name('li')))

        for info in elems:
            yield info

def get_chapters(page):
    try:
        checkAdult = page.find_element_by_id('checkAdult')
        checkAdult.click()
    except:
        pass

    try:
        expand = page.find_element_by_class_name('line-list-morebt')
        expand.click()
    except:
        pass

    chapters_list = page.find_element_by_id('chapterlist').find_element_by_tag_name('ul')
    chapters = []

    for chapter in chapters_list.find_elements_by_tag_name('a'):
        ch_info = SimpleNamespace()

        ch_info.link = chapter.get_attribute('href')
        vol = volume_re.search(ch_info.link)
        if vol is not None:
            ch_info.volume = int(vol.group(0)[1:])
        else:
            ch_info.volume = 0
        ch_info.chapter = int(chapter_re.search(ch_info.link).group(0)[1:])

        chapters.append(ch_info)

    return chapters


def collector():
    collector = SimpleNamespace()
    collector.base_url = base_url
    collector.get_links = get_links
    collector.get_chapters = get_chapters
    return collector
