from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .extractor import extract
from .transformer import transform
from .loader import load_to_db


@dataclass
class ETLServiceResult:
    records_processed: int
    records_loaded: int
    source: str


def run_full_etl(
    *,
    excel_bytes: bytes | None,
    csv_bytes: bytes | None,
    source_filename: str = '',
) -> tuple[pd.DataFrame, ETLServiceResult]:
    extraction = extract(excel_bytes=excel_bytes, csv_bytes=csv_bytes, source_filename=source_filename)
    df = transform(extraction.df)
    loaded = load_to_db(df)

    result = ETLServiceResult(
        records_processed=extraction.records_processed,
        records_loaded=loaded,
        source=extraction.source,
    )
    return df, result

