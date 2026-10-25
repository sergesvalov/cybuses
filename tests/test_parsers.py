import pytest
from parsers.base import BaseParser
from parsers.intercity import IntercityParser
from bs4 import BeautifulSoup


def test_base_parser_normalize_time():
    parser = BaseParser()
    assert parser.normalize_time("08.30") == "08:30"
    assert parser.normalize_time("8:30") == "08:30"
    assert parser.normalize_time("14:45") == "14:45"
    assert parser.normalize_time("  09:15  ") == "09:15"


def test_base_parser_extract_times():
    parser = BaseParser()
    sample_text = "Buses depart at 06:30*, 08:00, and 17:45** daily."
    times = parser.extract_times(sample_text)
    assert len(times) == 3
    assert times[0] == ("06:30", "*")
    assert times[1] == ("08:00", "")
    assert times[2] == ("17:45", "**")


def test_intercity_extract_footnotes():
    parser = IntercityParser()
    html = """
    <div>
        <p>* Runs only during school term</p>
        <p>** Via Polis Chrysochous</p>
        <p>Regular text</p>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    notes = parser.extract_footnotes(soup)
    assert "*" in notes
    assert "school term" in notes["*"]
    assert "**" in notes
    assert "Polis Chrysochous" in notes["**"]
