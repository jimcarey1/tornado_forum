const threadReplyElement = document.querySelector('button[type="submit"]');
console.log(threadReplyElement);


function renderCKEditor(){
    ClassicEditor
        .create(document.querySelector('#editor'))
        .catch(error=>{
            console.log(error)
        })
}
threadReplyElement.onclick = renderCKEditor;