import pandas as pd


def parse_presensi(data):
    rows = []
    for i in data:
        rows.append({
            "tanggal": i.get("tanggal"),
            "bulan": i.get("bulan"),
            "tahun": i.get("tahun"),
            "description": i.get("description"),
            "time": i.get("time")
        })
    return pd.DataFrame(rows)


def parse_rencana_kinerja(data):
    rows = []
    for i in data:
        rows.append({
            "rkid": i.get("rkid"),
            "rencana_kinerja": i.get("rencanakinerja"),
            "rencana_kinerja_atasan": i.get("rencanakinerjaatasan"),
            "tahun": i.get("tahun"),
            "tim": i.get("namatim"),
        })
    return pd.DataFrame(rows)
def parse_pelaksanaan(data):
    rows = []

    for i in data:
        rows.append({
            "tanggal": i.get("fullDate"),
            "waktu": i.get("fullTime"),
            "deskripsi": i.get("description"),
            "tahun": i.get("tahun"),
            "bulan": i.get("bulan")
        })

    return pd.DataFrame(rows)
