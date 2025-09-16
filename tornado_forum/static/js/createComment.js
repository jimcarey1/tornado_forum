//Only managing one CKEditor instance for all replies.
let ckEditorInstance = null
//This is to find out, if the user is authenticated or not, If he is not userId should be equal to zero.
const userId = document.querySelector('.main-page').dataset.userId;
const url = document.getElementById('thread-reply').dataset.url

//This block of code creates a CKEditor instance for creating the comment(parent comment for the topic.).
//Only works if the user is authenticated.
const replyButton = document.querySelector(".topic-meta .fa-reply")
const createCKEditorInstance = async (event)=>{
    const replyButton = event.target
    const topicReplyContainer = document.querySelector('#thread-reply')

    const isHidden = topicReplyContainer.style.display === 'none'
    const isUserAuthenticated = (userId !== '0');
    topicReplyContainer.style.display = (isUserAuthenticated && isHidden) ? 'block' : 'none'

    if (isHidden && !ckEditorInstance) {
        try {
            const editorElement = topicReplyContainer.querySelector('#editor')
            if (editorElement) {
                ckEditorInstance = await ClassicEditor.create(editorElement)
            }
        } catch (error) {
            console.error('Error creating top-level editor:', error);
        }
    }
}
replyButton.onclick = createCKEditorInstance;

//This block of code actually creates the comment.
//It sends a POST request to the backend and saves the comment to the database and 
//then asynchronously updates the newly added comment to the comment section without browser refresh.
const createTopicReplyButton = document.querySelector("#thread-reply .handle-comment .reply-comment")
const createParentComment = async (event)=>{
    console.log(createTopicReplyButton)
    const topicReplyElement = document.getElementById("thread-reply")
    const data = ckEditorInstance.getData();
    if(data){
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('_xsrf')
            },
            body: JSON.stringify({"content": data})
        })
        if(response){
            const data = await response.json()
            ckEditorInstance = null
            topicReplyElement.style.display = 'none'
            const commentHTML = `
                <div class="comment" id="comment-${data.id}" data-comment-id="${data.id}">
                    <div class="comment-author">
                        <a href="#">${data.user.username}</a>
                    </div>
                    <div class="comment-content">
                        ${data.content}
                    </div>
                    <div class="comment-action">
                        <div class="comment-vote-btn">
                            <i class="fa-solid fa-arrow-up vote-btn" data-vote-type="1" data-comment-id="${data.id}" onclick="handleVote(event)"></i>
                            <span class="score">${data.score}</span>
                            <i class="fa-solid fa-arrow-down vote-btn" data-vote-type="-1" data-comment-id="${data.id}" onclick="handleVote(event)"></i>
                        </div>
                        <div class="comment-reply-btn">
                            <i class="fa-solid fa-reply" data-comment-id="${data.id}" onclick="createCKEditorInstanceForCommentReply(event)"></i>
                        </div>
                    </div>
                    <div class="comment-reply" id="comment-reply-${data.id}" style="display:none">
                        <div id="editor-${data.id}">
                        </div>
                        <div class="handle-comment">
                            <button value="Reply" class="reply-comment" data-comment-id="${data.id}" type="button" onclick="createChildrenComment(event)">Reply</button>
                            <button value="Cancel" class="cancel-comment" type="button">Cancel</button>
                        </div>
                    </div>
                </div>
            `
            const commentSection = document.querySelector('.comments-section')
            commentSection.insertAdjacentHTML('beforeend', commentHTML)
        }
    }
}
createTopicReplyButton.onclick = createParentComment

