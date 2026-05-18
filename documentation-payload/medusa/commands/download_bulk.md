+++
title = "download_bulk"
chapter = false
weight = 100
hidden = false
+++

## Summary

Bulk download file(s), director(ies), or a mix from the target machine.

Two modes are supported:

- **archive** *(default)*: all files are bundled into a single in-memory zip archive that is streamed back to the Mythic server. The archive is never written to disk on the target.
- **iterative**: each file is transferred individually using the same chunked approach as the `download` command.

The command automatically detects whether each supplied path is a file or a directory. When a directory is specified, all files within it (recursively) are included. Files that do not exist or are not accessible are skipped rather than causing the entire task to fail.

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False
- Version: 1
- Author: @maclarel

### Arguments

#### path

- Description: An array of file or directory paths to download. Multiple entries can be added through the Mythic UI or provided as a JSON array.
- Required Value: True
- Default Value: None

#### mode

- Description: `archive` (default) to bundle everything into a single in-memory zip, or `iterative` to transfer each file individually.
- Required Value: False
- Default Value: `archive`

## Usage

Download an entire directory as a zip archive (default mode):

```
download_bulk {"path": ["/remote/directory"], "mode": "archive"}
```

Download a single file using archive mode:

```
download_bulk {"path": ["/remote/path/to/file.txt"]}
```

Download multiple specific files iteratively:

```
download_bulk {"path": ["/remote/file1.txt", "/remote/file2.txt"], "mode": "iterative"}
```

Download a directory, sending each file individually:

```
download_bulk {"path": ["/remote/directory"], "mode": "iterative"}
```

## MITRE ATT&CK Mapping

- T1020
- T1030
- T1041

## Detailed Summary

The `download_bulk` function extends the single-file `download` capability to support bulk transfers.

### Path detection

The `path` argument accepts an array of paths. Each entry is resolved using `os.path.isdir` and `os.path.isfile`. Relative paths are resolved against the agent's current working directory:

- **Directory** – the directory tree is walked with `os.walk`; every file found is added to the transfer list.
- **File** – added directly to the transfer list.
- **Non-existent** – skipped with a warning message; the task continues with remaining files.

### Archive mode

An in-memory `zipfile.ZipFile` (backed by `io.BytesIO`) is created and populated with all target files. The zip data is then chunked and sent to the Mythic server using the same `download` API used by the single-file `download` command.

Note: This can be extremely slow to transfer larger amounts of data due to chunking. Expect to take a walk or a nap if you're trying to pull thousands of files/hundreds of MB of data.

Directory structure is preserved inside the zip using `os.path.relpath` to compute each entry's arcname:

- **Directory input** (e.g. `/etc/nginx`): entries are anchored at the parent directory, so the top-level name is included — `nginx/nginx.conf`, `nginx/conf.d/default.conf`.
- **Single file input**: only the filename is stored (`passwd`).
- **Explicit list input**: entries are anchored at the filesystem root, preserving the full path — `etc/passwd`, `home/user/report.txt`.

### Iterative mode

Each file is transferred individually in the same chunked manner as the existing `download` command. A separate `file_id` is obtained from Mythic for each file, and the agent streams each one to completion before moving on to the next.

```Python
    def download_bulk(self, task_id, path, mode="archive"):
        import zipfile, io

        # Build file list from path array (files, directories, or mix)
        ...

        if mode == "iterative":
            for file_path in file_list:
                # chunk and send each file (same as download())
                ...
        else:
            # Build in-memory zip
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in file_list:
                    zf.write(file_path, arcname)
            # chunk and send zip_buffer.getvalue()
            ...
```
