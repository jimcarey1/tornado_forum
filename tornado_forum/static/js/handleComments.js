document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', async (event) => {
        if (event.target.classList.contains('toggle-children')) {
            const toggleButton = event.target;
            const commentId = toggleButton.dataset.commentId;
            const childrenContainer = document.getElementById(`children-of-${commentId}`);

            if (!childrenContainer) return;

            const isExpanded = toggleButton.textContent.includes('[-]');

            if (isExpanded) {
                childrenContainer.style.display = 'none';
                toggleButton.textContent = '[+]';
            } else {
                if (childrenContainer.innerHTML.trim() !== '') {
                    childrenContainer.style.display = 'block';
                    toggleButton.textContent = '[-]';
                } else {
                    try {
                        const response = await fetch(`/comment/${commentId}/children`);
                        if (!response.ok) {
                            throw new Error('Failed to fetch child comments.');
                        }
                        const children = await response.json();
                        renderComments(children, childrenContainer);
                        childrenContainer.style.display = 'block';
                        toggleButton.textContent = '[-]';
                    } catch (error) {
                        console.error(error);
                    }
                }
            }
        }
    });

    function renderComments(comments, container) {
        container.innerHTML = '';
        for (const comment of comments) {
            container.innerHTML += createCommentHTML(comment);
        }
    }

    function createCommentHTML(comment) {
        const hasChildren = comment.children_count > 0;
        return `
            <div class="comment-container" id="comment-${comment.id}" data-comment-id="${comment.id}">
                <div class="comment-main">
                    <div class="comment-toggle">
                        ${hasChildren ? `<span class="toggle-children" data-comment-id="${comment.id}">[+]</span>` : ''}
                    </div>
                    <div class="comment-content">
                        <div class="comment-details">
                            <p><strong>${comment.user.username}</strong></p>
                            <p>${comment.content}</p>
                        </div>
                        <div class="comment-meta">
                            <div class="comment-votes">
                                <i class="fa-solid fa-arrow-up vote-btn" data-vote-type="1" data-comment-id="${comment.id}"></i>
                                <span class="score">${comment.score}</span>
                                <i class="fa-solid fa-arrow-down vote-btn" data-vote-type="-1" data-comment-id="${comment.id}"></i>
                            </div>
                            <i class="fa-solid fa-reply reply-btn"></i>
                        </div>
                        <div class="reply-form" style="display: none;">
                            <div class="editor"></div>
                            <div class="handle-comment">
                                <button value="Reply" class="reply-comment" type="button">Reply</button>
                                <button value="Cancel" class="cancel-comment" type="button">Cancel</button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="children" id="children-of-${comment.id}"></div>
            </div>
        `;
    }
});

const deleteButtons = document.querySelectorAll('.comment-delete-btn')
const handleDeleteComment = async (event)=>{
    const deleteButton = event.target;
    const commentId = deleteButton.dataset.commentId;
    const commentElement = document.getElementById(`comment-${commentId}`)
    const response = await fetch(`/api/comments/delete/${commentId}`, {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('_xsrf'),
        }
    })
    if(response.ok){
        const message = await response.json()
        console.log('message deleted successfully')
        const commentContentElement = commentElement.querySelector('.comment-content')
        commentContentElement.innerHTML = `<p>deleted</p>`
    }else{
        console.log('Error deleting message')
    }
}
deleteButtons.forEach((button)=>{
    button.addEventListener('click', handleDeleteComment)
})