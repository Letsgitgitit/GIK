"""
HF NAV monitoring report -> gold Parquet                                BUILD 2026-11-05a

Reads every "HFDB Reporting - <Month> <YYYY>.xls*" file in SRC_DIR and writes ONE gold Parquet
(one row per fund per month-end) that Power BI reads as FACT_HF_NAV.

Same rules as the VBA loader (HFNavLoader.bas build 2026-11-05b), plus the fund -> entity map:
  - columns found by header text (banner | sub-header), never by letter: 5 layouts seen since Jan 2025
  - unknown header -> WARN ; missing required column -> FILE SKIPPED (WARN, the other files are published)
  - title date must equal the file-name month, else FILE SKIPPED ; a month in two files -> both SKIPPED
  - a month published last time but missing now -> FAIL, nothing published (protects history)
  - identical duplicate fund rows inside a file are merged ; different duplicates -> WARN, both kept
  - "N/A", "NA", "-" in number / date columns -> null, counted (INFO); anything else unreadable -> null, WARN
  - no locale: numbers are Excel numbers or parsed with explicit rules, dates are Excel dates or mm/dd/yyyy
  - Total Authorization and % of NAV are not loaded (limits come from the facts)
  - fund -> HeadOfficeSirisId from NAME_MAP (CSV: Fund_Name, HeadOfficeSirisId); unmapped names -> WARN, listed
Plausibility (INFO, never blocks): NAV_Prev x (1 + NAVChg_1M) vs NAV_Cur ; this month's NAV_Prev vs last month's
NAV_Cur for the same fund ; |monthly performance| > 50%.

Exit codes: 0 PASS, 1 WARN (gold published), 2 FAIL (nothing published: no readable file, a month lost vs the
last run, a write check failed, or a version mismatch).
Run:  python hfnav_run.py            (normal)
      python hfnav_run.py --dry-run  (read and report, publish nothing)
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys
import time

# =============================================================== CONFIG (edit these)
SRC_DIR = r"<NAV folder with the HFDB Reporting files>"
GOLD_DIR = r"<gold folder read by Power BI>"          # holds ONLY hfnav_gold.parquet (Folder.Files is recursive)
WORK_DIR = r"<work folder for reports + manifest>"    # never inside GOLD_DIR
NAME_MAP = r"<path to HF_NAME_MAP.csv>"
FILE_GLOB = "HFDB Reporting - *.xls*"
GOLD_FILE = "hfnav_gold.parquet"
CONTRACT_VERSION = "hfnav-gold-v1.0"
BUILD = "2026-11-05a"
PINNED = {"python": (3, 10), "pandas": "1.3.5", "numpy": "1.21.5", "pyarrow": "24.0.0"}
# ===============================================================

OUT_COLS = ["MonthEnd", "SourceFile", "Layout", "SourceRow", "CPH_Name", "Fund_Name", "HeadOfficeSirisId",
            "MapStatus", "Rating", "Strategy", "StrategyLatest", "ValidityDate", "LastDDDate",
            "NAV_EoY", "NAV_Prev", "NAV_Cur", "Perf_EoY", "Perf_Month", "Perf_YTD",
            "NAVChg_1M", "NAVChg_YTD", "Covenant"]
REQUIRED = ["NAV_EoY", "NAV_Prev", "NAV_Cur", "Perf_EoY", "Perf_Month", "Perf_YTD", "NAVChg_1M", "NAVChg_YTD",
            "Covenant"]
NUM_FIELDS = ["NAV_EoY", "NAV_Prev", "NAV_Cur", "Perf_EoY", "Perf_Month", "Perf_YTD", "NAVChg_1M", "NAVChg_YTD"]
DATE_FIELDS = ["ValidityDate", "LastDDDate"]
TEXT_FIELDS = ["Rating", "Strategy", "Covenant"]
NA_TOKENS = {"N/A", "NA", "-", "N.A.", "#N/A", "N.A"}
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september",
          "october", "november", "december"]


# --------------------------------------------------------------- report helpers
class Report:
    def __init__(self):
        self.lines = {"FAIL": [], "WARN": [], "KNOWN": [], "INFO": []}
        self.files = []

    def add(self, level, msg):
        self.lines[level].append(msg)

    def status(self):
        if self.lines["FAIL"]:
            return "FAIL"
        return "WARN" if self.lines["WARN"] else "PASS"


def log(msg):
    print(f"[{dt.datetime.now():%H:%M:%S}] {msg}", flush=True)


def check_versions(skip):
    import numpy, pandas, pyarrow, openpyxl
    found = {"python": sys.version_info[:2], "pandas": pandas.__version__, "numpy": numpy.__version__,
             "pyarrow": pyarrow.__version__}
    log(f"versions: python {sys.version.split()[0]}, pandas {pandas.__version__}, numpy {numpy.__version__}, "
        f"pyarrow {pyarrow.__version__}, openpyxl {openpyxl.__version__}")
    bad = [k for k, v in PINNED.items() if found[k] != v]
    if bad and not skip:
        log("STOP: version mismatch on " + ", ".join(f"{k} (found {found[k]}, pinned {PINNED[k]})" for k in bad))
        sys.exit(2)


# --------------------------------------------------------------- text / value helpers
def clean_text(v):
    if v is None:
        return ""
    s = str(v).replace(" ", " ").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return re.sub(r" {2,}", " ", s).strip()


def norm(v):
    return clean_text(v).lower().replace(" ", "")


def month_no(tok):
    t = tok.lower().replace(".", "")
    if t == "sept":
        return 9
    for i, m in enumerate(MONTHS):
        if t == m or t == m[:3]:
            return i + 1
    return 0


def month_end(y, m):
    nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
    return nxt - dt.timedelta(days=1)


def parse_file_month(name):
    base = os.path.splitext(name)[0].replace("-", " ")
    toks = clean_text(base).split(" ")
    for i in range(len(toks) - 1):
        m = month_no(toks[i])
        if m and re.fullmatch(r"\d{4}", toks[i + 1]):
            return month_end(int(toks[i + 1]), m)
    return None


def find_title_month(ws, hdr, name_col):
    for r in range(1, hdr + 1):
        for c in range(1, name_col + 2):
            v = ws.cell(r, c).value
            if isinstance(v, (dt.datetime, dt.date)):
                return month_end(v.year, v.month)
            if isinstance(v, str):
                toks = clean_text(v.replace(",", " ")).split(" ")
                for i in range(len(toks) - 2):
                    m = month_no(toks[i])
                    if m and toks[i + 1].isdigit() and re.fullmatch(r"\d{4}", toks[i + 2]):
                        return month_end(int(toks[i + 2]), m)
    return None


def num_value(v, cnt):
    """Excel number -> float; text parsed with explicit rules; returns None when not usable."""
    if v is None:
        return None
    if isinstance(v, bool):
        cnt["bad"] += 1
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        t = clean_text(v).upper()
        if t == "":
            return None
        if t in NA_TOKENS:
            cnt["na"] += 1
            return None
        t = t.replace(",", "").replace("$", "").strip()
        neg = t.startswith("(") and t.endswith(")")
        if neg:
            t = t[1:-1].strip()
        pct = t.endswith("%")
        if pct:
            t = t[:-1].strip()
        if not re.fullmatch(r"[+-]?\d+(\.\d+)?", t):
            cnt["bad"] += 1
            return None
        d = float(t) * (-1 if neg else 1) / (100 if pct else 1)
        cnt["textnum"] += 1
        return d
    cnt["bad"] += 1
    return None


def date_value(v, cnt):
    if v is None:
        return None
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if isinstance(v, (int, float)) and 20000 < v < 80000:          # Excel serial left as a number
        return (dt.datetime(1899, 12, 30) + dt.timedelta(days=float(v))).date()
    if isinstance(v, str):
        t = clean_text(v)
        if t == "":
            return None
        if t.upper() in NA_TOKENS:
            cnt["na"] += 1
            return None
        m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", t)               # report uses US mm/dd/yyyy
        if m:
            try:
                return dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
            except ValueError:
                pass
    cnt["bad"] += 1
    return None


# --------------------------------------------------------------- header mapping
def map_header(ban, sub):
    if sub.startswith("totalauthori") or sub.startswith("%ofnav"):
        return "IGNORE"
    if sub == "rating":
        return "Rating"
    if sub.startswith("strateg"):
        return "Strategy"
    if sub.startswith("validity"):
        return "ValidityDate"
    if "diligence" in sub:
        return "LastDDDate"
    if sub.startswith("compliant") and "breach" in sub:
        return "Covenant"
    if ban.startswith("navchange"):
        if sub.startswith("1month"):
            return "NAVChg_1M"
        if sub == "ytd":
            return "NAVChg_YTD"
    elif ban.startswith("nav"):
        if sub.startswith("endofpreviousmonth") and "endofyear" in sub:
            return "NAV_PREV_EOY"
        if sub.startswith("endofyear"):
            return "NAV_EoY"
        if sub.startswith("endofprevious"):
            return "NAV_Prev"
        if sub.startswith("endofcurrent"):
            return "NAV_Cur"
    elif ban.startswith("performance"):
        if sub.startswith("endofyear"):
            return "Perf_EoY"
        if sub.startswith("monthly"):
            return "Perf_Month"
        if re.fullmatch(r"performan\w*ytd", sub) or sub == "ytd":
            return "Perf_YTD"
    return ""


def merged_top_left(ws):
    """cell (r, c) inside a merged range -> value of the range's top-left cell"""
    out = {}
    for rng in ws.merged_cells.ranges:
        tl = ws.cell(rng.min_row, rng.min_col).value
        for r in range(rng.min_row, rng.max_row + 1):
            for c in range(rng.min_col, rng.max_col + 1):
                out[(r, c)] = tl
    return out


