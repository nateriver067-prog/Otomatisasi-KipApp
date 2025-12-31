# kipapp.py
import argparse
from logger import logger

from executor.scrap import main as scrap_main
from executor.post_rk import main as post_rk_main
from executor.generate_drive_links import main as gen_links_main
from executor.post_pelaksanaan import main as post_pelaksanaan_main


def main():
    parser = argparse.ArgumentParser(
        description="KipApp Automation CLI"
    )

    parser.add_argument(
        "command",
        choices=["scrap", "post-rk", "gen-links", "post", "all"],
        help="Perintah yang dijalankan"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulasi tanpa POST / MKCOL / Share"
    )

    args = parser.parse_args()

    logger.info(f"🚀 KipApp CLI | Command={args.command}")
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'REAL RUN'}")

    if args.command == "scrap":
        scrap_main()

    elif args.command == "post-rk":
        post_rk_main(dry_run=args.dry_run)

    elif args.command == "gen-links":
        gen_links_main(dry_run=args.dry_run)

    elif args.command == "post":
        post_pelaksanaan_main(dry_run=args.dry_run)

    elif args.command == "all":
        scrap_main()
        post_rk_main(dry_run=args.dry_run)
        gen_links_main(dry_run=args.dry_run)
        post_pelaksanaan_main(dry_run=args.dry_run)

    logger.info("✅ SELESAI")


if __name__ == "__main__":
    main()
