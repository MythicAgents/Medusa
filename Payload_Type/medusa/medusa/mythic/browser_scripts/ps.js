function(task, response){
    if(task.status.includes("error")){
        const combined = response.reduce( (prev, cur) => {
            return prev + cur;
        }, "");
        return {'plaintext': combined};
    }else if(task.completed){
        if(response.length > 0){
            try{
                    let data = JSON.parse(response[0]);
                    let entries = data["processes"];
                    let output_table = [];
                    
                    // Check which fields are present in any entry
                    let fieldPresent = {
                        "user_id": false,
                        "parent_process_id": false,
                        "name": false,
                        "architecture": false,
                        "bin_path": false
                    };
                    
                    // Scan all entries to determine which fields exist in the dataset
                    for(let i = 0; i < entries.length; i++){
                        if ("user_id" in entries[i]) fieldPresent["user_id"] = true;
                        if ("parent_process_id" in entries[i]) fieldPresent["parent_process_id"] = true;
                        if ("name" in entries[i]) fieldPresent["name"] = true;
                        if ("architecture" in entries[i]) fieldPresent["architecture"] = true;
                        if ("bin_path" in entries[i]) fieldPresent["bin_path"] = true;
                    }
                    
                    // Create rows based on available fields
                    for(let i = 0; i < entries.length; i++){
                        let row = {
                            "PID": {"plaintext": String(entries[i]["process_id"])},
                            "actions": {"button": {
                              "name": "Actions",
                              "type": "menu",
                              "value": [
                                      {
                                          "name": "List DLLs",
                                          "type": "task",
                                          "ui_feature": "process_dlls:list",
                                          "parameters": { "process_id": entries[i]["process_id"] }
                                      },
                                  ]
                              }},
                            "rowStyle": {}
                        };
                        
                        // Only add fields that exist in at least one entry
                        if (fieldPresent["user_id"]) {
                            row["UID"] = {"plaintext": "user_id" in entries[i] ? String(entries[i]['user_id']) : " "};
                        }
                        
                        if (fieldPresent["parent_process_id"]) {
                            row["PPID"] = {"plaintext": "parent_process_id" in entries[i] ? String(entries[i]['parent_process_id']) : " "};
                        }
                        
                        if (fieldPresent["name"]) {
                            row["Name"] = {"plaintext": ("name" in entries[i]) ? entries[i]['name'] : " "};
                        }
                        
                        if (fieldPresent["architecture"]) {
                            row["Arch"] = {"plaintext": ("architecture" in entries[i]) ? entries[i]['architecture'] : " "};
                        }
                        
                        if (fieldPresent["bin_path"]) {
                            row["Bin Path"] = {"plaintext": ("bin_path" in entries[i]) ? entries[i]['bin_path'] : " "};
                        }
                        
                        output_table.push(row);
                    }
                    
                    // Create headers based on available fields
                    let headers = [
                        {"plaintext": "PID", "type": "string", "width": 90, "disableSort": true},
                    ];
                    
                    // Only add headers for fields that exist in at least one entry
                    if (fieldPresent["user_id"]) {
                        headers.unshift({"plaintext": "UID", "type": "string", "width": 90, "disableSort": true});
                    }
                    
                    if (fieldPresent["parent_process_id"]) {
                        headers.push({"plaintext": "PPID", "type": "string", "width": 90, "disableSort": true});
                    }
                    
                    if (fieldPresent["name"]) {
                        headers.push({"plaintext": "Name", "type": "string", "width": 300});
                    }
                    
                    if (fieldPresent["architecture"]) {
                        headers.push({"plaintext": "Arch", "type": "string", "width": 70});
                    }
                    
                    if (fieldPresent["bin_path"]) {
                        headers.push({"plaintext": "Bin Path", "type": "string", "fillWidth": true});
                    }
                    
                    // Add actions header at the end
                    headers.push({"plaintext": "actions", "type": "button", "width": 90, "disableSort": true});
                    
                    return {
                        "table": [
                            {
                                "headers": headers,
                                "rows": output_table,
                                "title": "Running processes"
                            }
                        ]
                    }
            }catch(error){
                    console.log(error);
                    const combined = response.reduce( (prev, cur) => {
                        return prev + cur;
                    }, "");
                    return {'plaintext': combined};
            }
        }else{
            return {"plaintext": "No output from command"};
        }
    }else{
        return {"plaintext": "No data to display..."};
    }
  }