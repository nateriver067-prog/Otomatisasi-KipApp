import pandas as pd


def parse_pelaksanaan(data):
    rows = []

    for i in data:
        rows.append({
            "tanggal": i.get("fullDate") or i.get("tanggal"),
            "waktu": i.get("fullTime") or i.get("time"),
            "rkid": "",                     # DIKOSONGKAN
            "rencana_kinerja": "",          # DIKOSONGKAN
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
def parse_rencana_kinerja(data):
    rows = []

    for i in data:
        rows.append({
            "rkid": i.get("rkid"),
            "rencana_kinerja": i.get("rencanakinerja"),
            "rencana_kinerja_atasan": i.get("rencanakinerjaatasan"),
            "tahun": i.get("tahun"),
            "tim": i.get("namatim")
        })

    return pd.DataFrame(rows)

