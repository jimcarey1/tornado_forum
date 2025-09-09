const profileContainer = document.querySelector('.profile-container')
const profileUserId = profileContainer.dataset.profileId

const fetchUserPosts = async ()=>{
    const response = await fetch(`/api/topics/${profileUserId}`)
    const topics = await response.json()
    console.log(topics)
}


const fetchUserComments = async ()=>{
    const response = await fetch(`/api/comments/${profileUserId}`)
    const comments = await response.json()
    console.log(comments)
}

const fetchUserUpVotedPosts = async ()=>{
    const response = await fetch(`/api/upvoted_topics/${profileUserId}`)
    const upvotedTopics = await response.json()
    console.log(upvotedTopics)
}

const fetchUserDownVotedPosts = async ()=>{
    const response = await fetch(`/api/downvoted_topics/${profileUserId}`)
    const downvotedTopics = await response.json()
    console.log(downvotedTopics)
}

document.addEventListener('DOMContentLoaded', ()=>{
    fetchUserPosts()
    fetchUserComments()
    fetchUserUpVotedPosts()
    fetchUserDownVotedPosts()
});