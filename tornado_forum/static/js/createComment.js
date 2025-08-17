const replyIcon = document.querySelector('.fa-reply');
const threadReplyContainer = document.querySelector('#thread-reply');
let editorInstance = null;

function toggleReplyEditor() {
  const isHidden = threadReplyContainer.style.display === 'none';
  threadReplyContainer.style.display = isHidden ? 'block' : 'none';

  if (isHidden && !editorInstance) {
    ClassicEditor
      .create(document.querySelector('#editor'))
      .then(editor => {
        editorInstance = editor;
      })
      .catch(error => {
        console.log(error);
      });
  }
}

replyIcon.onclick = toggleReplyEditor;