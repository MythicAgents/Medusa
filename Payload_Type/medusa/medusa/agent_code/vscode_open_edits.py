    def vscode_open_edits(self, task_id, backups_path=""):
        import os, json
        import time

        path = backups_path if backups_path else "/Users/{}/Library/Application Support/Code/Backups".format(os.environ["USER"])

        if not os.path.exists(path):
            return "VSCode backups folder does not exist!"

        open_edits = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file != ".DS_Store" and file != "workspaces.json":
                    open_edit = {}
                    path = os.path.join(root, file)
                    with open(path, "r") as f:
                        file_content = f.readlines()
                        json_data = json.loads("{" + file_content[0].split("{")[1].rstrip())
                        if os.path.basename(root) == "untitled":
                            open_edit["backup"] = path
                            open_edit["original"] = file_content[0].split("{")[0].replace("untitled:","").rstrip()
                            open_edit["size"] = ""
                            open_edit["mtime"] = ""
                            open_edit["ctime"] = ""
                            open_edit["type"] = "New"
                        else:
                            open_edit["backup"] = path
                            open_edit["original"] = file_content[0].split("{")[0].replace("file://","").rstrip()
                            open_edit["size"] = f"{json_data['size']} B"
                            open_edit["mtime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(json_data["mtime"]/1000))
                            open_edit["ctime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(json_data["ctime"]/1000))
                            open_edit["type"] = "Edit"
                    open_edits.append(open_edit)
        return { "edits" : open_edits }
