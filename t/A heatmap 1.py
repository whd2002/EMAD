import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# ========== ✅ 设置全局字体为 Times New Roman ==========
plt.rcParams['font.family'] = 'Times New Roman'

# ========== 原有数据和逻辑保持不变 ==========
data = np.array([
    [287, 449, 266, 115,  38],
    [217, 451, 363, 182,  41],
    [108, 299, 627, 238,  77],
    [ 72, 225, 364, 365, 235],
    [ 36,  76, 180, 300, 389]
])

target_col_totals = np.array([720, 1500, 1800, 1200, 780])

print("✅ Final column sums:", data.sum(axis=0))
print("✅ Target totals:     ", target_col_totals)
print("✅ Match:", np.array_equal(data.sum(axis=0), target_col_totals))
print("✅ Any multiples of 10?", np.any(data % 10 == 0))
print("✅ Total sum:", data.sum())

for j in range(data.shape[1]):
    diff = target_col_totals[j] - data[:, j].sum()
    if diff != 0:
        idx = np.argmax(proportion_template[:, j])
        data[idx, j] += diff

print("✅ Final column sums:", data.sum(axis=0))
print("✅ Total sum:", data.sum())

x_labels = ["50-", "150~\n250", "250~\n350", "350~\n450", "450+"]
y_labels = ["85+", "70~85", "55~70", "40~55", "40-"]

total = data.sum()
percentages = data / total * 100

annot_labels = np.empty(data.shape, dtype=object)
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        annot_labels[i, j] = f"{data[i, j]}\n({percentages[i, j]:.1f}%)"

# ✅ 对齐 figure 尺寸和布局
plt.figure(figsize=(8.8, 7.01))
plt.subplots_adjust(left=0.15, right=0.85, bottom=0.21, top=0.95)

sns.set_style("whitegrid")

ax = sns.heatmap(
    data,
    annot=annot_labels,
    fmt='',
    cmap='Blues',
    cbar_kws={'label': 'Count', 'shrink': 1},
    xticklabels=x_labels,
    yticklabels=y_labels,
    linewidths=0.5,
    linecolor='lightgray',
    annot_kws={"size": 25, "fontfamily": "Times New Roman"},
    square=True
)

# 添加边框
for _, spine in ax.spines.items():
    spine.set_visible(True)
    spine.set_color('black')
    spine.set_linewidth(1.2)

# 颜色条设置
cbar = ax.collections[0].colorbar
cbar.ax.set_frame_on(True)
for _, spine in cbar.ax.spines.items():
    spine.set_visible(True)
    spine.set_color('black')
    spine.set_linewidth(1.2)

# ✅ 关键：移除 colorbar 的刻度线和数字（与第一段一致）
cbar.set_ticks([])

# ✅ colorbar ylabel 字号改为 31（原为 36）
cbar.ax.set_ylabel('Count', fontsize=31, fontfamily='Times New Roman')

# ✅ 坐标轴标签字号改为 31（原为 36）
plt.xlabel("Trade Volume (MWh)", fontsize=31, fontfamily='Times New Roman')
plt.ylabel("Price ($/MWh)", fontsize=31, fontfamily='Times New Roman')

# ✅ 刻度标签：显式指定 fontfamily，确保换行标签也用 Times New Roman
plt.xticks(rotation=0, fontsize=25, fontfamily='Times New Roman')
plt.yticks(rotation=0, fontsize=25, fontfamily='Times New Roman')

plt.tight_layout()
plt.savefig("A heatmap1.pdf", dpi=300, bbox_inches='tight')
plt.show()