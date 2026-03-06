"""
Validation Module
Provides validation utilities for reports and data structures.
"""

from validation.report_validator import validate_report, ReportValidationError

__all__ = ['validate_report', 'ReportValidationError']
