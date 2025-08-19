document.addEventListener('DOMContentLoaded', function() {
    const voteButtons = document.querySelectorAll('.vote-btn');
    voteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const voteType = this.dataset.voteType;
            const topicId = this.dataset.topicId;
            const commentId = this.dataset.commentId;

            let url;
            let body;

            if (topicId) {
                url = `/topic/${topicId}/vote`;
                body = JSON.stringify({ vote_type: parseInt(voteType) });
            } else if (commentId) {
                url = `/comment/${commentId}/vote`;
                body = JSON.stringify({ vote_type: parseInt(voteType) });
            }

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('_xsrf')
                },
                body: body
            })
            .then(response => response.json())
            .then(data => {
                const scoreElement = this.parentElement.querySelector('.score');
                scoreElement.textContent = data.upvotes - data.downvotes;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});