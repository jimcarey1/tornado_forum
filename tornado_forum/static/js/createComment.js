
document.addEventListener('DOMContentLoaded', () => {
    const editors = {};

    document.body.addEventListener('click', async (event) => {
        // Handle opening the reply form for a comment
        if (event.target.classList.contains('reply-btn')) {
            const commentDetail = event.target.closest('.comment-detail');
            const commentId = commentDetail.dataset.commentId;
            const replyForm = commentDetail.querySelector('.reply-form');

            const isHidden = replyForm.style.display === 'none';
            replyForm.style.display = isHidden ? 'block' : 'none';

            if (isHidden && !editors[commentId]) {
                try {
                    const editorElement = replyForm.querySelector('.editor');
                    if (editorElement) {
                        editors[commentId] = await ClassicEditor.create(editorElement);
                    }
                } catch (error) {
                    console.error('Error creating editor:', error);
                }
            }
        }

        // Handle submitting a reply
        if (event.target.classList.contains('reply-comment')) {
            const commentDetail = event.target.closest('.comment-detail');
            const parentId = commentDetail.dataset.commentId;
            const editor = editors[parentId];
            const content = editor.getData();
            
            const topicContainer = document.querySelector('.topic-page');
            const topicId = topicContainer.id;
            const url = `/topic/${topicId}/comment/create`;

            if (content) {
                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Xsrftoken': getCookie('_xsrf')
                        },
                        body: JSON.stringify({ content: content, parent_id: parentId })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP Error: ${response.status}`);
                    }

                    const newComment = await response.json();
                    
                    const newCommentHtml = `
                        <div class="comment-detail" id="comment-${newComment.id}" data-comment-id="${newComment.id}">
                            <div class="comment-message">
                                ${newComment.user.username}
                                <p>${newComment.content}</p>
                            </div>
                            <div class="comment-meta">
                                <div class="comment-votes">
                                    <i class="fa-solid fa-arrow-up vote-btn" data-vote-type="1" data-comment-id="${newComment.id}"></i>
                                    <span class="score">${newComment.score}</span>
                                    <i class="fa-solid fa-arrow-down vote-btn" data-vote-type="-1" data-comment-id="${newComment.id}"></i>
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
                            <div class="child-comments"></div>
                        </div>
                    `;

                    const childCommentsContainer = commentDetail.querySelector('.child-comments');
                    childCommentsContainer.insertAdjacentHTML('beforeend', newCommentHtml);

                    editor.setData('');
                    const replyForm = commentDetail.querySelector('.reply-form');
                    replyForm.style.display = 'none';

                } catch (error) {
                    console.error('Error:', error);
                }
            }
        }

        // Handle canceling a reply
        if (event.target.classList.contains('cancel-comment')) {
            const commentDetail = event.target.closest('.comment-detail');
            const replyForm = commentDetail.querySelector('.reply-form');
            replyForm.style.display = 'none';
        }
    });

    // Handling the top-level comment form
    const topLevelReplyIcon = document.querySelector('.topic-meta .fa-reply');
    const topLevelReplyContainer = document.querySelector('#thread-reply');
    let topLevelEditor;

    if (topLevelReplyIcon) {
        topLevelReplyIcon.addEventListener('click', async () => {
            const isHidden = topLevelReplyContainer.style.display === 'none';
            topLevelReplyContainer.style.display = isHidden ? 'block' : 'none';

            if (isHidden && !topLevelEditor) {
                try {
                    const editorElement = topLevelReplyContainer.querySelector('#editor');
                    if (editorElement) {
                        topLevelEditor = await ClassicEditor.create(editorElement);
                    }
                } catch (error) {
                    console.error('Error creating top-level editor:', error);
                }
            }
        });
    }

    const topLevelReplyButton = document.querySelector('#thread-reply .reply-comment');
    if (topLevelReplyButton) {
        topLevelReplyButton.addEventListener('click', async () => {
            const content = topLevelEditor.getData();
            const url = topLevelReplyContainer.dataset.url;

            if (content) {
                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Xsrftoken': getCookie('_xsrf')
                        },
                        body: JSON.stringify({ content: content, parent_id: null })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP Error: ${response.status}`);
                    }
                    
                    const newComment = await response.json();

                    const newCommentHtml = `
                        <div class="comment-detail" id="comment-${newComment.id}" data-comment-id="${newComment.id}">
                            <div class="comment-message">
                                ${newComment.user.username}
                                <p>${newComment.content}</p>
                            </div>
                            <div class="comment-meta">
                                <div class="comment-votes">
                                    <i class="fa-solid fa-arrow-up vote-btn" data-vote-type="1" data-comment-id="${newComment.id}"></i>
                                    <span class="score">${newComment.score}</span>
                                    <i class="fa-solid fa-arrow-down vote-btn" data-vote-type="-1" data-comment-id="${newComment.id}"></i>
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
                            <div class="child-comments"></div>
                        </div>
                    `;

                    const commentsSection = document.querySelector('.comments-section');
                    commentsSection.insertAdjacentHTML('beforeend', newCommentHtml);

                    topLevelEditor.setData('');
                    topLevelReplyContainer.style.display = 'none';

                } catch (error) {
                    console.error('Error:', error);
                }
            }
        });
    }
    
    const topLevelCancelButton = document.querySelector('#thread-reply .cancel-comment');
    if (topLevelCancelButton) {
        topLevelCancelButton.addEventListener('click', () => {
            topLevelReplyContainer.style.display = 'none';
        });
    }
});

function getCookie(name) {
    let r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
