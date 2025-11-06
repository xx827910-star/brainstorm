#!/usr/bin/env python3
"""
Test script for Gemini API integration in VS Code Terminal
Using REST API to avoid dependency issues
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

def test_gemini_api(api_key, output_file="result.md"):
    """Test Gemini API with the provided API key using REST API"""

    # 准备输出内容
    output_lines = []

    def log(message):
        """同时打印到控制台和保存到输出列表"""
        print(message)
        output_lines.append(message)

    try:
        # Gemini API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

        # Request payload
        payload = {
            "contents": [{
                "parts": [{
                    "text": "介绍一下gemini cli"
                }]
            }]
        }

        # Convert to JSON
        data = json.dumps(payload).encode('utf-8')

        # Create request
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        log("Testing Gemini API...")
        log("=" * 50)
        log(f"Endpoint: {url[:80]}...")
        log("=" * 50)

        # Send request
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))

        # Extract response text
        if 'candidates' in result and len(result['candidates']) > 0:
            response_text = result['candidates'][0]['content']['parts'][0]['text']

            log("\nResponse received:")
            log("-" * 50)
            log(response_text)
            log("-" * 50)
            log("\n✓ API test successful!")
            log(f"✓ Model used: gemini-2.5-flash")
            log(f"✓ Environment: VS Code Terminal")
            log(f"✓ Method: REST API (urllib)")

            # 保存到文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Gemini API 测试结果\n\n")
                f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**模型**: gemini-2.5-flash\n\n")
                f.write(f"## 输出内容\n\n")
                f.write('\n'.join(output_lines))
                f.write(f"\n\n## 完整响应\n\n```\n{response_text}\n```\n")

            log(f"\n✓ 结果已保存到: {output_file}")

            return True
        else:
            log("Error: Unexpected response format")
            log(json.dumps(result, indent=2))
            return False

    except urllib.error.HTTPError as e:
        log(f"HTTP Error: {e.code} - {e.reason}")
        error_body = e.read().decode('utf-8')
        log(f"Error details: {error_body}")
        return False
    except urllib.error.URLError as e:
        log(f"URL Error: {e.reason}")
        return False
    except Exception as e:
        log(f"Error during API call: {e}")
        log(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # API key provided by user
    API_KEY = "AIzaSyDucYAt4bWNkY-vPjfvb7uFuU_EmVeGKgE"

    print("Gemini API Integration Test")
    print("=" * 50)
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
    print("=" * 50)
    print()

    success = test_gemini_api(API_KEY)

    sys.exit(0 if success else 1)
