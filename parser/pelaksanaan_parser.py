import pandas as pd


def parse_pelaksanaan(data):
    """
    Output DataFrame:
    tanggal | waktu | rkid | rencana_kinerja | deskripsi | tahun | bulan

    Catatan:
    - rkid & rencana_kinerja sengaja dikosongkan
      → akan diisi manual / dropdown Excel
    """

    rows = []

    for i in data:
        rows.append({
            "tanggal": i.get("fullDate") or i.get("tanggal"),
            "waktu": i.get("fullTime") or i.get("time"),
            "rkid": "",                    # diisi kemudian
            "rencana_kinerja": "",         # diisi kemudian
            "deskripsi": i.get("description"),
            "tahun": i.get("tahun"),
            "bulan": i.get("bulan")
        })

    return pd.DataFrame(
        rows,
        columns=[
            "tanggal",
            "waktu",
            "rkid",
            "rencana_kinerja",
            "deskripsi",
            "tahun",
            "bulan"
        ]
    )
