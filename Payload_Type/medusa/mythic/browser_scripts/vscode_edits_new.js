function(task, responses){
  if(task.status.includes("error")){
      const combined = responses.reduce( (prev, cur) => {
          return prev + cur;
      }, "");
      return {'plaintext': combined};
  }else if(task.completed){
      if(responses.length == 1){
          try{

            let folder = {
                backgroundColor: "mediumpurple",
                color: "white"
              };
            let file = {};

            let data = JSON.parse(responses[0].replace((new RegExp("'", 'g')), '"'));
            let entries = data["edits"];
            let output_table = [];
            
            for(let i = 0; i < entries.length; i++){

                output_table.push({
                    "Backup File":{ "plaintext": entries[i]["backup"], "copyIcon": true },
                    "Original File":{ "plaintext": entries[i]["original"] },
                    "Size":{ "plaintext": entries[i]["size"] },
                    "Modified Time":{ "plaintext": entries[i]["mtime"] },
                    "Created Time":{ "plaintext": entries[i]["ctime"] },
                    "Type":{ "plaintext": entries[i]["type"] },
                    "rowStyle": {},
                })
            }
            return {
                "table": [
                    {
                        "headers": [
                            {"plaintext": "Backup File", "type": "string", "fillWidth": true},
                            {"plaintext": "Original File", "type": "string", "fillWidth": true},
                            {"plaintext": "Size", "type": "string", "width": 80},
                            {"plaintext": "Modified Time", "type": "string", "width": 200},
                            {"plaintext": "Created Time", "type": "string", "width": 200},
                            {"plaintext": "Type", "type": "string", "width": 80},
                        ],
                        "rows": output_table,
                        "title": "Unsaved VSCode Edits"
                    }
                ]
            }
          }catch(error){
                  console.log(error);
                  const combined = responses.reduce( (prev, cur) => {
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