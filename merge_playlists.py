import urllib.request
import re

# Sirf Playlist 1 aur Playlist 2 ko merge karna hai
URLS = [
    "https://raw.githubusercontent.com/PRTSTREAM/Fly-final-/refs/heads/main/playlist.m3u",
    "https://raw.githubusercontent.com/PRTSTREAM/Finalfly-720/refs/heads/main/playlist.m3u"
]

# 3rd playlist ka URL sirf position (order) check karne ke liye reference ki tarah use hoga
REF_URL = "https://raw.githubusercontent.com/PRTSTREAM/Filmyfy/refs/heads/main/playlist.m3u"

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
    # Poster image URL (tvg-logo) ko unique identifier maan kar match karenge
    match = re.search(r'tvg-logo=["\']([^"\']+)["\']', meta)
    if match:
        return match.group(1).strip().lower()
    return meta.strip().lower()

def main():
    # 1. 3rd playlist (Reference) se sirf order/positions nikalenge (ek bhi channel add nahi karna)
    ref_order = []
    try:
        content_ref = fetch_m3u(REF_URL)
        parsed_ref = parse_m3u(content_ref)
        for ch in parsed_ref:
            identifier = get_channel_identifier(ch['meta'])
            if identifier not in ref_order:
                ref_order.append(identifier)
        print(f"Loaded {len(ref_order)} reference positions from 3rd playlist.")
    except Exception as e:
        print(f"Error fetching reference playlist: {e}")

    # 2. Playlist 1 aur Playlist 2 ke saare unique channels collect karenge
    unique_channels = {}
    
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

                if identifier not in unique_channels:
                    unique_channels[identifier] = {
                        'ch': ch,
                        'playlist_index': index
                    }
                else:
                    existing = unique_channels[identifier]
                    existing_url = existing['ch']['url']
                    is_existing_pixeldrain = "pixeldrain.dev" in existing_url
                    is_existing_pub = "pub-" in existing_url or "pub." in existing_url

                    if is_current_pixeldrain and is_existing_pub:
                        unique_channels[identifier] = {'ch': ch, 'playlist_index': index}
                    elif not (is_existing_pixeldrain and is_current_pub):
                        if existing['playlist_index'] > index:
                            unique_channels[identifier] = {'ch': ch, 'playlist_index': index}
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # 3. Ab channels ko 3rd playlist ke reference order ke hisab se arrange karenge
    ordered_channels = []
    remaining_channels = []

    # Pehle jo channels 3rd playlist ke order me match honge, unhe unki position par rakhenge
    for identifier in ref_order:
        if identifier in unique_channels:
            ordered_channels.append(unique_channels[identifier]['ch'])
            del unique_channels[identifier] # Add ho gaya toh dictionary se hata do

    # Jo naye channels honge jo 3rd playlist me nahi the, unhe end me add kar denge
    for item in unique_channels.values():
        remaining_channels.append(item['ch'])

    final_list = ordered_channels + remaining_channels

    # Final M3U file generate karo
    final_output = ["#EXTM3U"]
    for ch in final_list:
        final_output.append(ch['meta'])
        final_output.append(ch['url'])

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(final_output))
    
    print(f"Playlist successfully sorted and merged! Total items: {len(final_list)}")

if __name__ == "__main__":
    main()
