function(task, responses){
    if(task.status.includes("error")){
        const combined = responses.reduce( (prev, cur) => {
            return prev + cur;
        }, "");
        return {'plaintext': combined};
    } else if(task.completed){
        if(responses.length === 0){
            return {'plaintext': 'No response from agent.'};
        }
        // Iterative mode returns one JSON object per file, one per line.
        // Archive mode returns a single JSON object with agent_file_id.
        const lines = responses[0].split('\n').filter(l => l.trim().length > 0);
        let downloads = [];
        let plainLines = [];
        for(let i = 0; i < lines.length; i++){
            try{
                let data = JSON.parse(lines[i].replace((new RegExp("'", 'g')), '"'));
                if("agent_file_id" in data){
                    let label = "file_path" in data
                        ? "Download " + data["file_path"]
                        : "Download " + task["display_params"];
                    downloads.push({
                        "agent_file_id": data["agent_file_id"],
                        "variant": "contained",
                        "name": label
                    });
                } else {
                    plainLines.push(lines[i]);
                }
            } catch(error){
                plainLines.push(lines[i]);
            }
        }
        if(downloads.length > 0){
            let result = {"download": downloads};
            if(plainLines.length > 0){
                result["plaintext"] = plainLines.join('\n');
            }
            return result;
        }
        return {'plaintext': responses[0]};
    } else if(task.status === "processed"){
        if(responses.length > 0){
            try{
                const task_data = JSON.parse(responses[0]);
                if("total_chunks" in task_data){
                    return {"plaintext": "Downloading with " + task_data["total_chunks"] + " total chunks..."};
                }
            } catch(error){}
            return {"plaintext": responses[0]};
        }
        return {"plaintext": "No data yet..."};
    } else {
        return {"plaintext": "No response yet from agent..."};
    }
}
