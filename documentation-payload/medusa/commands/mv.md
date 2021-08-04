+++
title = "mv"
chapter = false
weight = 100
hidden = false
+++

## Summary

Move a given file or folder to a specified location. No quotes are necessary and relative paths are fine 

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

### Arguments

#### source_path

- Description: path of file/folder to move
- Required Value: True  
- Default Value: None  

#### dest_path

- Description: path to move file/folder to  
- Required Value: True  
- Default Value: None  

## Usage

### Without Popup Option
```
mv path/of/file_or_folder /dest/to/move/to 
```

## Detailed Summary
You can either type `mv` and get a popup to fill in the paths, or provide the paths on the command line. 

```Python
    def mv(self, task_id, source, destination):
        import shutil
        source_path = source if source[0] == os.sep \
                else os.path.join(self.current_directory,source)
        dest_path = destination if destination[0] == os.sep \
                else os.path.join(self.current_directory,destination)
        shutil.move(source_path, dest_path)

```
