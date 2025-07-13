import pytest
from treeline.utils import format_size

def test_zero_bytes():
    assert format_size(0) == "0B"

def test_bytes_under_1024():
    assert format_size(1) == "1B"
    assert format_size(42) == "42B"
    assert format_size(512) == "512B"
    assert format_size(1023) == "1023B"

def test_kilobytes():
    assert format_size(1024) == "1.0KB"
    assert format_size(1536) == "1.5KB"
    assert format_size(2048) == "2.0KB"
    assert format_size(1048575) == "1024.0KB"

def test_megabytes():
    assert format_size(1048576) == "1.0MB"
    assert format_size(1572864) == "1.5MB"
    assert format_size(5242880) == "5.0MB"

def test_gigabytes():
    assert format_size(1073741824) == "1.0GB"
    assert format_size(2147483648) == "2.0GB"
    assert format_size(1610612736) == "1.5GB"

def test_terabytes():
    assert format_size(1099511627776) == "1.0TB"
    assert format_size(2199023255552) == "2.0TB"

def test_large_terabytes():
    huge_size = 1024 * 1024 * 1024 * 1024 * 1024
    result = format_size(huge_size)
    assert result.endswith("TB")
    assert "1024.0TB" == result

def test_fractional_values():
    assert format_size(1500) == "1.5KB"
    assert format_size(2560) == "2.5KB"
    assert format_size(7340032) == "7.0MB"

def test_edge_cases():
    assert format_size(1024) == "1.0KB"
    assert format_size(1048576) == "1.0MB"
    assert format_size(1073741824) == "1.0GB"
    
    assert format_size(1023) == "1023B"
    assert format_size(1048575) == "1024.0KB"

def test_decimal_precision():
    assert format_size(1126) == "1.1KB" 
    assert format_size(1331) == "1.3KB"
    assert format_size(1946157) == "1.9MB"

def test_integer_display_for_bytes():
    assert format_size(100) == "100B"
    assert format_size(999) == "999B"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])