function(task, responses){
  if(task.status.includes("error")){
      const combined = responses.reduce( (prev, cur) => {
          return prev + cur;
      }, "");
      return {'plaintext': combined};
  }else if(task.completed){
      if(responses.length > 0){
          try{
                  let data = JSON.parse(responses[0].replace((new RegExp("'", 'g')), '"'));
                  let entries = data["jobs"];
                  let output_table = [];
                  for(let i = 0; i < entries.length; i++){
                      output_table.push({
                          "command":{"plaintext": entries[i][0]},
                          "task_id": {"plaintext": entries[i][1], "copyIcon": true},
                          "rowStyle": {"backgroundColor": "mediumpurple"}
                      })
                  }
                  return {
                      "table": [
                          {
                              "headers": [
                                  {"plaintext": "command", "type": "string", "fillWidth": true},
                                  {"plaintext": "task_id", "type": "string", "fillWidth": true},
                              ],
                              "rows": output_table,
                              "title": "Running Jobs"
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