def layout_code(col_of):
    opt = [k in col_of for k in ("Rating", "Strategy", "ValidityDate", "LastDDDate")]
    if col_of["NAV_Prev"] == col_of["NAV_EoY"]:
        return "H?1" if any(opt) else "H1"
    if not any(opt):
        return "H2"
    if all(opt):
        return "H3"
    if opt == [True, True, False, False]:
        return "H4"
    if opt == [True, True, False, True]:
        return "H5"
    return "H?"


# --------------------------------------------------------------- one file
def read_file(path, rep):
    """returns (month_end, rows, file_summary) ; rows = list of dicts ; month_end None on FAIL"""
    import openpyxl
    name = os.path.basename(path)
    summ = {"file": name, "month": "", "layout": "", "status": "PASS", "funds": 0, "cphs": 0, "na": 0,
            "bad": 0, "msgs": []}

    def fail(msg):
        summ["status"] = "SKIP"
        summ["msgs"].append(msg)
        rep.add("WARN", f"FILE SKIPPED {name}: {msg}")
        return None, [], summ

    def warn(msg):
        if summ["status"] == "PASS":
            summ["status"] = "WARN"
        summ["msgs"].append(msg)
        rep.add("WARN", f"{name}: {msg}")

    fmonth = parse_file_month(name)
    if fmonth is None:
        return fail("file name has no '<Month> <YYYY>'")
    summ["month"] = fmonth.isoformat()
    try:
        wb = openpyxl.load_workbook(path, data_only=True, read_only=False)
    except Exception as e:                                       # noqa: BLE001 - reported, file skipped
        return fail(f"cannot open ({type(e).__name__}: {e})")
    ws = wb["Main Report"] if "Main Report" in wb.sheetnames else wb.worksheets[0]
    if ws.title != "Main Report":
        warn(f"sheet 'Main Report' not found, used '{ws.title}'")

    max_r, max_c = ws.max_row, ws.max_column
    hdr = next((r for r in range(1, min(60, max_r) + 1) for c in range(1, max_c + 1)
                if norm(ws.cell(r, c).value).startswith("compliant/breach")), 0)
    if not hdr:
        return fail("header row not found (no 'Compliant/Breach')")
    last_col = max(c for c in range(1, max_c + 1) if ws.cell(hdr, c).value is not None)
    name_col = next((c for r in range(hdr, 0, -1) for c in range(1, last_col + 1)
                     if "counterparties" in norm(ws.cell(r, c).value)), 0)
    if not name_col:
        name_col = 2
        warn("'Counterparties' label not found, name column assumed B")
    tmonth = find_title_month(ws, hdr, name_col)
    if tmonth is None:
        warn("title date not found, file-name month used")
    elif tmonth != fmonth:
        return fail(f"title date {tmonth} <> file-name month {fmonth}")

    merged = merged_top_left(ws)
    col_of, cur = {}, ""
    for c in range(1, last_col + 1):
        sub = norm(ws.cell(hdr, c).value)
        if c == name_col or sub == "":
            cur = ""
            continue
        ban = norm(merged.get((hdr - 1, c), ws.cell(hdr - 1, c).value)) if hdr > 1 else ""
        if ban:
            cur = ban
        else:
            ban = cur
        fld = map_header(ban, sub)
        letter = ws.cell(hdr, c).column_letter
        if fld == "IGNORE":
            continue
        if fld == "":
            warn(f"unknown header col {letter} '{ban}|{sub}'")
        elif fld == "NAV_PREV_EOY":
            col_of.setdefault("NAV_Prev", c)
            col_of.setdefault("NAV_EoY", c)
        elif fld in col_of:
            warn(f"duplicate {fld} in col {letter}, kept the first")
        else:
            col_of[fld] = c
    missing = [f for f in REQUIRED if f not in col_of]
    if missing:
        return fail("required column missing: " + ", ".join(missing))
    layout = layout_code(col_of)
    if layout.startswith("H?"):
        warn(f"new layout ({layout})")

    cnt = {"na": 0, "bad": 0, "textnum": 0}
    rows, seen, cph, blanks, n_cph, n_dup = [], {}, "", 0, 0, 0
    for r in range(hdr + 1, max_r + 1):
        nm = clean_text(ws.cell(r, name_col).value)
        if nm == "":
            blanks += 1
            if blanks >= 15:
                break
            continue
        blanks = 0
        vals = {f: ws.cell(r, c).value for f, c in col_of.items()}
        if all(clean_text(v) == "" for v in vals.values()):
            cph, n_cph = nm, n_cph + 1                              # CPH header row
            continue
        if nm.lower().startswith("total"):
            warn(f"row {r} looks like a total ('{nm}')")
        rec = {"MonthEnd": fmonth, "SourceFile": name, "Layout": layout, "SourceRow": r, "CPH_Name": cph or None,
               "Fund_Name": nm}
        for f in col_of:
            v = vals[f]
            if f in NUM_FIELDS:
                rec[f] = num_value(v, cnt)
            elif f in DATE_FIELDS:
                rec[f] = date_value(v, cnt)
            else:
                rec[f] = clean_text(v) or None
        key = nm.upper()
        if key in seen:
            old = seen[key]
            if all(old.get(f) == rec.get(f) for f in col_of):
                if not old["CPH_Name"] and rec["CPH_Name"]:
                    old["CPH_Name"] = rec["CPH_Name"]
                n_dup += 1
                continue
            warn(f"'{nm}' twice with different values (rows {old['SourceRow']}, {r}), both kept")
        else:
            seen[key] = rec
        rows.append(rec)
    wb.close()

    if n_dup:
        rep.add("INFO", f"{name}: {n_dup} identical duplicate fund row(s) merged")
    no_cph = sum(1 for x in rows if not x["CPH_Name"])
    if no_cph and n_cph:
        warn(f"{no_cph} fund row(s) without a CPH header above them")
    if not n_cph:
        warn("no CPH header rows (flat list)")
        layout += "-flat"
        for x in rows:
            x["Layout"] = layout
    if cnt["bad"]:
        warn(f"{cnt['bad']} unreadable value(s) left null")
    if cnt["na"]:
        rep.add("INFO", f"{name}: {cnt['na']} N/A value(s) -> null")
    if cnt["textnum"]:
        rep.add("INFO", f"{name}: {cnt['textnum']} number(s) stored as text, parsed")
    if not rows:
        return fail("no fund rows read")
    summ.update(layout=layout, funds=len(rows), cphs=n_cph, na=cnt["na"], bad=cnt["bad"])
    return fmonth, rows, summ


