#!/usr/bin/env python3
"""
Focused analysis of latest safe version handling - smaller dataset
"""

import sys
import asyncio
sys.path.append('src')

from vulnerability_scanner import VulnerabilityScanner
import re

async def analyze_focused_safe_versions():
    """Focused analysis with key packages"""
    
    print('📊 FOCUSED ANALYSIS: Latest Non-Vulnerable Version Handling')
    print('=' * 80)
    print()
    
    # Focus on key packages
    test_packages = [
        # Critical packages from validation
        ('SQLAlchemy', '1.4.39'),
        ('SQLAlchemy', '2.0.41'),
        ('requests', '2.25.0'),
        ('Django', '3.0.0'),
        ('Flask', '2.2.2'),
        ('cryptography', '2.0.0'),
        ('aiohttp', '3.8.3'),
        ('boto', '2.49.0'),
        ('numpy', '1.24.0'),
        ('setuptools', '68.0.0')
    ]
    
    scanner = VulnerabilityScanner()
    
    if not scanner.ai_analyzer or not scanner.ai_analyzer.is_enabled():
        print('❌ AI analyzer not available')
        return
    
    results = []
    
    print(f'{"Package":<20} {"Version":<10} {"Status":<12} {"Safe Ver":<10} {"Severity":<8} {"Summary":<50}')
    print('-' * 130)
    
    for package_name, version in test_packages:
        try:
            result = await scanner.scan_snyk(package_name, version)
            
            summary = result.get('summary', '')
            ai_analysis = result.get('ai_analysis', '')
            
            # Extract information
            latest_safe_version = None
            severity = None
            status = 'UNKNOWN'
            
            if 'None found' in summary:
                status = 'SAFE'
            elif 'Latest safe version:' in summary:
                status = 'VULNERABLE'
                
                # Extract safe version
                safe_version_match = re.search(r'Latest safe version:\s*([^\s]+)', summary)
                if safe_version_match:
                    latest_safe_version = safe_version_match.group(1).strip()
                
                # Extract severity
                severity_match = re.search(r'Severity:\s*([A-Z]+)', summary)
                if severity_match:
                    severity = severity_match.group(1)
            
            # Truncate summary for display
            display_summary = summary[:47] + '...' if len(summary) > 50 else summary
            
            print(f"{package_name:<20} {version:<10} {status:<12} {latest_safe_version or 'N/A':<10} {severity or 'N/A':<8} {display_summary:<50}")
            
            results.append({
                'package': package_name,
                'version': version,
                'status': status,
                'safe_version': latest_safe_version,
                'severity': severity,
                'full_summary': summary
            })
            
        except Exception as e:
            print(f"{package_name:<20} {version:<10} {'ERROR':<12} {'N/A':<10} {'N/A':<8} {f'Error: {str(e)[:40]}':<50}")
    
    await scanner.close()
    
    print('\n' + '=' * 80)
    print('📊 ANALYSIS SUMMARY')
    print('=' * 80)
    
    # Count results
    vulnerable = [r for r in results if r['status'] == 'VULNERABLE']
    safe = [r for r in results if r['status'] == 'SAFE']
    
    print(f'\n📈 Statistics:')
    print(f'- Total analyzed: {len(results)}')
    print(f'- Vulnerable: {len(vulnerable)} ({len(vulnerable)/len(results)*100:.0f}%)')
    print(f'- Safe: {len(safe)} ({len(safe)/len(results)*100:.0f}%)')
    
    print(f'\n🔴 Vulnerable Packages with Safe Version Guidance:')
    for r in vulnerable:
        if r['safe_version']:
            print(f"- {r['package']} {r['version']} → {r['safe_version']} (Severity: {r['severity']})")
        else:
            print(f"- {r['package']} {r['version']} → [No safe version extracted] (Severity: {r['severity']})")
    
    print(f'\n🟢 Safe Packages:')
    for r in safe:
        print(f"- {r['package']} {r['version']}")
    
    # Check enhanced logic effectiveness
    print(f'\n✅ Enhanced Logic Effectiveness:')
    with_safe_version = [r for r in vulnerable if r['safe_version']]
    print(f'- {len(with_safe_version)}/{len(vulnerable)} vulnerable packages have safe version guidance')
    print(f'- Success rate: {len(with_safe_version)/max(len(vulnerable),1)*100:.0f}%')
    
    # Show full summaries for vulnerable packages
    print(f'\n📋 Detailed Vulnerable Package Summaries:')
    print('-' * 80)
    for r in vulnerable:
        print(f"\n{r['package']} v{r['version']}:")
        print(f"Summary: {r['full_summary']}")

if __name__ == "__main__":
    asyncio.run(analyze_focused_safe_versions())