import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

METADATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'metadata.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'translations')
BASE_URL = 'https://tanzil.net/trans/'

def download_translations():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    translations = data.get('translations', [])
    total = len(translations)
    print(f"Found {total} translations in metadata.json.")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    success_count = 0
    failed = []
    
    for idx, item in enumerate(translations, 1):
        trans_id = item.get('id')
        file_name = item.get('fileName', f"{trans_id}.txt")
        url = f"{BASE_URL}?transID={trans_id}&type=txt-2"
        output_path = os.path.join(OUTPUT_DIR, file_name)
        
        print(f"[{idx}/{total}] Downloading {trans_id} ({item.get('language')}, {item.get('name')})...")
        
        retries = 3
        downloaded = False
        
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as response:
                    content = response.read()
                    
                    if not content or len(content) < 100:
                        raise ValueError(f"Content unexpectedly short: {len(content)} bytes")
                    
                    with open(output_path, 'wb') as out_f:
                        out_f.write(content)
                        
                    item['downloadDate'] = datetime.now(timezone.utc).isoformat()
                    item['fileSize'] = len(content)
                    print(f"  -> Saved {file_name} ({len(content):,} bytes)")
                    downloaded = True
                    success_count += 1
                    break
            except Exception as e:
                print(f"  -> Attempt {attempt + 1} failed for {trans_id}: {e}")
                time.sleep(2)
        
        if not downloaded:
            print(f"  [ERROR] Failed to download {trans_id}")
            failed.append(trans_id)
        
        time.sleep(0.5)

    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*50)
    print(f"Download complete: {success_count}/{total} succeeded.")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")
    print("="*50)

if __name__ == '__main__':
    download_translations()
