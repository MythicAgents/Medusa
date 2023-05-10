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
            let entries = data["recents"];
            let output_table = [];
            
            for(let i = 0; i < entries.length; i++){

                var icon = "";
                var rs = {};

                if (entries[i]["type"] == "folder") {
                    icon = 'closedFolder';
                    rs = folder;
                } else {
                    icon = 'code/source';
                    rs = file;
                }

                

                output_table.push({
                    "Name":{
                        "plaintext": entries[i]["path"],
                        "startIcon": icon
                    },
                    "rowStyle": rs,
                })
            }
            return {
                "table": [
                    {
                        "headers": [
                            {"plaintext": "Name", "type": "string", "fillWidth": true},
                        ],
                        "rows": output_table,
                        "title": "Recent VSCode Files"
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