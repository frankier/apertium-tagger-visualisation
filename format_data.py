# -- encoding: utf-8 --

TAGGER_ORDER = ['1st', 'unigram', 'bigram', 'lwsw', 'percep']


def attrs_to_sort_tuple(attrs):
    if attrs is None:
        return
    lattrs, kwattrs = attrs
    return (kwattrs['sup'], kwattrs['cg'], TAGGER_ORDER.index(lattrs[0]),
            kwattrs.get('i', 0), kwattrs.get('j', 0), kwattrs.get('mtx'))


def superscript(num):
    if num == 0:
        return chr(0x2070)
    elif num == 1:
        return chr(0xB9)
    elif num < 4:
        return chr(0xB0)
    else:
        return chr(0x2070 + num)


def attrs_to_str(attrs):
    lattrs, kwattrs = attrs

    if lattrs[0] == 'unigram':
        out = 'Unigram model ' + kwattrs['model']
    elif lattrs[0] == '1st':
        out = lattrs[0]
    else:
        out = lattrs[0].title()

    if kwattrs['cg'] > 1:
        out = "CG" + str(kwattrs['cg'] - 1) + "→" + out
    elif kwattrs['cg'] == 1:
        out = "CG→" + out

    if kwattrs.get('cgt'):
        out = "CGT" + str(attrs['cgt']) + "→" + out

    bracket_bits = []

    if lattrs[0] == 'gen' and kwattrs['model'] == 'bigram':
        bracket_bits.append('sup' if kwattrs['sup'] else 'unsup')

    if 'i' in kwattrs:
        bracket_bits.append('{} iters'.format(kwattrs['i']))

    if 'j' in kwattrs:
        bracket_bits.append('{} cats'.format(kwattrs['j']))

    if lattrs[0] == 'percep':
        bracket_bits.append(kwattrs['mtx'])

    if bracket_bits:
        out += ' ({})'.format(', '.join(bracket_bits))

    return out


def value_to_str(value):
    if hasattr(value, "__getitem__"):
        return "{2:.2f}±{3:.2f}".format(*(v * 100 for v in value))
    else:
        return "{0:.2f}".format(value * 100)


def read_data(fns):
    input_data = {}

    for fn in fns:
        i = eval(open(fn).read())
        for k in i:
            if not i[k]:
                continue
            if k not in input_data:
                input_data[k] = {}
            for l in i[k]:
                if not i[k][l]:
                    continue
                input_data[k][l] = i[k][l]

    return input_data
