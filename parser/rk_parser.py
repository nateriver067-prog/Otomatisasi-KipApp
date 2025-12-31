import pandas as pd


def parse_rencana_kinerja_tahunan(rk_list):
    """
    Output DataFrame:
    rkid | rencana_kinerja | iki_ids | iscopied | isused

    - iki_ids dipisah koma (untuk POST)
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
            "iki_ids": ",".join(iki_ids),
            "iscopied": rk.get("iscopied"),
            "isused": rk.get("isused")
        })

    return pd.DataFrame(
        rows,
        columns=[
            "rkid",
            "rencana_kinerja",
            "iki_ids",
            "iscopied",
            "isused"
        ]
    )
