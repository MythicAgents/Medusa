+++
title = "cp"
chapter = false
weight = 100
hidden = false
+++

## Summary

Copy a given file or folder to a specified location. No quotes are necessary and relative paths are fine 

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

### Arguments

#### source_path

- Description: path of file/folder to copy
- Required Value: True  
- Default Value: None  

#### dest_path

- Description: path to copy file/folder to  
- Required Value: True  
- Default Value: None  

## Usage

### Without Popup Option
```
cp path/of/file_or_folder /dest/to/copy/to 
```

## Detailed Summary
You can either type `cp` and get a popup to fill in the paths, or provide the paths on the command line. 

```Python
    def cp(self, task_id, source, destination):
        import shutil

        source_path = source if source[0] == os.sep \
                else os.path.join(self.current_directory,source)

        dest_path = destination if destination[0] == os.sep \
                else os.path.join(self.current_directory,destination)

        if os.path.isdir(source_path):
            shutil.copytree(source_path, dest_path)
        else:
            shutil.copy(source_path, dest_path)
```
