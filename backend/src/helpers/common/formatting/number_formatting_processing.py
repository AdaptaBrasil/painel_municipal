"""
Module providing numeric formatting and validation utilities.

This module defines the `NumberFormattingProcessing` class, which offers methods
for decimal manipulation, number validation (integer, nan), parsing, and locale-aware
formatting useful for handling data spreadsheet numeric values.
"""

from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd
from babel.numbers import format_decimal


class NumberFormattingProcessing:
    """
    Utility class for numeric value processing and formatting.

    Provides static methods for safe decimal conversion, truncation, decimal place validation,
    NaN checks, and formatting numbers according to locale conventions (e.g., Brazilian Portuguese).
    """

    def __init__(self) -> None:
        """Initialize the NumberFormattingProcessing class."""
        pass

    @staticmethod
    def to_decimal_truncated(value_number: Any, value_to_ignore: Any, precision: int) -> Decimal:
        """
        Convert a value to a truncated Decimal object.

        Truncates the decimal part of the number to the specified precision without rounding.
        Handles comma as decimal separator. Returns 0 if value is ignored or invalid.

        Args:
            value_number (Any): The number to convert.
            value_to_ignore (Any): A specific value (e.g., 'Unavailable') to treat as 0.
            precision (int): The number of decimal places to keep.

        Returns:
            Decimal: The truncated Decimal value, or 0 if invalid/ignored.
        """
        if pd.isna(value_number) or value_number == value_to_ignore:
            return Decimal("0")

        s_val = str(value_number).replace(",", ".")
        try:
            if "." in s_val:
                integer_part, decimal_part = s_val.split(".")
                truncated_val = f"{integer_part}.{decimal_part[:precision]}"
            else:
                truncated_val = s_val
            return Decimal(truncated_val)
        except (ValueError, InvalidOperation, Exception):
            return Decimal("0")

    @staticmethod
    def format_number_brazilian(n: float, locale: str = "pt_BR") -> str:
        """
        Format a number using Brazilian locale conventions.

        Args:
            n (float): Number to format.
            locale (str, optional): Locale string. Default is "pt_BR".

        Returns:
            str: Formatted number string (e.g., '1.234,56').
        """
        return format_decimal(number=n, locale=locale)