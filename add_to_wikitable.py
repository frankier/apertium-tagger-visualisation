# -- encoding: utf-8 --

import argparse
import locale
import sys

import mwparserfromhell
from format_data import (attrs_to_sort_tuple, attrs_to_str, name_to_attrs,
                         read_data, value_to_str)
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.wikicode import Wikicode


def rdict(d):
    return {v: k for k, v in d.items()}

LANG_CODE_NAME_MAP = {
    'cat': 'Catalan',
    'spa': 'Spanish',
    'hbs': 'Serbo-Croatian',
    'rus': 'Russian',
    'kaz': 'Kazakh',
    'por': 'Portuguese',
    'swe': 'Swedish',
}
LANG_NAME_CODE_MAP = rdict(LANG_CODE_NAME_MAP)


def mk_title_td(title):
    return Tag(
        'td',
        wiki_markup='|',
        contents=" '''{}''' ".format(title),
        closing_wiki_markup='')


def mk_val_td(val, is_last=False):
    return Tag(
        'td',
        wiki_markup='||',
        attrs=['align=right'],
        contents=" {} {}".format(val, "\n" if is_last else ""),
        wiki_style_separator='|',
        closing_wiki_markup='')


def mk_empty_td(is_last=False):
    return Tag(
        'td',
        wiki_markup='||',
        contents="\n" if is_last else "",
        closing_wiki_markup='')


def mk_wc_td(val, is_first=False, is_last=False):
    return Tag(
        'td',
        wiki_markup='!' if is_first else '!!',
        contents=" <small>{}</small>{}".format(val, "\n" if is_last else " "),
        closing_wiki_markup='')


def mk_initial_tr(title):
    return Tag(
        'tr',
        wiki_markup='|-\n',
        contents=Wikicode([mk_title_td(title), mk_empty_td(is_last=True)]),
        closing_wiki_markup='')


def insert_into_tr(tr, col_idx, val_str):
    if len(tr.contents.nodes) <= col_idx:
        last_td = tr.contents.get(-1)
        if last_td.contents.endswith('\n'):
            last_td.contents = last_td.contents[:-1]
        while len(tr.contents.nodes) < col_idx:
            tr.contents.append(mk_empty_td())
        tr.contents.append(mk_empty_td(is_last=True))
    target_cell = tr.contents.get(col_idx)
    has_newline = target_cell.contents.endswith('\n')
    val_td = mk_val_td(val_str, is_last=has_newline)
    tr.contents.set(col_idx, val_td)


def insert_into_wc(tr, col_idx, val_str):
    target_cell = tr.contents.get(col_idx)
    has_newline = target_cell.contents.endswith('\n')
    is_first = len(target_cell.wiki_markup) == 1
    val_td = mk_wc_td(val_str, is_first=is_first, is_last=has_newline)
    tr.contents.set(col_idx, val_td)


def format_word_count(word_count):
    locale.setlocale(locale.LC_ALL, 'en_US')
    number = locale.format("%d", word_count, grouping=True)
    return "{}".format(number)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Write results to a wikitable.")
    parser.add_argument(
        'results', nargs='+',
        help="File containing result of experiments")
    parser.add_argument(
        '--available',
        help="Write available statistics",
        action='store_true')
    parser.add_argument(
        '--blank',
        help="Blank out a column",
        action='store_true')

    return parser.parse_args()


def main():
    input_table = sys.stdin.read()

    lang_order = []

    args = parse_args()

    table = mwparserfromhell.parse(input_table.strip())
    table_inner = table.get(0).contents
    headings = table_inner.get(2).contents.nodes
    for tag in headings:
        if not isinstance(tag, Tag):
            continue
        title = tag.contents.strip()
        if not title:
            continue
        lang_order.append(LANG_NAME_CODE_MAP[title])

    if args.blank:
        # blank out columns
        for lang in args.results:
            col_idx = lang_order.index(lang) + 1
            table_idx = 3
            while table_idx < len(table_inner.nodes):
                tr = table_inner.get(table_idx)
                if len(tr.contents.nodes) > col_idx:
                    if tr.contents.get(col_idx).contents.endswith('\n'):
                        tr.contents.get(col_idx).contents = '\n'
                    else:
                        tr.contents.get(col_idx).contents = ''
                table_idx += 1
        print(table)
        sys.exit()

    value_idx = 1 if args.available else 0

    input_data = read_data(args.results)

    for lang, data in input_data.items():
        lang_idx = lang_order.index(lang)
        col_idx = lang_idx + 1
        word_count = data.pop('word_count', None)
        if word_count is not None:
            word_count_tr = table_inner.get(3)
            insert_into_wc(word_count_tr,
                           col_idx,
                           format_word_count(word_count))
        data = [(name_to_attrs(name), value_to_str(value[value_idx]))
                for name, value in data.items()]
        data = sorted(data, key=lambda pair: attrs_to_sort_tuple(pair[0]))
        table_idx = 4
        for attrs, val_str in data:
            title_str = attrs_to_str(attrs)
            while table_idx < len(table_inner.nodes):
                tr = table_inner.get(table_idx)
                if len(tr.contents) > 1:
                    cell_contents = tr.contents.get(0).contents
                    existing_title_str = str(cell_contents).strip(' ')\
                        .strip("'")
                    if existing_title_str == title_str:
                        # insert into existing
                        insert_into_tr(tr, col_idx, val_str)
                        break
                else:
                    table_inner.remove(tr, recursive=False)
                table_idx += 1
            else:
                # append to end
                tr = mk_initial_tr(title_str)
                insert_into_tr(tr, col_idx, val_str)
                table_inner.append(tr)

    print(table)


if __name__ == '__main__':
    main()
