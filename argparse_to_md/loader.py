import importlib
import sys
import typing as t
from unittest.mock import MagicMock


class FunctionLoader:
    def __init__(self, extra_sys_path: t.Optional[t.List[str]] = None):
        self.extra_sys_path = extra_sys_path
        self.modules_imported: t.Dict[str, t.Any] = {}

    @staticmethod
    def _sys_path_extend(extra_sys_path) -> t.ContextManager[None]:
        class SysPathContext:
            def __enter__(self):
                if extra_sys_path:
                    sys.path.extend(extra_sys_path)

            def __exit__(self, exc_type, exc_value, traceback):
                if extra_sys_path:
                    for path in extra_sys_path:
                        sys.path.remove(path)

        return SysPathContext()

    def load_function(self, module_name: str, function_name: str) -> t.Any:
        with self._sys_path_extend(self.extra_sys_path):
            last_missing_module_name = None
            while True:
                try:
                    if module_name in self.modules_imported:
                        module = self.modules_imported[module_name]
                        break

                    module = importlib.import_module(module_name)
                    self.modules_imported[module_name] = module
                    break

                except ImportError as e:
                    err = str(e)

                    if "No module named" in err:
                        # find the module name in the error message
                        missing_module_name = err.split("'")[1]
                        if missing_module_name == module_name:
                            print(f"Error importing module {module_name}", file=sys.stderr)
                            raise e
                        if missing_module_name == last_missing_module_name:
                            print(f"Error importing module {missing_module_name} after adding a mock", file=sys.stderr)
                            raise e
                        # create a mock module
                        missing_module = MagicMock()
                        # try again to import the module
                        print(f"Note: creating mock module {missing_module_name}", file=sys.stderr)
                        sys.modules[missing_module_name] = missing_module
                        continue

                    else:
                        raise e

            return getattr(module, function_name)
