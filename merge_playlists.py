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
            # Yeh URL line hai
            if current_meta:
                # Channel ka unique identifier nikalne ke liye title ya pura meta tag use karenge
                channels.append({
                    'meta': current_meta,
                    'url': line
                })
                current_meta = ""
    return channels

def get_channel_identifier(meta):
    # tvg-id ya title match karne ke liye clean name nikalna
    # Example: #EXTINF:-1 tvg-logo="..." title="NEW 4K", Movie Name
    match = re.search(r'title=["\']([^"\']+)["\']', meta)
    if match:
        return match.group(1).strip().lower()
    return meta.strip().lower()

def main():
    all_channels = []
    
    # 1. Dono playlists ko fetch aur parse karo
    for url in URLS:
        try:
            content = fetch_m3u(url)
            parsed = parse_m3u(content)
            all_channels.extend(parsed)
            print(print(f"Fetched {len(parsed)} items from {url}"))
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # 2. Duplicate handling aur Pixeldrain priority logic
    # Dictionary banayenge jisme key = channel title/identifier hogi
    channel_map = {}

    for ch in all_channels.get if isinstance(all_channels, list) else []:
        pass

    for ch in all_channels:
        identifier = get_channel_identifier(ch['meta'])
        url = ch['url']

        if identifier not in channel_map:
            channel_map[identifier] = ch
        else:
            existing_ch = channel_map[identifier]
            existing_url = existing_ch['url']

            # Rule check: Agar current ya existing me pixeldrain hai aur dusre me pub- hai
            is_current_pixeldrain = "pixeldrain.dev" in url
            is_existing_pixeldrain = "pixeldrain.dev" in existing_url
            
            is_current_pub = "pub-" in url or "pub." in url
            is_existing_pub = "pub-" in existing_url or "pub." in existing_url

            if is_current_pixeldrain and is_existing_pub:
                # Current pixeldrain hai, purana pub wala hai -> Pixeldrain ko rakho
                channel_map[identifier] = ch
            elif is_existing_pixeldrain and is_current_pub:
                # Purana pixeldrain hai, naya pub wala hai -> Purana hi rehne do (Pixeldrain priority)
                pass
            else:
                # Agar dono same category ke hain ya alag hain, toh latest ya pehla wala rakh sakte hain
                # Aapke mutabiq agar pixeldrain nahi hai toh jo hai use rakhlo
                if not is_existing_pixeldrain and is_current_pixeldrain:
                    channel_map[identifier] = ch

    # 3. Final M3U file generate karo
    final_output = ["#EXTM3U"]
    for ch in channel_map.values():
        final_output.append(ch['meta'])
        final_output.append(ch['url'])

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(final_output))
    
    print("Playlist successfully merged and cleaned!")

if __name__ == "__main__":
    main()
