//a namespace wrapper for all our stuff
fellsafe = {};

//hexify an arbitrary string
fellsafe.toHex = function(s) {
    let h = ''
    for (let i = s.length - 1; i >= 0; i--)
        h = '%'+ s.charCodeAt(i).toString(16) + h
    return h
};

//send an AJAX request and get JSON response
fellsafe.send = function(url,s,dest) {
    fetch('/'+url+'/'+encodeURI(s))
        .then(response => response.json())
        .then(data => document.getElementById(dest).innerHTML = data);
};
