function(task, response){
  var rows = [];

  for(var i = 0; i < response.length; i++){
    try{
        var data = JSON.parse(response[i]['response'].replace((new RegExp("'", 'g')), '"'));
    }catch(error){
      var msg = "Unhandled exception in list_apps.js for " + task.command + " (ID: " + task.id + "): " + error;
      console.error(msg);
        return response[i]['response'];
    }

    var entries = data['apps'];

    var row_style = "";
    var cell_style = {
      "PID":"max-width:0;",
      "Name":"max-width:0;",
      "Executable URL":"max-width:0;"
    };
    for (var j = 0; j < entries.length; j++)
    {
      rows.push({
        "PID": entries[j]["pid"],
        "Name": entries[j]["name"],
        "Executable URL": entries[j]["exec_url"],
        "row-style": row_style,
        "cell-style": cell_style
      });
    }
    var output = support_scripts['medusa_create_table']([
      {"name":"PID", "size":"5em"},
      {"name":"Name", "size":"10em"},
      {"name":"Executable URL", "size":"15em"}
    ], rows);
    return output;
}
}