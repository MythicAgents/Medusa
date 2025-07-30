function(task, responses){
  if(task.status.includes("error")){
      const combined = responses.reduce( (prev, cur) => {
          return prev + cur;
      }, "");
      return {'plaintext': combined};
  }else if(task.completed){
      if(responses.length == 1){
          try{
                  let data = JSON.parse(responses[0]);
                  let output = '';

                  output += "stdout/err:\n";

                  if(data["stdout"] && data["stdout"].length > 0){
                    output += data["stdout"];
                  } else {
                    output += "No stdout output\n";
                  }

                  output += "\reval return:\n";

                    if(data["result"] && data["result"].length > 0){
                      output += data["result"];
                    } else {
                      output += "No return value\n";
                    }
                    
                  return {
                      "plaintext": output,                  
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