#!/usr/bin/env python3
"""
Investigate boto 2.49.0 - another package where Doug found vulnerabilities but we show "None found"
"""

import sys
import asyncio
sys.path.append('src')

from vulnerability_scanner import VulnerabilityScanner

async def investigate_boto_2490():
    """Investigate boto 2.49.0 discrepancy"""
    
    print('🔍 INVESTIGATING: boto 2.49.0')
    print('=' * 50)
    print()
    print('📋 ISSUE: Doug found vulnerabilities, we show "None found"')
    print('🎯 Need to understand why this is happening')
    print()
    
    scanner = VulnerabilityScanner()
    
    if not scanner.ai_analyzer or not scanner.ai_analyzer.is_enabled():
        print('❌ AI analyzer not available')
        return
    
    print(f'✅ AI Analyzer: {scanner.ai_analyzer.model}')
    print(f'🔗 SNYK URL: https://security.snyk.io/package/pip/boto')
    print()
    
    # Test boto 2.49.0 specifically
    print('🧪 TESTING boto 2.49.0:')
    try:
        result = await scanner.scan_snyk('boto', '2.49.0')
        
        summary = result.get('summary', '')
        ai_analysis = result.get('ai_analysis', '')
        
        print(f'📝 Current Result: {summary}')
        print(f'🤖 Raw AI Analysis: {ai_analysis}')
        
        # Analyze the AI response
        if 'NOT_FOUND' in ai_analysis.upper():
            print('❌ AI explicitly says no vulnerabilities found')
            print('🔍 This conflicts with Doug\'s manual check')
        elif 'FOUND' in ai_analysis.upper():
            print('✅ AI found vulnerabilities')
        else:
            print('⚠️ Unclear AI response')
            
    except Exception as e:
        print(f'❌ Error: {e}')
    
    print()
    
    # Test some related boto versions to understand the pattern
    print('🔍 TESTING RELATED boto VERSIONS:')
    boto_versions = ['2.48.0', '2.49.0', '2.50.0', '2.51.0']
    
    for version in boto_versions:
        try:
            result = await scanner.scan_snyk('boto', version)
            summary = result.get('summary', '')
            
            if 'None found' in summary:
                status = '❌ None found'
            elif 'Latest safe version' in summary:
                status = '✅ Vulnerabilities found'
            else:
                status = '⚠️ Other'
                
            print(f'   boto {version}: {status}')
            
        except Exception as e:
            print(f'   boto {version}: ❌ Error - {e}')
    
    await scanner.close()
    
    print()
    print('🎯 BOTO ANALYSIS:')
    print('=' * 50)
    print('📊 POSSIBLE REASONS FOR DISCREPANCY:')
    print('1. boto may be an older package with different vulnerability patterns')
    print('2. Doug may have found vulnerabilities that are not in SNYK')
    print('3. boto vulnerabilities may be listed under different names')
    print('4. The AI may need more specific guidance for boto')
    print()
    print('🔧 POTENTIAL SOLUTIONS:')
    print('1. Add boto-specific guidance to AI prompt')
    print('2. Check if boto3 vulnerabilities affect boto')
    print('3. Look for AWS-related security issues')
    print('4. Consider manual verification needed')

if __name__ == "__main__":
    asyncio.run(investigate_boto_2490())