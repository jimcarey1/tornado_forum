const replyIcon = document.querySelector('.fa-reply')
const threadReplyContainer = document.querySelector('#thread-reply')
let editor;

function toggleReplyEditor() {
  const isHidden = threadReplyContainer.style.display === 'none'
  threadReplyContainer.style.display = isHidden ? 'block' : 'none'

  if (isHidden && !editor) {
    ClassicEditor
      .create(document.querySelector('#editor'))
      .then(CKeditor => {
        editor = CKeditor
      })
      .catch(error => {
        console.log(error)
      });
  }
}

replyIcon.onclick = toggleReplyEditor


const replyButton = document.querySelector('.reply-comment')
function createComment(){
  const content = editor.getData()
  const url = threadReplyContainer.getAttribute("data-url")
  console.log(url)
  if(content){
    fetch(url, {
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json',
        'X-Xsrftoken': getCookie('_xsrf')
      },
      body: JSON.stringify({
        content: content,
      })
    }).then((response)=>{
      if(!response.ok){
        throw new Error(`HTTP Error: ${response.status}`)
      }
      return response.json()
    })
    .then((data)=>console.log(data))
    .catch((error)=>console.log(error))
  }
}
replyButton.onclick = createComment