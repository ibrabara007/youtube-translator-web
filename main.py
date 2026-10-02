import streamlit as st
import urllib.parse
import json
import urllib.request
import re
import html

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="YouTube Title & Description Translator",
    page_icon="🎬",
    layout="wide"
)

# --- Fungsi Utility & Scraping ---
def clean_youtube_url(url):
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return url.strip()

def get_youtube_data(url):
    try:
        video_id = clean_youtube_url(url)
        full_url = f"https://www.youtube.com/watch?v={video_id}"
        
        req = urllib.request.Request(
            full_url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8,id;q=0.7'
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_data = response.read()
            html_text = raw_data.decode('utf-8', errors='ignore')
            
            title = ""
            title_match = re.search(r'<meta property="og:title" content="(.*?)">', html_text)
            if title_match:
                title = title_match.group(1)
            else:
                title_match_alt = re.search(r'<title>(.*?)</title>', html_text)
                if title_match_alt:
                    title = title_match_alt.group(1).replace(" - YouTube", "")
            
            description = ""
            desc_match = re.search(r'\"shortDescription\":\"(.*?)\",\"isCrawlable\"', html_text)
            if desc_match:
                raw_desc = desc_match.group(1)
                try:
                    description = json.loads(f'"{raw_desc}"')
                except Exception:
                    description = raw_desc.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            else:
                meta_desc = re.search(r'<meta property="og:description" content="(.*?)">', html_text)
                if meta_desc:
                    description = meta_desc.group(1)
                
            return html.unescape(title.strip()), html.unescape(description.strip())
    except Exception:
        return None, None

def translate_text(text, target_lang):
    if not text or not text.strip():
        return ""
    try:
        encoded_text = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={encoded_text}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=12) as response:
            result = json.loads(response.read().decode('utf-8'))
            translated_pieces = [item[0] for item in result[0] if item[0] is not None]
            return "".join(translated_pieces)
    except Exception:
        return text

# --- Tampilan UI Streamlit ---
st.title("🎬 YouTube Title & Description Translator")
st.write("Terjemahkan Judul dan Deskripsi Video YouTube secara otomatis dalam berbagai bahasa.")

url_input = st.text_input("Link Video YouTube:", placeholder="https://youtu.be/xxx atau https://www.youtube.com/watch?v=xxx")

languages_dict = {
    "Inggris (English)": "en",
    "Indonesia": "id",
    "Spanyol (Spanish)": "es",
    "Mandarin (Chinese Traditional)": "zh-TW",
    "Jepang (Japanese)": "ja",
    "Korea (Korean)": "ko",
    "Arab (Arabic)": "ar",
    "Jerman (German)": "de",
    "Prancis (French)": "fr",
    "Rusia (Russian)": "ru",
    "Hindi (Hindi)": "hi"
}

options = ["⚡ Semua Bahasa (Multi-Translate)"] + list(languages_dict.keys())
selected_option = st.selectbox("Pilih Bahasa Tujuan:", options)

if st.button("🚀 Terjemahkan Sekarang", type="primary"):
    if not url_input.strip():
        st.warning("Silakan masukkan link YouTube terlebih dahulu!")
    else:
        with st.spinner("Sedang mengambil dan menerjemahkan data..."):
            title, description = get_youtube_data(url_input)
            
            if not title:
                st.error("Gagal mengambil data video. Pastikan link YouTube valid!")
            else:
                target_langs = languages_dict if selected_option == "⚡ Semua Bahasa (Multi-Translate)" else {selected_option: languages_dict[selected_option]}
                
                tabs = st.tabs([lang.split(' ')[0] for lang in target_langs.keys()])
                
                for tab, (lang_name, lang_code) in zip(tabs, target_langs.items()):
                    with tab:
                        trans_title = translate_text(title, lang_code)
                        trans_desc = translate_text(description, lang_code) if description else "Deskripsi kosong."
                        
                        st.subheader("📌 Judul Hasil Terjemahan")
                        st.code(trans_title, language=None)
                        
                        st.subheader("📝 Deskripsi Hasil Terjemahan")
                        st.text_area(label="Deskripsi", value=trans_desc, height=300, key=f"desc_{lang_code}")