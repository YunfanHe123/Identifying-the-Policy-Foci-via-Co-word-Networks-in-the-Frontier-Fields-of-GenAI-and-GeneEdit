import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from kneed import KneeLocator

# 读取CSV文件
df = pd.read_csv('E:\kkk.csv')  # 替换为实际文件路径
df.sort_values('count', ascending=False, inplace=True)  # 按频次降序排序

# 准备数据
x = np.arange(1, len(df) + 1)  # 排名序列 (1,2,3,...)
y = df['count'].values  # 频次值

# 使用Kneedle算法检测拐点
kneedle = KneeLocator(
    x, y,
    curve='convex',  # 幂律曲线呈凸形下降
    direction='decreasing',  # 数值递减
    interp_method='polynomial',  # 多项式插值
    polynomial_degree=8  # 多项式阶数（根据数据调整）
)

# 获取拐点位置
knee_point = kneedle.knee
threshold_count = y[knee_point - 1]  # 拐点对应的频次阈值

# 输出结果
print(f"Kneedle算法检测结果:")
print(f"拐点位置: 排名第{knee_point}位")
print(f"频次阈值: {threshold_count}")
print(f"高频关键词数量: {knee_point}")

# 可视化结果
plt.figure(figsize=(10, 6))
plt.loglog(x, y, 'b-', label='频次分布')
plt.axvline(x=knee_point, color='r', linestyle='--', label=f'拐点 (排名: {knee_point})')
plt.scatter(knee_point, threshold_count, color='red', s=100, zorder=5)
plt.xlabel('排名 (log scale)')
plt.ylabel('频次 (log scale)')
plt.title('幂律分布与Kneedle拐点检测')
plt.legend()
plt.grid(True, which="both", ls="--")
plt.show()

# 获取高频关键词
high_freq_keywords = df[df['count'] >= threshold_count]
print(f"\n高频关键词示例:")
print(high_freq_keywords.head())