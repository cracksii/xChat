const renderGroup = (id, name, lastMessage, imageUrl) => {
    document.querySelector(".groups").insertAdjacentHTML("beforeend",
    `${document.querySelector(".groups").childElementCount != 0 ? "<hr>": ""}
    <div class="groupCard" onClick="openChat(${id})">
        <img src="${imageUrl}">
        <p class="groupName">${name}</p>
        <p class="lastMessage">${lastMessage}</p>
    </div>`);
};

const renderMessage = (id, content, author, timestamp) => {
    if(messageQueue.length !== 0 && id !== messageQueue[0])
        return setTimeout(() => renderMessage(id, content, author, timestamp), 10);
    messageQueue.splice(0, 1);
    let time = new Date(timestamp * 1000);
    document.querySelector(".messages").insertAdjacentHTML("beforeend", 
    `<div class="${author === "You" ? "message ownMessage": "message"}">
        <p class="messageContent">${content}</p>
        <p class="messageAuthor">${author}</p>
        <p class="messageTimestamp">${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}</p>
    </div>`);
};