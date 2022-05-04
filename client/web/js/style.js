const renderGroup = (name, lastMessage, imageUrl) => {
    document.querySelector(".groups").insertAdjacentHTML("beforeend",
    `${document.querySelector(".groups").childElementCount != 0 ? "<hr>": ""}
    <div class="groupCard">
        <img src="${imageUrl}">
        <p class="groupName">${name}</p>
        <p class="lastMessage">${lastMessage}</p>
    </div>`);
};

var rendering = false;
const renderMessage = (content, author, timestamp) => {
    
    while(rendering)
        continue;

    rendering = true;
    let time = new Date(timestamp * 1000);
    document.querySelector(".messages").insertAdjacentHTML("beforeend", 
    `<div class="${author === "You" ? "message ownMessage": "message"}">
        <p class="messageContent">${content}</p>
        <p class="messageAuthor">${author}</p>
        <p class="messageTimestamp">${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}</p>
    </div>`);

    rendering = false;
};