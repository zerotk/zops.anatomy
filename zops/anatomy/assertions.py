

def assert_file_contents(filename, expected):
    from zops.anatomy.text import dedent
    import os

    expected = dedent(expected)
    assert os.path.isfile(filename)
    obtained = open(filename, 'r').read()
    assert obtained == expected
