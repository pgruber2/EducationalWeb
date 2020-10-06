var hideExp = function(){
    $("#docs-div").empty();
    $("#helpfulButton").css("display", "none");
     $("#notHelpfulButton").css("display", "none");
     helpBut = document.getElementById('helpfulButton');
     notHelpBut = document.getElementById('notHelpfulButton');
     helpBut.removeEventListener("click", logExp, true); 

     helpBut.removeEventListener("click", logExp, true); 
      notHelpBut.removeEventListener("contextmenu", logExp, true); 
     notHelpBut.removeEventListener("contextmenu", logExp, true); 
}

var docDiv = (doc,searchString) => {
    console.log('bb',doc)
    return(`<div class="card">
     <div class="card-header">
<div style="display: flex;justify-content: space-between;">


         <b style="font-size:14pt;margin-left: 10px;
    padding: 10px;">Explanation of \"${searchString}\"</b>
    <span id="close" style="cursor:pointer;float:right;background:transparent;display:inline-block;
    padding:4px; margin:10px; font-size: 12pt; font-weight: bold;" onclick="hideExp()">X</span>
</div>
</div>
      <div class="card-body">
        <span id='explain_div' style= "display:inline-block; 
    margin:10px;
    padding:10px;
    word-break:break-all;">${doc}</span>
        <br>
    </div>
    </div>`
        );
   
}



var test = function(){
    return "blah";
}

// var socket = io.connect('http://' + document.domain + ':' + location.port);
// console.log("io",io)

$(document).ready(function(){
var socket = io()
socket.connect('http://localhost:8096/', {transports: ['websocket']});

socket.on('message', function(searchString) {
    console.log("1")
    console.log(searchString)
                 doSearch(searchString);
            });
});

var logExp = function(isHelpful,expId,expTerm){
    logdata = JSON.stringify({
            action: isHelpful+'###EXP_###'+expTerm+'###'+expId,
            route: window.location.pathname
          });
            navigator.sendBeacon('http://localhost:8096/log_action', logdata);
         
}
var doSearch = function(searchString) {
    const data = {
        "searchString": searchString,
    }
    console.log("2")
    console.log(searchString)
    if (searchString!='')
    {
       
    var num_fetched_res = 0
    fetch("http://localhost:8096/search", {
    // fetch("http://expertsearch.centralus.cloudapp.azur`1e.com/search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    }).then(response => {
        response.json().then(data => {
            console.log("bbb",data)
            
            const doc = data.explanation;
            
            $("#docs-div").empty();
            if (data.num_results==1){
                $("#docs-div").append(
                    docDiv(doc,searchString)
                );
            
          
            $("#helpfulButton").css("display", "block");
            $("#notHelpfulButton").css("display", "block");

     helpBut = document.getElementById('helpfulButton');
     notHelpBut = document.getElementById('notHelpfulButton');
      helpBut.addEventListener('click', function() {
          logExp('1',data.file_names,searchString);
      } , true);

      helpBut.addEventListener('contextmenu', function() {
          logExp('1',data.file_names,searchString);
      } , true);

      notHelpBut.addEventListener('click', function() {
          logExp('0',data.file_names,searchString);
      } , true);
        notHelpBut.addEventListener('contextmenu', function() {
          logExp('0',data.file_names,searchString);
      } , true);
       
  
        
         // else{
        //    $("#loadMoreButton").css("display", "none")
        }
        else{
            $("#docs-div").append(`<h3 style="text-align: center;margin-top:20px;">No Explanation Found</h3>`);
        }
        
       })


    });
}
}



