#!/usr/bin/env python3
"""
Critical Investigation: SQLAlchemy 1.4.39 SNYK Analysis
This is the specific example Doug highlighted in his email - must be fixed!
"""

import sys
import asyncio
sys.path.append('src')

from vulnerability_scanner import VulnerabilityScanner
from ai_cve_analyzer import AICVEAnalyzer

async def investigate_sqlalchemy_1439():
    """
    Investigate SQLAlchemy 1.4.39 - the specific example Doug flagged
    Doug's Manual Result: "SNYK Analysis: FOUND - SQLAlchemy 1.4.39 is affected by known vulnerabilities"
    Our Current Result: "None found"
    """
    
    print('🔍 CRITICAL INVESTIGATION: SQLAlchemy 1.4.39')
    print('=' * 60)
    print()
    print('🚨 ISSUE: This is the specific example Doug highlighted!')
    print('Doug\'s Manual Result: "FOUND - SQLAlchemy 1.4.39 is affected by known vulnerabilities"')
    print('Our Current Result: "None found"')
    print()
    
    # Test the specific version Doug mentioned
    package_name = 'SQLAlchemy'
    problem_version = '1.4.39'
    
    scanner = VulnerabilityScanner()
    
    if not scanner.ai_analyzer or not scanner.ai_analyzer.is_enabled():
        print('❌ AI analyzer not available - cannot investigate')
        return
    
    print(f'✅ AI Analyzer: {scanner.ai_analyzer.model}')
    print(f'🔗 SNYK URL: https://security.snyk.io/package/pip/sqlalchemy')
    print()
    
    # Test current implementation
    print('🔍 TESTING CURRENT IMPLEMENTATION:')
    try:
        result = await scanner.scan_snyk(package_name, problem_version)
        
        print(f'📝 Current Result: {result.get("summary", "No summary")}')
        print(f'🤖 Raw AI Analysis: {result.get("ai_analysis", "No analysis")}')
        
        # Check if our enhanced logic is being triggered
        if 'None found' in result.get('summary', ''):
            print('❌ PROBLEM CONFIRMED: Returning "None found" instead of vulnerabilities')
        elif 'Latest safe version' in result.get('summary', ''):
            print('✅ Enhanced logic activated - vulnerabilities detected')
        else:
            print('⚠️ Unexpected result format')
            
    except Exception as e:
        print(f'❌ Error in current implementation: {e}')
    
    print()
    
    # Let's test the AI directly with more specific instructions
    print('🧪 TESTING AI ANALYZER DIRECTLY:')
    try:
        ai_analyzer = AICVEAnalyzer()
        if ai_analyzer.is_enabled():
            
            # Test with enhanced prompt focusing on SQLAlchemy 1.4.39
            direct_result = await ai_analyzer.analyze_snyk_result(
                package_name='SQLAlchemy',
                current_version='1.4.39',
                snyk_lookup_url='https://security.snyk.io/package/pip/sqlalchemy'
            )
            
            print(f'📝 Direct AI Result: {direct_result}')
            
            # Analyze the response
            if 'NOT_FOUND' in direct_result.upper():
                print('❌ AI says no vulnerabilities found')
                print('🔍 This conflicts with Doug\'s manual check')
            elif 'FOUND' in direct_result.upper():
                print('✅ AI found vulnerabilities')
                print('🔍 This matches Doug\'s expectation')
            else:
                print('⚠️ Unclear AI response')
                
    except Exception as e:
        print(f'❌ Error testing AI directly: {e}')
    
    print()
    
    # Let's also test some related versions to understand the pattern
    print('🔍 TESTING RELATED SQLALCHEMY VERSIONS:')
    related_versions = ['1.4.38', '1.4.39', '1.4.40', '1.4.41', '1.4.42']
    
    for version in related_versions:
        try:
            result = await scanner.scan_snyk('SQLAlchemy', version)
            summary = result.get('summary', '')
            
            if 'None found' in summary:
                status = '❌ None found'
            elif 'Latest safe version' in summary:
                status = '✅ Vulnerabilities found'
            else:
                status = '⚠️ Other'
                
            print(f'   SQLAlchemy {version}: {status}')
            
        except Exception as e:
            print(f'   SQLAlchemy {version}: ❌ Error - {e}')
    
    await scanner.close()
    
    print()
    print('🎯 ANALYSIS SUMMARY:')
    print('=' * 60)
    print()
    print('🚨 CRITICAL ISSUE IDENTIFIED:')
    print('- SQLAlchemy 1.4.39 is returning "None found"')
    print('- Doug\'s manual check found vulnerabilities')
    print('- This is the specific example he highlighted')
    print()
    print('📊 POSSIBLE CAUSES:')
    print('1. Version range parsing issue in AI prompt')
    print('2. AI model accessing different SNYK data than Doug')
    print('3. Timing difference in SNYK database updates')
    print('4. AI prompt not specific enough for this version')
    print()
    print('🔧 REQUIRED ACTIONS:')
    print('1. Manually verify SQLAlchemy 1.4.39 on SNYK website')
    print('2. Update AI prompt to be more specific about version ranges')
    print('3. Add debugging for this specific case')
    print('4. Test fix before responding to Doug')
    print()
    print('⚠️ RECOMMENDATION:')
    print('DO NOT respond to Doug until this specific issue is resolved!')
    print('This is the example he used to demonstrate the problem.')

if __name__ == "__main__":
    asyncio.run(investigate_sqlalchemy_1439())