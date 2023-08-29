import os
import sys

import unittest
from unittest import mock

import importlib

import settipy


class TestFeatures(unittest.TestCase):
    """
    Took over the testing style from the official argparse.
    https://github.com/python/cpython/blob/main/Lib/test/test_argparse.py#L182
    """

    def setUp(self):
        importlib.reload(settipy)

    def tearDown(self):
        pass

    def test_happy_path_default(self):
        setpy = settipy.settipy

        expected = "default value for foobar"
        setpy.set(
            flag_name="FOOBAR",
            default=expected,
            message="explain why something is foobar"
        )
        setpy.parse()
        self.assertEqual(expected, setpy.get("FOOBAR"))

    def test_happy_path_get_pythonic(self):
        setpy = settipy.settipy

        expected = "default value for foobar"
        setpy.set(
            flag_name="FOOBAR",
            default=expected,
            message="explain why something is foobar"
        )
        setpy.parse()
        self.assertEqual(expected, setpy["FOOBAR"])

    def test_happy_path_env(self):
        setpy = settipy.settipy

        expected = "value set in env"
        patched_environ = {"FOOBAR": expected}

        with mock.patch.dict(os.environ, patched_environ, clear=True):
            setpy.set(
                flag_name="FOOBAR",
                default="default value for foobar",
                message="explain why something is foobar"
            )
            setpy.parse()
            self.assertEqual(expected, setpy.get("FOOBAR"))

    def test_happy_path_cli(self):
        setpy = settipy.settipy

        expected = "value_set_with_cli"

        patched_argv = ["./foo.py", "--FOOBAR", expected]
        with mock.patch.object(sys, "argv", patched_argv):
            setpy.set(
                flag_name="FOOBAR",
                default="default value for foobar",
                message="explain why something is foobar"
            )
            setpy.parse()
            self.assertEqual(expected, setpy.get("FOOBAR"))

    def test_happy_path_order_of_precedence_cli(self):
        setpy = settipy.settipy

        expected = "value_set_with_cli"
        not_expected = "value_set_with_env"
        patched_argv = ["./foo.py", "--FOOBAR", expected]
        patched_environ = {"FOOBAR": not_expected}

        with mock.patch.dict(os.environ, patched_environ, clear=True):
            with mock.patch.object(sys, "argv", patched_argv):
                setpy.set(
                    flag_name="FOOBAR",
                    default="default value for foobar",
                    message="explain why something is foobar"
                )
                setpy.parse()
                self.assertEqual(expected, setpy.get("FOOBAR"))

    def test_happy_path_order_of_precedence_switched_mocking(self):
        setpy = settipy.settipy

        expected = "value_set_with_cli"
        not_expected = "value_set_with_env"
        patched_argv = ["./foo.py", "--FOOBAR", expected]
        patched_environ = {"FOOBAR": not_expected}

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set(
                    flag_name="FOOBAR",
                    default="default value for foobar",
                    message="explain why something is foobar"
                )
                setpy.parse()
                self.assertEqual(expected, setpy.get("FOOBAR"))

    def test_var_not_set(self):
        setpy = settipy.settipy

        cli_value = "value_set_with_cli"
        env_value = "value_set_with_env"
        patched_argv = ["./foo.py", "--FOOBAR", cli_value]
        patched_environ = {"FOOBAR": env_value}

        flag_name = "DOENST_EXIT"

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set(
                    flag_name="FOOBAR",
                    default="default value for foobar",
                    message="explain why something is foobar"
                )
                setpy.parse()

                with self.assertRaises(KeyError):
                    setpy.get(flag_name)

    def test_var_should_be_set_and_is_env(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        cli_value = "value_set_with_cli"
        env_value = "value_set_with_env"
        flag_name = "FOOBAR"
        patched_argv = ["./foo.py", "--something", cli_value]
        patched_environ = {flag_name: env_value}

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set(
                    flag_name=flag_name,
                    default="default value for foobar",
                    message="explain why something is foobar",
                    should=True
                )
                setpy.parse()
                self.assertEqual(env_value, setpy.get(flag_name))

    def test_var_should_be_set(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        cli_value = "value_set_with_cli"
        env_value = "value_set_with_env"
        patched_argv = ["./foo.py", "--FOOBAR", cli_value]
        patched_environ = {"FOOBAR": env_value}

        flag_name = "DOENST_EXIT"
        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set(
                    flag_name=flag_name,
                    default="default value for foobar",
                    message="explain why something is foobar",
                    should=True
                )

                with self.assertRaises(Exception):
                    setpy.parse()

    def test_var_should_be_of_options(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        cli_value = "value_set_env"
        env_value = "value_set_with_env"
        patched_argv = ["./foo.py", "--FOOBAR", cli_value]
        patched_environ = {"FOOBAR": env_value}

        flag_name = "FOOBAR"
        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set(
                    flag_name=flag_name,
                    default="default value for foobar",
                    message="explain why something is foobar",
                    options=["foo", "bar"],
                )

                with self.assertRaises(Exception):
                    setpy.parse()

    def test_happy_path_multiple(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        cli_value = "cli-set"
        env_value = "env-set"
        patched_argv = ["./foo.py", "-a", cli_value]
        patched_environ = {"b": env_value}

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set("a", "default a", "msg a")
                setpy.set("b", "default b", "msg b")
                setpy.set("c", "default c", "msg c")
                setpy.set("d", "default d", "msg d")
                setpy.set("e", "default e", "msg e")
                setpy.parse()

                self.assertEqual(cli_value, setpy["a"])
                self.assertEqual(env_value, setpy["b"])
                self.assertEqual("default c", setpy["c"])
                self.assertEqual("default d", setpy["d"])
                self.assertEqual("default e", setpy["e"])

    def test_happy_path_multiple_should(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        cli_value = "cli-set"
        env_value = "env-set"
        patched_argv = ["./foo.py", "-a", cli_value]
        patched_environ = {"b": env_value}

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set("a", "default a", "msg a")
                setpy.set("b", "default b", "msg b", should=True)
                setpy.set("c", "default c", "msg c")
                setpy.set("d", "default d", "msg d")
                setpy.set("e", "default e", "msg e")
                setpy.parse()

                self.assertEqual(cli_value, setpy["a"])
                self.assertEqual(env_value, setpy["b"])
                self.assertEqual("default c", setpy["c"])
                self.assertEqual("default d", setpy["d"])
                self.assertEqual("default e", setpy["e"])

    def test_happy_path_multiple_should_if(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        cli_value = "cli-set"
        env_value = "env-set"
        patched_argv = ["./foo.py", "-a", cli_value]
        patched_environ = {"b": env_value}

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set("a", "default a", "msg a")
                setpy.set("b", "default b", "msg b", should_if=["a"])
                setpy.set("c", "default c", "msg c")
                setpy.set("d", "default d", "msg d")
                setpy.set("e", "default e", "msg e")
                setpy.parse()

                self.assertEqual(cli_value, setpy["a"])
                self.assertEqual(env_value, setpy["b"])
                self.assertEqual("default c", setpy["c"])
                self.assertEqual("default d", setpy["d"])
                self.assertEqual("default e", setpy["e"])

    def test_multiple_should_if(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        cli_value = "cli-set"
        env_value = "env-set"
        patched_argv = ["./foo.py", "-a", cli_value]
        patched_environ = {"b": env_value}

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set("a", "default a", "msg a")
                setpy.set("b", "default b", "msg b")
                setpy.set("c", "default c", "msg c", should_if=["b"])
                setpy.set("d", "default d", "msg d")
                setpy.set("e", "default e", "msg e")

                with self.assertRaises(Exception):
                    setpy.parse()

    def test_happy_path_multiple_should_if_fixed(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        cli_value = "cli-set"
        env_value = "env-set"
        env_value_2 = "also-env-set"
        patched_argv = ["./foo.py", "-a", cli_value]
        patched_environ = {"b": env_value, "c": env_value_2}

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set("a", "default a", "msg a")
                setpy.set("b", "default b", "msg b", should_if=["a"])
                setpy.set("c", "default c", "msg c", should_if=["b"])
                setpy.set("d", "default d", "msg d")
                setpy.set("e", "default e", "msg e")
                setpy.parse()

                self.assertEqual(cli_value, setpy["a"])
                self.assertEqual(env_value, setpy["b"])
                self.assertEqual(env_value_2, setpy["c"])
                self.assertEqual("default d", setpy["d"])
                self.assertEqual("default e", setpy["e"])

    def test_multiple_should_if_multiple(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        cli_value = "cli-set"
        env_value = "env-set"
        env_value_2 = "also-env-set"
        patched_argv = ["./foo.py", "-a", cli_value]
        patched_environ = {"b": env_value, "c": env_value_2}

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set("a", "default a", "msg a")
                setpy.set("b", "default b", "msg b", should_if=["a"])
                setpy.set("c", "default c", "msg c", should_if=["b"])
                setpy.set("d", "default d", "msg d", should_if=["a", "b", "c"])
                setpy.set("e", "default e", "msg e")
                with self.assertRaises(Exception):
                    setpy.parse()

    def test_happy_path_multiple_should_if_multiple_fixed(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        cli_value = "cli-set"
        cli_value_2 = "also-cli-set"
        cli_value_3 = "also-cli-set-too"
        env_value = "env-set"
        patched_argv = ["./foo.py", "-a", cli_value, "--c", cli_value_2, "-d",  cli_value_3]
        patched_environ = {"b": env_value}

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set("a", "default a", "msg a")
                setpy.set("b", "default b", "msg b", should_if=["a"])
                setpy.set("c", "default c", "msg c", should_if=["b"])
                setpy.set("d", "default d", "msg d", should_if=["a", "b", "c"])
                setpy.set("e", "default e", "msg e")
                setpy.parse()

                self.assertEqual(cli_value, setpy["a"])
                self.assertEqual(env_value, setpy["b"])
                self.assertEqual(cli_value_2, setpy["c"])
                self.assertEqual(cli_value_3, setpy["d"])
                self.assertEqual("default e", setpy["e"])


class TestTypes(unittest.TestCase):
    """
    Took over the testing style from the official argparse.
    https://github.com/python/cpython/blob/main/Lib/test/test_argparse.py#L182
    """

    def setUp(self):
        importlib.reload(settipy)

    def tearDown(self):
        pass

    def test_happy_path_all_cli(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        expected_str = "foobar"
        expected_int = 42
        expected_bool = True
        expected_list = ["a", "b", "c"]
        expected_dict = {"foo": "bar", "foo1": "bar1"}
        expected_dict_list = {
            "foo": ["bar"],
            "foo1": ["bar1", "bar2"]
        }

        cli_str = "foobar"
        cli_int = "42"
        cli_bool = "y"
        cli_list = "a,b,c"
        cli_dict = "foo:bar;foo1:bar1"
        cli_dict_list = "foo:bar;foo1:bar1,bar2"
        patched_argv = [
            "./foo.py",
            "-a", cli_str,
            "-b", cli_int,
            "-c", cli_bool,
            "-d", cli_list,
            "-e", cli_dict,
            "-f", cli_dict_list,
        ]
        patched_environ = {}

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set("a", "default a", "msg a")
                setpy.set_int("b", 2, "msg b")
                setpy.set_bool("c", False, "msg c")
                setpy.set_list("d", [], "msg d")
                setpy.set_dict("e", {}, "msg e")
                setpy.set_dict_list("f", {}, "msg f")
                setpy.parse()

                self.assertEqual(expected_str, setpy["a"])
                self.assertEqual(expected_int, setpy["b"])
                self.assertEqual(expected_bool, setpy["c"])

                # Assert list
                self.assertCountEqual(expected_list, setpy["d"])
                self.assertListEqual(expected_list, setpy["d"])

                # Assert Dict
                self.assertDictEqual(expected_dict, setpy["e"])
                self.assertDictEqual(expected_dict_list, setpy["f"])

    def test_happy_path_all_env(self):
        setpy = settipy.settipy
        setpy.test_mode = True

        expected_str = "foobar"
        expected_int = 42
        expected_bool = True
        expected_list = ["a", "b", "c"]
        expected_dict = {"foo": "bar", "foo1": "bar1"}
        expected_dict_list = {
            "foo": ["bar"],
            "foo1": ["bar1", "bar2"]
        }

        env_str = "foobar"
        env_int = "42"
        env_bool = "y"
        env_list = "a,b,c"
        env_dict = "foo:bar;foo1:bar1"
        env_dict_list = "foo:bar;foo1:bar1,bar2"
        patched_argv = [
            "./foo.py"
        ]
        patched_environ = {
            "a": env_str,
            "b": env_int,
            "c": env_bool,
            "d": env_list,
            "e": env_dict,
            "f": env_dict_list,
        }

        with mock.patch.object(sys, "argv", patched_argv):
            with mock.patch.dict(os.environ, patched_environ, clear=True):
                setpy.set("a", "default a", "msg a")
                setpy.set_int("b", 2, "msg b")
                setpy.set_bool("c", False, "msg c")
                setpy.set_list("d", [], "msg d")
                setpy.set_dict("e", {}, "msg e")
                setpy.set_dict_list("f", {}, "msg f")
                setpy.parse()

                self.assertEqual(expected_str, setpy["a"])
                self.assertEqual(expected_int, setpy["b"])
                self.assertEqual(expected_bool, setpy["c"])

                # Assert list
                self.assertCountEqual(expected_list, setpy["d"])
                self.assertListEqual(expected_list, setpy["d"])

                # Assert Dict
                self.assertDictEqual(expected_dict, setpy["e"])
                self.assertDictEqual(expected_dict_list, setpy["f"])


if __name__ == '__main__':
    unittest.main()
