from libs.executors.app_executor.implicit_plugins.implicit_plugin_list import ImplicitPluginList
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.data_structures.type_check import TypeCheck
from libs.variables.keys import AppKeys


class ImplicitPlugin():
    @staticmethod
    def add_implicit_header_plugins(app):
        # The plug-ins added before the explicit plug-ins
        header = ImplicitPluginList.header_plugins()
        TypeCheck.list(header)
        header_dicts = ImplicitPlugin.functions_to_dicts(header)

        # The plug-ins in the YAML file
        explicit_plugins = Dictionary.get_value(app, AppKeys.functions, type=list)
        TypeCheck.list(explicit_plugins)

        # Add all plug-ins together
        all_plugins = header_dicts + explicit_plugins

        Dictionary.set_value(app, AppKeys.functions, all_plugins)
        return app

    @staticmethod
    def add_implicit_footer_plugins(app):
        # The plug-ins added after the explicit plug-ins
        footer = ImplicitPluginList.footer_plugins()
        TypeCheck.list(footer)
        footer_dicts = ImplicitPlugin.functions_to_dicts(footer)

        # The plug-ins in the YAML file
        explicit_plugins = Dictionary.get_value(app, AppKeys.functions, type=list)
        TypeCheck.list(explicit_plugins)

        # Add all plug-ins together
        all_plugins = explicit_plugins + footer_dicts

        Dictionary.set_value(app, AppKeys.functions, all_plugins)
        return app

    @staticmethod
    def functions_to_dicts(functions):
        dicts = list()
        for function in functions:
            dictionary = dict()
            Dictionary.set_value(dictionary, AppKeys.func_name, function.func_name())
            dicts.append(dictionary)
        return dicts
