#导入关键的包
from itertools import combinations
from collections import defaultdict
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import csv


def process_keywords(csv_file_path):
    grouped = []

    with open(csv_file_path, 'r', encoding='gbk') as file:
        reader = csv.reader(file)

        # 读取标题行并找到"keywords"列索引
        headers = next(reader)
        keyword_col = headers.index("keywords")

        # 处理每一行数据
        for row in reader:
            if len(row) > keyword_col:
                # 拆分关键词并去除首尾空格
                keywords = [kw.strip() for kw in row[keyword_col].split(';')]
                grouped.append(keywords)

    return grouped

#函数三：定义h-strength和h-degree的统用计算函数
def h_index_cutoff(data, metric_values):
    sorted_values = sorted(metric_values, reverse=True)
    h = 0
    for i, val in enumerate(sorted_values):
        if val >= (i + 1):
            h = i + 1
        else:
            break
    return h

#函数四：定义第一次h截断函数
#第一次截断：基于边权重的h-strength
def first_cutoff(co_citation):
    # 计算h-strength
    edge_weights = list(co_citation.values())
    h_strength = h_index_cutoff(co_citation, edge_weights)

    # 执行第一次截断
    first_filtered = {pair: w for pair, w in co_citation.items() if w >= h_strength}
    return first_filtered, h_strength

#函数五：定义第二次h截断函数
#第二次截断：基于节点度中心性的h-degree
def second_cutoff(first_filtered):
    # 计算节点度中心性
    node_degrees = defaultdict(int)
    for (n1, n2) in first_filtered.keys():
        node_degrees[n1] += 1
        node_degrees[n2] += 1

    # 计算h-degree
    degree_values = list(node_degrees.values())
    h_degree = h_index_cutoff(node_degrees, degree_values)

    # 执行第二次截断
    second_filtered = {}
    for (n1, n2), w in first_filtered.items():
        if node_degrees[n1] >= h_degree and node_degrees[n2] >= h_degree:
            second_filtered[(n1, n2)] = w

    return second_filtered, h_degree

#主程序
result = process_keywords("E:\hhh.csv")  # 替换为你的文件路径

# 统计边（共被引次数）
co_citation = defaultdict(int)
for refs in result:
    # 关键步骤：将参考文献列表排序，消除顺序影响
    sorted_refs = sorted(refs)  # 所有文献对按字母顺序排列
    for pair in combinations(sorted(sorted_refs), 2):  # 生成无向对
        co_citation[pair] += 1

# 转换为边（共被引频次）列表
edges = [{'source': u, 'target': v, 'weight': w} for (u, v), w in co_citation.items()]

# 统计点（节点度中心性）
degree_counts = defaultdict(int)
for h1, h2 in co_citation.keys():
    degree_counts[h1] += 1  # 节点h1的度+1
    degree_counts[h2] += 1  # 节点h2的度+1

# 转换为节点度中心性列表
degrees = [{'node': node, 'degree': degree} for node, degree in degree_counts.items()]

# 统计节点被引频次
node_counts = defaultdict(int)
for refs in result:
    for ref in refs:
        node_counts[ref] += 1

# 转换为节点被引频次列表
nodes = [{'id': ref, 'count': cnt} for ref, cnt in node_counts.items()]

# 第一次截断
first_result, h_strength = first_cutoff(co_citation)
print(f"第一次截断(h_strength={h_strength})后保留边数:", len(first_result))

# 第二次截断
second_result, h_degree = second_cutoff(first_result)
print(f"第二次截断(h_degree={h_degree})后保留边数:", len(second_result))

# 输出最终结果
print("\n最终保留的共被引关系:")
for (n1, n2), w in second_result.items():
    print(f"{n1}-{n2}: {w}")

'''
# 共引网络图绘制
G = nx.Graph()
for (n1, n2), w in second_result.items():
    G.add_edge(n1, n2, weight=w)
# 绘制网络
pos = nx.spring_layout(G, k=0.15)  # k为节点间距系数
nx.draw(G, pos, with_labels=True, node_size=500, font_size=8)
plt.show()'''


# 导出为CSV
pd.DataFrame(nodes).to_csv('E:\odes.csv', index=False)
pd.DataFrame(edges).to_csv('E:\edges.csv', index=False)
pd.DataFrame(degrees).to_csv('E:\degree.csv', index=False)

'''
# 转换为VOSviewer格式
df = pd.DataFrame(
    [(n1, n2, w) for (n1, n2), w in co_citation.items()],
    columns=["Source", "Target", "Weight"]
)
df.to_csv("E:\etwork_vos.txt", sep="\t", index=False, header=True, encoding="utf-8")

print("文件已生成：network_vos.txt")'''