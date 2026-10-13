#!/usr/bin/env python3
"""
Test client for the Image to PDF converter API.
This script creates test images and sends them to the backend.
"""

import requests
import os
import tempfile
from PIL import Image, ImageDraw
import sys

def create_test_images(output_dir, num_images=3):
    """Create test images for testing the API."""
    image_paths = []
    
    for i in range(num_images):
        # Create a simple image with text
        img = Image.new('RGB', (800, 600), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        
        # Draw some text
        text = f"Test Image {i+1}"
        d.text((400, 300), text, fill=(255, 255, 255))
        
        # Save as different formats
        if i == 0:
            # PNG
            img_path = os.path.join(output_dir, f"test_image_{i+1}.png")
            img.save(img_path, 'PNG')
        elif i == 1:
            # JPG
            img_path = os.path.join(output_dir, f"test_image_{i+1}.jpg")
            img.save(img_path, 'JPEG', quality=95)
        else:
            # Another JPG with different name
            img_path = os.path.join(output_dir, f"test_image_{i+1}.jpeg")
            img.save(img_path, 'JPEG', quality=90)
        
        image_paths.append(img_path)
        print(f"Created test image: {os.path.basename(img_path)}")
    
    return image_paths

def test_api(api_url="http://localhost:3000"):
    """Test the Image to PDF API."""
    
    print(f"\n=== Testing Image to PDF API at {api_url} ===\n")
    
    # Create temporary directory for test images
    with tempfile.TemporaryDirectory() as temp_dir:
        # Step 1: Create test images
        print("1. Creating test images...")
        image_paths = create_test_images(temp_dir, 3)
        
        # Step 2: Test /api/pdf-info endpoint
        print("\n2. Testing /api/pdf-info endpoint...")
        try:
            response = requests.get(f"{api_url}/api/pdf-info")
            if response.status_code == 200:
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.json()}")
            else:
                print(f"   Error: Status {response.status_code}")
                print(f"   Response: {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"   Error: Cannot connect to {api_url}")
            print("   Make sure the Flask server is running!")
            return False
        
        # Step 3: Test /api/images-to-pdf endpoint
        print("\n3. Testing /api/images-to-pdf endpoint...")
        
        # Prepare files for upload
        files = []
        for img_path in image_paths:
            files.append(('files', (os.path.basename(img_path), open(img_path, 'rb'), 'image/jpeg' if img_path.endswith(('.jpg', '.jpeg')) else 'image/png')))
        
        try:
            response = requests.post(f"{api_url}/api/images-to-pdf", files=files)
            
            # Clean up - close file handles
            for _, file_tuple in files:
                file_tuple[1].close()
            
            if response.status_code == 200:
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('Content-Type')}")
                print(f"   Content-Disposition: {response.headers.get('Content-Disposition')}")
                print(f"   File size: {len(response.content)} bytes")
                
                # Save the PDF for inspection
                pdf_path = os.path.join(temp_dir, "output.pdf")
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                print(f"   PDF saved to: {pdf_path}")
                
                # Check if it's a valid PDF
                if response.content[:4] == b'%PDF':
                    print("   ✓ PDF appears to be valid (starts with %PDF)")
                else:
                    print("   ✗ PDF appears to be invalid")
                
                return True
            else:
                print(f"   Error: Status {response.status_code}")
                print(f"   Response: {response.json()}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"   Error: Cannot connect to {api_url}")
            print("   Make sure the Flask server is running!")
            return False
        except Exception as e:
            print(f"   Unexpected error: {e}")
            return False

def main():
    """Main test function."""
    
    # Get API URL from command line or use default
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
    
    print("\n" + "="*60)
    print("Image to PDF Converter API Test")
    print("="*60)
    
    success = test_api(api_url)
    
    print("\n" + "="*60)
    if success:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")
    print("="*60)

if __name__ == "__main__":
    main()