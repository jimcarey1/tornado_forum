//Only managing one CKEditor instance for all replies.
let ckEditorInstance = null
const url = document.getElementById('thread-reply').dataset.url

const replyButton = document.querySelector(".topic-meta .fa-reply")
const createCKEditorInstance = async (event)=>{
    const replyButton = event.target
    const topicReplyContainer = document.querySelector('#thread-reply')

    const isHidden = topicReplyContainer.style.display === 'none'
    topicReplyContainer.style.display = isHidden ? 'block' : 'none'

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

const createTopicReplyButton = document.querySelector("#thread-reply .handle-comment .reply-comment")
const createParentComment = async (event)=>{
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
        }
    }
}
createTopicReplyButton.onclick = createParentComment

const commentReplyButtons = document.querySelectorAll(".comment-action .comment-reply-btn .fa-reply")
const createCKEditorInstanceForCommentReply = async (event) =>{
    const commentReplyButton = event.target
    const commentId = commentReplyButton.dataset.commentId;
    const commentReplyContainer = document.getElementById(`comment-reply-${commentId}`)
    const isHidden = commentReplyContainer.style.display === 'none'
    commentReplyContainer.style.display = isHidden ? 'block' : 'none'
    if (isHidden && !ckEditorInstance){
        const editorElement = document.getElementById(`editor-${commentId}`)
        try{
            if(editorElement){
                ckEditorInstance = await ClassicEditor.create(editorElement)
                console.log(ckEditorInstance)
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


const createChildrenCommentButtons = document.querySelectorAll('.reply-comment')
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
                console.log(data)
                ckEditorInstance = null
                commentReplyContainer.style.direction = 'none'
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