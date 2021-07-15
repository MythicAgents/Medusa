function(task, response){
  var rows = [];

  auth_values = [
    "Access Denied", 
    "Unknown",
    "Allowed",
    "Limited"
  ];

  auth_reason = [
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

  client_type = [
    "Bundle Identifier",
    "Absolute Path"
  ];

  var uniqueName = task.id + "_csreq_info_modal";

  for(var i = 0; i < response.length; i++){
    try{
        var data = JSON.parse(response[i]['response'].replace((new RegExp("'", 'g')), '"'));
    }catch(error){
      var msg = "Unhandled exception in tcc.js for " + task.command + " (ID: " + task.id + "): " + error;
      console.error(msg);
        return response[i]['response'];
    }

    var entries = data['tcc'];

    var row_style = "";
    var cell_style = {
      "service":"max-width:0;",
      "client":"max-width:0;",
      "client type":"max-width:0;",
      "auth value":"max-width:0;",
      "auth reason":"max-width:0;",
      "auth version":"max-width:0;",
      "csreq":"max-width:0;",
      "policy id":"max-width:0;",
      "indirect object identifier type":"max-width:0;",
      "indirect object identifier":"max-width:0;",
      "indirect object code identity":"max-width:0;",
      "flags":"max-width:0;",
      "last modified":"max-width:0;"
    };
    for (var j = 0; j < entries.length; j++)
    {
      var additionalInfo = btoa(entries[j]['client']) + "|" + btoa(entries[j]['service']) + "|" + btoa(entries[j]['csreq']);
      copycsreqicon = '<i class="fas fa fa-clipboard" data-toggle="tooltip" title="Copy base64 csreq to clipboard" additional-info=' + btoa(entries[j]['csreq']) + ' style="cursor: pointer;" onclick=support_scripts[\"medusa_copy_additional_info_to_clipboard\"](this)></i>';   
      copycodeidenticon = '<i class="fas fa fa-clipboard" data-toggle="tooltip" title="Copy base64 indirect object code identity to clipboard" additional-info=' + btoa(entries[j]['indirect_object_code_identity']) + ' style="cursor: pointer;" onclick=support_scripts[\"medusa_copy_additional_info_to_clipboard\"](this)></i>';   

      rows.push({
        "service":entries[j]['service'],
        "client":entries[j]['client'],
        "client type": client_type[entries[j]['client_type']],
        "auth value": auth_values[entries[j]['auth_value']],
        "auth reason": auth_reason[entries[j]['auth_reason']],
        "auth version": entries[j]['auth_version'],
        "csreq": ((entries[j]['csreq'] == 'None') ? '-' : copycsreqicon),
        "policy id": ((entries[j]['policy_id'] == 'None') ? '-' : entries[j]['policy_id']),
        "indirect object identifier type": ((entries[j]['indirect_object_identifier_type'] == 'None') ? '-' : entries[j]['indirect_object_identifier_type']),
        "indirect object identifier": ((entries[j]['indirect_object_identifier'] == 'UNUSED') ? '-' : entries[j]['indirect_object_identifier']),
        "indirect object code identity": ((entries[j]['indirect_object_code_identity'] == 'None') ? '-' : copycodeidenticon),
        "flags": ((entries[j]['flags'] == 'None') ? '-' : entries[j]['flags']),
        "last modified": new Date(entries[j]['last_modified'] * 1000),
        "row-style": row_style,
        "cell-style": cell_style
      });
    }
    var output = support_scripts['medusa_create_table']([
      {"name":"service", "size":"30em"},
      {"name":"client", "size":"6em"},
      {"name":"client type", "size":"8em"},
      {"name":"auth value", "size":"8em"},
      {"name":"auth reason", "size":"8em"},
      {"name":"auth version", "size":"8em"},
      {"name":"csreq", "size":"8em"},
      {"name":"policy id", "size":"8em"},
      {"name":"indirect object identifier type", "size":"8em"},
      {"name":"indirect object identifier", "size":"8em"},
      {"name":"indirect object code identity", "size":"8em"},
      {"name":"flags", "size":"8em"},
      {"name":"last modified", "size":"8em"}
    ], rows);
    return output;
}
}