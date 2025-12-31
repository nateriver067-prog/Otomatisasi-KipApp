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
def parse_rencana_kinerja_bulanan(rk_list):
    """
    Output:
    rkid | rencana_kinerja | iki_ids | iscopied | isused
    """
    rows = []

    for rk in rk_list:
        iki_ids = []

        for iki in rk.get("iki", []):
            if iki.get("id"):
                iki_ids.append(str(iki["id"]))

        rows.append({
            "rkid": str(rk.get("id")),
            "rencana_kinerja": rk.get("rencanakinerja"),
            "iki_ids": ",".join(iki_ids),   # penting untuk POST
            "iscopied": rk.get("iscopied"),
            "isused": rk.get("isused"),
        })

    return pd.DataFrame(rows)

