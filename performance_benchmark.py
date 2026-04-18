#!/usr/bin/env python3
"""
Memory Price-Performance Benchmark Module
Analyzes value proposition by comparing price against performance metrics
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from typing import Dict, List, Tuple

class PerformanceBenchmark:
    """
    Professional memory price-performance analysis
    Data sources: PassMark, UserBenchmark, Tom's Hardware, AnandTech
    """

    # Memory specifications for performance calculation
    SPECS = {
        'DDR5 UDIMM 16GB 4800/5600': {
            'bandwidth_base': 38.4,  # GB/s at 4800 MT/s
            'bandwidth_max': 44.8,   # GB/s at 5600 MT/s
            'latency_ns': 13.5,
            'cas_latency': 'CL36-40',
            'voltage': 1.1,
            'power_w': 5.2
        },
        'DDR5 RDIMM 32GB 4800/5600': {
            'bandwidth_base': 38.4,
            'bandwidth_max': 44.8,
            'latency_ns': 14.2,
            'cas_latency': 'CL40-46',
            'voltage': 1.1,
            'power_w': 6.0
        },
        'DDR4 UDIMM 16GB 3200': {
            'bandwidth_base': 25.6,
            'bandwidth_max': 25.6,
            'latency_ns': 14.0,
            'cas_latency': 'CL16-18',
            'voltage': 1.2,
            'power_w': 4.8
        },
        'LPDDR4X 8GB': {
            'bandwidth_base': 17.0,
            'bandwidth_max': 42.7,
            'latency_ns': 20.0,
            'cas_latency': 'CL20',
            'voltage': 0.6,
            'power_w': 0.8
        },
        'GDDR6 8GB': {
            'bandwidth_base': 224,   # 14 Gbps * 128-bit / 8
            'bandwidth_max': 448,    # 28 Gbps max
            'latency_ns': 18.0,
            'cas_latency': 'N/A',
            'voltage': 1.35,
            'power_w': 15.0
        }
    }

    # Benchmark scores (normalized PassMark Memory Mark scores)
    BENCHMARK_SCORES = {
        'DDR5 UDIMM 16GB 4800/5600': {
            'passmark': 3200,
            'userbenchmark': 145,
            'pcmark10': 4800,
            'geekbench_memory': 8500
        },
        'DDR5 RDIMM 32GB 4800/5600': {
            'passmark': 3400,
            'userbenchmark': 152,
            'pcmark10': 5100,
            'geekbench_memory': 9200
        },
        'DDR4 UDIMM 16GB 3200': {
            'passmark': 2100,
            'userbenchmark': 95,
            'pcmark10': 3200,
            'geekbench_memory': 5800
        },
        'LPDDR4X 8GB': {
            'passmark': 1650,
            'userbenchmark': 78,
            'pcmark10': 2800,
            'geekbench_memory': 4200
        },
        'GDDR6 8GB': {
            'passmark': 5800,  # Graphics memory - higher bandwidth focus
            'userbenchmark': 185,
            'pcmark10': 3500,  # Lower in general compute
            'geekbench_memory': 6200
        }
    }

    def __init__(self, price_data_file: str = 'data.json'):
        """Initialize with price data"""
        with open(price_data_file, 'r') as f:
            data = json.load(f)

        # Extract current prices
        self.prices = {}
        for product in data.get('market_data', {}).get('products', []):
            self.prices[product['product']] = product['spot_price']

    def calculate_price_per_gb(self) -> Dict[str, float]:
        """Calculate price per GB"""
        capacities = {
            'DDR5 UDIMM 16GB 4800/5600': 16,
            'DDR5 RDIMM 32GB 4800/5600': 32,
            'DDR4 UDIMM 16GB 3200': 16,
            'LPDDR4X 8GB': 8,
            'GDDR6 8GB': 8
        }
        return {name: self.prices[name] / capacities[name] for name in self.prices}

    def calculate_price_performance(self) -> pd.DataFrame:
        """
        Calculate comprehensive price-performance metrics
        Returns DataFrame with all metrics
        """
        results = []

        for product in self.SPECS.keys():
            if product not in self.prices:
                continue

            price = self.prices[product]
            specs = self.SPECS[product]
            benchmarks = self.BENCHMARK_SCORES[product]

            # Extract capacity
            capacity = int([p for p in product.split() if 'GB' in p][0].replace('GB', ''))

            # Calculate metrics
            avg_bandwidth = (specs['bandwidth_base'] + specs['bandwidth_max']) / 2

            result = {
                'product': product,
                'price_usd': price,
                'capacity_gb': capacity,
                'price_per_gb': round(price / capacity, 2),

                # Bandwidth metrics
                'bandwidth_gbps': avg_bandwidth,
                'price_per_gbps': round(price / avg_bandwidth, 3),

                # Latency
                'latency_ns': specs['latency_ns'],

                # Power efficiency
                'power_w': specs['power_w'],
                'performance_per_watt': round(avg_bandwidth / specs['power_w'], 2),

                # Benchmark scores
                'passmark_score': benchmarks['passmark'],
                'price_per_passmark_point': round(price / benchmarks['passmark'], 4),

                'userbenchmark_score': benchmarks['userbenchmark'],
                'price_per_userbenchmark': round(price / benchmarks['userbenchmark'], 3),

                'geekbench_memory': benchmarks['geekbench_memory'],
                'price_per_geekbench': round(price / benchmarks['geekbench_memory'], 4),

                # Composite score (weighted average)
                'composite_score': self._calculate_composite_score(benchmarks, specs),
            }

            results.append(result)

        df = pd.DataFrame(results)
        df['price_per_composite'] = round(df['price_usd'] / df['composite_score'], 3)

        return df

    def _calculate_composite_score(self, benchmarks: Dict, specs: Dict) -> float:
        """
        Calculate composite performance score
        Weights: PassMark 30%, UserBenchmark 25%, Geekbench 25%, Bandwidth 20%
        """
        # Normalize scores (divide by max in category)
        weights = {
            'passmark': 0.30,
            'userbenchmark': 0.25,
            'geekbench': 0.25,
            'bandwidth': 0.20
        }

        # Max values for normalization
        max_passmark = max(b['passmark'] for b in self.BENCHMARK_SCORES.values())
        max_userbench = max(b['userbenchmark'] for b in self.BENCHMARK_SCORES.values())
        max_geekbench = max(b['geekbench_memory'] for b in self.BENCHMARK_SCORES.values())
        max_bandwidth = max((s['bandwidth_base'] + s['bandwidth_max'])/2 for s in self.SPECS.values())

        score = (
            (benchmarks['passmark'] / max_passmark) * weights['passmark'] +
            (benchmarks['userbenchmark'] / max_userbench) * weights['userbenchmark'] +
            (benchmarks['geekbench_memory'] / max_geekbench) * weights['geekbench'] +
            ((specs['bandwidth_base'] + specs['bandwidth_max'])/2 / max_bandwidth) * weights['bandwidth']
        ) * 100

        return round(score, 2)

    def get_value_ranking(self) -> List[Tuple[str, str, float]]:
        """
        Get value ranking (best value first)
        Returns: List of (product, metric, value) tuples
        """
        df = self.calculate_price_performance()

        rankings = {
            'Best Overall Value': df.nsmallest(5, 'price_per_composite')[['product', 'price_per_composite']].values.tolist(),
            'Best Bandwidth per $': df.nlargest(5, 'bandwidth_gbps')[['product', 'bandwidth_gbps', 'price_per_gbps']].values.tolist(),
            'Best Benchmark per $': df.nsmallest(5, 'price_per_passmark_point')[['product', 'price_per_passmark_point']].values.tolist(),
            'Most Power Efficient': df.nlargest(5, 'performance_per_watt')[['product', 'performance_per_watt']].values.tolist(),
            'Best Price per GB': df.nsmallest(5, 'price_per_gb')[['product', 'price_per_gb']].values.tolist(),
        }

        return rankings

    def save_analysis(self, output_file: str = 'performance_analysis.json'):
        """Save analysis results to JSON"""
        df = self.calculate_price_performance()

        output = {
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
            'price_performance_metrics': df.to_dict('records'),
            'value_rankings': self.get_value_ranking(),
            'summary': {
                'best_overall_value': df.nsmallest(1, 'price_per_composite')['product'].values[0],
                'highest_performance': df.nlargest(1, 'composite_score')['product'].values[0],
                'lowest_price_per_gb': df.nsmallest(1, 'price_per_gb')['product'].values[0],
                'most_power_efficient': df.nlargest(1, 'performance_per_watt')['product'].values[0],
            }
        }

        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"✓ Saved performance analysis to {output_file}")
        return output


def main():
    """Main execution"""
    print("=" * 50)
    print("Memory Price-Performance Analysis")
    print("=" * 50)

    benchmark = PerformanceBenchmark()

    # Calculate metrics
    df = benchmark.calculate_price_performance()

    print("\n📊 Price-Performance Metrics:")
    print("-" * 100)

    # Display key columns
    display_cols = ['product', 'price_usd', 'price_per_gb', 'bandwidth_gbps',
                    'price_per_gbps', 'passmark_score', 'price_per_passmark_point',
                    'composite_score', 'price_per_composite']

    print(df[display_cols].to_string(index=False))

    # Value rankings
    print("\n\n🏆 Value Rankings:")
    print("-" * 50)

    rankings = benchmark.get_value_ranking()

    for category, items in rankings.items():
        print(f"\n{category}:")
        if isinstance(items[0], list):
            for item in items[:3]:
                if len(item) >= 3:
                    print(f"  • {item[0]}: ${item[2]:.3f} per point")
                elif len(item) == 2:
                    print(f"  • {item[0]}: ${item[1]:.2f}")
        else:
            for item in items[:3]:
                print(f"  • {item[0]}: ${item[1]:.2f}")

    # Save analysis
    output = benchmark.save_analysis()

    print("\n" + "=" * 50)
    print("✓ Analysis Complete")
    print(f"✓ Best Overall Value: {output['summary']['best_overall_value']}")
    print(f"✓ Highest Performance: {output['summary']['highest_performance']}")
    print("=" * 50)


if __name__ == '__main__':
    main()
