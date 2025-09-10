const profileContainer = document.querySelector('.profile-container')
const userActivityContentElement = document.querySelector('.user-activity-content')
const profileUserId = profileContainer.dataset.profileId

//When the user clicks on the posts button, We will check if the user is already in
//the posts section, If he is, We return if not we will fetch them from the backend
//and asynchronously add them to the userActivityElement.
const postsButton = document.querySelector('.post-display-button')
const handlePostButton = async ()=>{
    const currentlyShownTab = userActivityContentElement.dataset.currentContent
    if(currentlyShownTab == 'posts'){
        return
    }else{
        const topics = await fetchUserPosts()
        userActivityContentElement.dataset.currentContent = 'posts'
        let htmlToRender = ''
        topics['topics'].forEach((topic) => {
            htmlToRender += 
            `<div id="topic-${topic.id}" class="topic-list">
                <a href="/topic/${topic.id}">${topic.title}</a>
            </div>
            `
        });
        console.log(htmlToRender)
        userActivityContentElement.innerHTML = htmlToRender
    }
}
postsButton.onclick = handlePostButton


//When the user clicks on the comments button, We will check if the user is already in
//the comments section, If he is, We return if not we will fetch them from the backend
//and asynchronously add them to the userActivityElement.
const commentButton = document.querySelector('.comment-display-button')
const handleCommentButton = async ()=>{
    const currentlyShownTab = userActivityContentElement.dataset.currentContent
    if(currentlyShownTab == 'comments'){
        return
    }else{
        const comments = await fetchUserComments()
        userActivityContentElement.dataset.currentContent = 'comments'
        let htmlToRender = ''
        comments['comments'].forEach((comment)=>{
            htmlToRender += 
            `<div id="comment-${comment.id}" class="comment-list">
                ${comment.content}
            </div>
            `
        })
        userActivityContentElement.innerHTML = htmlToRender
    }
}
commentButton.onclick = handleCommentButton

//When the user clicks on the upVotedPosts button, We will check if the user is already in
//the upVotedPosts section, If he is, We return if not we will fetch them from the backend
//and asynchronously add them to the userActivityElement.
const upVoteButton = document.querySelector('.likes-display-button')
const handleLikesDisplayButton = async ()=>{
    const currentlyShownTab = userActivityContentElement.dataset.currentContent
    if(currentlyShownTab == 'likedPosts'){
        return
    }else{
        const likedPosts = await fetchUserUpVotedPosts()
        userActivityContentElement.dataset.currentContent = 'likedPosts'
        let htmlToRender = ''
        likedPosts['upvotedTopics'].forEach((topic)=>{
            htmlToRender +=
            `<div id="topic-${topic.id}" class="topic-list">
                <a href="/topic/${topic.id}">${topic.title}</a>
            </div>
            `
        })
        userActivityContentElement.innerHTML = htmlToRender
    }
}
upVoteButton.onclick = handleLikesDisplayButton

//When the user clicks on the downVotedPosts button, We will check if the user is already in
//the downVotedPosts section, If he is, We return if not we will fetch them from the backend
//and asynchronously add them to the userActivityElement.
const downVoteButton = document.querySelector('.dislikes-display-button')
const handleDisLikesDisplayButton = async ()=>{
    const currentlyShownTab = userActivityContentElement.dataset.currentContent
    if(currentlyShownTab == 'dislikedPosts'){
        return
    }else{
        const dislikedPosts = await fetchUserDownVotedPosts()
        userActivityContentElement.dataset.currentContent = 'dislikedPosts'
        let htmlToRender = ''
        dislikedPosts['downvotedTopics'].forEach((topic)=>{
            htmlToRender +=
            `<div id="topic-${topic.id}" class="topic-list">
                <a href="/topic/${topic.id}">${topic.title}</a>
            </div>
            `
        })
        userActivityContentElement.innerHTML = htmlToRender
    }
}
downVoteButton.onclick = handleDisLikesDisplayButton


const fetchUserPosts = async ()=>{
    const response = await fetch(`/api/topics/${profileUserId}`)
    const topics = await response.json()
    return topics
}


const fetchUserComments = async ()=>{
    const response = await fetch(`/api/comments/${profileUserId}`)
    const comments = await response.json()
    return comments
}

const fetchUserUpVotedPosts = async ()=>{
    const response = await fetch(`/api/upvoted_topics/${profileUserId}`)
    const upvotedTopics = await response.json()
    return upvotedTopics
}

const fetchUserDownVotedPosts = async ()=>{
    const response = await fetch(`/api/downvoted_topics/${profileUserId}`)
    const downvotedTopics = await response.json()
    return downvotedTopics
}