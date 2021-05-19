import os
import sys

# We need to insert at the beginning to override the system path
# lookup. This will enable the tests to import the local packages.
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import math
from unittest import mock
import pytest
from some_module import some_module


class TestSomeFun:
    def test_zero(self, monkeypatch):
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        is_valid = mock.MagicMock(return_value=False)
        monkeypatch.setattr(some_module, "logger", logger)
        monkeypatch.setattr(some_module, "is_valid", is_valid)
        result =  some_module.some_fun(0)
        is_valid.assert_called_with(0)
        logger.log.assert_called_with("Invalid input to x")
        assert result is None

    def test_negative(self, monkeypatch):
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        is_valid = mock.MagicMock(return_value=False)
        monkeypatch.setattr(some_module, "logger", logger)
        monkeypatch.setattr(some_module, "is_valid", is_valid)
        result =  some_module.some_fun(-3)
        is_valid.assert_called_with(-3)
        logger.log.assert_called_with("Invalid input to x")
        assert result is None

    def test_infinity(self, monkeypatch):
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        is_valid = mock.MagicMock(return_value=False)
        monkeypatch.setattr(some_module, "logger", logger)
        monkeypatch.setattr(some_module, "is_valid", is_valid)
        result =  some_module.some_fun(math.inf)
        is_valid.assert_called_with(math.inf)
        logger.log.assert_called_with("Invalid input to x")
        assert result is None

    def test_positive_int(self, monkeypatch):
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        is_valid = mock.MagicMock(return_value=True)
        monkeypatch.setattr(some_module, "logger", logger)
        monkeypatch.setattr(some_module, "is_valid", is_valid)
        result =  some_module.some_fun(5)
        is_valid.assert_called_with(5)
        logger.log.assert_not_called()
        assert result == 25
