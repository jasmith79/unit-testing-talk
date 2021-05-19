import math
from unittest import mock
import pytest

# Note we don't even care about some_fun itself anymore
from context import better_is_valid as is_valid, not_quite_some_fun


class TestIsValid:
    def test_non_number(self):
        assert not is_valid(None)
        assert not is_valid([])
        assert not is_valid({})
        assert not is_valid("foo")

    def test_infinity(self):
        assert not is_valid(math.inf)

    def test_zero(self):
        assert not is_valid(0)

    def test_happy(self):
        assert is_valid(10)

# times_five is so trivial we won't even bother


class TestNQSF:
    def test_valid(self):
        validator = mock.MagicMock(return_value=True)
        xform = mock.MagicMock(return_value=3)
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        result = not_quite_some_fun(logger, validator, xform, 3)
        assert result == 3
        logger.log.assert_not_called()
        xform.assert_called_with(3)

    def test_invalid(self):
        validator = mock.MagicMock(return_value=False)
        xform = mock.MagicMock()
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        result = not_quite_some_fun(logger, validator, xform, 3)
        logger.log.assert_called_with("Invalid input")
        xform.assert_not_called()
        assert result is None
