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
if (replyButton) {
    replyButton.onclick = createComment;
}

function createComment(){
    const content = editor.getData();
    const url = threadReplyContainer.getAttribute("data-url");

    if(content) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Xsrftoken': getCookie('_xsrf')
            },
            body: JSON.stringify({ content: content })
        })
        .then(response => {
            if(!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const comment = data;
            const commentsSection = document.querySelector('.comments-section');
            const newCommentElement = document.createElement('div');
            newCommentElement.classList.add('comment-detail');
            newCommentElement.id = comment.id;
            newCommentElement.innerHTML = `
                <div class="comment-message">
                    ${comment.user.username}
                    <p>${comment.content}</p>
                </div>
                <div class="comment-meta">
                    <div class="comment-votes">
                        <i class="fa-solid fa-arrow-up vote-btn" data-vote-type="1" data-comment-id="${comment.id}" onclick="handleVote(event)"></i>
                        <span class="score">${comment.score}</span>
                        <i class="fa-solid fa-arrow-down vote-btn" data-vote-type="-1" data-comment-id="${comment.id}" onclick="handleVote(event)"></i>
                    </div>
                    <i class="fa-solid fa-reply"></i>
                </div>
            `;
            commentsSection.appendChild(newCommentElement);

            editor.setData('');
            threadReplyContainer.style.display = 'none';
        })
        .catch(error => console.error('Error:', error));
    }
}