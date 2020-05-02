import collections
import heapq
import pathlib
import pickle
import logging

NORMALIZED_CHARS = {
    'ァ': 'ア', 'ィ': 'イ', 'ゥ': 'ウ', 'ェ': 'エ', 'ォ': 'オ',
    'ガ': 'カ', 'ギ': 'キ', 'グ': 'ク', 'ゲ': 'ケ', 'ゴ': 'コ',
    'ザ': 'サ', 'ジ': 'シ', 'ズ': 'ス', 'ゼ': 'セ', 'ゾ': 'ソ',
    'ダ': 'タ', 'ヂ': 'チ', 'ッ': 'ツ', 'ヅ': 'ツ', 'デ': 'テ', 'ド': 'ト',
    'バ': 'ハ', 'パ': 'ハ',
    'ビ': 'ヒ', 'ピ': 'ヒ', 'ブ': 'フ', 'プ': 'フ',
    'ベ': 'ヘ', 'ペ': 'ヘ', 'ボ': 'ホ',
    'ポ': 'ホ', 'ャ': 'ヤ', 'ュ': 'ユ',
    'ョ': 'ヨ', 'ヮ': 'ワ', 'ヰ': 'イ',
    'ヱ': 'エ', 'ヲ': 'オ', 'ヴ': 'ハ',
    'ー': '',
}
VALID_KATAKANA = [
    'ア', 'イ', 'ウ', 'エ', 'オ',
    'カ', 'キ', 'ク', 'ケ', 'コ',
    'サ', 'シ', 'ス', 'セ', 'ソ',
    'タ', 'チ', 'ツ', 'テ', 'ト',
    'ナ', 'ニ', 'ヌ', 'ネ', 'ノ',
    'ハ', 'ヒ', 'フ', 'ヘ', 'ホ',
    'マ', 'ミ', 'ム', 'メ', 'モ',
    'ヤ', 'ユ', 'ヨ',
    'ラ', 'リ', 'ル', 'レ', 'ロ',
    'ワ', 'ン',
]
KATAKANA_INDEX = {c: i for i, c in enumerate(VALID_KATAKANA)}
N = len(VALID_KATAKANA)


def normalize_kana(c):
    if c < 'ァ' or 'ヴ' < c:
        return ''
    return NORMALIZED_CHARS[c] if c in NORMALIZED_CHARS else c


def get_char_index(c):
    assert 'ァ' <= c <= 'ヴ', c
    normalized = normalize_kana(c)
    assert normalized in KATAKANA_INDEX
    return KATAKANA_INDEX[normalized]


def katakana_to_bits(word):
    ret = 0
    for c in word:
        normalized = normalize_kana(c)
        if normalized == '':
            continue
        ret |= 1 << KATAKANA_INDEX[normalized]
    return ret


def bits_to_katakana(bits):
    ret = set()
    i = 0
    while bits > 0:
        if bits & 1:
            ret.add(VALID_KATAKANA[i])
        bits >>= 1
        i += 1
    return ret


def normalize_word(w):
    return ''.join(filter(lambda c: c, map(lambda c: normalize_kana(c), w)))


class Word:
    def __init__(self, surface, reading=None):
        if reading is None:
            reading = surface
        self.surface = surface
        self.reading = reading
        normalized_word = normalize_word(reading)
        self.normalized = normalized_word
        self.size = len(normalized_word)
        self.bits = katakana_to_bits(normalized_word)
        self.first_char_index = get_char_index(normalized_word[0])
        self.last_char_index = get_char_index(normalized_word[-1])

    def __str__(self):
        return str((self.surface, self.reading))

    def __repr__(self):
        return 'Word({}, {})'.format(self.surface, self.reading)


class Edge:
    def __init__(self, word):
        self.word = word


class Node:
    def __init__(self, word, cost):
        self.word = word
        self.edges = {}
        self.cost = cost


def load_graph(dictionary, *, logger=None):
    dump_file_name = dictionary + '.graph.dump'
    logger = logger or logging.getLogger(__name__)
    if pathlib.Path(dump_file_name).is_file():
        with open(dump_file_name, 'rb') as dump:
            return pickle.load(dump)
    else:
        return generate_graph(dictionary, logger=logger)


def generate_graph(dictionary, *, logger=None):
    logger = logger or logging.getLogger(__name__)
    logger.info('START generating graph.')

    g = [[{} for j in range(N)] for i in range(N)]
    logger.debug('seed file:{}'.format(dictionary))
    with open(dictionary) as words:
        for line in words:
            surface, reading = map(lambda x: x.strip(), line.split(','))

            # 1文字の単語は使えない
            if len(reading) < 2:
                continue
            normalized_reading = normalize_word(reading)
            if len(normalized_reading) < 2:
                continue

            # 末尾の'ン'対策
            if normalized_reading[-1] == 'ン':
                continue

            first_char_index = get_char_index(normalized_reading[0])
            last_char_index = get_char_index(normalized_reading[-1])
            words_bits = katakana_to_bits(normalized_reading)
            if words_bits not in g[first_char_index][last_char_index] or len(reading) < g[first_char_index][last_char_index][words_bits].size:
                g[first_char_index][last_char_index][words_bits] = Word(
                    surface, reading)
    logger.info('FINISH generating graph.')

    logger.info('START dumping graph.')
    dump_file_name = dictionary + '.graph.dump'
    with open(dump_file_name, 'wb') as dump:
        pickle.dump(g, dump)
    logger.info('FINISH dumping graph.')
    return g


def find_path(g, start, target, *, logger=None):
    logger = logger or logging.getLogger(__name__)
    logger.info('START searching a shortest path.')
    target_bits = katakana_to_bits(target)
    init_cost = (float('inf'), float('inf'))
    costs = collections.defaultdict(
        lambda: [init_cost for i in range(N)])
    costs[0][start.last_char_index] = (1, start.size)
    hq = [((1, start.size), (0, start.last_char_index))]
    prev = collections.defaultdict(lambda: [None for i in range(N)])
    while hq:
        cost, node = heapq.heappop(hq)
        pop, size = cost
        bits, char_index = node

        for i in range(N):
            for _, word in g[char_index][i].items():
                assert word.first_char_index == char_index
                next_cost = (pop+1, size+word.size)
                next_bits = bits | (target_bits & word.bits)
                next_char_index = word.last_char_index
                if next_cost < costs[next_bits][next_char_index]:
                    costs[next_bits][next_char_index] = next_cost
                    heapq.heappush(
                        hq, (next_cost, (next_bits, next_char_index)))
                    prev[next_bits][next_char_index] = (bits, char_index, word)
    path = []
    cost = costs[target_bits][start.first_char_index]
    if costs[target_bits][start.first_char_index] == init_cost:
        return path, init_cost
    bits = target_bits
    char_index = start.first_char_index
    while prev[bits][char_index] is not None:
        path.append(prev[bits][char_index][2])
        bits, char_index, word = prev[bits][char_index]
    path.append(start)
    path.reverse()
    logger.info('FINISH searching a shortest path.')
    return path, costs[target_bits][start.first_char_index]


def solve(g, start, target, *, logger=None):
    logger = logger or logging.getLogger(__name__)
    target = ''.join(
        list(set(c for c in normalize_word(target) if c not in start.normalized)))
    logger.debug('target:{}'.format(target))
    path, cost = find_path(g, start, target, logger=logger)
    return path, cost