//This block of code creates a CKEditor instance for any of the comment(instance for creating nested comment.)
//We get all commentReplyButtons using querySelectorAll and use forEach on them to attach the callback function
//createCKEditorInstanceForCommentReply for every button.
const commentReplyButtons = document.querySelectorAll(".comment-action .comment-reply-btn .fa-reply")
const createCKEditorInstanceForCommentReply = async (event) =>{
    const commentReplyButton = event.target
    const commentId = commentReplyButton.dataset.commentId;
    const commentReplyContainer = document.getElementById(`comment-reply-${commentId}`)
    const isHidden = commentReplyContainer.style.display === 'none'
    const isUserAuthenticated = (userId != '0')
    commentReplyContainer.style.display = (isUserAuthenticated && isHidden) ? 'block' : 'none'
    ckEditorInstance = null
    if (isUserAuthenticated && isHidden){
        const editorElement = document.getElementById(`editor-${commentId}`)
        try{
            if(editorElement){
                ckEditorInstance = await ClassicEditor.create(editorElement)
            }else{
                console.log('editorElement not found.')
            }
        }catch(error){
            console.log('Error creating the CKEditor Instance:', error)
        }
    }
}
commentReplyButtons.forEach((button)=>{
    button.addEventListener('click', createCKEditorInstanceForCommentReply)
})

//This block of code actually creates the comment.
//similar to createParentComment, but It adds(parent_comment to the comment attribute.)
const createChildrenCommentButtons = document.querySelectorAll('.comment-reply .handle-comment .reply-comment')
const createChildrenComment = async(event)=>{
    const commentId = event.target.dataset.commentId
    const commentReplyContainer = document.getElementById(`comment-reply-${commentId}`)
    const content = ckEditorInstance.getData()
    if(content){
        try{
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('_xsrf')
                },
                body: JSON.stringify({'content': content, 'parent_id':commentId})
            })
            if(response){
                const data = await response.json()
                ckEditorInstance = null
                commentReplyContainer.style.display = 'none'
            }
        }catch(error){
            console.log('An error occured:', error)
        }
    }else{
        console.log('There is no content.')
    }

}
createChildrenCommentButtons.forEach((button)=>{
    button.addEventListener('click', createChildrenComment)
})

//This block of code destroys CKEditor instance when the user clicks on the cancel button.
const cancelCommentButton = document.querySelector('#thread-reply .cancel-comment')
const handleCancelCommentButton = ()=>{
    const topicReplyContainer = document.querySelector('#thread-reply')
    topicReplyContainer.style.display = 'none'
    const editorElement = document.getElementById('editor')
    const ckEditorElement = editorElement.nextElementSibling
    ckEditorElement.remove()
    ckEditorInstance = null
}
cancelCommentButton.onclick = handleCancelCommentButton

//Does the same job as cancelCommentButton for every nested comment cancel buttons.
const nestedCancelCommentButton = document.querySelectorAll('.comment-reply .handle-comment .cancel-comment')
const handleNestedCancelCommentButton = async (event)=>{
    const commentButton = event.target
    const commentId = commentButton.dataset.commentId;
    const commentReplyContainer = document.getElementById(`comment-reply-${commentId}`)
    commentReplyContainer.style.display = 'none'
    const editorElement = document.querySelector(`#editor-${commentId}`)
    const ckEditorElement = editorElement.nextElementSibling
    ckEditorElement.remove()
    ckEditorInstance = null
}
nestedCancelCommentButton.forEach((button)=>{
    button.addEventListener('click', handleNestedCancelCommentButton)
})

const commentToggleButtons = document.querySelectorAll('.toggle-comment-button')
const handleToggleCommentButton = (event)=>{
    const buttonElement = event.target;
    const toggleDivElement = buttonElement.closest('.toggle-comment-visibility')
    console.log(toggleDivElement)
    const commentId = toggleDivElement.dataset.commentId
    const commentElement = document.getElementById(`comment-${commentId}`)
    const nestedCommentsElement = commentElement.nextElementSibling
    commentElement.style.display = 'none'
    nestedCommentsElement.style.display='none'
}

commentToggleButtons.forEach((toggleButton)=>{
    toggleButton.addEventListener('click', handleToggleCommentButton)
})