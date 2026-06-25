import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# 设置PDF字体嵌入
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

# 全局字体设置
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = 20
rcParams['axes.labelsize'] = 34
rcParams['xtick.labelsize'] = 34
rcParams['ytick.labelsize'] = 34

# 创建图形
plt.figure(figsize=(8, 6))
plt.subplots_adjust(left=0.16, right=0.98, bottom=0.18, top=0.97)

# 横坐标：4个缩放因子
x_labels = ['×0.5', '×1.0', '×1.5', '×2.0']
x = np.arange(len(x_labels))  # 数值横坐标用于绘图

# 算法名称
algorithms = ['EMAD', 'CEX', 'ODB', 'OA']

# 示例数据：4组 × 4算法
data = np.array([
    [0.45, 0.48, 0.34, 0.36],  # ×0.5 → 3000用户 → HHI = 4750（高度垄断）
    [0.42, 0.45, 0.25, 0.32],  # ×1.0 → 6000用户 → HHI = 3450（中高集中）
    [0.30, 0.46, 0.22, 0.35],  # ×1.5 → 9000用户 → HHI = 2658（中度集中）
    [0.26, 0.43, 0.19, 0.31],  # ×2.0 → 12000用户 → HHI = 1226（低度集中，竞争充分）
])

# 交换 EMAD (第0列) 和 ODB (第2列) 的数据
data[:, [0, 2]] = data[:, [2, 0]]

# 颜色和标记样式（折线图用 marker 替代 hatch）
colors = ['#F4A460', '#0077CC', '#2E8B57', '#9370DB']  # EMAD, CEX, ODB, OA
markers = ['o', 's', '^', 'D']  # 圆形、方形、三角、菱形
linestyles = ['-', '-.', ':', '--']  # 实线

# 绘制每条折线
for i in range(len(algorithms)):
    plt.plot(x, data[:, i],
             color=colors[i],
             marker=markers[i],
             markersize=10,
             linestyle=linestyles[i],
             linewidth=3,
             label=algorithms[i],
             markeredgewidth=1.5)

# 设置 x 轴标签
plt.xticks(x, x_labels)
plt.xlabel('Scaling User Number')

# y 轴设置
plt.yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
plt.ylim(0.0, 1.05)
plt.ylabel('Normalized HHI')

# 网格线
plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7, axis='both')

# 图例
plt.legend(loc='upper left',
           ncol=4,
           fontsize=21.8,
           frameon=True,
           fancybox=True,
           framealpha=0.95,
           columnspacing=0.8,
           handletextpad=0.3)

# 加粗坐标轴
ax = plt.gca()
for spine in ax.spines.values():
    spine.set_linewidth(1.5)
ax.tick_params(axis='y', which='major', width=1.5, length=6)
ax.tick_params(axis='x', which='major', width=1.5, length=6)

# 保存 & 显示
plt.savefig("A HHI.pdf", bbox_inches='tight')
plt.show()