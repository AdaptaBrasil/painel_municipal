"""
Module providing numeric formatting and validation utilities.

This module defines the `NumberFormattingProcessing` class, which offers methods
for decimal manipulation, number validation (integer, nan), parsing, and locale-aware
formatting useful for handling data spreadsheet numeric values.
"""

from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd
from babel.numbers import format_decimal, parse_number
import babel.numbers as babel_numbers


class NumberFormattingProcessing:
    """
    Utility class for numeric value processing and formatting.

    Provides static methods for safe decimal conversion, truncation, decimal place validation,
    NaN checks, and formatting numbers according to locale conventions (e.g., Brazilian Portuguese).
    """
    babel_numbers: Any = babel_numbers

    def __init__(self) -> None:
        """Initialize the NumberFormattingProcessing class."""
        pass
    
    @staticmethod
    def is_integer(d: Decimal) -> bool:
        """Check if a Decimal value is an integer (no fractional part)."""
        return d.is_finite() and d == d.to_integral_value()

    @staticmethod
    def is_float(d: Decimal) -> bool:
        """Check if a Decimal value has a fractional part (is a float)."""
        return d.is_finite() and d != d.to_integral_value()
    
    @staticmethod
    def is_nan(d: Decimal) -> bool:
        """Check if a Decimal value is NaN (Not a Number)."""
        return d.is_nan()
    
    @staticmethod
    def parse_to_decimal(value: Any) -> Decimal:
        """
        Safely parse a value to a Decimal object.

        Handles comma as decimal separator and returns 0 for invalid inputs.

        Args:
            value (Any): The value to parse.
        Returns:
            Decimal: The parsed Decimal value, or 0 if invalid.
        """
        if pd.isna(value):
            return Decimal("0")

        s_val = str(value).replace(",", ".")
        try:
            return Decimal(s_val)
        except (ValueError, InvalidOperation, Exception):
            return Decimal("0")

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
                decimal_part = decimal_part + "0" * precision
                truncated_val = f"{integer_part}.{decimal_part[:precision]}"
            else:
                truncated_val = s_val
                
            return Decimal(truncated_val)
        except (ValueError, InvalidOperation, Exception):
            return Decimal("0")

    @staticmethod
    def format_number_brazilian(n: float | int, locale: str = "pt_BR") -> str:
        """
        Format a number using Brazilian locale conventions.

        Args:
            n (float | int): Number to format.
            locale (str, optional): Locale string. Default is "pt_BR".

        Returns:
            str: Formatted number string (e.g., '1.234,56').
        """
        # If it's a strictly integer value (like population), format without decimal places
        if isinstance(n, int):
            return format_decimal(number=n, locale=locale)
        
        # For floats (like area, risks), force the format with exactly 2 decimal places
        return format_decimal(number=n, format='#,##0.00', locale=locale)
    
    @staticmethod
    def format_number_brazilian_ignore_two_zeros(n: float | int, locale: str = "pt_BR") -> str:
        """
        Format a number using Brazilian locale conventions.

        Args:
            n (float | int): Number to format.
            locale (str, optional): Locale string. Default is "pt_BR".

        Returns:
            str: Formatted number string (e.g., '1.234,56').
        """
        # If it's a strictly integer value (like population), format without decimal places
        if NumberFormattingProcessing.is_integer(Decimal(n)):
            return format_decimal(number=n, locale=locale)
        
        # For floats (like area, risks), force the format with exactly 2 decimal places
        return format_decimal(number=n, format='#,##0.00', locale=locale)