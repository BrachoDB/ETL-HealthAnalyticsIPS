from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class ExtractionResult:
    df: pd.DataFrame
    source: str
    records_processed: int


def extract_csv(csv_bytes: bytes, *, source_filename: str = 'csv') -> ExtractionResult:
    csv_file = io.BytesIO(csv_bytes)
    df = pd.read_csv(csv_file)
    return ExtractionResult(df=df, source=source_filename, records_processed=int(len(df)))


def extract_excel(excel_bytes: bytes, *, source_filename: str = 'excel') -> ExtractionResult:
    excel_file = io.BytesIO(excel_bytes)
    df = pd.read_excel(excel_file)
    return ExtractionResult(df=df, source=source_filename, records_processed=int(len(df)))


def extract(
    *,
    excel_bytes: bytes | None,
    csv_bytes: bytes | None,
    source_filename: str = '',
) -> ExtractionResult:
    if excel_bytes:
        return extract_excel(excel_bytes, source_filename=source_filename or 'excel')
    if csv_bytes:
        return extract_csv(csv_bytes, source_filename=source_filename or 'csv')
    raise ValueError('No input file provided')

