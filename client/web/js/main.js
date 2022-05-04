var token;
var lastGroupIds = [];
var currentGroupID = 1;

// Base64 from https://stackoverflow.com/questions/246801/how-can-you-encode-a-string-to-base64-in-javascript
var Base64={_keyStr:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",encode:function(e){var t="";var n,r,i,s,o,u,a;var f=0;e=Base64._utf8_encode(e);while(f<e.length){n=e.charCodeAt(f++);r=e.charCodeAt(f++);i=e.charCodeAt(f++);s=n>>2;o=(n&3)<<4|r>>4;u=(r&15)<<2|i>>6;a=i&63;if(isNaN(r)){u=a=64}else if(isNaN(i)){a=64}t=t+this._keyStr.charAt(s)+this._keyStr.charAt(o)+this._keyStr.charAt(u)+this._keyStr.charAt(a)}return t},decode:function(e){var t="";var n,r,i;var s,o,u,a;var f=0;e=e.replace(/[^A-Za-z0-9\+\/\=]/g,"");while(f<e.length){s=this._keyStr.indexOf(e.charAt(f++));o=this._keyStr.indexOf(e.charAt(f++));u=this._keyStr.indexOf(e.charAt(f++));a=this._keyStr.indexOf(e.charAt(f++));n=s<<2|o>>4;r=(o&15)<<4|u>>2;i=(u&3)<<6|a;t=t+String.fromCharCode(n);if(u!=64){t=t+String.fromCharCode(r)}if(a!=64){t=t+String.fromCharCode(i)}}t=Base64._utf8_decode(t);return t},_utf8_encode:function(e){e=e.replace(/\r\n/g,"\n");var t="";for(var n=0;n<e.length;n++){var r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r)}else if(r>127&&r<2048){t+=String.fromCharCode(r>>6|192);t+=String.fromCharCode(r&63|128)}else{t+=String.fromCharCode(r>>12|224);t+=String.fromCharCode(r>>6&63|128);t+=String.fromCharCode(r&63|128)}}return t},_utf8_decode:function(e){var t="";var n=0;var r=c1=c2=0;while(n<e.length){r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r);n++}else if(r>191&&r<224){c2=e.charCodeAt(n+1);t+=String.fromCharCode((r&31)<<6|c2&63);n+=2}else{c2=e.charCodeAt(n+1);c3=e.charCodeAt(n+2);t+=String.fromCharCode((r&15)<<12|(c2&63)<<6|c3&63);n+=3}}return t}}


const request = async (url, method, data, headers) => {
    headers = headers === undefined ? {}: headers;
    data = data === undefined ? {}: data;
    url = HOST + url;
    
    if(token !== undefined)
        headers["Token"] = token;
    
    let form_data = new FormData();
    for ( let key in data )
        form_data.append(key, data[key]);

    let options = {
        headers: headers,
        body: form_data
    }

    switch(method)
    {
        case "GET":
            if(data !== undefined)
            {
                if(Object.keys(data).length !== 0)
                {
                    let str = [];
                    for(let p in data)
                        str.push(encodeURIComponent(p) + "=" + encodeURIComponent(data[p]));
                    url += "?" + str.join("&");
                };
                
                options = {
                    method: "GET",
                    headers: headers
                };
            }
            break;
        case "POST":
            options["method"] = "POST";
            break;
        case "PUT":
            options["method"] = "PUT";
            break;
        case "DELETE":
            options["method"] = "DELETE";
            break;
        default:
            return console.error("Unrecognized request method");        
    }
    let resp = await fetch(url, options);
        
    if(resp.ok !== true)
        return console.error(resp); 
        
    return await resp.json();
};

const loadGroups = async () => {
    let groupIds = await request("/groups", "GET");
    
    if(groupIds.length === lastGroupIds.length && groupIds.every((value, index) => value === lastGroupIds[index]))  // Check if the groups have changed
        return;
    else
        lastGroupIds = groupIds;

    document.querySelector(".groups").innerHTML = "";

    groupIds.forEach(async id => {
        let group = await request(`/group/${id}`, "GET");
        let messages = await request(`/messages/${id}`, "GET", {
            timespan: "*"
        });
        console.log(group);
        let lastMessage = await request(`/message/${messages.slice(-1)}`, "GET");
        let lastMessageAuthor = lastMessage.authorID !== USER ? await request(`/user/${lastMessage.authorID}`, "GET"): {name: "You"};

        console.log(lastMessageAuthor);

        renderGroup(group.name, `${lastMessageAuthor.name}: ${lastMessage.content}`, group.groupPicture);
        await loadMessages(id);
    });
};

const app = async () => {
    let resp = await request("/token", "GET", {}, {"Authorization": Base64.encode(`${USER}:${PASSWORD}`)});
    token = resp["Token"];
    console.log(token);
    
    /*loadGroups();
    var groupTask = setInterval(loadGroups, 5000);*/

    loadMessages(1);
};

const loadMessages = async (groupID) => {
    let messages = await request(`/messages/${groupID}`, "GET", {
        timespan: "*"
    });
    messages.forEach(async messageID => {
        console.log(messageID);
        let message = await request(`/message/${messageID}`, "GET");
        let author = await request(`/user/${message.authorID}`, "GET");
        renderMessage(message.content, (author.ID === USER) ? "You": author.name, message.timestamp);
    });
};


app();

document.querySelector(".sendButton").addEventListener("click", () => {
    let text = document.querySelector(".input").value;
    if(text.length === 0 || text === " " || text.startsWith("\n"))
        return;

    request(`/messages/${currentGroupID}`, "POST", {
        "content": text
    });

    document.querySelector(".input").value = "";
});
