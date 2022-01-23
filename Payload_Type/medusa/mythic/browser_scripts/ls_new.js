function(task, response){
  
  if(task.status.includes("error")){
    const combined = response.reduce( (prev, cur) => {
        return prev + cur;
    }, "");
    return {'plaintext': combined};
  }else if(task.completed && response.length > 0){

    // tables styles
    let folder = {
      backgroundColor: "mediumpurple",
      color: "white"
    };
    let file = {};

    var archiveFormats = [".a",".ar",".cpio",".shar",".LBR",".lbr",".mar",".sbx",".tar",".bz2",".F",".gz",".lz",".lz4",".lzma",".lzo",".rz",".sfark",".sz",".?Q?",".?Z?",".xz",".z",".Z",".zst",".??",".7z",".s7z",".ace",".afa",".alz",".apk",".arc",".arc",".arj",".b1",".b6z",".ba",".bh",".cab",".car",".cfs",".cpt",".dar",".dd",".dgc",".ear",".gca",".ha",".hki",".ice",".jar",".kgb",".lzh",".lzx",".pak",".pak",".parti",".paq6",".pea",".pim",".pit",".qda",".rar",".rk",".sda",".sea",".sen",".sfx",".shk",".sit",".sitx",".sqx",".tar",".tbz2",".uc",".uca",".uha",".war",".wim",".xar",".xp3",".yz1",".zip",".zoo",".zpaq",".zz",".ecc",".ecsbx",".par",".par2",".rev"];
    var diskImages = [".dmg", ".iso", ".vmdk"];
    var wordDocs = [".doc", ".docx", ".dotm", ".dot", ".wbk", ".docm", ".dotx", ".docb"];
    var excelDocs = [".xls", ".xlsx", ".xlsm", ".xltx", ".xltm", ".xlmx", ".xlmt"];
    var powerPoint = [".ppt", ".pptx", ".potx", ".ppsx", ".thmx", ".pot", ".pps"];
    var pdfExt = [".pdf"];
    var dbExt = [".db", ".sql", ".psql"];
    var keyFiles = [".pem", ".ppk"];
    var scriptFiles = [".config", ".ps1", ".psm1", ".psd1", ".vbs", ".js", ".py", ".pl", ".rb", ".go", ".xml", ".html", ".css", ".sh", ".bash", ".yaml", ".yml"];
    // var uniqueName = task.id + "_additional_permission_info_modal";
    
    let rows = [];
    let data = "";

    try{
      data = JSON.parse(response[0].replace((new RegExp("'", 'g')), '"').replace((new RegExp("True", 'g')), 'true').replace((new RegExp("False", 'g')), 'false'));
    }catch(error){
      const combined = response.reduce( (prev, cur) => {
          return prev + cur;
      }, "");
      return {'plaintext': combined};
    }
    
    let headers = [
      {"plaintext": "name", "type": "string", "fillWidth": true},
      {"plaintext": "size", "type": "size", "width": 185},
      {"plaintext": "last_accessed", "type": "string", "width": 285},
      {"plaintext": "last_modified", "type": "string", "width": 285},
      {"plaintext": "actions", "type": "button", "width": 90, "disableSort": true},
    ];

    

    for(let i = 0; i < data["files"].length; i++){
      let ls_path = "";
      let sep = data["parent_path"].includes("/") ? "/": "\\";

      if(data["parent_path"] === "/"){
          ls_path = data["parent_path"] + data["name"] + sep + data["files"][i]["name"];
      }else{
          ls_path = data["parent_path"] + sep + data["name"] + sep + data["files"][i]["name"];
      }
      
      var icon = "";
      if (data["files"][i]["is_file"] ===  true) {
        var fileExt = "." + data["files"][i]['name'].split(".").slice(-1)[0].toLowerCase();
        
        if (archiveFormats.includes(fileExt)) {
          icon = 'archive/zip';
        } else if (diskImages.includes(fileExt)) {
          icon = 'diskimage';
        } else if (wordDocs.includes(fileExt)) {
          icon = 'word';
        } else if (excelDocs.includes(fileExt)){
          icon = 'excel';
        } else if (powerPoint.includes(fileExt)) {
          icon = 'powerpoint';
        } else if (pdfExt.includes(fileExt)){
          icon = 'pdf/adobe';
        } else if (dbExt.includes(fileExt)) {
          icon = 'database';
        } else if (keyFiles.includes(fileExt)) {
          icon = 'key';
        } else if (scriptFiles.includes(fileExt)) {
          icon = 'code/source';
        } else {
          icon = 'code/source';
        }
      } else {
        icon = 'closedFolder';
      }

      let row = {
          "rowStyle": data["files"][i]["is_file"] ? file:  folder,
          "name": {
            "plaintext": data["files"][i]["name"],
            "startIcon": icon
          },
          "size": {"plaintext": data["files"][i]["size"]},
          "last_accessed": {"plaintext": data["files"][i]["access_time"]},
          "last_modified": {"plaintext": data["files"][i]["modify_time"]},
          "actions": {"button": {
          "name": "Actions",
          "type": "menu",
          "value": [
                  {
                      "name": "View XATTRs",
                      "type": "dictionary",
                      "value": data["files"][i]["permissions"],
                      "leftColumnTitle": "XATTR",
                      "rightColumnTitle": "Values",
                      "title": "Viewing XATTRs"
                  },
                  {
                      "name": "LS Path",
                      "type": "task",
                      "ui_feature": "file_browser:list",
                      "parameters": ls_path
                  },
                  {
                    "name": "Download File",
                    "type": "task",
                    "disabled": !data["files"][i]["is_file"],
                    "ui_feature": "file_browser:download",
                    "parameters": ls_path
                  }
              ]
          }}
      };
      rows.push(row);
    }

    return {"table":[{
      "headers": headers,
      "rows": rows,
      "title": "File Listing Data"
    }]};

  }
  else if(task.status === "processed"){
    // this means we're still downloading
    return {"plaintext": "Only have partial data so far..."}
  }else{
    // this means we shouldn't have any output
    return {"plaintext": "Not response yet from agent..."}
}
  

}