# アポロしりとり

QuizKnockが考案したゲームであるアポロしりとりのソルバーです。

## 「アポロしりとり」とは

「スタート単語」と「集める単語」が指定されるので、「集める単語」に含まれる文字をすべて含むような「スタート単語」を含むしりとりループを見つけなさいというゲームです。

詳しくは下記の動画を参照してください。
* [暇つぶしにもバトルにも！斬新なゲーム「アポロしりとり」 - YouTube](https://www.youtube.com/watch?v=DcxzHIGrgzI)
* [【アポロしりとり】白瀬矗を出発して木口小平を集めろ！ - YouTube](https://www.youtube.com/watch?v=Ye9dbHWuzIw)
* [【名作動画コメンタリー】アポロしりとり編 byふくらP - YouTube](https://www.youtube.com/watch?v=UKcv5VLaRTo)

## 実行方法

```
$ python apollo_shiritori.py -h
usage: apollo_shiritori.py [-h] [--start START] [--target TARGET] [--dict DICT]

optional arguments:
  -h, --help       show this help message and exit
  --start START    set start word by KATAKANA.
  --target TARGET  set target word by KATAKANA.
  --dict DICT      set dictonary file.
```

```
$ python apollo_shiritori.py --start オハギ --target キナコ
オハギ(オハギ)->きのこ(キノコ)->粉ミルク(コナミルク)->グレゴリオ(グレゴリオ)
````


## 辞書ファイルを作ろう
しりとりに使える単語をnoun.csvで定義しています。単語を追加したい場合は「単語」と「フリガナ」をカンマ区切りで追加してください。

neologdを使う場合は下記の手順で同様のファイルを作ることができます。

```sh
git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
cd mecab-ipadic-neologd/seed/
xz -dv *.xz
cat *.csv | grep -e ",名詞," | grep -v "人名"| cut -d "," -f 11,12 > noun.csv
```