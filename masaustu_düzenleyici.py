import ctypes
import os
from pathlib import Path
import shutil
import subprocess
import urllib.request

# 1. MASAÜSTÜ YOLUNU BULMA (OneDrive veya Standart Windows)
home = Path.home()
desktop_path = home / "Desktop"
if not desktop_path.exists():
    desktop_path = home / "OneDrive" / "Desktop"

# 2. SINIFLANDIRMA VE DOĞRUDAN .ICO İKON BAĞLANTILARI
CATEGORIES = {
    "Gorseller": {
        "exts": [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".svg",
            ".webp",
            ".ico",
        ],
        "icon": "https://img.icons8.com/color/48/image-file.ico",
    },
    "Belgeler": {
        "exts": [
            ".pdf",
            ".docx",
            ".doc",
            ".txt",
            ".xlsx",
            ".xls",
            ".pptx",
            ".csv",
        ],
        "icon": "https://img.icons8.com/color/48/folder-invoices.ico",
    },
    "Videolar": {
        "exts": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"],
        "icon": "https://img.icons8.com/color/48/video-file.ico",
    },
    "Muzik_ve_Ses": {
        "exts": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
        "icon": "https://img.icons8.com/color/48/audio-file.ico",
    },
    "Arsivler": {
        "exts": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
        "icon": "https://img.icons8.com/color/48/zip.ico",
    },
    "Uygulamalar": {
        "exts": [".exe", ".msi", ".bat", ".sh"],
        "icon": "https://img.icons8.com/color/48/exe.ico",
    },
    "Kod_Dosyalari": {
        "exts": [
            ".py",
            ".html",
            ".css",
            ".js",
            ".json",
            ".cpp",
            ".c",
            ".java",
            ".php",
        ],
        "icon": "https://img.icons8.com/color/48/code.ico",
    },
}


def download_icon(url, save_path):
    """Web'den .ico dosyasını doğrudan indirir."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with (
            urllib.request.urlopen(req, timeout=10) as response,
            open(save_path, "wb") as out_file,
        ):
            shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        print(f"İkon indirilemedi ({url}): {e}")
        return False


def apply_folder_icon(folder_path, icon_path):
    """Windows klasörüne ikonu desktop.ini ile tanımlar."""
    try:
        ini_path = os.path.join(folder_path, "desktop.ini")

        # Var olan desktop.ini varsa gizliliğini kaldır
        if os.path.exists(ini_path):
            subprocess.run(
                f'attrib -h -s "{ini_path}"', shell=True, capture_output=True
            )

        # desktop.ini içeriğini yaz
        ini_content = (
            "[.ShellClassInfo]\n"
            f"IconResource={icon_path},0\n"
            "[ViewState]\n"
            "Mode=\n"
            "Vid=\n"
            "FolderType=Generic\n"
        )

        with open(ini_path, "w", encoding="utf-8") as f:
            f.write(ini_content)

        # Öznitelikleri ayarla (Windows'un ikonu tanıması için şarttır)
        subprocess.run(
            f'attrib +h +s "{ini_path}"', shell=True, capture_output=True
        )
        subprocess.run(
            f'attrib +r "{folder_path}"', shell=True, capture_output=True
        )
    except Exception as e:
        print(f"İkon uygulanırken hata: {e}")


def refresh_windows_icon_cache():
    """Windows Önbelleğini yenileyerek ikonların anında görünmesini sağlar."""
    try:
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, 0, 0)
    except Exception:
        pass


def start_organizing():
    print("=" * 50)
    print(f"Masaüstü taranıyor: {desktop_path}")
    print("=" * 50)

    # Betiğin kendi adını al (Kendi kendini bir klasöre taşımasın)
    try:
        current_script = os.path.basename(__file__)
    except NameError:
        current_script = ""

    moved_count = 0

    for item in os.listdir(desktop_path):
        item_path = os.path.join(desktop_path, item)

        # Klasörleri, kısayolları, sistem dosyalarını ve bu kodu atla
        if (
            os.path.isdir(item_path)
            or item.endswith(".lnk")
            or item.endswith(".ini")
            or item == current_script
        ):
            continue

        _, ext = os.path.splitext(item)
        ext = ext.lower()

        # Doğru kategoriyi bul
        target_category = "Diger"
        for category, data in CATEGORIES.items():
            if ext in data["exts"]:
                target_category = category
                break

        # Hedef Klasörü Oluştur
        target_folder = os.path.join(desktop_path, target_category)

        if not os.path.exists(target_folder):
            os.makedirs(target_folder, exist_ok=True)

            # Klasör yeni oluşturulduysa ikon indir ve uygula
            if target_category in CATEGORIES:
                icon_path = os.path.join(target_folder, "folder_icon.ico")
                print(f"[{target_category}] için özel ikon indiriliyor...")
                if download_icon(CATEGORIES[target_category]["icon"], icon_path):
                    apply_folder_icon(target_folder, icon_path)

        # Dosyayı Hedef Klasöre Taşı
        destination_file = os.path.join(target_folder, item)

        # Aynı isimde dosya varsa ismini değiştir (Üzerine yazmasın)
        if os.path.exists(destination_file):
            base, extension = os.path.splitext(item)
            destination_file = os.path.join(
                target_folder, f"{base}_kopya{extension}"
            )

        try:
            shutil.move(item_path, destination_file)
            print(f"✓ Taşındı: {item} -> {target_category}/")
            moved_count += 1
        except Exception as e:
            print(f"X Taşıma başarısız ({item}): {e}")

    # Windows ikon önbelleğini zorla yenile
    refresh_windows_icon_cache()

    print("=" * 50)
    print(
        f"İŞLEM TAMAMLANDI! Toplam {moved_count} dosya başarıyla düzenlendi."
    )
    print("=" * 50)


if __name__ == "__main__":
    start_organizing()
