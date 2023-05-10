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
                  let entries = data["dlls"];
                  let output_table = [];
                  for(let i = 0; i < entries.length; i++){
                      output_table.push({
                          "DLL":{"plaintext": entries[i], "copyIcon": true},
                          "rowStyle": {}
                      })
                  }
                  return {
                      "table": [
                          {
                              "headers": [
                                  {"plaintext": "DLL", "type": "string"},
                              ],
                              "rows": output_table,
                              "title": "Loaded DLLs"
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