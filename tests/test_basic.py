from envertor.core import detect_placeholder

def test_placeholder_detection():
    assert detect_placeholder("123") == "0"
    assert detect_placeholder("3.14") == "0.0"
    assert detect_placeholder("true") == "false"
    assert detect_placeholder("hello") == "''"

