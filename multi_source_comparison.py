#!/usr/bin/env python3
"""
Multi-Source Memory Price Comparison Module
Aggregates and compares data from DRAMeXchange, ORNN, TrendForce, ICIS, and other sources
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List

class MultiSourceComparison:
    """
    Compare memory price data across multiple sources
    Sources: DRAMeXchange, Ornn OCPI, TrendForce, ICIS, Silicon Data
    """

    # DRAMeXchange live prices (Apr 17, 2026)
    DRAMEXCHANGE_DATA = {
        'source': 'DRAMeXchange (TrendForce)',
        'url': 'https://www.dramexchange.com/',
        'update_time': '2026-04-17 18:00 (GMT+8)',
        'frequency': 'Daily/Weekly',
        'access': 'Public (limited) / Membership',
        'products': {
            'DDR5 16Gb (2Gx8) 4800/5600': {
                'daily_high': 49.50,
                'daily_low': 28.00,
                'session_avg': 37.833,
                'session_change': '+0.35%'
            },
            'DDR5 16Gb eTT': {
                'daily_high': 24.00,
                'daily_low': 20.60,
                'session_avg': 21.500,
                'session_change': '0.00%'
            },
            'DDR4 16Gb (2Gx8) 3200': {
                'daily_high': 87.50,
                'daily_low': 29.00,
                'session_avg': 69.182,
                'session_change': '-0.39%'
            },
            'DDR4 16Gb eTT': {
                'daily_high': 14.70,
                'daily_low': 13.00,
                'session_avg': 13.475,
                'session_change': '0.00%'
            },
            'GDDR6 8Gb': {
                'weekly_high': 20.00,
                'weekly_low': 9.50,
                'session_avg': 12.412,
                'weekly_change': '-2.35%'
            },
            '512Gb TLC NAND': {
                'weekly_high': 23.50,
                'weekly_low': 17.00,
                'session_avg': 21.679,
                'weekly_change': '-2.15%'
            }
        }
    }

    # Ornn OCPI (Compute Price Index)
    ORNN_DATA = {
        'source': 'Ornn OCPI (Ornn Compute Price Index)',
        'url': 'https://ornn.com/',
        'update_time': 'Live',
        'frequency': 'Real-time',
        'access': 'Institutional / API',
        'regulation': 'U.S.-regulated derivatives exchange',
        'indices': {
            'OCPI-H100': {
                'price': 1.90,
                'description': 'NVIDIA H100 GPU Compute (per $/hour)',
                'underlying': 'Live traded spot prices',
                'products': ['H100 SXM', 'H100 PCIe']
            },
            'OCPI-H200': {
                'price': None,  # Not published in current data
                'description': 'NVIDIA H200 GPU Compute',
                'underlying': 'Live traded spot prices',
                'products': ['H200 SXM', 'H200 PCIe']
            },
            'OCPI-B200': {
                'price': None,
                'description': 'NVIDIA B200 GPU Compute',
                'underlying': 'Live traded spot prices',
                'products': ['B200 SXM', 'B200 PCIe']
            },
            'OCPI-RTX5090': {
                'price': None,
                'description': 'NVIDIA RTX 5090 GPU Compute',
                'underlying': 'Live traded spot prices',
                'products': ['RTX 5090']
            }
        },
        'financial_products': {
            'futures': 'Cash-settled GPU compute futures',
            'swaps': 'GPU compute swaps for hedging',
            'settlement': 'Cash-settled based on OCPI',
            'bloomberg_terminal': 'Listed on Bloomberg Terminal'
        }
    }

    # TrendForce Market Research
    TRENDFORCE_DATA = {
        'source': 'TrendForce Market Research',
        'url': 'https://www.trendforce.com/',
        'update_time': '2026-04-17',
        'frequency': 'Monthly/Quarterly reports',
        'access': 'Free (limited) / Paid subscription',
        'forecasts': {
            'Q1_2026': {
                'conventional_dram': '+90-95% QoQ',
                'nand_flash': '+55-60% QoQ',
                'enterprise_ssd': '+53-58% QoQ',
                'main_driver': 'AI server demand surge'
            },
            'Q2_2026': {
                'conventional_dram': '+58-63% QoQ',
                'nand_flash': '+70-75% QoQ',
                'consumer_dram': '+45-50% QoQ',
                'main_driver': 'Supply constraints, strong demand'
            }
        },
        'key_insights': [
            'AI servers driving 70-75% NAND price increase in Q2 2026',
            'HBM production constraining DDR5 output',
            'Major manufacturers allocating >40% capacity to HBM',
            'Contract prices diverging from spot prices'
        ]
    }

    # ICIS Pricing Data
    ICIS_DATA = {
        'source': 'ICIS (Independent Chemical Information Service)',
        'url': 'https://www.icis.com/',
        'update_time': 'Daily',
        'frequency': 'Daily spot prices',
        'access': 'Subscription only',
        'coverage': {
            'dram_spot': 'DRAM spot prices (global)',
            'nand_spot': 'NAND Flash spot prices',
            'ssd_pricing': 'Enterprise SSD pricing',
            'contract_prices': 'Long-term contract pricing'
        },
        'methodology': 'Price assessments based on market transactions',
        'strengths': [
            'Daily price updates',
            'Global coverage',
            'Industry-standard methodology'
        ]
    }

    # Other Market Data Sources
    OTHER_SOURCES = {
        'Bloomberg Terminal': {
            'url': 'https://www.bloomberg.com/professional/',
            'access': 'Subscription',
            'data': 'Real-time memory chip prices, OCPI indices',
            'strengths': 'Real-time data, comprehensive coverage'
        },
        'Reuters Eikon': {
            'url': 'https://www.refinitiv.com/',
            'access': 'Subscription',
            'data': 'DRAM/NAND spot and contract prices',
            'strengths': 'News-integrated, historical data'
        },
        'Silicon Data': {
            'url': 'API access',
            'access': 'API subscription',
            'data': 'Memory chip prices, market data',
            'strengths': 'API integration, developer-friendly'
        }
    }

    def __init__(self):
        self.sources = {
            'dramexchange': self.DRAMEXCHANGE_DATA,
            'ornn': self.ORNN_DATA,
            'trendforce': self.TRENDFORCE_DATA,
            'icis': self.ICIS_DATA,
            'other': self.OTHER_SOURCES
        }

    def compare_ddr5_prices(self) -> pd.DataFrame:
        """Compare DDR5 prices across sources"""
        comparison = []

        # DRAMeXchange DDR5 module prices
        ddr5_udimm_module = {
            'source': 'DRAMeXchange',
            'product': 'DDR5 UDIMM 16GB 4800/5600',
            'price_type': 'Module price',
            'price': 222.50,  # Weekly average from our earlier data
            'currency': 'USD',
            'frequency': 'Weekly',
            'timestamp': '2026-04-17'
        }
        comparison.append(ddr5_udimm_module)

        # DDR5 chip price from DRAMeXchange
        ddr5_chip = {
            'source': 'DRAMeXchange',
            'product': 'DDR5 16Gb (2Gx8) 4800/5600',
            'price_type': 'Chip price',
            'price': 37.833,
            'currency': 'USD',
            'frequency': 'Daily',
            'timestamp': '2026-04-17'
        }
        comparison.append(ddr5_chip)

        # TrendForce forecast (not current price, but directional)
        trendforce = {
            'source': 'TrendForce',
            'product': 'Conventional DRAM (Q2 2026 forecast)',
            'price_type': 'Forecast change',
            'price': '+58-63%',
            'currency': 'QoQ change',
            'frequency': 'Quarterly forecast',
            'timestamp': '2026-04-17'
        }
        comparison.append(trendforce)

        return pd.DataFrame(comparison)

    def compare_gpu_compute(self) -> pd.DataFrame:
        """Compare GPU compute prices (ORNN OCPI vs alternatives)"""
        comparison = []

        # Ornn OCPI
        ornn_data = {
            'source': 'Ornn OCPI',
            'product': 'H100 Compute',
            'price': 1.90,
            'unit': '$/hour',
            'methodology': 'Live traded transactions',
            'regulation': 'U.S.-regulated',
            'transparency': 'Transaction-based'
        }
        comparison.append(ornn_data)

        # Cloud provider alternatives (estimated)
        cloud_providers = [
            {'provider': 'AWS', 'price_range': '$2.50-$3.50', 'unit': '$/hour'},
            {'provider': 'GCP', 'price_range': '$2.40-$3.20', 'unit': '$/hour'},
            {'provider': 'Azure', 'price_range': '$2.60-$3.40', 'unit': '$/hour'}
        ]

        for cp in cloud_providers:
            comparison.append({
                'source': f"{cp['provider']} (estimated)",
                'product': 'H100 Compute',
                'price': cp['price_range'],
                'unit': '$/hour',
                'methodology': 'Cloud provider pricing',
                'regulation': 'N/A',
                'transparency': 'Provider-set pricing'
            })

        return pd.DataFrame(comparison)

    def source_comparison_matrix(self) -> pd.DataFrame:
        """Create a comparison matrix of all data sources"""
        matrix = []

        for source_name, source_data in self.sources.items():
            if source_name == 'other':
                for sub_name, sub_data in source_data.items():
                    matrix.append({
                        'Source': sub_name,
                        'URL': sub_data.get('url', 'N/A'),
                        'Update Frequency': sub_data.get('data', 'N/A'),
                        'Access': sub_data.get('access', 'N/A'),
                        'Strengths': sub_data.get('strengths', 'N/A'),
                        'Best For': 'Varies'
                    })
            else:
                matrix.append({
                    'Source': source_data.get('source', source_name),
                    'URL': source_data.get('url', 'N/A'),
                    'Update Frequency': source_data.get('frequency', 'N/A'),
                    'Access': source_data.get('access', 'N/A'),
                    'Strengths': self._get_source_strengths(source_name),
                    'Best For': self._get_best_use(source_name)
                })

        return pd.DataFrame(matrix)

    def _get_source_strengths(self, source: str) -> str:
        """Get key strengths of each source"""
        strengths = {
            'dramexchange': 'Live spot prices, industry standard',
            'ornn': 'Transaction-based, regulated derivatives',
            'trendforce': 'Market forecasts, deep analysis',
            'icis': 'Daily assessments, global coverage'
        }
        return strengths.get(source, 'N/A')

    def _get_best_use(self, source: str) -> str:
        """Get best use case for each source"""
        uses = {
            'dramexchange': 'Real-time spot price tracking',
            'ornn': 'GPU derivatives trading, hedging',
            'trendforce': 'Market forecasting, planning',
            'icis': 'Daily price assessments'
        }
        return uses.get(source, 'N/A')

    def generate_comparison_report(self) -> Dict:
        """Generate comprehensive comparison report"""
        return {
            'report_date': datetime.now().isoformat(),
            'dram_spot_prices': self.compare_ddr5_prices().to_dict('records'),
            'gpu_compute_prices': self.compare_gpu_compute().to_dict('records'),
            'source_comparison': self.source_comparison_matrix().to_dict('records'),
            'key_findings': [
                'DRAMeXchange provides most granular DRAM spot prices',
                'Ornn OCPI is only regulated derivatives exchange for GPU compute',
                'TrendForce offers best QoQ forecasts for planning',
                'ICIS provides daily price assessments via subscription',
                'Bloomberg Terminal lists OCPI for institutional access'
            ],
            'data_quality_ranking': [
                {'rank': 1, 'source': 'Ornn OCPI', 'reason': 'Transaction-based pricing, regulated'},
                {'rank': 2, 'source': 'DRAMeXchange', 'reason': 'Industry standard, frequent updates'},
                {'rank': 3, 'source': 'ICIS', 'reason': 'Daily assessments, methodology'},
                {'rank': 4, 'source': 'TrendForce', 'reason': 'Excellent forecasts, less frequent'}
            ]
        }

    def save_report(self, output_file: str = 'multi_source_comparison.json'):
        """Save comparison report to JSON"""
        report = self.generate_comparison_report()

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✓ Saved multi-source comparison to {output_file}")
        return report


def main():
    """Main execution"""
    print("=" * 60)
    print("Multi-Source Memory Price Comparison")
    print("=" * 60)

    comparison = MultiSourceComparison()

    # DDR5 Price Comparison
    print("\n📊 DDR5 Price Comparison:")
    print("-" * 60)
    ddr5_df = comparison.compare_ddr5_prices()
    print(ddr5_df.to_string(index=False))

    # GPU Compute Comparison
    print("\n🎮 GPU Compute Price Comparison:")
    print("-" * 60)
    gpu_df = comparison.compare_gpu_compute()
    print(gpu_df.to_string(index=False))

    # Source Comparison Matrix
    print("\n📋 Data Source Comparison Matrix:")
    print("-" * 60)
    matrix_df = comparison.source_comparison_matrix()
    print(matrix_df.to_string(index=False))

    # Key Findings
    print("\n🔍 Key Findings:")
    print("-" * 60)
    report = comparison.generate_comparison_report()
    for finding in report['key_findings']:
        print(f"  • {finding}")

    # Quality Ranking
    print("\n🏆 Data Quality Ranking:")
    print("-" * 60)
    for item in report['data_quality_ranking']:
        print(f"  {item['rank']}. {item['source']} - {item['reason']}")

    # Save report
    comparison.save_report()

    print("\n" + "=" * 60)
    print("✓ Multi-source comparison complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
