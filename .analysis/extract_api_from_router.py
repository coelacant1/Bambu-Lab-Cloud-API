#!/usr/bin/env python3
"""
Extract API Endpoints from Bambu Studio Router

This script extracts API endpoint patterns from the Bambu Studio/Connect
router JavaScript file after extracting the application resources.

Methodology:
1. Extract Bambu Studio .exe using 7z
2. Extract app.asar using asar tool  
3. Locate router-*.js in .vite/renderer/main_window/assets/
4. Run this script to extract API patterns

This script does pattern matching to find API endpoints - it does NOT
deobfuscate code or extract proprietary logic.

Usage:
    python extract_api_from_router.py <path_to_router.js> [output_file.json]
    
Example:
    python extract_api_from_router.py ./extracted/router-abc123.js api_structure.json
"""
import re
import json
from collections import defaultdict
from datetime import datetime
import sys
import os

def extract_api_from_router(router_file_path, output_file='discovered_api_structure.json'):
    """Extract API endpoints from router JavaScript file"""
    
    print("=" * 80)
    print("EXTRACTING API ENDPOINTS FROM BAMBU STUDIO ROUTER")
    print("=" * 80)
    print()
    
    # Read router file
    print(f"Reading: {router_file_path}")
    try:
        with open(router_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {router_file_path}")
        print("\nPlease extract Bambu Studio first:")
        print("  1. 7z x BambuStudio.exe -o./bambu_extracted")
        print("  2. asar extract ./bambu_extracted/resources/app.asar ./app_extracted")
        print("  3. Find router-*.js in .vite/renderer/main_window/assets/")
        print("\nExample:")
        print("  python extract_api_from_router.py ./app_extracted/.vite/renderer/main_window/assets/router-*.js")
        sys.exit(1)
    
    print(f"File size: {len(content):,} characters")
    print()
    
    # Storage for discovered patterns
    api_structure = {
        'base_urls': set(),
        'endpoints': defaultdict(list),
        'http_methods': set(),
        'headers': set(),
        'query_params': set(),
    }
    
    # Pattern 1: Extract base URLs
    print("Step 1: Extracting base URLs...")
    url_pattern = re.compile(r'["\']https?://[^"\']+["\']')
    for match in url_pattern.finditer(content):
        url = match.group().strip('"\'')
        if 'bambu' in url.lower():
            api_structure['base_urls'].add(url.split('?')[0])
    
    print(f"  Found {len(api_structure['base_urls'])} base URLs")
    
    # Pattern 2: Extract API paths
    print("Step 2: Extracting API endpoint paths...")
    
    # Look for /v1/ or /api/ patterns
    v1_paths = re.findall(r'["\']/(v1/[a-z0-9_/\-]+)["\']', content)
    api_paths = re.findall(r'["\']/(api/[a-z0-9_/\-]+)["\']', content)
    
    all_paths = set(v1_paths + api_paths)
    
    # Categorize by first path segment after /v1/ or /api/
    for path in all_paths:
        parts = path.strip('/').split('/')
        if len(parts) >= 2:
            category = parts[1] if parts[0] in ['v1', 'api'] else parts[0]
            if len(path) < 100:  # Reasonable length
                api_structure['endpoints'][category].append(path)
    
    print(f"  Found {len(all_paths)} API endpoint paths")
    
    # Pattern 3: Extract endpoint definitions
    print("Step 3: Finding endpoint variable definitions...")
    endpoint_defs = re.findall(
        r'(endpoint|path|url)\s*[:=]\s*["\']([^"\']+)["\']',
        content,
        re.IGNORECASE
    )
    
    for name, path in endpoint_defs:
        if '/' in path and len(path) < 100:
            parts = path.strip('/').split('/')
            if parts:
                category = parts[0]
                api_structure['endpoints'][category].append(path)
    
    print(f"  Found {len(endpoint_defs)} endpoint definitions")
    
    # Pattern 4: Extract HTTP methods
    print("Step 4: Finding HTTP methods...")
    http_methods = re.findall(r'\b(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b', content)
    api_structure['http_methods'].update(http_methods)
    print(f"  Found {len(api_structure['http_methods'])} HTTP methods")
    
    # Pattern 5: Extract custom headers
    print("Step 5: Finding custom headers...")
    # Look for custom headers (x-* pattern and common auth headers)
    header_patterns = [
        r'["\']([xX]-[a-zA-Z0-9\-]+)["\']',
        r'["\']([Aa]uthorization)["\']',
        r'["\']([Cc]ontent-[Tt]ype)["\']',
    ]
    for pattern in header_patterns:
        headers = re.findall(pattern, content)
        api_structure['headers'].update(h.lower() for h in headers)
    print(f"  Found {len(api_structure['headers'])} custom headers")
    
    # Pattern 6: Extract query parameters
    print("Step 6: Finding query parameters...")
    # Look for common parameter patterns
    query_params = re.findall(r'[?&]([a-z_]+)=', content.lower())
    api_structure['query_params'].update(query_params)
    print(f"  Found {len(api_structure['query_params'])} query parameters")
    
    # Display results
    print("\n" + "=" * 80)
    print("DISCOVERED API STRUCTURE")
    print("=" * 80)
    
    if api_structure['base_urls']:
        print(f"\n🌐 BASE URLs ({len(api_structure['base_urls'])} found):")
        print("-" * 80)
        for url in sorted(api_structure['base_urls'])[:20]:
            print(f"  {url}")
        if len(api_structure['base_urls']) > 20:
            print(f"  ... and {len(api_structure['base_urls']) - 20} more")
    
    if api_structure['endpoints']:
        print(f"\nAPI ENDPOINTS BY CATEGORY:")
        print("-" * 80)
        
        for category in sorted(api_structure['endpoints'].keys())[:20]:
            endpoints = sorted(set(api_structure['endpoints'][category]))
            if endpoints and len(endpoints) <= 30:
                print(f"\n  {category.upper()} ({len(endpoints)} endpoints):")
                for ep in endpoints[:15]:
                    print(f"    {ep}")
                if len(endpoints) > 15:
                    print(f"    ... and {len(endpoints) - 15} more")
    
    # Save to JSON
    output_data = {
        'base_urls': sorted(list(api_structure['base_urls'])),
        'endpoints': {
            category: sorted(list(set(endpoints)))
            for category, endpoints in api_structure['endpoints'].items()
        },
        'http_methods': sorted(list(api_structure['http_methods'])),
        'headers': sorted(list(api_structure['headers'])),
        'query_params': sorted(list(api_structure['query_params'])),
        'source_file': os.path.basename(router_file_path),
        'total_endpoints': sum(len(set(endpoints)) for endpoints in api_structure['endpoints'].values()),
        'extraction_date': datetime.now().isoformat()
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n\nAPI structure saved to: {output_file}")
    print(f"   Total endpoints discovered: {output_data['total_endpoints']}")
    print(f"   Total base URLs: {len(output_data['base_urls'])}")
    print("\nNext steps:")
    print(f"  1. Review {output_file}")
    print("  2. Test endpoints with tools/testing/test_cloud_api.py")
    print("  3. Document verified endpoints in docs/")
    print("=" * 80)
    
    return output_data


def print_usage():
    """Print usage information"""
    print("Extract API Endpoints from Bambu Studio Router")
    print("=" * 80)
    print("\nUsage:")
    print("  python extract_api_from_router.py <path_to_router.js> [output_file.json]")
    print("\nArguments:")
    print("  path_to_router.js    Path to the router JavaScript file (required)")
    print("  output_file.json     Output JSON file (default: discovered_api_structure.json)")
    print("\nExample:")
    print("  python extract_api_from_router.py ./extracted/router-abc123.js")
    print("  python extract_api_from_router.py ./extracted/router-abc123.js my_api.json")
    print("\nExtraction Steps:")
    print("  1. Extract the application:")
    print("     7z x BambuStudio.exe -o./bambu_extracted")
    print("\n  2. Extract the ASAR archive:")
    print("     npm install -g asar")
    print("     asar extract ./bambu_extracted/resources/app.asar ./app_extracted")
    print("\n  3. Locate the router file:")
    print("     find ./app_extracted -name 'router-*.js' -type f")
    print("\n  4. Run this script:")
    print("     python extract_api_from_router.py <path_from_step_3>")
    print("\nNote: This script performs pattern matching only. It does NOT deobfuscate")
    print("      code or extract proprietary logic.")
    print("=" * 80)


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)
    
    router_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'discovered_api_structure.json'
    
    # Validate input file exists
    if not os.path.isfile(router_file):
        print(f"Error: File not found: {router_file}\n")
        print_usage()
        sys.exit(1)
    
    extract_api_from_router(router_file, output_file)
