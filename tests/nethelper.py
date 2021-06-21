import pytest

from .context import calc_subnet_mask


class TestCalcSubnetMask:
    """Tests the calc_subnet_mask function"""

    def test_zero(self):
        assert calc_subnet_mask(0) == "0.0.0.0"

    def test_32(self):
        assert calc_subnet_mask(32) == "255.255.255.255"

    def test_16(self):
        assert calc_subnet_mask(16) == "255.255.0.0"

    def test_negative(self):
        with pytest.raises(ValueError, match="CIDR values are between 0 and 32 inclusive"):
            calc_subnet_mask(-1)

    def test_too_high(self):
        with pytest.raises(ValueError, match="CIDR values are between 0 and 32 inclusive"):
            calc_subnet_mask(33)
