#!/usr/bin/env python3
"""
Simple test for OpenAI import
"""

import os

print("=== SIMPLE API TEST ===")

# Set API key
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

try:
    import openai
    print("✅ OpenAI library imported successfully")
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"✅ API key loaded: {api_key[:10]}...")
    
    # Initialize client
    client = openai.OpenAI(api_key=api_key)
    print("✅ OpenAI client initialized")
    
    # The API key you provided looks like an Azure OpenAI key
    # Let's check what type it is
    if api_key.startswith('sk-'):
        print("🔑 Standard OpenAI API key format")
    else:
        print("🔑 Non-standard key format (possibly Azure OpenAI or other service)")
        print("⚠️  This looks like an Azure OpenAI key, not a standard OpenAI key")
        print("   Azure OpenAI requires different configuration")
    
except ImportError as e:
    print(f"❌ Failed to import openai: {e}")
except Exception as e:
    print(f"❌ Error: {e}")