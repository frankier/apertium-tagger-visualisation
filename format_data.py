# -- encoding: utf-8 --

TAGGER_ORDER = ['1st', 'unigram1', 'unigram2', 'unigram3', 'bigram', 'lwsw']


def name_to_attrs(name):
    attrs = {}
    for tagger in TAGGER_ORDER:
        if tagger in name:
            attrs['tagger'] = tagger

    if 'tagger' not in attrs:
        return

    if 'cgdual_' in name:
        attrs['cg'] = 2
    elif 'cginv_' in name:
        attrs['cg'] = 3
    elif 'cg_' in name:
        attrs['cg'] = 1
    else:
        attrs['cg'] = 0

    if 'cgt' in name:
        attrs['cgt'] = int(name.split('cgt')[1].split('_')[0])
    else:
        attrs['cgt'] = 0

    if attrs['tagger'] == 'lwsw':
        attrs['label_sup'] = None
        attrs['sup'] = False
    elif 'unsup' in name:
        attrs['label_sup'] = False
        attrs['sup'] = False
    elif 'sup' in name:
        attrs['label_sup'] = True
        attrs['sup'] = True
    else:
        attrs['label_sup'] = None
        attrs['sup'] = 'unigram' in name

    if '_i' in name:
        attrs['iters'] = int(name.split('_i')[1].split('_')[0])
    else:
        attrs['iters'] = None

    if '_j' in name:
        attrs['cattrim'] = int(name.split('_j')[1].split('_')[0])
    else:
        attrs['cattrim'] = None

    return attrs


def attrs_to_sort_tuple(attrs):
    if attrs is None:
        return
    return (attrs['sup'], attrs['cg'], TAGGER_ORDER.index(attrs['tagger']),
            attrs['iters'] or 0, attrs['cattrim'] or 0)


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
    if attrs['tagger'].startswith('unigram'):
        out = 'Unigram model ' + attrs['tagger'][len('unigram'):]
    elif attrs['tagger'] == '1st':
        out = attrs['tagger']
    else:
        out = attrs['tagger'].title()

    if attrs['cg'] > 1:
        out = "CG" + str(attrs['cg'] - 1) + "→" + out
    elif attrs['cg'] == 1:
        out = "CG→" + out

    if attrs['cgt']:
        out = "CGT" + str(attrs['cgt']) + "→" + out

    if attrs['label_sup'] is not None or attrs['iters'] is not None:
        bits = []
        if attrs['label_sup'] is not None:
            bits.append('sup' if attrs['label_sup'] else 'unsup')
        if attrs['iters'] is not None:
            bits.append('{} iters'.format(attrs['iters']))
        if attrs['cattrim'] is not None:
            bits.append('{} cats'.format(attrs['cattrim']))
        out += ' ({})'.format(', '.join(bits))

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
