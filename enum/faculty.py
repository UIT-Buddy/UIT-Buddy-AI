"""Faculty and Major mapping for UIT."""

from __future__ import annotations
import re

FACULTY_MAJOR_MAP = {
    "CNPM": ["KTPM", "TTDPT"],
    "HTTT": ["HTTT", "TMDT"],
    "KHMT": ["KHMT", "TTNT"],
    "KTMT": ["TKVM", "KTMT"],
    "MMTTT": ["ATTT", "MMTTTT"],
    "KTTT": ["CNTT", "KHDL"],
}

PREFIX_TO_MAJOR = {
    "SE": "KTPM",
    "IS": "HTTT",
    "CS": "KHMT",
    "NT": "MMTTT",
    "IE": "KTTT",
    "DS": "KTTT",
}

# Reverse map for quick major-to-faculty lookup
MAJOR_TO_FACULTY = {
    major: faculty for faculty, majors in FACULTY_MAJOR_MAP.items() for major in majors
}


def extract_major_code(class_name: str) -> str | None:
    """
    Extract major code from a class name like 'KTPM2024.3'.
    Returns 'KTPM' or None if no match.
    """
    if not class_name:
        return None
    # Matches letters at the start of the string
    match = re.match(r"^([A-Z]+)", str(class_name).upper())
    if match:
        return match.group(1)
    return None


def get_faculty_by_major(major_code: str) -> str | None:
    """Return the faculty code for a given major code."""
    return MAJOR_TO_FACULTY.get(str(major_code).upper())


def get_major_from_subject(subject_code: str) -> str | None:
    """
    Determine major code from a subject code prefix (e.g., 'SE330' -> 'KTPM').
    """
    if not subject_code:
        return None
    match = re.match(r"^([A-Z]+)", str(subject_code).upper())
    if match:
        prefix = match.group(1)
        return PREFIX_TO_MAJOR.get(prefix)
    return None
