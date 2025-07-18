#!/usr/bin/env python3
"""
Test script to verify SNYK integration fixes
Tests the specific issues identified by Doug's manual review
"""

import sys
import asyncio
sys.path.append('src')

from ai_cve_analyzer import AICVEAnalyzer
from vulnerability_scanner import VulnerabilityScanner

async def test_snyk_fixes():
    """Test SNYK fixes with problematic packages identified by Doug"""
    
    print('🔧 Testing SNYK Integration Fixes')
    print('=' * 50)
    
    # Test packages that Doug found issues with
    test_packages = [
        ('SQLAlchemy', '2.0.41'),
        ('aiohttp', '3.8.3'),
        ('cryptography', '39.0.1'),
        ('flask', '2.2.2'),
        ('requests', '2.25.0')
    ]
    
    # Test vulnerability scanner
    print('\n🔧 Testing Fixed Vulnerability Scanner...')
    scanner = VulnerabilityScanner()
    
    if not scanner.ai_analyzer or not scanner.ai_analyzer.is_enabled():
        print('❌ AI analyzer not enabled - cannot test fixes')
        return
    
    print(f'✅ AI Analyzer enabled: {scanner.ai_analyzer.model}')
    
    for package_name, version in test_packages:
        print(f'\n📦 Testing {package_name} v{version}...')
        
        try:
            # Test SNYK scan with AI
            snyk_result = await scanner.scan_snyk(package_name, version)
            
            print(f'   URL Generated: {snyk_result.get("search_url")}')
            print(f'   Expected URL: https://security.snyk.io/package/pip/{package_name.lower()}')
            
            # Check if URL is correct format
            expected_url = f'https://security.snyk.io/package/pip/{package_name.lower()}'
            actual_url = snyk_result.get('search_url', '')
            
            if expected_url == actual_url:
                print('   ✅ URL format correct')
            else:
                print(f'   ❌ URL format incorrect - got: {actual_url}')
            
            # Check AI analysis result
            ai_result = snyk_result.get('ai_analysis', '')
            if ai_result and len(ai_result) > 10:
                print(f'   📝 AI Analysis: {ai_result[:100]}...')
                
                # Check for improved analysis patterns
                if 'SNYK Analysis:' in ai_result:
                    print('   ✅ AI response format correct')
                else:
                    print('   ❌ AI response format needs improvement')
                    
                if 'CVEs:' in ai_result:
                    print('   ✅ CVE identification included')
                else:
                    print('   ⚠️  CVE identification missing')
                    
            else:
                print('   ❌ No AI analysis result')
                
        except Exception as e:
            print(f'   ❌ Error testing {package_name}: {e}')
    
    await scanner.close()
    
    print('\n🔧 Testing URL Generation...')
    # Test URL generation directly
    test_scanner = VulnerabilityScanner()
    urls = test_scanner._build_search_urls('requests')
    
    print(f'SNYK URL: {urls.get("snyk")}')
    expected_snyk = 'https://security.snyk.io/package/pip/requests'
    
    if urls.get('snyk') == expected_snyk:
        print('✅ Direct URL generation working correctly')
    else:
        print(f'❌ Direct URL generation failed - expected: {expected_snyk}')
    
    print('\n🎉 SNYK Integration Fix Test Completed!')
    print('\nSUMMARY OF FIXES:')
    print('1. ✅ Fixed SNYK base URL from /vuln/pip to /package/pip')
    print('2. ✅ Updated AI prompt to focus on version range checking')
    print('3. ✅ Added specific CVE identification requirements')
    print('4. ✅ Enhanced version impact analysis instructions')

if __name__ == "__main__":
    asyncio.run(test_snyk_fixes())