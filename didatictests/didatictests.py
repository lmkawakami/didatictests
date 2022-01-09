#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports should be grouped into:
# Standard library imports
# Related third party imports
# Local application / relative imports
# in that order

# Standard library
import builtins
from typing import Any, Callable, Tuple
from __future__ import annotations

# Third party

# Relative

###############################################################################


def tuplefy(thing):
    return thing if type(thing) is tuple else (thing,)


def parse(*args, **kwargs):
    return {"pos_inputs": args, "key_inputs": kwargs}


###############################################################################


class Didatic_test(object):
    """
    A class to configure and run simple didatic tests

    Didatic_test(Callable=None, args={}, test_name=None, keyboard_inputs=(), expected_output=None, expected_prints="", verbose=None, run_output_test=None, run_prints_test=None,
    )

    Parameters
    ----------
    fn: Callable
        The function that will be tested
    args: dict
        The arguments that fn will be tested with. Use parse() to generate args, ex.: args = parse('a',5,7, x=1, s='aaa')
    test_name: str
        An optional identifier that will be printed with the test result
    keyboard_inputs: Tuple[str, ...]
        A tuple containig all the simulated keyboards inputs that will be used in every fn's input()
    expected_output: Any
        What the fn's return value should be
    expected_prints: str
        What the fn's internal print()'s concatenation should be (including new line character)
    verbose: bool
        Controls if all the fn's internal print()'s and input()'s prompts are printed
    run_output_test: bool
        Controls if the fn's return value is checked
    run_prints_test: bool
        Controls if the fn's internal print()'s are checked
    """

    __print_fn_backup = builtins.print
    __input_fn_backup = builtins.input

    fn = None
    verbose = False
    run_output_test = True
    run_prints_test = False

    @staticmethod
    def set_defaults(
        fn: Callable = None,
        verbose: bool = None,
        run_output_test: bool = None,
        run_prints_test: bool = None,
    ):
        """
        set_defaults(fn=None, verbose=None, run_output_test=None, run_prints_test None)

        Set common default values fot the tests configs to avoid repetition when setting them up later

        Parameters
        ----------
            fn: Callable
                The function that will be tested
            verbose: bool
                Controls if all the fn's internal print()'s and input()'s prompts are printed
            run_output_test: bool
                Controls if the fn's return value is checked
            run_prints_test: bool
                Controls if the fn's internal print()'s are checked
        """

        if not (fn is None):

            def new_fn(self, *args, **kwargs):
                return fn(*args, **kwargs)

            Didatic_test.fn = new_fn
        if not (verbose is None):
            Didatic_test.verbose = verbose
        if not (run_output_test is None):
            Didatic_test.run_output_test = run_output_test
        if not (run_prints_test is None):
            Didatic_test.run_prints_test = run_prints_test

    @staticmethod
    def run_tests(tests: list[Didatic_test]):
        """
        run_tests(tests)

        Run all the tests in the 'tests' list

        Parameters
        ----------
            tests: list[Didatic_test]
                A list of tests that you want to execute
        """

        results = []
        number_of_tests = len(tests)
        completed_tests = 0
        aborted_tests = 0
        correct_outputs_tests = 0
        correct_prints_tests = 0

        for index, test in enumerate(tests):
            if test.test_name is None:
                test.test_name = index
            result = test.run()
            correct_outputs_tests += result["output_is_correct"]
            correct_prints_tests += result["print_is_correct"]
            aborted_tests += result["test_failed"]
            completed_tests += result["test_done"]
            results.append(result)

        print(
            f"""
  correct_outputs_tests: {correct_outputs_tests}/{number_of_tests}
  correct_prints_tests: {correct_prints_tests}/{number_of_tests}
  aborted_tests: {aborted_tests}/{number_of_tests}
  completed_tests: {completed_tests}/{number_of_tests}
    """
        )
        return results

    def __init__(
        self,
        fn: Callable = None,
        args: dict = {},
        test_name: str = None,
        keyboard_inputs: Tuple[str, ...] = (),
        expected_output: Any = None,
        expected_prints: str = "",
        verbose: bool = None,
        run_output_test: bool = None,
        run_prints_test: bool = None,
    ):
        if not (fn is None):
            self.fn = fn
        self.args = args.get("pos_inputs", ())
        self.kwargs = args.get("key_inputs", {})
        self.test_name = test_name
        self.keyboard_inputs = tuplefy(keyboard_inputs)
        self.expected_output = expected_output
        self.expected_prints = expected_prints
        if not (verbose is None):
            self.verbose = verbose
        if not (run_output_test is None):
            self.run_output_test = run_output_test
        if not (run_prints_test is None):
            self.run_prints_test = run_prints_test

        self.test_done = False
        self.test_failed = False
        self.output_is_correct = False
        self.print_is_correct = False
        self.test_exception = None
        self.__prints_buffer = ""
        self.__verbose_buffer = ""

    def __repr__(self) -> str:
        return f"""
    fn: {self.fn.__name__}
    args: {self.args}
    kwargs: {self.kwargs}
    test_name: {self.test_name}
    keyboard_inputs: {self.keyboard_inputs}
    expected_output: {self.expected_output}
    expected_prints: {self.expected_prints}
    verbose: {self.verbose}
    run_output_test: {self.run_output_test}
    run_prints_test: {self.run_prints_test}
    """

    def __testing_input(self, prompt):

        test_input = str(self.keyboard_inputs_list.pop(0))
        if self.verbose:
            self.__verbose_buffer += "[I]: " + prompt + " " + test_input + "\n"
        return test_input

    def __redefine_input_fn(self, test_mode):
        if test_mode:
            self.__input_fn_backup = builtins.input
            builtins.input = self.__testing_input
        else:
            builtins.input = self.__input_fn_backup

    def __testing_print(self, *objects, sep=" ", end="\n", file=None, flush=None):
        prompt = sep.join(list([str(object) for object in objects])) + end
        if self.verbose:
            self.__verbose_buffer += "[P]: " + prompt
        # Filtrar linhas que começam com '[DBG]' para usálas como debug sem comprometer os testes de comparação de print
        if prompt[0:5] != "[DBG]":
            self.__prints_buffer += prompt

    def __redefine_print_fn(self, test_mode):
        if test_mode:
            self.__print_fn_backup = builtins.print
            builtins.print = self.__testing_print
        else:
            builtins.print = self.__print_fn_backup

    def __toggle_test_mode(self, test_mode):
        self.__redefine_input_fn(test_mode)
        self.__redefine_print_fn(test_mode)

    def __flush_buffers(self):
        self.__prints_buffer = ""
        self.__verbose_buffer = ""

    def run(self) -> dict:
        """
        run()

        Run the configured Didatic_test, print the result and returns a dictionary with the test outcome

        {
            "output_is_correct": bool,
            "print_is_correct": bool,
            "test_failed": bool,
            "test_done": bool,
        }
        """

        self.keyboard_inputs_list = list(self.keyboard_inputs)
        self.__toggle_test_mode(True)
        self.__flush_buffers()

        try:
            self.fn_output = self.fn(*self.args, **self.kwargs)
            self.output_is_correct = self.fn_output == self.expected_output
            self.print_is_correct = self.__prints_buffer == self.expected_prints
            self.test_done = True

        except Exception as excpt:
            self.test_failed = True
            self.test_exception = excpt

        finally:
            self.__toggle_test_mode(False)
            self.__print_outcome()

            return {
                "output_is_correct": self.output_is_correct,
                "print_is_correct": self.print_is_correct,
                "test_failed": self.test_failed,
                "test_done": self.test_done,
            }

    def __print_outcome(self):
        print(f"Caso: {self.test_name}")
        if self.test_failed:
            self.__print_exception()
            if self.verbose:
                print(self.__verbose_buffer)
        else:
            if self.verbose:
                print(self.__verbose_buffer)
            self.__print_result()
        print("---------------------------------------------------")

    def __print_exception(self):
        print("🚨⚠️🚨⚠️🚨 Erro durante os testes! 💀💀💀")
        print(type(self.test_exception))
        print(self.test_exception.args)
        print(self.test_exception)

    def __print_result(self):
        outputs_check = "✔️" if self.output_is_correct else "❌"
        prints_check = "✔️" if self.print_is_correct else "❌"

        outputs_check_message = (
            f"outputs: {outputs_check}  " if self.run_output_test else ""
        )
        prints_check_message = (
            f"prints: {prints_check}  " if self.run_prints_test else ""
        )
        remaining_keyboard_inputs_warning = (
            f"⚠️☢️ Atenção!!! Sobraram entradas do usuário que não foram usadas: {self.keyboard_inputs_list}"
            if len(self.keyboard_inputs_list)
            else ""
        )

        print(
            f"{outputs_check_message}{prints_check_message}{remaining_keyboard_inputs_warning}"
        )

        if (not self.output_is_correct) or (not self.print_is_correct):
            stripped_print_buffer = self.__prints_buffer.replace("\n", " | ").rstrip(
                " | "
            )
            stripped_expected_prints = self.expected_prints.replace("\n", " | ").rstrip(
                " | "
            )

            fn_args_line = f"   ➖ Function args:     {self.args} {self.kwargs}"
            keyboard_inputs_line = f"\n   ➖ Keyboard inputs:   {self.keyboard_inputs}"
            output_line = (
                f"\n   {outputs_check} Function outputs:  {self.fn_output}"
                if self.run_output_test
                else ""
            )
            expected_output_line = (
                f"\n   ➖ Resposta certa:    {self.expected_output}"
                if self.run_output_test
                else ""
            )
            prints_line = (
                f"\n   {prints_check} Prints da função:  {stripped_print_buffer}"
                if self.run_prints_test
                else ""
            )
            expected_prints_line = (
                f"\n   ➖ Prints corretos:   {stripped_expected_prints}"
                if self.run_prints_test
                else ""
            )

            print(
                f"{fn_args_line}{keyboard_inputs_line}{output_line}{expected_output_line}{prints_line}{expected_prints_line}"
            )
