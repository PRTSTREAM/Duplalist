import urllib.request
import re

# Dono M3U playlist ke URLs
URLS = [
    "https://raw.githubusercontent.com/PRTSTREAM/Fly-final-/refs/heads/main/playlist.m3u",
    "https://raw.githubusercontent.com/PRTSTREAM/Finalfly-720/refs/heads/main/playlist.m3u"
]

def fetch_m3u(url):
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8', errors='ignore')

def parse_m3u(content):
    lines = content.splitlines()
    channels = []
    current_meta = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF:"):
            current_meta = line
        elif not line.startswith("#"):
            if current_meta:
                channels.append({
                    'meta': current_meta,
                    'url': line
                })
                current_meta = ""
    return channels

def get_channel_identifier(meta):
    # Poster image URL (tvg-logo) ko unique identifier maan kar duplicate check karenge
    match = re.search(r'tvg-logo=["\']([^"\']+)["\']', meta)
    if match:
        return match.group(1).strip().lower()
    return meta.strip().lower()

def main():
    merged_channels = []
    seen_identifiers = set()
    
    # Dono playlists ka data ek-ek karke fetch karenge
    all_parsed_lists = []
    for url in URLS:
        try:
            content = fetch_m3u(url)
            parsed = parse_m3u(content)
            print(f"Fetched {len(parsed)} items from {url}")
            all_parsed_lists.append(parsed)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # Ab dono playlists ko alternate ya sequence me process karenge taaki positions maintain rahein
    # Yahan hum pehle playlist 1 ke items lenge, phir playlist 2 ke jo unique honge unhe add karenge
    # Agar aapko ek iska ek uska (zipper merge) chahiye, toh wo bhi ho jayega. 
    # Neeche standard sequence merge hai jo pehli list ki positions ko pehle priority deta hai:
    
    for parsed in all_parsed_lists:
        for ch in parsed:
            identifier = get_channel_identifier(ch['meta'])
            
            # Agar ye movie pehle nahi aayi hai, toh isko iski current position par hi add kar lo
            if identifier not in seen_identifiers:
                seen_identifiers.add(identifier)
                merged_channels.append(ch)
            else:
                # Agar ye pehle aa chuki hai (duplicate hai), toh doosri jagah wale ko skip kar do
                # taaki pehli wali original position safe rahe!
                pass

    # Final M3U file generate karo
    final_output = ["#EXTM3U"]
    for ch in merged_channels:
        final_output.append(ch['meta'])
        final_output.append(ch['url'])

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(final_output))
    
    print(f"Playlist successfully merged! Total unique items: {len(merged_channels)}")

if __name__ == "__main__":
    main()
