function(task, response){
  if(task.status.includes("error")){
      const combined = response.reduce( (prev, cur) => {
          return prev + cur;
      }, "");
      return {'plaintext': combined};
  }else if(task.completed){
      if(response.length > 0){
          try{
                  let data = JSON.parse(response[0].replace((new RegExp("'", 'g')), '"'));
                  let entries = data["processes"];
                  let output_table = [];

                  for(let i = 0; i < entries.length; i++){
                    output_table.push({
                          "PID":{"plaintext": entries[i]["process_id"] },
                          "Name":{"plaintext": ((!"name" in entries[i]) ? ' ' : entries[i]['name']) },
                          "Arch":{"plaintext": ((!"architecture" in entries[i]) ? ' ' : entries[i]['architecture']) },
                          "Bin Path":{"plaintext": ((!"bin_path" in entries[i]) ? ' ' : entries[i]['bin_path']) },
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
                      })
                  }
                  return {
                      "table": [
                          {
                              "headers": [
                                {"plaintext": "PID", "type": "string","width": 90,"disableSort": true},
                                {"plaintext": "Name", "type": "string", "fillWidth": true},
                                {"plaintext": "Arch", "type": "string", "width": 70},
                                {"plaintext": "Bin Path", "type": "string", "fillWidth": true},
                                {"plaintext": "actions", "type": "button", "width": 90, "disableSort": true},
                                ],
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