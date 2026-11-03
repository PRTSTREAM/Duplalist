import urllib.request
import re

# Dono M3U playlist ke URLs (Order important hai: 1st list pehle aayegi)
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
    # Ab duplicate pehchanne ke liye poster image URL (tvg-logo) ka use karenge
    match = re.search(r'tvg-logo=["\']([^"\']+)["\']', meta)
    if match:
        # Logo URL ko clean karke return karenge taaki exact match ho
        logo_url = match.group(1).strip().lower()
        # Agar image URL me size ya dimensions ka koi parameter ho toh use hata sakte hain, 
        # par filmyfly me direct URL hota hai isliye ye seedha kaam karega
        return logo_url
    
    # Agar kisi me logo na ho toh fallback ke liye pura meta line le lo
    return meta.strip().lower()

def main():
    channel_map = {}
    
    for index, url in enumerate(URLS):
        try:
            content = fetch_m3u(url)
            parsed = parse_m3u(content)
            print(f"Fetched {len(parsed)} items from {url}")
            
            for ch in parsed:
                identifier = get_channel_identifier(ch['meta'])
                url_val = ch['url']
                
                is_current_pixeldrain = "pixeldrain.dev" in url_val
                is_current_pub = "pub-" in url_val or "pub." in url_val

                if identifier not in channel_map:
                    channel_map[identifier] = {
                        'ch': ch,
                        'playlist_index': index
                    }
                else:
                    existing = channel_map[identifier]
                    existing_ch = existing['ch']
                    existing_url = existing_ch['url']
                    
                    is_existing_pixeldrain = "pixeldrain.dev" in existing_url
                    is_existing_pub = "pub-" in existing_url or "pub." in existing_url

                    # Rule 1: Pixeldrain ko priority do agar dusre me pub ho
                    if is_current_pixeldrain and is_existing_pub:
                        channel_map[identifier] = {'ch': ch, 'playlist_index': index}
                    elif is_existing_pixeldrain and is_current_pub:
                        pass 
                    else:
                        # Rule 2: Pehli playlist ko priority do
                        if existing['playlist_index'] > index:
                            channel_map[identifier] = {'ch': ch, 'playlist_index': index}

        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # Final M3U file generate karo
    final_output = ["#EXTM3U"]
    for item in channel_map.values():
        ch = item['ch']
        final_output.append(ch['meta'])
        final_output.append(ch['url'])

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(final_output))
    
    print(f"Playlist successfully merged using Poster Image URL! Total unique items: {len(channel_map)}")

if __name__ == "__main__":
    main()
