from libs.functions.collate_attach_files.collate_attach_files import CollateAttachFiles
from libs.functions.ddc_collection.ddc_collection import DDCCollection
from libs.variables.configuration import Configuration


class ImplicitPluginList():
    @staticmethod
    def header_plugins():
        """
        The plug-ins which will be done before all other plug-ins
        :return: A lit of plug-in classes
        """
        plugins = list()
        return plugins

    @staticmethod
    def footer_plugins():
        """
        The plug-ins which will be done after all other plug-ins
        :return: A lit of plug-in classes
        """
        plugins = list()

        # the plug-ins cannot be mis-ordered
        if (Configuration.DDC_collection):
            plugins.append(DDCCollection)

        plugins.append(CollateAttachFiles)

        return plugins
