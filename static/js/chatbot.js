const chat=document.getElementById("chatMessages");

const input=document.getElementById("message");

const button=document.getElementById("sendBtn");

function addUserMessage(text){

chat.innerHTML+=`

<div class="user-message">

<div class="bubble">

${text}

</div>

</div>

`;

chat.scrollTop=chat.scrollHeight;

}

function addAIMessage(text){

chat.innerHTML+=`

<div class="ai-message">

<div class="bubble">

${text}

</div>

</div>

`;

chat.scrollTop=chat.scrollHeight;

}

async function sendMessage(){

const message=input.value.trim();

if(message==="") return;

addUserMessage(message);

input.value="";

const loading=document.createElement("div");

loading.className="typing";

loading.id="typing";

loading.innerHTML="AI is typing...";

chat.appendChild(loading);

chat.scrollTop=chat.scrollHeight;

try{

const response=await fetch("/api/chat",{

method:"POST",

headers:{

"Content-Type":"application/json"

},

body:JSON.stringify({

message:message

})

});

const data=await response.json();

document.getElementById("typing").remove();

addAIMessage(data.reply);

}catch(error){

document.getElementById("typing").remove();

addAIMessage("Sorry, something went wrong.");

}

}

button.addEventListener("click",sendMessage);

input.addEventListener("keypress",function(e){

if(e.key==="Enter"){

sendMessage();

}

});
