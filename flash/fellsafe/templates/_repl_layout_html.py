# _repl_layout.html: Autogenerated file start
def render(vars):
    yield """<script>
//add objects to our namespace - this can be done immediately
fs.replLoad = function(data,dest) """
    yield """{
    //load an array into a list
    //data is the array
    //dest is the list element ID to load it into
    eid = dest;
    list = document.getElementById(eid); //NB: does not work if use function param!!
    list.innerHTML = '';
    for (let response=0; response<data.length; response++) """
    yield """{
        li = document.createElement('li');
        li.innerHTML = data[response];
        list.appendChild(li);
    };
 };
fs.doReplLine = function(e) """
    yield """{
    //send a repl command to the server and get its response
    function replResponse(data) """
    yield """{
        //callback with the response from our command send
        if (command == '_clear') """
    yield """{
            fs.responses = [];
            fs.commands  = [];
        }
        fs.commands.push(command);
        fs.responses.push(data);
        fs.replLoad(fs.commands ,'fs-repl-command-history');
        fs.replLoad(fs.responses,'fs-repl-response-history');
    };
    if (e.keyCode == 13) """
    yield """{
        //user pressed the enter key
        command = e.target.value
        fs.send('repl',command,replResponse);
        e.target.value = '';
    }
 };
fs.responses = [];
fs.commands  = [];
//prepare the page - we have to wait for the document to be ready for this, so...
document.addEventListener('DOMContentLoaded',function(event)"""
    yield """{
"""
    if len(vars[1]) > 0:
        for r in vars[1]:
            yield """    fs.responses.push("""
            yield str(r)
            yield """);
"""
        yield """    fs.replLoad(fs.responses,'fs-repl-response-history');
"""
    if len(vars[0]) > 0:
        for c in vars[0]:
            yield """    fs.commands.push("""
            yield str(c)
            yield """);
"""
        yield """    fs.replLoad(fs.commands,'fs-repl-command-history');
"""
    yield """});
</script>
<div id='fs-repl'>
    <div class='fs-repl-response'>
        <p>Response history:</p>
        <ol id='fs-repl-response-history'></ol>
    </div>
    <div class='fs-repl-command'>
        <input type='text' size='80' placeholder='enter a command' onkeydown='fs.doReplLine(event)'/>
    </div>
    <div class='fs-repl-command'>
        <p>Command history:</p>
        <ol id='fs-repl-command-history'></ol>
    </div>
</div>
"""
# _repl_layout.html: Autogenerated file end
