#!/usr/bin/env python3
"""Generate all figures for the smoltcp security testing final report."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

OUT = os.path.join(os.path.dirname(__file__), 'figures')
os.makedirs(OUT, exist_ok=True)

# ── Color palette ──
C_BLUE = '#3B82F6'
C_RED = '#EF4444'
C_GREEN = '#10B981'
C_AMBER = '#F59E0B'
C_PURPLE = '#8B5CF6'
C_GRAY = '#6B7280'
C_TEAL = '#14B8A6'
C_DARK = '#1E293B'
C_LIGHT = '#F8FAFC'
C_WIN = '#0078D4'
C_WSL = '#E95420'

plt.rcParams.update({
    'figure.facecolor': C_LIGHT,
    'axes.facecolor': '#FFFFFF',
    'axes.edgecolor': '#CBD5E1',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.color': '#CBD5E1',
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
})


# ═══════════════════════════════════════════════════════════════
# FIGURE 1: Mutation Kill Ratio by Module (Grouped Bar)
# ═══════════════════════════════════════════════════════════════
def fig1_mutation_kill_ratio():
    modules = ['assembler.rs', 'ipv4.rs', 'udp.rs', 'tcp.rs']
    killed  = [76, 54, 23, 76]
    total   = [85, 88, 40, 120]
    ratios  = [k/t for k, t in zip(killed, total)]
    survived = [t - k for k, t in zip(killed, total)]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(modules))
    w = 0.35
    bars_k = ax.bar(x - w/2, killed, w, label='Killed', color=C_GREEN, edgecolor='white', linewidth=0.5)
    bars_s = ax.bar(x + w/2, survived, w, label='Survived', color=C_RED, edgecolor='white', linewidth=0.5, alpha=0.8)

    for i, (k, t, r) in enumerate(zip(killed, total, ratios)):
        ax.text(i, t + 1, f'{r:.1%}', ha='center', fontweight='bold', fontsize=10, color=C_DARK)

    ax.set_ylabel('Number of Mutants')
    ax.set_title('Mutation Kill Ratio by Source Module')
    ax.set_xticks(x)
    ax.set_xticklabels(modules)
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.set_ylim(0, max(total) + 15)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig1_mutation_kill_ratio.png'), dpi=200)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════
# FIGURE 2: Overall Mutation Summary (Pie)
# ═══════════════════════════════════════════════════════════════
def fig2_mutation_pie():
    labels = ['Killed (229)', 'Survived (104)']
    sizes = [229, 104]
    colors = [C_GREEN, C_RED]
    explode = (0.03, 0.06)

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', startangle=140, textprops={'fontsize': 12},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    for t in autotexts:
        t.set_fontweight('bold')
    ax.set_title('Overall Mutation Adequacy (333 Mutants)')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig2_mutation_pie.png'), dpi=200)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════
# FIGURE 3: Mutation Operator Distribution
# ═══════════════════════════════════════════════════════════════
def fig3_operator_distribution():
    operators = ['const', 'arith', 'rel', 'bool', 'bit', 'assign', 'shift']
    counts = [98, 52, 48, 36, 44, 28, 27]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(operators, counts, color=[C_BLUE, C_PURPLE, C_AMBER, C_GREEN, C_TEAL, C_RED, C_GRAY],
                   edgecolor='white', linewidth=0.5, height=0.6)
    for bar, c in zip(bars, counts):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                str(c), va='center', fontweight='bold', fontsize=10)
    ax.set_xlabel('Number of Mutants')
    ax.set_title('Distribution of Mutation Operators Applied')
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig3_operator_distribution.png'), dpi=200)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════
# FIGURE 4: Performance – Windows vs Ubuntu Throughput
# ═══════════════════════════════════════════════════════════════
def fig4_performance_throughput():
    runs = [1, 2, 3, 4, 5]
    win = [16.777, 16.777, 16.026, 16.777, 19.174]
    wsl = [51.131, 53.687, 53.687, 51.131, 51.131]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(runs, win, 'o-', color=C_WIN, linewidth=2.5, markersize=8, label='Windows (MSVC)', zorder=5)
    ax.plot(runs, wsl, 's-', color=C_WSL, linewidth=2.5, markersize=8, label='Ubuntu 24.04 (Linux)', zorder=5)
    ax.fill_between(runs, win, alpha=0.15, color=C_WIN)
    ax.fill_between(runs, wsl, alpha=0.15, color=C_WSL)
    ax.set_xlabel('Trial Run')
    ax.set_ylabel('Throughput (Gbps)')
    ax.set_title('Loopback Throughput: Windows vs. Ubuntu 24.04')
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.set_ylim(0, 60)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig4_performance_throughput.png'), dpi=200)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════
# FIGURE 5: White-Box Coverage by Module
# ═══════════════════════════════════════════════════════════════
def fig5_whitebox_coverage():
    modules = ['assembler.rs', 'ipv4.rs', 'udp.rs', 'tcp.rs', 'Overall']
    region = [98.28, 90.12, 90.98, 72.58, 80.63]
    func   = [98.41, 96.10, 91.67, 83.70, 82.35]
    line   = [98.46, 90.65, 87.45, 74.45, 81.00]

    x = np.arange(len(modules))
    w = 0.25

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(x - w, region, w, label='Region', color=C_BLUE, edgecolor='white', linewidth=0.5)
    ax.bar(x,     func,   w, label='Function', color=C_PURPLE, edgecolor='white', linewidth=0.5)
    ax.bar(x + w, line,   w, label='Line', color=C_TEAL, edgecolor='white', linewidth=0.5)

    ax.axhline(y=80, color=C_AMBER, linestyle='--', linewidth=1, alpha=0.7, label='80% Target')
    ax.set_ylabel('Coverage (%)')
    ax.set_title('White-Box Coverage by Module (cargo-llvm-cov)')
    ax.set_xticks(x)
    ax.set_xticklabels(modules, rotation=15)
    ax.legend(frameon=True, fancybox=True, shadow=True, ncol=2)
    ax.set_ylim(60, 105)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig5_whitebox_coverage.png'), dpi=200)
    plt.close(fig)



# ═══════════════════════════════════════════════════════════════
# FIGURE 7: Input Space Partition Model
# ═══════════════════════════════════════════════════════════════
def fig7_partition_heatmap():
    buf_lens = ['0', '7', '8', '12']
    len_fields = ['0', '4', '8', '12', '20']
    # pass_count[buf][len] = how many of the 12 combos (3 cksum × 2 ip × 2 rx ÷ filtering) pass
    data = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 4, 0, 0],
        [0, 0, 4, 4, 0],
    ])

    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(data, cmap='YlGn', aspect='auto', vmin=0, vmax=6)
    ax.set_xticks(np.arange(len(len_fields)))
    ax.set_yticks(np.arange(len(buf_lens)))
    ax.set_xticklabels(len_fields)
    ax.set_yticklabels(buf_lens)
    ax.set_xlabel('UDP Length Field Value')
    ax.set_ylabel('Buffer Length (bytes)')
    ax.set_title('Input Space Partition: Passing Test Cases')

    for i in range(len(buf_lens)):
        for j in range(len(len_fields)):
            ax.text(j, i, str(data[i, j]), ha='center', va='center',
                    fontweight='bold', fontsize=12,
                    color='white' if data[i, j] > 3 else C_DARK)

    fig.colorbar(im, ax=ax, label='Passing cases (parse=true)')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig7_partition_heatmap.png'), dpi=200)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════
# FIGURE 8: Safety – Unsafe Code Distribution
# ═══════════════════════════════════════════════════════════════
def fig8_unsafe_inventory():
    files = ['tuntap_interface.rs', 'bpf.rs', 'raw_socket.rs', 'mod.rs']
    counts = [6, 5, 5, 2]

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = [C_RED, C_AMBER, C_AMBER, C_GREEN]
    wedges, texts, autotexts = ax.pie(
        counts, labels=files, colors=colors,
        autopct='%1.0f%%', startangle=90,
        textprops={'fontsize': 10},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    for t in autotexts:
        t.set_fontweight('bold')
    ax.set_title('Unsafe Code Distribution (18 Total Occurrences)')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig8_unsafe_inventory.png'), dpi=200)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════
# FIGURE 9: Fuzzing Coverage Progression
# ═══════════════════════════════════════════════════════════════
def fig9_fuzzing_coverage():
    # Simplified data from the fuzzing log
    execs = [0, 100, 500, 1000, 5000, 10000, 50000, 100000, 200000, 380000]
    cov   = [0, 359, 522, 532,  567,  593,   636,   665,    739,    759]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(execs, cov, 'o-', color=C_PURPLE, linewidth=2, markersize=5)
    ax.fill_between(execs, cov, alpha=0.15, color=C_PURPLE)
    ax.set_xlabel('Fuzzer Executions')
    ax.set_ylabel('Unique Coverage Edges')
    ax.set_title('libFuzzer Coverage Progression (packet\\_parser target)')
    ax.set_xscale('symlog', linthresh=100)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig9_fuzzing_coverage.png'), dpi=200)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════
# FIGURE 11: Enhanced Coverage (IPv4 Combinatorial + Microbench)
# ═══════════════════════════════════════════════════════════════
def fig11_enhanced_coverage():
    suites = ['IPv4 Combinatorial', 'Microbench']
    coverage = [98.53, 98.76]
    missed = [4, 2]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    # Bar chart
    bars = ax1.bar(suites, coverage, color=[C_BLUE, C_TEAL], edgecolor='white', linewidth=0.5, width=0.5)
    ax1.axhline(y=95, color=C_AMBER, linestyle='--', linewidth=1, alpha=0.7)
    for bar, c in zip(bars, coverage):
        ax1.text(bar.get_x() + bar.get_width()/2, c + 0.3, f'{c}%',
                ha='center', fontweight='bold', fontsize=11)
    ax1.set_ylabel('Coverage (%)')
    ax1.set_title('Enhanced Suite Coverage')
    ax1.set_ylim(90, 101)

    # Missed regions
    ax2.bar(suites, missed, color=[C_RED, C_AMBER], edgecolor='white', linewidth=0.5, width=0.5)
    for i, m in enumerate(missed):
        ax2.text(i, m + 0.1, str(m), ha='center', fontweight='bold', fontsize=11)
    ax2.set_ylabel('Missed Regions')
    ax2.set_title('Regions Not Covered')
    ax2.set_ylim(0, 6)

    fig.suptitle('White-Box Adequacy: Enhanced Suites', fontweight='bold', fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig11_enhanced_coverage.png'), dpi=200)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════
# FIGURE 12: Test Suite Summary Dashboard
# ═══════════════════════════════════════════════════════════════
def fig12_test_dashboard():
    suites = ['Mutation\nAdequacy', 'Input\nPartition', 'Conformance', 'Fuzzing', 'Performance',
              'White-Box\nCoverage', 'Safety', 'IPv4\nCombinatorial', 'Microbench']
    scores = [69.67, 100, 100, 100, 100, 80.63, 100, 100, 100]
    colors_list = []
    for s in scores:
        if s >= 95: colors_list.append(C_GREEN)
        elif s >= 80: colors_list.append(C_AMBER)
        else: colors_list.append(C_RED)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(suites, scores, color=colors_list, edgecolor='white', linewidth=1, width=0.65)
    ax.axhline(y=80, color=C_GRAY, linestyle='--', linewidth=1, alpha=0.5)
    for bar, s in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, s + 1.5, f'{s:.1f}%',
                ha='center', fontweight='bold', fontsize=9, color=C_DARK)
    ax.set_ylabel('Score / Pass Rate (%)')
    ax.set_title('Quality Assessment Dashboard — All Test Suites')
    ax.set_ylim(0, 115)

    legend_items = [
        mpatches.Patch(color=C_GREEN, label='≥95%'),
        mpatches.Patch(color=C_AMBER, label='80–94%'),
        mpatches.Patch(color=C_RED, label='<80%'),
    ]
    ax.legend(handles=legend_items, frameon=True, fancybox=True, shadow=True, loc='upper right')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig12_test_dashboard.png'), dpi=200)
    plt.close(fig)



if __name__ == '__main__':
    print("Generating figures...")
    fig1_mutation_kill_ratio()
    print("  [1/14] Mutation kill ratio")
    fig2_mutation_pie()
    print("  [2/14] Mutation pie chart")
    fig3_operator_distribution()
    print("  [3/14] Operator distribution")
    fig4_performance_throughput()
    print("  [4/14] Performance throughput")
    fig5_whitebox_coverage()
    print("  [5/14] White-box coverage")

    fig7_partition_heatmap()
    print("  [7/14] Partition heatmap")
    fig8_unsafe_inventory()
    print("  [8/14] Unsafe inventory")
    fig9_fuzzing_coverage()
    print("  [9/14] Fuzzing coverage progression")

    fig11_enhanced_coverage()
    print("  [11/14] Enhanced coverage")
    fig12_test_dashboard()
    print("  [12/14] Test dashboard")

    print(f"\nAll figures saved to: {OUT}")
