function(task, response){
  var rows = [];

  for(var i = 0; i < response.length; i++){
    try{
        var data = JSON.parse(response[i]['response'].replace((new RegExp("'", 'g')), '"'));
    }catch(error){
      var msg = "Unhandled exception in jobs.js for " + task.command + " (ID: " + task.id + "): " + error;
      console.error(msg);
        return response[i]['response'];
    }

    var entries = data['jobs'];

    var row_style = "";
    var cell_style = {
      "task id":"max-width:0;",
      "command":"max-width:0;"
    };
    for (var j = 0; j < entries.length; j++)
    {
      copy_taskid_icon = '<i class="fas fa fa-clipboard" data-toggle="tooltip" title="Copy task id to clipboard" additional-info=' + btoa(entries[j][1]) + ' style="cursor: pointer;" onclick=support_scripts[\"medusa_copy_additional_info_to_clipboard\"](this)></i>';   
      
      rows.push({
        "": copy_taskid_icon,
        "task id":entries[j][1],
        "command":entries[j][0],
        "row-style": row_style,
        "cell-style": cell_style
      });
    }
    var output = support_scripts['medusa_create_table']([
      {"name":"", "size":"1em"},
      {"name":"task id", "size":"15em"},
      {"name":"command", "size":"6em"}
    ], rows);
    return output;
}
}