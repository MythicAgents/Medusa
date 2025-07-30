    def clipboard(self, task_id):
        from ctypes import _dlopen, CDLL, c_void_p, c_char_p, c_uint, c_size_t, c_buffer, c_ulonglong, c_bool, c_longlong, POINTER, c_int, CFUNCTYPE, Structure, c_ulong, c_char_p, byref, cast, sizeof, c_int32, pointer, string_at

        class Id(c_void_p):
            def __getattr__(self, name):
                name = name.replace("_", ":")
                return lambda *args: self.I(name, *args)
            
            def I(self, selector, *args): 
                clazz = _libObjC.object_getClass(self)
                sel = _libObjC.sel_registerName(selector.encode('utf-8'))
                method = _libObjC.class_getInstanceMethod(clazz, sel)

                class_name = _libObjC.class_getName(clazz)

                if not method:
                    raise Exception(f"Method {selector} not found in class {class_name.decode('utf-8')}")
                returnType, argTypes = _getReturnAndArgTypes(method)

                typed_objc_msgSend = _libObjC.objc_msgSend

                typed_objc_msgSend.restype = returnType
                typed_objc_msgSend.argtypes = argTypes

                return typed_objc_msgSend(self, sel, *args)

        id_subclasses = [
            "Ivar", "Method", "Property", "Protocol", "Class", "SEL", "IMP", "Block",
        ]

        for class_name in id_subclasses:
            globals()[class_name] = type(class_name, (Id,), {})

        def _load_lib(name):
            if not _dlopen(name):
                raise OSError('Cannot find library %s' % name)
                
            return CDLL(name)

        def _csignature(libfunc, restype, *argtypes, variadic=False):
            libfunc.restype = restype

            if argtypes:
                libfunc.argtypes = argtypes
            
            return libfunc

        def objcArgTypeToCType(argtype):
            _objcArgTypeToCType = {
                b"c": c_char_p,
                b"v": None,
                b"@": Id,
                b"#": Class,
                b":": SEL,
                b"Q": c_ulonglong,
                b"r*": c_char_p,
                b"B": c_bool,
                b"q": c_longlong,
                b"^@": POINTER(c_void_p),
                b"i": c_int,
                b"@?": Block
            }

            if argtype in _objcArgTypeToCType:
                return _objcArgTypeToCType[argtype]
            else:
                raise Exception(f"Unknown Objective-C argument type: {argtype.decode('utf-8')}")


        _libFoundation = _load_lib('/System/Library/Frameworks/Foundation.framework/Foundation')

        if _libFoundation:
            _csignature(_libFoundation.NSLog, None, c_void_p, variadic=True)

        _libObjC = _load_lib('/usr/lib/libobjc.dylib')

        if _libObjC:
            _csignature(_libObjC.class_getName, c_char_p, Class)
            _csignature(_libObjC.objc_getClass, Class, c_char_p)
            _csignature(_libObjC.sel_registerName, SEL, c_char_p)
            _csignature(_libObjC.class_getClassMethod, Method, Class, SEL)
            _csignature(_libObjC.class_getInstanceMethod, Method, Class, SEL)
            _csignature(_libObjC.method_getImplementation, IMP, Method)
            _csignature(_libObjC.method_getName, SEL, Method)
            _csignature(_libObjC.sel_getName, c_char_p, SEL)
            _csignature(_libObjC.method_getTypeEncoding, c_char_p, Method)
            _csignature(_libObjC.method_getNumberOfArguments, c_uint, Method)        
            _csignature(_libObjC.method_getArgumentType, None, Method, c_uint, c_char_p, c_size_t)
            _csignature(_libObjC.method_getReturnType, None, Method, c_char_p, c_size_t)
            _csignature(_libObjC.objc_msgSend, Id, Id, SEL, variadic=True)
            _csignature(_libObjC.object_getClassName, c_char_p, Id)
            _csignature(_libObjC.object_getClass, Class, Id)

        def _getReturnAndArgTypes(method):
            numArgs = _libObjC.method_getNumberOfArguments(method)
            argTypes = []

            for i in range(numArgs):
                argType = c_buffer(512)
                _libObjC.method_getArgumentType(method, i, argType, len(argType))
                argTypeCType = objcArgTypeToCType(argType.value)
                argTypes.append(argTypeCType)

            returnType = c_buffer(512)
            _libObjC.method_getReturnType(method, returnType, len(returnType))
            returnTypeCType = objcArgTypeToCType(returnType.value)

            return returnTypeCType, argTypes

        class NSObject:
            def __init__(self, className):
                clazz = _libObjC.objc_getClass(className.encode('utf-8'))

                if not clazz:
                    raise Exception("Cannot find class %s" % className)
                
                self._class = clazz
                self._className = className

            def ptr(self):
                return self._class

            def __getattr__(self, name):
                name = name.replace("_", ":")
                return lambda *args: self.C(name, *args)

            def C(self, selector, *args,):
                sel = _libObjC.sel_registerName(selector.encode('utf-8'))
                method = _libObjC.class_getClassMethod(self._class, sel)

                returnType, argTypes = _getReturnAndArgTypes(method)

                typed_objc_msgSend = _libObjC.objc_msgSend
                typed_objc_msgSend.restype = returnType
                typed_objc_msgSend.argtypes = argTypes

                return typed_objc_msgSend(self._class, sel, *args)
            
        class ObjCBlockDescriptor(Structure):
            _fields_=[
                ('reserved',c_ulong),
                ('size',c_ulong),
                ('signature', c_char_p)
            ]
            
            def __init__(self,block):
                self.size=sizeof(block)

        def ObjCBlock(invoke,restype,argtypes):
            BLOCK_FUNC = CFUNCTYPE(restype,c_void_p,*argtypes)
            class Block(Structure):
                _fields_=  [
                    ('isa',c_void_p),
                    ('flags',c_int32),
                    ('reserved',c_int32),
                    ('invoke',BLOCK_FUNC),
                    ('descriptor',POINTER(ObjCBlockDescriptor))
                ]   
                
                def __init__(self):
                    self.descriptor=pointer(ObjCBlockDescriptor(self))
                    self.isa=NSObject("NSBlock").ptr()
                    self.invoke=BLOCK_FUNC(invoke)

            return byref(Block())

        _load_lib('/System/Library/Frameworks/AppKit.framework/AppKit')

        pasteboardStringType = NSObject("NSString").stringWithUTF8String_(b"public.utf8-plain-text")
        clipboardString = NSObject("NSPasteboard").generalPasteboard().stringForType_(pasteboardStringType)

        if clipboardString:
            return clipboardString.UTF8String().decode('utf8')
        else:
            return "No string found in clipboard."