# --------------------------------------------------------------- name map
def load_name_map(rep):
    import pandas as pd
    if not os.path.isfile(NAME_MAP):
        rep.add("WARN", f"name map not found ({NAME_MAP}): every fund unmapped")
        return {}
    df = pd.read_csv(NAME_MAP, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    cols = {c.strip().lower(): c for c in df.columns}
    if "fund_name" not in cols or "headofficesirisid" not in cols:
        rep.add("WARN", f"name map needs columns Fund_Name, HeadOfficeSirisId (found {list(df.columns)})")
        return {}
    out, bad, clash = {}, 0, 0
    for _, row in df.iterrows():
        nm = clean_text(row[cols["fund_name"]]).upper()
        raw = clean_text(row[cols["headofficesirisid"]])
        raw = raw[:-2] if raw.endswith(".0") else raw
        if nm == "":
            continue
        if not re.fullmatch(r"\d{1,10}", raw):
            bad += 1
            rep.add("WARN", f"name map: '{nm}' has an invalid id '{raw}' (ignored)")
            continue
        pid = raw.lstrip("0").rjust(10, "0")
        if nm in out and out[nm] != pid:
            clash += 1
            rep.add("WARN", f"name map: '{nm}' points to two ids ({out[nm]}, {pid}); first kept")
            continue
        out[nm] = pid
    rep.add("INFO", f"name map: {len(out)} names, {len(set(out.values()))} entities, {bad} invalid, {clash} clashes")
    return out


# --------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="read and report, publish nothing")
    ap.add_argument("--skip-version-check", action="store_true", help="sandbox only")
    args = ap.parse_args()
    t0 = time.time()
    log(f"HF NAV bake BUILD {BUILD} contract {CONTRACT_VERSION}{' DRY RUN' if args.dry_run else ''}")
    check_versions(args.skip_version_check)
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    rep = Report()
    for d, label in ((SRC_DIR, "SRC_DIR"), (WORK_DIR, "WORK_DIR")):
        if not os.path.isdir(d):
            log(f"STOP: {label} not found: {d}")
            sys.exit(2)
    if os.path.abspath(WORK_DIR).startswith(os.path.abspath(GOLD_DIR)):
        log("STOP: WORK_DIR is inside GOLD_DIR (Folder.Files is recursive)")
        sys.exit(2)

    files = sorted(f for f in glob.glob(os.path.join(SRC_DIR, FILE_GLOB))
                   if not os.path.basename(f).startswith("~$"))
    log(f"files found: {len(files)}")
    by_month, all_rows = {}, {}
    for i, path in enumerate(files, 1):
        t = time.time()
        m, rows, summ = read_file(path, rep)
        rep.files.append(summ)
        log(f"{i}/{len(files)} {summ['file']}  {summ['status']}  {summ['layout']}  funds {summ['funds']}  "
            f"{time.time() - t:.1f}s")
        if m is None:
            continue
        by_month.setdefault(m, []).append(summ["file"])
        all_rows[summ["file"]] = rows
    for m, names in by_month.items():
        if len(names) > 1:
            rep.add("WARN", f"FILE SKIPPED month {m} in {len(names)} files: {', '.join(names)} (none loaded)")
            for n in names:
                all_rows.pop(n, None)
    rows = [r for f in sorted(all_rows) for r in all_rows[f]]
    if not rows:
        rep.add("FAIL", "no readable file")

    mpath = os.path.join(WORK_DIR, "hfnav_manifest.json")
    if os.path.isfile(mpath):
        try:
            last = set(json.load(open(mpath, encoding="utf-8")).get("months", []))
            now = {str(r["MonthEnd"]) for r in rows}
            lost = sorted(last - now)
            if lost:
                rep.add("FAIL", "months in the last published gold but missing now (fix or remove the file on purpose, "
                                "then delete hfnav_manifest.json): " + ", ".join(lost))
        except (ValueError, OSError) as e:
            rep.add("WARN", f"manifest unreadable ({e}), month-loss check skipped")
    nmap = load_name_map(rep)
    df = pd.DataFrame(rows)
    if len(df):
        for c in OUT_COLS:
            if c not in df.columns:
                df[c] = None
        key = df["Fund_Name"].str.upper()
        df["HeadOfficeSirisId"] = key.map(nmap)
        df["MapStatus"] = np.where(df["HeadOfficeSirisId"].notna(), "mapped", "unmapped")
        un = df[df["MapStatus"] == "unmapped"].groupby("Fund_Name")["MonthEnd"].agg(["min", "max", "count"])
        for nm, r in un.iterrows():
            rep.add("WARN", f"unmapped fund '{nm}' ({r['count']} month(s), {r['min']} -> {r['max']})")
        # latest non-blank strategy per fund (entity when mapped, else name)
        df["_fk"] = df["HeadOfficeSirisId"].fillna("N:" + key)
        st = df[df["Strategy"].notna()].sort_values("MonthEnd").groupby("_fk")["Strategy"].last()
        df["StrategyLatest"] = df["_fk"].map(st)
        # one entity per month must not come from two fund names
        dup = df[df["HeadOfficeSirisId"].notna()].groupby(["MonthEnd", "HeadOfficeSirisId"])["Fund_Name"].nunique()
        for (m, pid), n in dup[dup > 1].items():
            rep.add("WARN", f"{m}: entity {pid} carries {n} fund names in one report")
        # plausibility (INFO)
        exp = df["NAV_Prev"] * (1 + df["NAVChg_1M"])
        off = (exp - df["NAV_Cur"]).abs() > 0.02 * df["NAV_Cur"].abs().clip(lower=1)
        if off.sum():
            rep.add("INFO", f"plausibility: {int(off.sum())} row(s) where NAV_Prev x (1+NAVChg_1M) differs from "
                            f"NAV_Cur by > 2%")
        s = df.sort_values("MonthEnd")
        prev_cur = s.groupby("_fk")["NAV_Cur"].shift(1)
        prev_m = s.groupby("_fk")["MonthEnd"].shift(1)
        consec = prev_m.notna() & ((pd.to_datetime(s["MonthEnd"]) - pd.to_datetime(prev_m)).dt.days.between(27, 32))
        brk = consec & ((s["NAV_Prev"] - prev_cur).abs() > 0.02 * prev_cur.abs().clip(lower=1))
        if brk.sum():
            rep.add("INFO", f"plausibility: {int(brk.sum())} row(s) where NAV_Prev differs from last month's "
                            f"NAV_Cur by > 2% (restatement or rename)")
        big = df["Perf_Month"].abs() > 0.5
        if big.sum():
            rep.add("INFO", f"plausibility: {int(big.sum())} row(s) with |monthly performance| > 50%")
        df = df[OUT_COLS].sort_values(["MonthEnd", "SourceRow"]).reset_index(drop=True)

    status = rep.status()
    out_path = os.path.join(GOLD_DIR, GOLD_FILE)
    published = False
    if status != "FAIL" and not args.dry_run and len(df):
        schema = pa.schema([
            ("MonthEnd", pa.date32()), ("SourceFile", pa.string()), ("Layout", pa.string()),
            ("SourceRow", pa.int32()), ("CPH_Name", pa.string()), ("Fund_Name", pa.string()),
            ("HeadOfficeSirisId", pa.string()), ("MapStatus", pa.string()), ("Rating", pa.string()),
            ("Strategy", pa.string()), ("StrategyLatest", pa.string()),
            ("ValidityDate", pa.date32()), ("LastDDDate", pa.date32())]
            + [(c, pa.float64()) for c in NUM_FIELDS] + [("Covenant", pa.string())])
        arrays = []
        for f in schema:
            vals = df[f.name].tolist()
            vals = [None if (v is None or (isinstance(v, float) and np.isnan(v))) else v for v in vals]
            arrays.append(pa.array(vals, type=f.type))
        table = pa.Table.from_arrays(arrays, schema=schema)
        os.makedirs(GOLD_DIR, exist_ok=True)
        tmp = out_path + ".tmp"
        pq.write_table(table, tmp, compression="snappy")
        back = pq.read_table(tmp)
        if back.num_rows != len(df) or back.schema != schema:
            rep.add("FAIL", "post-write check failed (rows or schema), nothing published")
            os.remove(tmp)
        else:
            for k in range(5):
                try:
                    os.replace(tmp, out_path)
                    published = True
                    break
                except PermissionError:
                    log(f"target locked (Power BI open?), retry {k + 1}/5")
                    time.sleep(3)
            if not published:
                rep.add("FAIL", f"could not replace {out_path} (locked), new file left as {tmp}")
    status = rep.status()

    # ---- report + manifest
    os.makedirs(os.path.join(WORK_DIR, "reports"), exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    rpath = os.path.join(WORK_DIR, "reports", f"hfnav_{'dry_' if args.dry_run else ''}{stamp}.txt")
    months = sorted(df["MonthEnd"].unique()) if len(df) else []
    with open(rpath, "w", encoding="utf-8") as fh:
        fh.write(f"HF NAV bake  BUILD {BUILD}  contract {CONTRACT_VERSION}  {stamp}\n")
        fh.write(f"STATUS {status}{'  (dry run, nothing published)' if args.dry_run else ''}\n\n")
        for lvl in ("FAIL", "WARN", "KNOWN", "INFO"):
            fh.write(f"== {lvl} ({len(rep.lines[lvl])})\n" + "".join(f"  {x}\n" for x in rep.lines[lvl]) + "\n")
        fh.write("== Files\n")
        for s in rep.files:
            fh.write(f"  {s['file']:<44} {s['month']:<11} {s['layout']:<9} {s['status']:<5} funds {s['funds']:>3}  "
                     f"cph {s['cphs']:>3}  na {s['na']:>2}  bad {s['bad']:>2}\n")
        fh.write(f"\n== Output\n  rows {len(df)}  months {len(months)}"
                 f"{(' ' + str(months[0]) + ' -> ' + str(months[-1])) if months else ''}\n")
        if len(df):
            fh.write(f"  mapped rows {int((df['MapStatus'] == 'mapped').sum())} / {len(df)}  "
                     f"distinct funds {df['Fund_Name'].nunique()}  entities {df['HeadOfficeSirisId'].nunique()}\n")
        fh.write(f"  published {published}  {out_path if published else ''}\n")
        fh.write(f"  elapsed {time.time() - t0:.1f}s\n")
    if published:
        sha = hashlib.sha256(open(out_path, "rb").read()).hexdigest()
        with open(os.path.join(WORK_DIR, "hfnav_manifest.json"), "w", encoding="utf-8") as fh:
            json.dump({"build": BUILD, "contract": CONTRACT_VERSION, "written": stamp, "rows": len(df),
                       "months": [str(m) for m in months], "sha256": sha,
                       "files": [{k: s[k] for k in ("file", "month", "layout", "status", "funds")} for s in rep.files]},
                      fh, indent=1)
    log(f"STATUS {status}  rows {len(df)}  published {published}  report {rpath}  ({time.time() - t0:.1f}s)")
    sys.exit({"PASS": 0, "WARN": 1, "FAIL": 2}[status])


if __name__ == "__main__":
    main()
