function(task, responses){
  if(task.status.includes("error")){
      const combined = responses.reduce( (prev, cur) => {
          return prev + cur;
      }, "");
      return {'plaintext': combined};
  }else if(task.completed){
      if(responses.length == 1){
          var auth_values = [
            "Access Denied", 
            "Unknown",
            "Allowed",
            "Limited"
          ];
      
          var auth_reason = [
            "Error",
            "User Consent",
            "User Set",
            "System Set",
            "Service Policy",
            "MDM Policy",
            "Override Policy",
            "Missing usage string",
            "Prompt Timeout",
            "Preflight Unknown",
            "Entitled",
            "App Type Policy",
          ];
      
          var client_type = [
            "Bundle Identifier",
            "Absolute Path"
          ];

          try{
                  let data = JSON.parse(responses[0].replace((new RegExp("'", 'g')), '"'));
                  let entries = data["tcc"];
                  let output_table = [];
                  for(let i = 0; i < entries.length; i++){
                      
                      let clienttype = client_type[entries[i]['client_type']];
                      let authval = auth_values[entries[i]['auth_value']];
                      let authres = auth_reason[entries[i]['auth_reason']];

                      output_table.push({
                          "Client":{"plaintext": entries[i]["client"]},
                          "Service":{"plaintext": entries[i]["service"]},
                          "Client Type":  { "plaintext": clienttype },
                          "Auth Value":  { "plaintext": authval },
                          "Auth Reason":  { "plaintext": authres },
                          "Last Modified": { "plaintext": new Date(entries[i]['last_modified'] * 1000).toString() },
                          "actions": {"button": {
                            "name": "Actions",
                            "type": "menu",
                            "value": [
                                    {
                                        "name": "View All Data",
                                        "type": "dictionary",
                                        "value": entries[i],
                                        "leftColumnTitle": "Field",
                                        "rightColumnTitle": "Value",
                                        "title": "Viewing All Data"
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
                                  {"plaintext": "Client", "type": "string", "fillWidth": true},
                                  {"plaintext": "Service", "type": "string", "fillWidth": true},
                                  {"plaintext": "Client Type", "type": "string", "width": 160},
                                  {"plaintext": "Auth Value", "type": "string", "width": 130},
                                  {"plaintext": "Auth Reason", "type": "string", "width": 135},
                                  {"plaintext": "Last Modified", "type": "string", "width": 285},
                                  {"plaintext": "actions", "type": "button", "width": 90, "disableSort": true},
                              ],
                              "rows": output_table,
                              "title": "TCC"
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