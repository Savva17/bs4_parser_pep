import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_DOC_URL
from exceptions import ParserFindTagException
from outputs import control_output
from utils import create_object_bs4, find_tag, get_response


def whats_new(session):

    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = create_object_bs4(session, whats_new_url)
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag.get('href')
        version_link = urljoin(whats_new_url, href)
        response = session.get(version_link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (
                version_link,
                h1.text,
                dl_text
            )
        )

    return results


def latest_versions(session):

    soup = create_object_bs4(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'menu-wrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException('Не найден список c версиями Python')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )

    return results


def download(session):

    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = create_object_bs4(session, downloads_url)
    table = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(table, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    href = pdf_a4_tag.get('href')
    full_link = urljoin(downloads_url, href)
    filename = full_link.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(full_link)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep_links(category):

    total = 0
    results = []
    for table in category.find_all('table'):
        for rows in table.find_all('tr')[1:]:
            a_href = find_tag(rows, 'a')
            if a_href:
                href = a_href.get('href')
                full_url = urljoin(PEP_DOC_URL, href)
                results.append(full_url)
                total += 1

    return results, total


def pep(session):

    soup = create_object_bs4(session, PEP_DOC_URL)
    category = find_tag(soup, 'section', attrs={'id': 'index-by-category'})
    results, total = pep_links(category)

    count_for_status = {}
    for page in tqdm(results):
        page_response = get_response(session, page)
        if page_response is None:
            return
        page_soup = BeautifulSoup(page_response.text, 'lxml')
        dl = find_tag(page_soup, 'dl')
        status = find_tag(dl, 'dd', attrs={'class': 'field-even'})
        if status:
            status_text = status.text.strip()
            for key, values in EXPECTED_STATUS.items():
                if status_text in values:
                    if values[0] not in count_for_status:
                        count_for_status[values[0]] = 0
                    count_for_status[values[0]] += 1
                    break

    count_for_status['Total'] = total

    results_for_table = [['Статус', 'Количество']]
    results_for_table.extend(count_for_status.items())

    return results_for_table


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode

    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
