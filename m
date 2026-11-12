let
    FolderPath = "<GOLD_DIR of hfnav_run.py>",
    FileName = "hfnav_gold.parquet",
    Contract = {"MonthEnd", "Region", "SourceFile", "Layout", "SourceRow", "CPH_Name", "Fund_Name", "HeadOfficeSirisId",
                "MapStatus", "Rating", "Strategy", "StrategyLatest", "ValidityDate", "LastDDDate",
                "NAV_EoY", "NAV_Prev", "NAV_Cur", "Perf_EoY", "Perf_Month", "Perf_YTD", "NAVChg_1M", "NAVChg_YTD",
                "Covenant", "CovenantNote"},
    Source = Folder.Files(FolderPath),
    Files = Table.SelectRows(Source, each Text.Lower([Name]) = FileName),
    Checked = if Table.RowCount(Files) = 1 then Files
        else error Error.Record("Gold contract violation",
            "G1 expected exactly one " & FileName & " under " & FolderPath & ", found " & Text.From(Table.RowCount(Files))),
    Data = Parquet.Document(Checked{0}[Content]),
    Cols = Table.ColumnNames(Data),
    Missing = List.Difference(Contract, Cols),
    Extra = List.Difference(Cols, Contract),
    Guarded = if List.IsEmpty(Missing) and List.IsEmpty(Extra) then Data
        else error Error.Record("Gold contract violation",
            "G3 " & FileName & ": missing {" & Text.Combine(Missing, ", ") & "} extra {" & Text.Combine(Extra, ", ") & "}"),
    AnyCols = Table.SelectRows(Table.Schema(Guarded), each [Kind] = "any")[Name],
    Typed = if List.IsEmpty(AnyCols) then Guarded
        else error Error.Record("Gold contract violation", "G4 column of type any: " & Text.Combine(AnyCols, ", ")),
    BadRows = Table.RowCount(Table.SelectRows(Typed, each [MonthEnd] = null or [Fund_Name] = null or [Fund_Name] = "")),
    Result = if BadRows = 0 then Typed
        else error Error.Record("Gold contract violation", "G5 " & Text.From(BadRows) & " row(s) without MonthEnd or Fund_Name")
in
    Result
