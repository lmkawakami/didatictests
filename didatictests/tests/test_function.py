#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple example of a test file using a function.
NOTE: All test file names must have one of the two forms.
- `test_<XYY>.py`
- '<XYZ>_test.py'

Docs: https://docs.pytest.org/en/latest/
      https://docs.pytest.org/en/latest/goodpractices.html#conventions-for-python-test-discovery
"""

import pytest
from didatictests import Example
from didatictests import Didatic_test


# If you only have a single condition you need to test, a single test is _okay_
# but parametrized tests are encouraged
def test_value_change():
    start_val = 5
    new_val = 20

    example = Example(start_val)
    example.update_value(new_val)
    assert example.get_value() == new_val and example.get_previous_value() == start_val


# Generally, you should parametrize your tests, but you should include exception tests
# like below!
@pytest.mark.parametrize(
    "start_val, next_val, expected_values",
    [
        # (start_val, next_val, expected_values)
        (5, 20, (20, 5)),
        (10, 40, (40, 10)),
        (1, 2, (2, 1)),
    ],
)
def test_parameterized_value_change(start_val, next_val, expected_values):
    example = Example(start_val)
    example.update_value(next_val)
    assert expected_values == example.values


# The best practice would be to parametrize your tests, and include tests for any
# exceptions that would occur
@pytest.mark.parametrize(
    "start_val, next_val, expected_values",
    [
        # (start_val, next_val, expected_values)
        (5, 20, (20, 5)),
        (10, 40, (40, 10)),
        (1, 2, (2, 1)),
        pytest.param(
            "hello",
            None,
            None,
            marks=pytest.mark.raises(
                exception=ValueError
            ),  # Init value isn't an integer
        ),
        pytest.param(
            1,
            "hello",
            None,
            marks=pytest.mark.raises(
                exception=ValueError
            ),  # Update value isn't an integer
        ),
    ],
)
def test_parameterized_value_change_with_exceptions(
    start_val, next_val, expected_values
):
    example = Example(start_val)
    example.update_value(next_val)
    assert expected_values == example.values


# New tests
def test_generate_test():
    def func(x, y, z):
        print(x, y, z)
        return x + y + z

    test_code = Didatic_test.generate_test(
        func, Didatic_test.parse_args(1, 2, z=3), "teste-A", True, True, True, True
    )
    assert (
        test_code
        == "Didatic_test(func, Didatic_test.parse_args(1, 2, z=3), \
'teste-A', [], 6, '1 2 3\n', True, True, True)"
    )


def test_parse_args():
    args = Didatic_test.parse_args(
        0,
        1,
        2,
        "a",
        True,
        None,
        (0, 1, 0),
        ["1", False],
        {1: 5},
        a=2,
        b="a",
        c=True,
        d=None,
        e=(0, 1, 0),
        f=["1", False],
        g={1: 5},
    )
    assert args == {
        "pos_inputs": (0, 1, 2, "a", True, None, (0, 1, 0), ["1", False], {1: 5}),
        "key_inputs": {
            "a": 2,
            "b": "a",
            "c": True,
            "d": None,
            "e": (0, 1, 0),
            "f": ["1", False],
            "g": {1: 5},
        },
    }


def test_redefine():
    def func(x, y, z):
        w = int(input("Digite o valor de w: "))
        print(w, x, y, z)
        return w + x + y + z

    redefined_func = Didatic_test.redefine(func, ["10"], True)
    assert redefined_func(1, 2, 3) == 16


def test_run_tests():
    def func(x, y, z):
        print(x, y, z)
        return x + y + z

    tests = [
        Didatic_test(
            func,
            Didatic_test.parse_args(1, 2, z=3),
            "teste-A",
            [],
            6,
            "1 2 3\n",
            True,
            True,
            True,
        )
    ]
    assert Didatic_test.run_tests(tests) == [
        {
            "output_is_correct": True,
            "print_is_correct": True,
            "test_failed": False,
            "test_done": True,
        }
    ]


def test_intercepted_fn():
    def func(x, y, z):
        print(x, y, z)
        return x + y + z

    interceptions = {}
    func2 = Didatic_test.intercepted_fn(
        func, interceptions, verbose=False, input_identifier="", print_identifier=""
    )
    func2(1, 2, 3)
    interceptions
    assert interceptions == {
        "prints": ["1 2 3\n"],
        "inputs": [],
        "args": (1, 2, 3),
        "kwargs": {},
        "output": 6,
    }
