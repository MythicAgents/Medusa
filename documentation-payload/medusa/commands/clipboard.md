+++
title = "clipboard"
chapter = false
weight = 100
hidden = false
+++

## Summary

Get all the types of contents on the clipboard, return specific types, or set the contents of the clipboard. 

{{% notice warning %}}
 Root does _*NOT*_ have a clipboard
{{% /notice %}}
 
- Needs Admin: False  
- Version: 1
- Author: @ajpc500

### Reading Clipboard

```
clipboard
```
This will read the plaintext data on the clipboard only. Any non-text content will be omitted.

## MITRE ATT&CK Mapping

- T1115  

## Detailed Summary

This uses Objective C API calls to read all the types available on the general clipboard for the current user. The clipboard on macOS has a lot more data than _just_ what you copy. All of that data is collected and returned in a JSON blob of key:base64(data). To do this, we use this JavaScript code:
```JavaScript
let pb = $.NSPasteboard.generalPasteboard;
let types = pb.types.js;
let clipboard = {};
for(let i = 0; i < types.length; i++){
    let typejs = types[i].js;
    clipboard[typejs] = pb.dataForType(types[i]);
    if(clipboard[typejs].js !== undefined){
        clipboard[typejs] = clipboard[typejs].base64EncodedStringWithOptions(0).js;
    }else{
        clipboard[typejs] = "";
    }
}
```
There's a browserscript for this function that'll return all of the keys and the plaintext data if it's there.
