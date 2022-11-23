"""Module with statistical tools for analyzing spam."""

from collections import Counter


def get_count(emails):
    """Count the number of emails."""
    counter = Counter(emails)
    return counter
