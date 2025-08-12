import csv
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# 初始化词形还原器
lemmatizer = WordNetLemmatizer()


def get_wordnet_pos(treebank_tag):
    """将POS标签转换为WordNet格式"""
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # 默认为名词


def lemmatize_keyword(keyword):
    """对单个关键词进行词形还原"""
    # 如果关键词是短语（包含空格），则分别处理每个单词
    if ' ' in keyword:
        return ' '.join(lemmatize_keyword(word) for word in keyword.split())

    # 获取词性标注
    try:
        pos_tags = nltk.pos_tag([keyword])
        word, pos = pos_tags[0]
        wordnet_pos = get_wordnet_pos(pos)

        # 应用词形还原
        return lemmatizer.lemmatize(word, pos=wordnet_pos)
    except Exception as e:
        # 如果处理出错，返回原词
        print(f"处理关键词 '{keyword}' 时出错: {e}")
        return keyword


def process_keywords(keyword_str):
    """处理关键词字符串：删除SDG条目、统一小写、词形还原"""
    # 检查空值或无效输入
    if keyword_str is None or not isinstance(keyword_str, str) or keyword_str.strip() == "":
        return ""

    # 分割关键词并去除空白字符
    keywords = [k.strip() for k in keyword_str.split(';') if k.strip()]

    # 定义SDG匹配模式（不区分大小写）
    sdg_pattern = re.compile(r'^sdg \d+:', re.IGNORECASE)

    processed = []
    for kw in keywords:
        # 过滤符合SDG模式的关键词
        if not sdg_pattern.match(kw):
            # 统一转小写
            kw_lower = kw.lower()
            # 词形还原
            kw_lemma = lemmatize_keyword(kw_lower)
            processed.append(kw_lemma)

    return '; '.join(processed)


# 读取CSV文件
with open('E:\hhh.csv', 'r', newline='', encoding='gbk') as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)
    fieldnames = reader.fieldnames

# 处理keywords字段
for row in rows:
    if 'keywords' in row:
        row['keywords'] = process_keywords(row['keywords'])

# 写入新的CSV文件
with open('E:\processed.csv', 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)