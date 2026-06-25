import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
import matplotlib

# 设置PDF保存时字体嵌入
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# 全局字体设置（与模板一致）
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = 48
rcParams['axes.labelsize'] = 48
rcParams['xtick.labelsize'] = 48
rcParams['ytick.labelsize'] = 48
rcParams['legend.fontsize'] = 36

# 创建双子图
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(22, 8))
fig.subplots_adjust(left=0.105, right=0.99, bottom=0.175, top=0.97, hspace=0.05)

# 数据（已移除 y2 / OA）
x = [500, 1000, 1500, 2000, 2500, 3000]
x_labels = ['×0.4', '×0.6', '×0.8', '×1.2', '×1.4', '×1.6']
y1 = [7714.0, 3863.333, 1570.667, 1266.667, 2432.0, 3521.333]     # ETAM
y3 = [0.60, 0.525, 0.45, 0.45, 0.525, 0.60]   # CEX
y4 = [0.33333, 0.29167, 0.25, 0.25, 0.29167, 0.33333]   # ODB

width = 150

# 定义颜色和纹理（仅保留3个）
colors = ['#CD5C5C', '#6495ED', '#C0C0C0']      # ETAM, CEX, ODB
patterns = ['//', 'x', '+']                     # 对应纹理

# 设置Y轴范围
ax1.set_ylim(150, 8000)
ax2.set_ylim(0, 0.9)

# 调整柱子位置：现在只有3组，居中排列
# 偏移：-width, 0, +width
bars1_upper = ax1.bar(np.array(x) - width, y1, width=width, color=colors[0], label='EMAD', edgecolor='none', hatch=patterns[0])
bars2_upper = ax1.bar(np.array(x),        y3, width=width, color=colors[1], label='CEX',  edgecolor='none', hatch=patterns[1])
bars3_upper = ax1.bar(np.array(x) + width, y4, width=width, color=colors[2], label='ODB',  edgecolor='none', hatch=patterns[2])

bars1_lower = ax2.bar(np.array(x) - width, y1, width=width, color=colors[0], label='EMAD', edgecolor='none', hatch=patterns[0])
bars2_lower = ax2.bar(np.array(x),        y3, width=width, color=colors[1], label='CEX',  edgecolor='none', hatch=patterns[1])
bars3_lower = ax2.bar(np.array(x) + width, y4, width=width, color=colors[2], label='ODB',  edgecolor='none', hatch=patterns[2])

# 为每个柱子添加白色半透明边框
for bars in [bars1_upper, bars2_upper, bars3_upper,
             bars1_lower, bars2_lower, bars3_lower]:
    for bar in bars:
        bar.set_edgecolor([1, 1, 1, 0.7])

# 添加网格线
ax1.grid(axis='both', linestyle='-', linewidth=0.5, alpha=0.7)
ax2.grid(axis='both', linestyle='-', linewidth=0.5, alpha=0.7)

# 设置坐标轴
ax2.set_xticks(x)
ax2.set_xticklabels(x_labels)
ax2.set_xlabel('Multiple of Dictate Energy Price')

# 设置Y轴标签
ax2.set_ylabel('Normalized Cost', fontsize=48)
ax2.yaxis.set_label_coords(-0.08, 1)

# 设置Y轴刻度
ax1.set_yticks([1000, 3000, 5000, 7000])
ax2.set_yticks([0, 0.2, 0.4, 0.6, 0.8])

# 隐藏中间的spine，制造"断开"视觉
ax1.spines.bottom.set_visible(False)
ax2.spines.top.set_visible(False)
ax1.xaxis.tick_top()
ax1.tick_params(labeltop=False)

# 关闭顶部X轴刻度线
ax1.tick_params(axis='x', top=False, bottom=False)
ax2.tick_params(axis='x', top=False)

# 绘制斜杠断点线
d = 0.015
kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
              linestyle="none", color='k', mec='k', mew=1.5, clip_on=False)
ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

# 设置X轴范围（根据新的柱宽调整）
ax2.set_xlim(x[0] - 1.9 * width, x[-1] + 1.9 * width)

# 图例设置（3列）
legend = ax1.legend(
    loc='upper center',
    ncol=3,
    handletextpad=0.3,
    columnspacing=0.8,
    handlelength=1.5,
    title_fontsize=26,
    bbox_to_anchor=(0.45, 1.0)  # ← 关键：自定义位置
)

# 加粗坐标轴边框
for ax in [ax1, ax2]:
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

# 保存为高分辨率 PDF
plt.savefig("A dictate prices.pdf", bbox_inches='tight')
plt.show()