    def pip_freeze(self, task_id):
        out=""
        try:
            import pkg_resources
            installed_packages = pkg_resources.working_set
            installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
            return "\n".join(installed_packages_list)
        except:
            out+="[*] pkg_resources module not installed.\n"

        try:
            from pip._internal.operations.freeze import freeze
            installed_packages_list = freeze(local_only=True)
            return "\n".join(installed_packages_list)
        except:
            out+="[*] pip module not installed.\n"

        try:
            import pkgutil
            installed_packages_list = [ a for _, a, _ in pkgutil.iter_modules()]
            return "\n".join(installed_packages_list)
        except:
            out+="[*] pkgutil module not installed.\n"

        return out+"[!] No modules available to list installed packages."
