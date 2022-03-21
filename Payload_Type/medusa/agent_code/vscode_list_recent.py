    def vscode_list_recent(self, task_id, db=""):
        import os, sqlite3, json
        
        path = db if db else "/Users/{}/Library/Application Support/Code/User/globalStorage/state.vscdb".format(os.environ["USER"])
        recent_files = []

        if not os.path.exists(path):
            return "VSCode State database path does not exist!"

        with sqlite3.connect(path) as con:
            for row in con.execute('SELECT * FROM "ItemTable" WHERE KEY = "history.recentlyOpenedPathsList"'):
                data = json.loads(row[1])
                for entry in data["entries"]:
                    recent_file = {}
                    if "folderUri" in entry:
                        recent_file["path"] = entry["folderUri"].replace("file://", "")
                        recent_file["type"] = "folder"
                    elif "fileUri" in entry:
                        recent_file["path"] = entry["fileUri"].replace("file://", "")
                        recent_file["type"] = "file"
                    recent_files.append(recent_file)
        return { "recents": recent_files }
