import builtins
import sys


class Didatic_test:
    """
    A class to configure and run simple didatic tests

    Didatic_test(Callable=None, args={}, test_name=None, keyboard_inputs=(), \
        expected_output=None, expected_prints="", verbose=None, \
            run_output_test=None, run_prints_test=None,
    )

    Parameters
    ----------
    fn: Callable
        The function that will be tested
    args: dict
        The arguments that fn will be tested with. Use parse() to generate args,\
             ex.: args = parse('a',5,7, x=1, s='aaa')
    test_name: str
        An optional identifier that will be printed with the test result
    keyboard_inputs: Tuple[str, ...]
        A tuple containig all the simulated keyboards inputs that will be used in \
            every fn's input()
    expected_output: Any
        What the fn's return value should be
    expected_prints: str
        What the fn's internal print()'s concatenation should be \
            (including new line character)
    verbose: bool
        Controls if all the fn's internal print()'s and input()'s prompts are printed
    run_output_test: bool
        Controls if the fn's return value is checked
    run_prints_test: bool
        Controls if the fn's internal print()'s are checked
    """

    # Função input que inputs copia pro 'inputs' tbm (não retorna pra print original)
    @staticmethod
    def __intercepted_input_fn(
        inputs: list, verbose: bool = False, identifier: str = ""
    ):
        input_fn_backup = builtins.input
        print_fn_backup = builtins.print

        def new_input(prompt):
            user_input = input_fn_backup(prompt)
            if verbose:
                print_fn_backup(f"{identifier}{prompt}{user_input}")
            inputs.append(user_input)
            return user_input

        return new_input

    # Função print que copia prints pro 'prints' tbm (não retorna pra print original)
    @staticmethod
    def __intercepted_print_fn(
        prints: list, verbose: bool = False, identifier: str = ""
    ):
        print_fn_backup = builtins.print

        def new_print(*objects, sep=" ", end="\n", file=sys.stdout, flush=False):
            str_list = [str(obj) for obj in objects]
            print_str = sep.join(str_list) + end
            if verbose:
                print_fn_backup(f"{identifier}{print_str}", sep="", end="")
            prints.append(print_str)
            return

        return new_print

    @staticmethod
    def __fake_input_fn(fake_inputs, verbose=False):
        fake_inputs = list(fake_inputs)

        def fake_input_fn(prompt):
            try:
                fake_input = str(fake_inputs.pop(0))
                if verbose:
                    print(prompt, fake_input)
                return fake_input

            except Exception as excpt:
                if excpt.args[0] == "pop from empty list":
                    print("⚠️ Error! insufficient simulated inputs")
                raise excpt

        return fake_input_fn

    # Redefine fn interceptando tudo: args, inputs, prints, output
    @staticmethod
    def intercepted_fn(
        fn, interceptions, verbose=False, input_identifier="", print_identifier=""
    ):
        interceptions.setdefault("prints", [])
        interceptions.setdefault("inputs", [])

        def new_fn(*args, **kwargs):
            input_fn_backup = builtins.input
            print_fn_backup = builtins.print
            builtins.input = Didatic_test.__intercepted_input_fn(
                interceptions["inputs"], verbose, input_identifier
            )
            builtins.print = Didatic_test.__intercepted_print_fn(
                interceptions["prints"], verbose, print_identifier
            )
            interceptions["args"] = args
            interceptions["kwargs"] = kwargs
            output = fn(*args, **kwargs)
            interceptions["output"] = output
            builtins.print = print_fn_backup
            builtins.input = input_fn_backup
            return output

        return new_fn

    @staticmethod
    def __stringify_args(args={}):
        quotes = "'"
        pos_args = args.get("pos_inputs", ())
        key_args = args.get("key_inputs", {})
        pos_args_str = str(pos_args).replace("(", "").replace(")", "")
        key_args_str = ", ".join(
            [
                f"{key}={quotes+value+quotes if type(value)==str else value}"
                for key, value in key_args.items()
            ]
        )
        args_str = ", ".join([pos_args_str, key_args_str]).strip(", ")
        return f"({args_str})"

    @staticmethod
    def generate_test(
        fn=None,
        args={},
        test_name="Test",
        verbose=None,
        run_output_test=None,
        run_prints_test=None,
        generator_verbose=None,
    ):
        """
        generate_test(fn, args, test_name="Test", verbose=False, \
        run_output_test=True, run_prints_test=False, generator_verbose=False,)

        Run the function once using ther given 'args' and intercepts all\
            the inpus, prints and outpus
        Generate and return the string to create the test with the given configs.\
            and the intercepted infos.

        ex.: generate_test(fn, Didatic_test.parse_args(1,2,3), "Test-5", True, True)

        Parameters
        ----------
            fn: The function that will be tested


            args: dict in the format {"pos_inputs": args, "key_inputs": kwargs}
            test_name: test name to identify the results and hint the type of test
            verbose: controls if the fn's internal inputs and prints will be printed
            run_output_test: controls if the output of the test run will be checked \
                against the expected output value
            run_prints_test: controls if the prints of the test run will be checked \
                against the expected prints
            generator_verbose: controls if the fn's internal inputs and prints \
                will be printed in the fist run (the interception run)

        Returns
        -------
            constructor_str: Return the string with the test constuctor containing\
                all the configurations and args predefined, and with the intecepted\
                    inputs, prints and outputs as the expected values
        """
        if fn is None:
            fn = Didatic_test.default_fn

        if verbose is None:
            verbose = Didatic_test.default_verbose or False

        if run_output_test is None:
            run_output_test = Didatic_test.default_run_output_test or True

        if run_prints_test is None:
            run_prints_test = Didatic_test.default_run_prints_test or False

        if generator_verbose is None:
            Didatic_test.default_generator_verbose = generator_verbose or False

        interceptions = {}
        intercepted_fn = Didatic_test.intercepted_fn(
            fn, interceptions, generator_verbose, "[I]: ", "[O]: "
        )

        pos_args = args.get("pos_inputs", ())
        key_args = args.get("key_inputs", {})

        output = intercepted_fn(*pos_args, **key_args)

        fn_name = fn.__name__
        args_str = Didatic_test.__stringify_args(args)
        output_str = "'" + output + "'" if type(output) == str else str(output)
        prints_str = "".join(interceptions["prints"])

        constructor_str = f"Didatic_test({fn_name}, Didatic_test.parse_args\
{args_str}, '{test_name}', {interceptions['inputs']}, {output_str}, \
'{prints_str}', {verbose}, {run_output_test}, {run_prints_test})"

        return constructor_str

    @staticmethod
    def auto_redefine(fn, args={}, verbose=False):
        """
        auto_redefine(fn, verbose=False)

        Run fn normally once and save all the inputs, then return a\
            redefined fn that reuses the same user inputs (simulated)
        The args and kwarks continue to work normally

        ex.: open_menu = auto_redefine(open_menu)

        Parameters
        ----------
            fn: The function that will be called with intercepted inputs
            verbose: flag that controls if the inputs primpts will be printed

        Returns
        -------
            auto_redefined: Return a new function that will always use the same\
                keyboard inputs as typed on the first run
        """

        interceptions = {}
        intercepted_fn = Didatic_test.intercepted_fn(
            fn, interceptions, verbose, "[I]: ", "[O]: "
        )

        pos_args = args.get("pos_inputs", ())
        key_args = args.get("key_inputs", {})
        intercepted_fn(*pos_args, **key_args)

        inputs_list = interceptions["inputs"]
        auto_redefined = Didatic_test.redefine(fn, inputs_list, verbose)
        return auto_redefined

    @staticmethod
    def redefine(fn, keyboard_inputs, verbose=False):
        """
        redefine(fn, keyboard_inputs, verbose=False)

        Return a new function that will use the 'keyboard_inputs' tuple\
            as simulated inputs, but will work as fn otherwise

        ex.: call_menu = redefine(call_menu,('lorem ipsum','25','y','n'))

        Parameters
        ----------
            fn: The function that will be copied but will use \
                the simulated inputs
            keyboard_inputs: The inputs that will be simulated

        Returns
        -------
            refedined_fn: Return a fn copy that will always \
                use the 'keyboard_inputs' as input simulation
        """

        def refedined_fn(*args, **kwargs):
            inputs_list = list(keyboard_inputs)

            input_fn_backup = builtins.input
            builtins.input = Didatic_test.__fake_input_fn(inputs_list, verbose)

            try:
                output = fn(*args, **kwargs)
            except Exception as excpt:
                raise excpt
            finally:
                builtins.input = input_fn_backup
            return output

        return refedined_fn

    @staticmethod
    def parse_args(*args, **kwargs):
        """
        parse_args(args, kwargs)

        Auxiliar function to pass fn's args and kwargs like in a normal fn call
        Just passs the positional args first and then key arguments

        ex.: parse_args(1,2,3,x=15,y=[0,0,1],z='aa')

        Parameters
        ----------
            args: The positional arguments of fn
            kwargs: The key arguments of fn

        Returns
        -------
            values: dict with 2 keys: 'pos_inputs' and 'key_inputs'
        """
        return {"pos_inputs": args, "key_inputs": kwargs}

    @staticmethod
    def run_tests(tests):
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
            else:
                test.test_name = f"{index} - {test.test_name}"
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
        """
        set_defaults(fn=None, verbose=None, run_output_test=None, run_prints_test None)

        Set common default values fot the tests configs to avoid repetition when \
            setting them up later

        Parameters
        ----------
            fn: Callable
                The function that will be tested
            verbose: bool
                Controls if all the fn's internal print()'s and \
                    input()'s prompts are printed
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
    def set_generator_defaults(
        fn=None,
        verbose=None,
        run_output_test=None,
        run_prints_test=None,
        generator_verbose=None,
    ):
        """
        set_generator_defaults(fn=None, verbose=None, run_output_test=None, \
            run_prints_test=None, generator_verbose=None)

        Set common default values fot the test generator to avoid unnecessary repetition

        Parameters
        ----------
            fn: Callable
                The function that will be tested
            verbose: bool
                Controls if all the fn's internal print()'s and \
                    input()'s prompts are printed when a test runs
            run_output_test: bool
                Controls if the fn's return value is tested
            run_prints_test: bool
                Controls if the fn's internal print()'s are tested
            generator_verbose: bool
                Controls if all the fn's internal print()'s and\
                    input()'s prompts are printed on the test\
                        generator run
        """
        if not (fn is None):
            Didatic_test.default_fn = fn

        if not (verbose is None):
            Didatic_test.default_verbose = verbose

        if not (run_output_test is None):
            Didatic_test.default_run_output_test = run_output_test

        if not (run_prints_test is None):
            Didatic_test.default_run_prints_test = run_prints_test

        if not (generator_verbose is None):
            Didatic_test.default_generator_verbose = generator_verbose

    def run(self):
        """
        run()

        Run the configured Didatic_test, print the result and \
            returns a dictionary with the test outcome

        {
            "output_is_correct": bool,
            "print_is_correct": bool,
            "test_failed": bool,
            "test_done": bool,
        }
        """
        self.keyboard_inputs_list = list(self.keyboard_inputs)
        self.interceptions = {}
        fn_temp = Didatic_test.intercepted_fn(
            self.fn, self.interceptions, self.verbose, "[I]: ", "[P]: "
        )
        new_fn = Didatic_test.redefine(fn_temp, self.keyboard_inputs_list, False)

        try:
            new_fn(*self.args, **self.kwargs)
            fn_output = self.interceptions["output"]
            self.output_is_correct = fn_output == self.expected_output
            fn_prints = "".join(self.interceptions["prints"])
            self.print_is_correct = fn_prints == self.expected_prints
            self.test_done = True

        except Exception as excpt:
            self.test_failed = True
            self.test_exception = excpt

        finally:
            print(f"Case: {self.test_name}")
            if self.test_failed:
                self.__print_exception()
            else:
                self.__print_result()
            print("---------------------------------------------------")

            return {
                "output_is_correct": self.output_is_correct,
                "print_is_correct": self.print_is_correct,
                "test_failed": self.test_failed,
                "test_done": self.test_done,
            }

    def just_run(self):
        """
        just_run()

        Run the configured Didatic_test, print the result and \
            returns a dictionary with the test outcome

        {
            "output_is_correct": bool,
            "print_is_correct": bool,
            "test_failed": bool,
            "test_done": bool,
        }
        """
        self.keyboard_inputs_list = list(self.keyboard_inputs)
        self.interceptions = {}
        fn_temp = Didatic_test.intercepted_fn(
            self.fn, self.interceptions, self.verbose, "[I]: ", "[P]: "
        )
        new_fn = Didatic_test.redefine(fn_temp, self.keyboard_inputs_list, False)

        print(f"Case: {self.test_name}")
        try:
            new_fn(*self.args, **self.kwargs)

        except Exception as excpt:
            self.test_exception = excpt
            self.__print_exception()

    def __init__(
        self,
        fn=None,
        args={},
        test_name="Test",
        keyboard_inputs=[],
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
        self.keyboard_inputs = keyboard_inputs
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
        self.output_is_correct = None
        self.print_is_correct = None
        self.test_exception = None
        self.interceptions = {}

    def __repr__(self) -> str:
        return f"fn: {self.fn.__name__}/n\
            args: {self.args}/n\
            kwargs: {self.kwargs}/n\
            test_name: {self.test_name}/n\
            keyboard_inputs: {self.keyboard_inputs}/n\
            expected_output: {self.expected_output}/n\
            expected_prints: {self.expected_prints}/n\
            verbose: {self.verbose}/n\
            run_output_test: {self.run_output_test}/n\
            run_prints_test: {self.run_prints_test}/n\
            interceptions: {str(self.interceptions)}"

    def __print_exception(self):
        print("🚨⚠️🚨⚠️🚨 Error! 💀💀💀")
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
            f"⚠️☢️ Warning!!! some inputs were not used: \
              {self.keyboard_inputs_list}"
            if len(self.keyboard_inputs_list) > len(self.interceptions["inputs"])
            else ""
        )

        print(
            f"{outputs_check_message}{prints_check_message}\
              {remaining_keyboard_inputs_warning}"
        )

        if (not self.output_is_correct) or (not self.print_is_correct):
            stripped_print_buffer = (
                "".join(self.interceptions["prints"]).replace("\n", " | ").rstrip(" | ")
            )
            stripped_expected_prints = self.expected_prints.replace("\n", " | ").rstrip(
                " | "
            )

            fn_args_line = f"   ➖ Function args:      {self.args} {self.kwargs}"
            keyboard_inputs_line = f"\n   ➖ Keyboard inputs:    {self.keyboard_inputs}"
            output_line = (
                f"\n   {outputs_check} Function outputs:   \
{self.interceptions['output']}"
                if self.run_output_test
                else ""
            )
            expected_output_line = (
                f"\n   ➖ Expected output:    {self.expected_output}"
                if self.run_output_test
                else ""
            )
            prints_line = (
                f"\n   {prints_check} fn internal prints: {stripped_print_buffer}"
                if self.run_prints_test
                else ""
            )
            expected_prints_line = (
                f"\n   ➖ Expected prints:    {stripped_expected_prints}"
                if self.run_prints_test
                else ""
            )

            print(
                f"{fn_args_line}{keyboard_inputs_line}{output_line}\
                  {expected_output_line}{prints_line}{expected_prints_line}"
            )
