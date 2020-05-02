import argparse
import logging
import time

import logic

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s\t%(levelname)s\t%(message)s', datefmt='%Y/%m/%d %H:%M:%S')
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.propagate = False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start", type=str, help="set start word by KATAKANA.", default='チキュウ')
    parser.add_argument(
        "--target", type=str, help="set target word by KATAKANA.", default='ツキノイシ')
    parser.add_argument(
        "--dict", type=str, help="set dictonary file.", default='noun.csv')
    args = parser.parse_args()

    logger.info('start word:{}\ttarget word:{}\tdictonary file:{}'.format(
        args.start, args.target, args.dict))

    logger.info('START loading graph.')
    # g = generate_graph(args.dict)
    g = logic.load_graph(args.dict, logger=logger)
    logger.info('FINISH loading graph.')

    path, cost = logic.solve(g, logic.Word(
        args.start), args.target, logger=logger)
    if path:
        result = '->'.join(['{}({})'.format(w.surface, w.reading)
                            for w in path])
        logger.info('result:{}'.format(result))
        logger.info('pop:{}\tchars:{}'.format(*cost))
        print(result)
    else:
        logger.error('Path could not be found')


if __name__ == "__main__":
    main()
