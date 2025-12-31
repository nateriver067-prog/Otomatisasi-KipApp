import datetime
import pandas as pd

from config import TAHUN, BULAN, OUTPUT_DIR
from logger import logger

from api.drive import (
    login_drive_session,
    get_drive_user_id,
    create_folder,
    get_or_create_share
)

OUTPUT_FILE = f"{OUTPUT_DIR}/KipApp_{TAHUN}_{BULAN:02d}_links.xlsx"


# ==================================================
# MAIN
# ==================================================
def main(dry_run=False):
    logger.info("🚀 Generate Drive Folder & Share Link")

    if dry_run:
        logger.warning("🧪 DRY RUN — tidak membuat folder & link Drive")
        return
    # =========================
    # LOGIN DRIVE
    # =========================
    cookies, requesttoken = login_drive_session()
    user_id = get_drive_user_id(cookies, requesttoken)

    # =========================
    # STRUKTUR DASAR
    # KipApp/YYYY/MM/YYYY-MM-DD
    # =========================
    base_root = "KipApp"
    year_path = f"{base_root}/{TAHUN}"
    month_path = f"{year_path}/{BULAN:02d}"

    if not dry_run:
        create_folder(user_id, base_root, cookies, requesttoken)
        create_folder(user_id, year_path, cookies, requesttoken)
        create_folder(user_id, month_path, cookies, requesttoken)
    else:
        logger.info(f"[DRY RUN] Buat folder: {base_root}")
        logger.info(f"[DRY RUN] Buat folder: {year_path}")
        logger.info(f"[DRY RUN] Buat folder: {month_path}")

    rows = []

    # =========================
    # LOOP TANGGAL DALAM BULAN
    # =========================
    for day in range(1, 32):
        try:
            tanggal = datetime.date(TAHUN, BULAN, day)
        except ValueError:
            continue

        tgl_str = tanggal.strftime("%Y-%m-%d")
        folder_path = f"{month_path}/{tgl_str}"

        if dry_run:
            logger.info(f"[DRY RUN] Folder: {folder_path}")
            share_link = f"(dry-run)/{folder_path}"
        else:
            # 1️⃣ buat folder (aman: idempotent)
            create_folder(user_id, folder_path, cookies, requesttoken)

            # 2️⃣ ambil / buat link (1 folder = 1 link)
            share_link = get_or_create_share(
                f"/{folder_path}",
                cookies,
                requesttoken
            )

        rows.append({
            "tanggal": tgl_str,
            "folder_path": folder_path,
            "share_link": share_link
        })

        logger.info(f"🔗 {tgl_str} → {share_link}")

    # =========================
    # EXPORT EXCEL
    # =========================
    df = pd.DataFrame(rows)
    df.to_excel(OUTPUT_FILE, index=False)

    logger.info("✅ Generate Drive Link selesai")
    logger.info(f"📄 File output: {OUTPUT_FILE}")


# ==================================================
# ENTRY
# ==================================================
if __name__ == "__main__":
    main()
