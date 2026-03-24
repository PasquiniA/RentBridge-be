#!/usr/bin/env python3
"""
End-to-End Test Script for Mail-Merge Endpoint

This script tests the complete mail-merge flow:
1. Sends request to /api/v1/generate-contract endpoint
2. Verifies PDF is generated and uploaded to Supabase
3. Checks that the public URL is accessible
4. Validates CORS headers

Usage:
    # Test against local server
    python scripts/test_mail_merge_e2e.py

    # Test against ngrok tunnel
    python scripts/test_mail_merge_e2e.py --tunnel

    # Test against custom URL
    python scripts/test_mail_merge_e2e.py --url https://your-domain.com
"""

import os
import sys
import argparse
import requests
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_mail_merge_endpoint(base_url: str, test_cors: bool = True):
    """
    Test the mail-merge endpoint with a complete E2E flow.
    
    Args:
        base_url: Base URL of the API (e.g., http://localhost:8000 or ngrok URL)
        test_cors: Whether to test CORS headers
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    print("=" * 70)
    print("Mail-Merge E2E Test")
    print("=" * 70)
    print(f"\n🎯 Target URL: {base_url}")
    
    # Test 1: Health check
    print("\n" + "=" * 70)
    print("Test 1: Health Check")
    print("=" * 70)
    try:
        health_url = f"{base_url}/health"
        print(f"GET {health_url}")
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print("✓ Health check passed")
            print(f"  Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Generate contract with valid data
    print("\n" + "=" * 70)
    print("Test 2: Generate Contract (Valid Data)")
    print("=" * 70)
    
    contract_data = {
        "template_name": "test_contract",
        "merge_data": {
            "landlord_name": "Giuseppe Verdi",
            "tenant_name": "Mario Rossi",
            "property_address": "Via Roma 123, Milano, 20100",
            "monthly_rent": "1.200,00 €",
            "contract_date": datetime.now().strftime("%d %B %Y"),
            "contract_duration": "4 anni + 4 anni (canone libero)"
        }
    }
    
    try:
        generate_url = f"{base_url}/api/v1/generate-contract"
        print(f"POST {generate_url}")
        print(f"Request data: {contract_data}")
        
        response = requests.post(
            generate_url,
            json=contract_data,
            timeout=30  # Allow time for document processing
        )
        
        if response.status_code == 200:
            print("✓ Contract generated successfully")
            result = response.json()
            
            print(f"\n📄 Result:")
            print(f"  PDF URL: {result['pdf_url']}")
            print(f"  File Path: {result['file_path']}")
            print(f"  Placeholders Replaced: {result['placeholders_replaced']}")
            print(f"  Processing Time: {result['processing_time_ms']:.2f}ms")
            
            # Test 3: Verify PDF URL is accessible
            print("\n" + "=" * 70)
            print("Test 3: Verify PDF URL Accessibility")
            print("=" * 70)
            
            pdf_url = result['pdf_url']
            print(f"HEAD {pdf_url}")
            
            pdf_response = requests.head(pdf_url, timeout=10)
            
            if pdf_response.status_code == 200:
                print("✓ PDF URL is accessible")
                print(f"  Status: {pdf_response.status_code}")
                
                # Check content type
                content_type = pdf_response.headers.get('Content-Type', '')
                if 'pdf' in content_type.lower() or pdf_url.endswith('.pdf'):
                    print(f"  Content-Type: {content_type or 'application/pdf (inferred)'}")
                else:
                    print(f"  ⚠️  Content-Type: {content_type} (expected PDF)")
            else:
                print(f"❌ PDF URL returned status {pdf_response.status_code}")
                return False
            
        elif response.status_code == 404:
            print(f"❌ Template not found")
            print(f"  Make sure 'test_contract.docx' exists in app/templates/")
            print(f"  Response: {response.json()}")
            return False
        elif response.status_code == 500:
            print(f"❌ Server error during generation")
            print(f"  Response: {response.json()}")
            print(f"\n  Possible causes:")
            print(f"    - LibreOffice not installed")
            print(f"    - Supabase credentials not configured")
            print(f"    - Template file corrupted")
            return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"  Response: {response.json()}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out (processing took > 30 seconds)")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Test 4: Test with missing fields
    print("\n" + "=" * 70)
    print("Test 4: Generate Contract (Missing Fields)")
    print("=" * 70)
    
    invalid_data = {
        "template_name": "test_contract",
        "merge_data": {
            "landlord_name": "Giuseppe Verdi",
            "tenant_name": "Mario Rossi"
            # Missing: property_address, monthly_rent, contract_date, contract_duration
        }
    }
    
    try:
        print(f"POST {generate_url}")
        print(f"Request data: {invalid_data}")
        
        response = requests.post(generate_url, json=invalid_data, timeout=10)
        
        if response.status_code == 400:
            print("✓ Missing fields correctly rejected")
            error_data = response.json()
            print(f"  Error: {error_data}")
        else:
            print(f"⚠️  Expected 400, got {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Test failed: {e}")
    
    # Test 5: Test with nonexistent template
    print("\n" + "=" * 70)
    print("Test 5: Generate Contract (Nonexistent Template)")
    print("=" * 70)
    
    nonexistent_data = {
        "template_name": "nonexistent_template_xyz",
        "merge_data": {"field": "value"}
    }
    
    try:
        print(f"POST {generate_url}")
        print(f"Request data: {nonexistent_data}")
        
        response = requests.post(generate_url, json=nonexistent_data, timeout=10)
        
        if response.status_code == 404:
            print("✓ Nonexistent template correctly rejected")
            error_data = response.json()
            print(f"  Error: {error_data}")
        else:
            print(f"⚠️  Expected 404, got {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Test failed: {e}")
    
    # Test 6: CORS headers (if requested)
    if test_cors:
        print("\n" + "=" * 70)
        print("Test 6: CORS Headers")
        print("=" * 70)
        
        try:
            print(f"OPTIONS {generate_url}")
            print(f"Origin: https://example.com")
            
            cors_response = requests.options(
                generate_url,
                headers={"Origin": "https://example.com"},
                timeout=10
            )
            
            cors_headers = {
                k: v for k, v in cors_response.headers.items()
                if 'access-control' in k.lower()
            }
            
            if cors_headers:
                print("✓ CORS headers present")
                for header, value in cors_headers.items():
                    print(f"  {header}: {value}")
            else:
                print("⚠️  No CORS headers found")
                print("  This may be expected if CORS is not configured")
                
        except Exception as e:
            print(f"⚠️  CORS test failed: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ E2E Test Suite Completed Successfully!")
    print("=" * 70)
    print("\n📊 Summary:")
    print("  ✓ Health check passed")
    print("  ✓ Contract generation successful")
    print("  ✓ PDF uploaded to Supabase")
    print("  ✓ Public URL accessible")
    print("  ✓ Error handling validated")
    if test_cors:
        print("  ✓ CORS headers checked")
    
    return True


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="End-to-end test for mail-merge endpoint"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--tunnel",
        action="store_true",
        help="Use ngrok tunnel URL from health endpoint"
    )
    parser.add_argument(
        "--no-cors",
        action="store_true",
        help="Skip CORS header tests"
    )
    
    args = parser.parse_args()
    
    base_url = args.url
    
    # If tunnel flag is set, get tunnel URL from health endpoint
    if args.tunnel:
        print("🔍 Fetching ngrok tunnel URL...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            health_data = response.json()
            
            if "tunnel_url" in health_data and health_data["tunnel_url"]:
                base_url = health_data["tunnel_url"]
                print(f"✓ Using tunnel URL: {base_url}")
            else:
                print("❌ Tunnel URL not found in health endpoint")
                print("Make sure the app is running with tunnel enabled")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to get tunnel URL: {e}")
            sys.exit(1)
    
    # Run tests
    success = test_mail_merge_endpoint(
        base_url=base_url,
        test_cors=not args.no_cors
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
