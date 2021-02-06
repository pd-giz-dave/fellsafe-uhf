//a global namespace wrapper for all our stuff (to prevent name clashes)
//fs == FellSafe
fs = {};

//hexify an arbitrary string
//useful for sending binary data to some end-point url
fs.toHex = function(s) {
    let h = ''
    for (let i = s.length - 1; i >= 0; i--)
        h = '%'+ s.charCodeAt(i).toString(16) + h;
    return h;
};

//send an AJAX request and get JSON response
fs.send = function(url,s,cb) {
    //url is the prefix url
    //s is the suffix url
    //dest is a document id to send the result to
    fetch('/'+url+'/'+encodeURI(s))
        .then(response => response.json())
        .then(data => cb(data));
};
