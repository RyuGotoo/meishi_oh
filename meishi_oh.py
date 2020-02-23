import collections
import requests
from bs4 import BeautifulSoup
from janome.tokenizer import Tokenizer
import csv

the_part_of_speech_for_deciding_the_king = '名詞'
# 名詞, 動詞, 助詞, 副詞, 助動詞, 形容詞, 接続詞, 連体詞, 接頭詞, 感動詞


class Blog(object):
    def __init__(self, url):
        self.url = url
        self.title = ''
        self.pos_num = 0
        self.pos_counts = {}

    def get_pos_rates(self):
        pos_rates = {}
        for pos, count in self.pos_counts.items():
            pos_rates[pos] = count / self.pos_num
        return pos_rates


def get_urls():
    with open('urls.txt', 'r') as urls_txt:
        urls = [url.strip() for url in urls_txt.readlines()]
    return urls


def format_text(text):
    soup = BeautifulSoup(text, 'html.parser').find(class_='wrapper-article-detail-inner')
    soup.find('dl').decompose()
    while len(soup.find_all('pre')) > 0:
        soup.find('pre').decompose()
    while len(soup.find_all('code')) > 0:
        soup.find('code').decompose()
    while len(soup.find_all(class_='prettyprint')) > 0:
        soup.find(class_='prettyprint').decompose()
    formatted_text = '\n'.join(soup.stripped_strings)
    return formatted_text


def create_blogs(urls):
    blogs = []
    for url in urls:
        blog = Blog(url)

        # テキスト取得、スクレイピング
        text_all = requests.get(blog.url).text
        text = format_text(text_all)
        title = text.splitlines()[0]
        blog.title = title

        # 形態素解析
        pos_list = []
        for token in Tokenizer().tokenize(text):
            pos = token.part_of_speech.split(',')[0]
            base_pos = ('名詞', '助詞', '動詞', '助動詞', '副詞', '形容詞', '連体詞', '接頭詞', '接続詞', '感動詞')
            if pos in base_pos:
                pos_list.append(pos)
        blog.pos_num = len(pos_list)

        # 品詞 (pos) カウント
        blog.pos_counts = collections.Counter(pos_list)
        blog.pos_counts = dict(sorted(blog.pos_counts.items(), key=lambda x: -x[1]))

        blogs.append(blog)
        print(blog.title)
    return blogs


def show_fields(blog):
    print(blog.url)
    print(blog.title)
    print('総単語数 :', blog.pos_num)
    print(dict(blog.pos_counts))
    pos_rates = blog.get_pos_rates()
    for pos, rate in pos_rates.items():
        pos_rates[pos] = str(round(rate * 100, 1)) + '%'
    print(pos_rates)
    print()


def who_is_the_king(pos, blogs):
    # pos率高い順にソート
    ranking = {}
    for blog in blogs:
        if pos in blog.get_pos_rates().keys():
            rate = blog.get_pos_rates()[pos]
            ranking[blog] = rate
        else:
            ranking[blog] = 0
    ranking = dict(sorted(ranking.items(), key=lambda x: -x[1]))

    ranked_blogs = []
    for blog in ranking.keys():
        ranked_blogs.append(blog)

    print('【 {}率ランキング 】'.format(pos))
    for rank, blog in enumerate(ranked_blogs):
        print(str(rank + 1) + '位')
        show_fields(blog)


def export_csv(blogs):
    with open('results.csv', 'a') as f:
        base_pos = ['名詞', '助詞', '動詞', '助動詞', '副詞', '形容詞', '連体詞', '接頭詞', '接続詞', '感動詞']
        header = ['id'] + base_pos
        writer = csv.DictWriter(f, header)
        for blog in blogs:
            pos_rates = blog.get_pos_rates()
            pos_rates['id'] = blog.url
            writer.writerow(pos_rates)


def main():
    urls = get_urls()
    blogs = create_blogs(urls)
    who_is_the_king(the_part_of_speech_for_deciding_the_king, blogs)
    export_csv(blogs)


if __name__ == '__main__':
    main()
