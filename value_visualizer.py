#!/usr/bin/env python3
"""
Price-Performance Visualization Module
Creates charts for memory value analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import numpy as np
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f8f9fa'


class ValueVisualizer:
    """Visualize price-performance metrics"""

    def __init__(self, data_file: str = 'performance_analysis.json'):
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        self.df = pd.DataFrame(self.data['price_performance_metrics'])

        # Colors for each product
        self.colors = {
            'DDR5 UDIMM': '#3498db',
            'DDR5 RDIMM': '#2980b9',
            'DDR4 UDIMM': '#2ecc71',
            'LPDDR4X': '#e74c3c',
            'GDDR6': '#f39c12'
        }

        self.bar_colors = [self.colors.get(p.split()[0] + ' ' + p.split()[1], '#95a5a6')
                          for p in self.df['product']]

    def plot_value_quadrant(self, save_path: str = 'charts/value_quadrant.png'):
        """
        Value Quadrant Chart
        X-axis: Price | Y-axis: Performance
        Shows best value (low price, high performance)
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        # Normalize for visualization
        max_price = self.df['price_usd'].max()
        max_perf = self.df['composite_score'].max()

        x = self.df['price_usd'] / max_price * 100
        y = self.df['composite_score']

        # Create scatter plot
        scatter = ax.scatter(x, y, s=self.df['capacity_gb'] * 50,
                           c=self.bar_colors, alpha=0.7, edgecolors='black', linewidth=2)

        # Add labels
        for i, row in self.df.iterrows():
            ax.annotate(row['product'], (x[i], y[i]),
                       fontsize=10, ha='center', va='bottom',
                       xytext=(0, 8), textcoords='offset points')

        # Quadrant lines (medians)
        ax.axvline(x=x.median(), color='gray', linestyle='--', alpha=0.5)
        ax.axhline(y=y.median(), color='gray', linestyle='--', alpha=0.5)

        # Quadrant labels
        ax.text(x.max() * 0.75, y.max() * 0.9, 'Premium\nPerformance',
               fontsize=12, ha='center', style='italic', color='#7f8c8d')
        ax.text(x.min() * 1.5, y.max() * 0.9, 'BEST VALUE\nLow $, High Perf',
               fontsize=12, ha='center', style='italic', color='#27ae60', fontweight='bold')
        ax.text(x.min() * 1.5, y.min() * 1.5, 'Budget',
               fontsize=12, ha='center', style='italic', color='#7f8c8d')
        ax.text(x.max() * 0.75, y.min() * 1.5, 'Overpriced',
               fontsize=12, ha='center', style='italic', color='#c0392b')

        # Size legend
        sizes = [8, 16, 32]
        for size in sizes:
            ax.scatter([], [], s=size * 50, c='gray', alpha=0.5, edgecolors='black')
        ax.legend([f'{s}GB' for s in sizes], loc='upper left',
                 title='Capacity', fontsize=10)

        ax.set_xlabel('Normalized Price (Lower is Better)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Composite Performance Score', fontsize=12, fontweight='bold')
        ax.set_title('Memory Value Quadrant Analysis\n(April 2026)',
                    fontsize=14, fontweight='bold')
        ax.set_ylim(y.min() * 0.9, y.max() * 1.1)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")

    def plot_price_per_performance(self, save_path: str = 'charts/price_per_performance.png'):
        """
        Price per Performance Comparison
        Lower is better
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        products = [p.replace(' ', '\n') for p in self.df['product']]

        # Price per GB
        bars1 = ax1.bar(range(len(self.df)), self.df['price_per_gb'],
                       color=self.bar_colors, edgecolor='black', linewidth=1.5)
        ax1.set_xticks(range(len(self.df)))
        ax1.set_xticklabels(products, rotation=45, ha='right')
        ax1.set_ylabel('Price per GB ($)', fontsize=12, fontweight='bold')
        ax1.set_title('Price per Capacity\n(Lower is Better)', fontsize=12, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar, val in zip(bars1, self.df['price_per_gb']):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    f'${val:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Price per Composite Score
        bars2 = ax2.bar(range(len(self.df)), self.df['price_per_composite'],
                       color=self.bar_colors, edgecolor='black', linewidth=1.5)
        ax2.set_xticks(range(len(self.df)))
        ax2.set_xticklabels(products, rotation=45, ha='right')
        ax2.set_ylabel('Price per Performance Point ($)', fontsize=12, fontweight='bold')
        ax2.set_title('Price per Performance Score\n(Lower is Better)', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

        for bar, val in zip(bars2, self.df['price_per_composite']):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'${val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")

    def plot_bandwidth_efficiency(self, save_path: str = 'charts/bandwidth_efficiency.png'):
        """
        Bandwidth vs Price Analysis
        Shows $ per GB/s throughput
        """
        fig, ax = plt.subplots(figsize=(12, 7))

        products = [p.replace(' ', '\n').replace('4800/5600', '') for p in self.df['product']]

        x = np.arange(len(self.df))
        width = 0.35

        # Bandwidth (left axis)
        bars1 = ax.bar(x - width/2, self.df['bandwidth_gbps'], width,
                      label='Bandwidth (GB/s)', color=self.bar_colors,
                      edgecolor='black', linewidth=1.5, alpha=0.8)

        ax.set_ylabel('Bandwidth (GB/s)', fontsize=12, fontweight='bold', color='#2c3e50')
        ax.set_xticks(x)
        ax.set_xticklabels(products, rotation=45, ha='right')
        ax.set_title('Memory Bandwidth Efficiency Analysis\n(April 2026)',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(axis='y', alpha=0.3)

        # Price per GB/s (right axis)
        ax2 = ax.twinx()
        bars2 = ax2.bar(x + width/2, self.df['price_per_gbps'], width,
                       label='$ per GB/s', color='#34495e',
                       edgecolor='black', linewidth=1.5, alpha=0.6)
        ax2.set_ylabel('Price per GB/s ($)', fontsize=12, fontweight='bold', color='#34495e')
        ax2.legend(loc='upper right')

        # Value labels on bars
        for bar, val in zip(bars1, self.df['bandwidth_gbps']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                   f'{val:.0f}', ha='center', va='bottom', fontsize=9)

        for bar, val in zip(bars2, self.df['price_per_gbps']):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'${val:.1f}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")

    def plot_workload_recommendations(self, save_path: str = 'charts/workload_recommendations.png'):
        """
        Workload-based Recommendations
        Shows which memory is best for different use cases
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        # Define workload scores (0-100 for each product)
        workloads = {
            'Gaming': {
                'DDR5 UDIMM 16GB 4800/5600': 95,
                'DDR5 RDIMM 32GB 4800/5600': 90,
                'DDR4 UDIMM 16GB 3200': 85,
                'LPDDR4X 8GB': 70,
                'GDDR6 8GB': 100  # Best for gaming
            },
            'Content Creation': {
                'DDR5 UDIMM 16GB 4800/5600': 95,
                'DDR5 RDIMM 32GB 4800/5600': 100,  # Best - high capacity + bandwidth
                'DDR4 UDIMM 16GB 3200': 75,
                'LPDDR4X 8GB': 60,
                'GDDR6 8GB': 80
            },
            'Server/AI': {
                'DDR5 UDIMM 16GB 4800/5600': 85,
                'DDR5 RDIMM 32GB 4800/5600': 100,  # Best - ECC + capacity
                'DDR4 UDIMM 16GB 3200': 70,
                'LPDDR4X 8GB': 40,
                'GDDR6 8GB': 95  # Good for AI inference
            },
            'Mobile/Laptop': {
                'DDR5 UDIMM 16GB 4800/5600': 80,
                'DDR5 RDIMM 32GB 4800/5600': 60,
                'DDR4 UDIMM 16GB 3200': 75,
                'LPDDR4X 8GB': 100,  # Best for mobile
                'GDDR6 8GB': 50
            },
            'Budget PC': {
                'DDR5 UDIMM 16GB 4800/5600': 60,
                'DDR5 RDIMM 32GB 4800/5600': 40,
                'DDR4 UDIMM 16GB 3200': 100,  # Best value
                'LPDDR4X 8GB': 80,
                'GDDR6 8GB': 50
            }
        }

        products = list(self.df['product'])
        x = np.arange(len(workloads))
        width = 0.15

        # Find best product for each workload
        best_scores = {w: max(scores.items(), key=lambda x: x[1])[0]
                      for w, scores in workloads.items()}

        for i, product in enumerate(products):
            scores = [workloads[w][product] for w in workloads]
            color = '#27ae60' if [best_scores[w] for w in workloads].count(product) > 0 else self.bar_colors[i]
            ax.bar(x + i * width, scores, width, label=product.split()[0] + ' ' + product.split()[1],
                  color=color, alpha=0.8, edgecolor='black', linewidth=0.5)

        ax.set_xlabel('Workload Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Suitability Score (0-100)', fontsize=12, fontweight='bold')
        ax.set_title('Memory Recommendation by Workload\n(Green = Best Choice)',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels(workloads.keys(), fontsize=11)
        ax.legend(loc='upper left', fontsize=9, ncol=2)
        ax.set_ylim(0, 110)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")

    def plot_power_efficiency(self, save_path: str = 'charts/power_efficiency.png'):
        """
        Power Efficiency Analysis
        Performance per Watt
        """
        fig, ax = plt.subplots(figsize=(12, 7))

        products = [p.replace(' ', '\n').replace('4800/5600', '') for p in self.df['product']]

        bars = ax.bar(range(len(self.df)), self.df['performance_per_watt'],
                     color=self.bar_colors, edgecolor='black', linewidth=2)

        ax.set_xticks(range(len(self.df)))
        ax.set_xticklabels(products, rotation=45, ha='right')
        ax.set_ylabel('Performance per Watt (GB/s per W)', fontsize=12, fontweight='bold')
        ax.set_title('Power Efficiency Analysis\n(Higher is Better)',
                    fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        # Value labels
        for bar, val in zip(bars, self.df['performance_per_watt']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                   f'{val:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Highlight winner
        winner_idx = self.df['performance_per_watt'].idxmax()
        bars[winner_idx].set_edgecolor('#27ae60')
        bars[winner_idx].set_linewidth(4)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {save_path}")


def main():
    """Generate all value analysis charts"""
    print("Generating price-performance visualizations...")
    print("=" * 50)

    viz = ValueVisualizer()

    # Generate all charts
    viz.plot_value_quadrant()
    viz.plot_price_per_performance()
    viz.plot_bandwidth_efficiency()
    viz.plot_workload_recommendations()
    viz.plot_power_efficiency()

    print("=" * 50)
    print("✓ All visualizations complete!")


if __name__ == '__main__':
    main()
