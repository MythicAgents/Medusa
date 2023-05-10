function(task, responses){
  if(task.status.includes("error")){
      const combined = responses.reduce( (prev, cur) => {
          return prev + cur;
      }, "");
      return {'plaintext': combined};
  }else if(task.completed){
      if(responses.length == 1){
          try{
                  let data = JSON.parse(responses[0].replace((new RegExp("'", 'g')), '"'));
                  let entries = data["apps"];
                  let output_table = [];
                  for(let i = 0; i < entries.length; i++){
                      output_table.push({
                          "PID":{"plaintext": entries[i]["pid"]},
                          "Name":{"plaintext": entries[i]["name"]},
                          "Executable URL":{"plaintext": entries[i]["exec_url"], "copyIcon": true},
                          "rowStyle": {}
                      })
                  }
                  return {
                      "table": [
                          {
                              "headers": [
                                  {"plaintext": "PID", "type": "string"},
                                  {"plaintext": "Name", "type": "string","width": 180},
                                  {"plaintext": "Executable URL", "type": "string"},
                              ],
                              "rows": output_table,
                              "title": "Apps"
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