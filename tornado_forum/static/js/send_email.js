const sendVerificationEmailButton = document.querySelector('.send-verification-email');
const checkIfEmailSent = async ()=>{
    const userId = document.querySelector('.main-page').dataset.userId;
    const response = await fetch('/send-verification-email', {
        method: 'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken': getCookie('_xsrf')
        },
        body: JSON.stringify({"user_id":userId})
    })
    if(response.status == 200){
        const message = await response.json()
        console.log(message)
    }
}
sendVerificationEmailButton.onclick = checkIfEmailSent