#!/usr/bin/env python3
"""
Memory Price Visualizer
Creates charts and analysis for memory price tracking
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
from datetime import datetime
import numpy as np

# Set style for better looking charts
plt.style.use('seaborn-v0_8-darkgrid')

class MemoryPriceVisualizer:
    """Create visualizations for memory price data"""

    def __init__(self, data_file='data.json'):
        with open(data_file, 'r') as f:
            self.data = json.load(f)

        # Convert historical data to DataFrame
        if 'historical' in self.data:
            hist_data = []
            for week in self.data['historical']:
                row = {'date': week['date'], 'week': week['week']}
                for product, prices in week['products'].items():
                    row[product] = prices['price']
                hist_data.append(row)

            self.df = pd.DataFrame(hist_data)
            self.df['date'] = pd.to_datetime(self.df['date'])
        else:
            print("No historical data found")
            self.df = None

    def plot_price_trends(self, save_path='charts/price_trends.png'):
        """Create main price trend chart"""
        if self.df is None:
            print("No data available for plotting")
            return

        fig, ax = plt.subplots(figsize=(14, 8))

        # Plot each product
        products = ['DDR5 UDIMM 16GB', 'DDR5 RDIMM 32GB', 'DDR4 UDIMM 16GB',
                   'LPDDR4X 8GB', 'GDDR6 8GB']
        colors = ['#2ecc71', '#e74c3c', '#3498db', '#9b59b6', '#f39c12']

        for product, color in zip(products, colors):
            if product in self.df.columns:
                ax.plot(self.df['date'], self.df[product],
                       label=product, linewidth=2, color=color)

        # Add Q1 2026 marker
        q1_2026 = pd.Timestamp('2026-01-01')
        ax.axvline(q1_2026, color='gray', linestyle='--', alpha=0.5, label='Q1 2026 Start')

        # Add trend annotation
        ax.annotate('AI Server Demand Surge',
                   xy=(pd.Timestamp('2025-12-01'), 800),
                   xytext=(pd.Timestamp('2025-08-01'), 1000),
                   arrowprops=dict(arrowstyle='->', color='red'),
                   fontsize=11, color='red')

        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price (USD)', fontsize=12)
        ax.set_title('DRAM/Memory Price Trends - Weekly Spot Prices\n'
                    'Benchmark for Perpetual Futures Contracts',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', framealpha=0.9)
        ax.grid(True, alpha=0.3)

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()

    def plot_price_volatility(self, save_path='charts/price_volatility.png'):
        """Create volatility chart"""
        if self.df is None:
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        products = ['DDR5 UDIMM 16GB', 'DDR5 RDIMM 32GB', 'DDR4 UDIMM 16GB']

        # Calculate rolling volatility (4-week window)
        for product in products:
            if product in self.df.columns:
                volatility = self.df[product].pct_change().rolling(4).std() * np.sqrt(52) * 100
                ax1.plot(self.df['date'], volatility, label=product, linewidth=2)

        ax1.set_ylabel('Annualized Volatility (%)', fontsize=12)
        ax1.set_title('Memory Price Volatility (4-Week Rolling)', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        # Price spread (high-low) - using current market data
        market_data = self.data.get('market_data', {})
        products = market_data.get('products', [])
        spreads = [p['weekly_high'] - p['weekly_low'] for p in products]

        ax2.bar(range(len(products)), spreads,
                   color=['#2ecc71', '#e74c3c', '#3498db', '#9b59b6', '#f39c12'])
        ax2.set_ylabel('Price Spread ($)', fontsize=12)
        ax2.set_title('Weekly High-Low Spread (Current Week)', fontsize=12, fontweight='bold')
        ax2.set_xticks(range(len(products)))
        ax2.set_xticklabels([p['product'].replace(' ', '\n') for p in products], rotation=45, ha='right')

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()

    def plot_product_comparison(self, save_path='charts/product_comparison.png'):
        """Create product price comparison chart"""
        market_data = self.data.get('market_data', {})
        products = market_data.get('products', [])

        fig, ax = plt.subplots(figsize=(12, 7))

        product_names = [p['product'] for p in products]
        spot_prices = [p['spot_price'] for p in products]
        contract_prices = [p['contract_price'] for p in products]
        weekly_highs = [p['weekly_high'] for p in products]
        weekly_lows = [p['weekly_low'] for p in products]

        x = np.arange(len(product_names))
        width = 0.2

        ax.bar(x - width*1.5, weekly_highs, width, label='Weekly High',
               color='#95a5a6', alpha=0.8)
        ax.bar(x - width*0.5, spot_prices, width, label='Spot Price',
               color='#2ecc71', alpha=0.8)
        ax.bar(x + width*0.5, contract_prices, width, label='Contract Price',
               color='#3498db', alpha=0.8)
        ax.bar(x + width*1.5, weekly_lows, width, label='Weekly Low',
               color='#e74c3c', alpha=0.8)

        ax.set_xlabel('Memory Product', fontsize=12)
        ax.set_ylabel('Price (USD)', fontsize=12)
        ax.set_title('Memory Product Price Comparison\nWeek of April 6, 2026',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(product_names, rotation=45, ha='right')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for i, (spot, contract) in enumerate(zip(spot_prices, contract_prices)):
            ax.text(i - width*0.5, spot + 5, f'${spot:.0f}',
                   ha='center', va='bottom', fontsize=8)
            ax.text(i + width*0.5, contract + 5, f'${contract:.0f}',
                   ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()

    def plot_forecast_comparison(self, save_path='charts/forecast_comparison.png'):
        """Create forecast comparison with existing indices"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Forecast data
        quarters = ['Q4 2025', 'Q1 2026', 'Q2 2026', 'Q3 2026 (Est)']
        ddr4_forecast = [100, 195, 310, 380]
        ddr5_forecast = [120, 220, 355, 450]

        x = np.arange(len(quarters))
        width = 0.35

        bars1 = ax.bar(x - width/2, ddr4_forecast, width, label='DDR4 16GB Contract Price',
                       color='#3498db', alpha=0.8)
        bars2 = ax.bar(x + width/2, ddr5_forecast, width, label='DDR5 16GB Contract Price',
                       color='#2ecc71', alpha=0.8)

        # Add forecast annotations
        ax.annotate('+95% QoQ', xy=(1, ddr4_forecast[1]), xytext=(1, ddr4_forecast[1]+40),
                   arrowprops=dict(arrowstyle='->', color='blue'),
                   ha='center', fontsize=10, color='blue')
        ax.annotate('+63% QoQ', xy=(2, ddr5_forecast[2]), xytext=(2, ddr5_forecast[2]+50),
                   arrowprops=dict(arrowstyle='->', color='green'),
                   ha='center', fontsize=10, color='green')

        ax.set_xlabel('Quarter', fontsize=12)
        ax.set_ylabel('Contract Price Index (Base=Q4 2025=100)', fontsize=12)
        ax.set_title('DRAM Contract Price Forecast vs Market Indices\n'
                    'Source: TrendForce Market Intelligence',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(quarters)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')

        # Add y-axis on right for comparison with other indices
        ax2 = ax.twinx()
        ax2.set_ylabel('vs DRAMeXchange Index', fontsize=10)
        ax2.set_ylim(0, 500)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()

    def generate_summary_stats(self):
        """Generate summary statistics"""
        if self.df is None:
            return {}

        stats = {}

        for product in self.df.columns:
            if product not in ['date', 'week']:
                prices = self.df[product].dropna()
                stats[product] = {
                    'current': prices.iloc[-1],
                    'ytd_change': ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100,
                    'min': prices.min(),
                    'max': prices.max(),
                    'volatility': prices.pct_change().std() * np.sqrt(52) * 100
                }

        return stats

def main():
    import os
    os.makedirs('/Users/startup/memory_price_tracker/charts', exist_ok=True)

    viz = MemoryPriceVisualizer('/Users/startup/memory_price_tracker/data.json')

    print("Generating visualizations...")
    print("=" * 50)

    viz.plot_price_trends()
    viz.plot_price_volatility()
    viz.plot_product_comparison()
    viz.plot_forecast_comparison()

    print("\n" + "=" * 50)
    print("Summary Statistics:")
    print("-" * 50)

    stats = viz.generate_summary_stats()
    for product, values in stats.items():
        print(f"\n{product}:")
        print(f"  Current Price: ${values['current']:.2f}")
        print(f"  YTD Change: {values['ytd_change']:+.1f}%")
        print(f"  52W Range: ${values['min']:.2f} - ${values['max']:.2f}")
        print(f"  Volatility: {values['volatility']:.1f}%")

    print("\n✅ All visualizations saved to charts/")

if __name__ == "__main__":
    main()
