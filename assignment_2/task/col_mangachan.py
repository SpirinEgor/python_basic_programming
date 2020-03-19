import re
from types import SimpleNamespace

base_url = 'https://manga-chan.me/'
title_re = re.compile(r'\(')
volume_re = re.compile(r'v(\d)+')
chapter_re = re.compile(r'- (\d)+(.(\d)+)?')

def get_links(data):
    catalog_url = base_url + '/mostfavorites?offset='
    offset = 0
    links_cnt = 1

    while links_cnt > 0:
        links_cnt = 0
        data.driver.get(catalog_url + str(offset))

        def build_info(elem):
            info = SimpleNamespace()

            title_link = elem.find_element_by_class_name('title_link')

            info.title = title_re.split(title_link.text)[0][:-1]
            info.link  = title_link.get_attribute('href')
            info.cover = elem.find_element_by_tag_name('img').get_attribute('src')

            return info

        elems = list(map(build_info, data.driver.find_elements_by_class_name('content_row')))

        links_cnt = len(elems)
        offset += links_cnt

        for info in elems:
            yield info

def get_chapters(page):
    chapters = []

    zaliv = page.find_elements_by_class_name('zaliv')
    no_zaliv = page.find_elements_by_class_name('no_zaliv')

    for chapter in zaliv + no_zaliv:
        ch_info = SimpleNamespace()

        link_elem = chapter.find_element_by_class_name('manga2').find_element_by_tag_name('a')

        ch_info.link = link_elem.get_attribute('href')
        text = link_elem.get_attribute('innerHTML')
        ch_info.volume = int(volume_re.search(text).group(0)[1:])
        ch_info.chapter = chapter_re.search(text).group(0)[2:]

        chapters.append(ch_info)

    return chapters

def collector():
    collector = SimpleNamespace()
    collector.base_url = base_url
    collector.get_links = get_links
    collector.get_chapters = get_chapters
    return collector
