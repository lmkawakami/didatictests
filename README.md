# didatictests

[![PyPI version shields.io](https://img.shields.io/pypi/status/didatictests.svg)](https://pypi.org/project/didatictests/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/didatictests.svg)](https://pypi.org/project/didatictests/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/didatictests.svg)](https://pypi.org/project/didatictests/)
[![Commits](https://img.shields.io/github/commits-since/lmkawakami/didatictests/v0.0.1.svg)](https://github.com/lmkawakami/didatictests/commits/main)
[![GitHub latest commit](https://img.shields.io/github/last-commit/lmkawakami/didatictests/main)](https://github.com/lmkawakami/didatictests/commits/main)
[![License](https://img.shields.io/github/license/lmkawakami/didatictests.svg)](https://github.com/lmkawakami/didatictests/blob/main/LICENSE)

[![Build Status](https://github.com/lmkawakami/didatictests/workflows/Build%20Main/badge.svg)](https://github.com/lmkawakami/didatictests/actions)
[![Documentation](https://github.com/lmkawakami/didatictests/workflows/Documentation/badge.svg)](https://lmkawakami.github.io/didatictests/)
[![Code Coverage](https://codecov.io/gh/lmkawakami/didatictests/branch/main/graph/badge.svg)](https://codecov.io/gh/lmkawakami/didatictests)

---

## Features

-   Run functions with preconfigured simulated keyboard inputs

-   Build simple tests to validate functions prints and outputs with configurable args, kwargs and simulated user inputs

## Installation

**Stable Release:** `pip install didatictests`<br>
**Development Head:** `pip install git+https://github.com/lmkawakami/didatictests.git`

## Documentation

[Notebook showcase em português](notebooks/exemplos.ipynb)

[Notebook de funcionalidades extras em português](notebooks/brindes.ipynb)

For full package documentation please visit [lmkawakami.github.io/didatictests](https://lmkawakami.github.io/didatictests).
## Quick Start

```python
from didatictests import Didatic_test
```

Demo function: `the_function(arg)`:
  - receives 1 argument `arg`
  - receives 1 user input `inp`
  - calculates `total = arg + int(inp)`
  - prints `total`
  - return `total`

```python
def the_function(arg):
    inp = input("One number, please: ")
    total = arg + int(inp)
    print(total)
    return total
```

Create and run some tests:

---
### Test-1

```python
test1 = Didatic_test(
    fn = the_function,
    args = Dt.parse_args(40),
    keyboard_inputs = ('2'),
    test_name = 'This one shall pass!',
    expected_output = 42,
    expected_prints = '42\n',
    run_prints_test = True,
    run_output_test = True,
    verbose=True
)

test1.run()
```
- print:
```
Case: This one shall pass!
[I]: One number, please:  2
[P]: 42

outputs: ✔️  prints: ✔️
---------------------------------------------------
```
- return:
```python
{'output_is_correct': True, 'print_is_correct': True, 'test_failed': False, 'test_done': True}
```

---
### Test-2

```python
test2 = Didatic_test(
    fn = the_function,
    args = Dt.parse_args(40),
    keyboard_inputs = ('2'),
    test_name = 'You Shall Not Pass!!!',
    expected_output = 42,
    expected_prints = '13\n',
    run_prints_test = True,
    run_output_test = True,
    verbose=True
)

test2.run()
```
- print:
```
Case: You Shall Not Pass!!!
[I]: One number, please:  2
[P]: 42

outputs: ✔️  prints: ❌
   ➖ Function args:      (40,) {}
   ➖ Keyboard inputs:    ('2',)
   ✔️ Function outputs:   42
   ➖ Expected output:    42
   ❌ fn internal prints: 42
   ➖ Expected prints:    13
---------------------------------------------------
```
- return:
```python
{'output_is_correct': True, 'print_is_correct': False, 'test_failed': False, 'test_done': True}
```

---
### Test-3

```python
test3 = Didatic_test(
    fn = the_function,
    args = Dt.parse_args('forty'),
    keyboard_inputs = ('two'),
    test_name = 'Error demo',
    expected_output = 42,
    expected_prints = '42\n',
    run_prints_test = True,
    run_output_test = True,
    verbose=True
)

test3.run()
```
- print:
```
Case: Error demo
🚨⚠️🚨⚠️🚨 Error! 💀💀💀
<class 'ValueError'>
("invalid literal for int() with base 10: 'two'",)
invalid literal for int() with base 10: 'two'
[I]: One number, please:  two

---------------------------------------------------
```
- return:
```python
{'output_is_correct': False, 'print_is_correct': False, 'test_failed': True, 'test_done': False}
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.
[**MIT license**](LICENSE)

