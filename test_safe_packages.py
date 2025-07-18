#!/usr/bin/env python3
"""
Test script for packages that should return "None found" to ensure standard logic works
"""

import sys
import asyncio
sys.path.append('src')

from vulnerability_scanner import VulnerabilityScanner

async def test_safe_packages():
    """Test packages that should return standard 'None found' message"""
    
    print('🛡️  Testing Safe Packages (Standard Logic)')
    print('=' * 50)
    print()
    
    # Test packages that should be safe or have current versions that are safe
    test_cases = [
        ('numpy', '1.24.0', 'Recent version, likely safe'),
        ('pandas', '2.0.0', 'Recent version, should be safe'),
        ('setuptools', '68.0.0', 'Recent version, should be safe')
    ]
    
    scanner = VulnerabilityScanner()
    
    if not scanner.ai_analyzer or not scanner.ai_analyzer.is_enabled():
        print('❌ AI analyzer not available')
        return
    
    print(f'✅ AI Analyzer enabled: {scanner.ai_analyzer.model}')
    print()
    
    for package_name, test_version, description in test_cases:
        print(f'📦 Testing {package_name} v{test_version}')
        print(f'   Context: {description}')
        
        try:
            result = await scanner.scan_snyk(package_name, test_version)
            
            summary = result.get('summary', '')
            ai_analysis = result.get('ai_analysis', '')
            
            print(f'   📝 Summary: {summary}')
            
            # Check if standard logic is working
            if 'None found' in summary:
                print('   ✅ Standard logic: "None found" message')
            elif 'NOT_FOUND' in ai_analysis or 'NOT_AFFECTED' in ai_analysis:
                print('   ✅ Safe version confirmed by AI')
            elif 'Latest safe version' in summary:
                print('   ⚠️  Enhanced logic triggered (vulnerabilities found)')
            else:
                print('   ℹ️  Other result - may need review')
            
            print()
            
        except Exception as e:
            print(f'   ❌ Error: {e}')
            print()
    
    await scanner.close()
    
    print('✅ Standard logic verification completed!')

if __name__ == "__main__":
    asyncio.run(test_safe_packages())