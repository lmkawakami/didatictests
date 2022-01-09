import builtins


def tuplefy(thing):
    return thing if type(thing) is tuple else (thing,)


def parse(*args, **kwargs):
    return {"pos_inputs": args, "key_inputs": kwargs}


class Didatic_test:
    __print_fn_backup = builtins.print
    __input_fn_backup = builtins.input

    @staticmethod
    def run_tests(tests):
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

    fn = None
    verbose = False
    run_output_test = True
    run_prints_test = False

    @staticmethod
    def set_defaults(fn=None, verbose=None, run_output_test=None, run_prints_test=None):
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

    def __init__(
        self,
        fn=None,
        args={},
        test_name=None,
        keyboard_inputs=(),
        expected_output=None,
        expected_prints="",
        verbose=None,
        run_output_test=None,
        run_prints_test=None,
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
        # Filtrar linhas que começam com '[DBG]'
        # para usálas como debug sem comprometer os testes de comparação de print
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

    def run(self):

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
            self.print_outcome()

            return {
                "output_is_correct": self.output_is_correct,
                "print_is_correct": self.print_is_correct,
                "test_failed": self.test_failed,
                "test_done": self.test_done,
            }

    def print_outcome(self):
        print(f"Caso: {self.test_name}")
        if self.test_failed:
            self.print_exception()
            if self.verbose:
                print(self.__verbose_buffer)
        else:
            if self.verbose:
                print(self.__verbose_buffer)
            self.print_result()
        print("---------------------------------------------------")

    def print_exception(self):
        print("🚨⚠️🚨⚠️🚨 Erro durante os testes! 💀💀💀")
        print(type(self.test_exception))
        print(self.test_exception.args)
        print(self.test_exception)

    def print_result(self):
        outputs_check = "✔️" if self.output_is_correct else "❌"
        prints_check = "✔️" if self.print_is_correct else "❌"

        outputs_check_message = (
            f"outputs: {outputs_check}  " if self.run_output_test else ""
        )
        prints_check_message = (
            f"prints: {prints_check}  " if self.run_prints_test else ""
        )
        remaining_keyboard_inputs_warning = (
            f"⚠️☢️ Atenção!!! Sobraram entradas do usuário que \
              não foram usadas: {self.keyboard_inputs_list}"
            if len(self.keyboard_inputs_list)
            else ""
        )

        print(
            f"{outputs_check_message}{prints_check_message}\
              {remaining_keyboard_inputs_warning}"
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
                f"{fn_args_line}{keyboard_inputs_line}{output_line}\
                  {expected_output_line}{prints_line}{expected_prints_line}"
            )
