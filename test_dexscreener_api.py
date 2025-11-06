#!/usr/bin/env python3
"""
DexScreener API Test Script
Demonstrates API access capabilities in Claude Code Web environment
"""

import urllib.request
import json
import sys

def fetch_pair_data(pair_address, chain="ethereum"):
    """
    获取指定交易对的数据

    Args:
        pair_address: 交易对地址
        chain: 区块链名称 (默认: ethereum)
    """
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pair_address}"

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        })

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def fetch_token_data(token_address):
    """
    通过 token 地址获取所有相关交易对

    Args:
        token_address: Token 合约地址
    """
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        })

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Error fetching token data: {e}")
        return None

def display_pair_info(pair_data):
    """格式化显示交易对信息"""
    if not pair_data or 'pairs' not in pair_data:
        print("No pair data available")
        return

    for idx, pair in enumerate(pair_data['pairs'][:3], 1):  # 只显示前3个
        print(f"\n{'='*80}")
        print(f"交易对 #{idx}")
        print('='*80)

        print(f"\n🔗 基本信息:")
        print(f"  链: {pair.get('chainId', 'N/A')}")
        print(f"  DEX: {pair.get('dexId', 'N/A')}")
        print(f"  地址: {pair.get('pairAddress', 'N/A')}")
        print(f"  URL: {pair.get('url', 'N/A')}")

        if 'baseToken' in pair and 'quoteToken' in pair:
            print(f"\n💰 Token:")
            print(f"  {pair['baseToken']['symbol']} / {pair['quoteToken']['symbol']}")
            print(f"  {pair['baseToken']['name']} / {pair['quoteToken']['name']}")

        print(f"\n💵 价格:")
        print(f"  USD: ${pair.get('priceUsd', 'N/A')}")

        if 'priceChange' in pair:
            pc = pair['priceChange']
            print(f"\n📊 价格变化:")
            print(f"  5m: {pc.get('m5', 0):.2f}%")
            print(f"  1h: {pc.get('h1', 0):.2f}%")
            print(f"  6h: {pc.get('h6', 0):.2f}%")
            print(f"  24h: {pc.get('h24', 0):.2f}%")

        if 'volume' in pair:
            vol = pair['volume']
            print(f"\n📈 交易量:")
            if 'h24' in vol:
                print(f"  24h: ${vol['h24']:,.2f}")

        if 'liquidity' in pair and 'usd' in pair['liquidity']:
            print(f"\n💧 流动性: ${pair['liquidity']['usd']:,.2f}")

        if 'txns' in pair and 'h24' in pair['txns']:
            h24_txns = pair['txns']['h24']
            print(f"\n🔄 24h 交易笔数:")
            print(f"  买入: {h24_txns.get('buys', 0)}")
            print(f"  卖出: {h24_txns.get('sells', 0)}")

def main():
    print("DexScreener API 测试")
    print("=" * 80)

    # 示例 1: WETH/USDC on Uniswap V3
    print("\n示例 1: 查询 WETH/USDC 交易对")
    weth_usdc_pair = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
    data = fetch_pair_data(weth_usdc_pair)
    if data:
        display_pair_info(data)

    print("\n" + "=" * 80)

    # 示例 2: 通过 WETH token 地址查询
    print("\n示例 2: 查询 WETH token 的所有交易对 (仅显示前3个)")
    weth_token = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    token_data = fetch_token_data(weth_token)
    if token_data:
        display_pair_info(token_data)

    print("\n" + "=" * 80)
    print("✓ API 测试完成!")

if __name__ == "__main__":
    main()
