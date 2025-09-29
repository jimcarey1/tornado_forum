const buttonElement = document.querySelector("button[type='button']")
console.log(buttonElement)
const handleChangeUsername = async (event)=>{
    event.preventDefault()
    const username = document.querySelector("input[name='change-username']").value 
    const confirmUsername = document.querySelector("input[name='confirm-change-username']").value
    const currentUrl = window.location.href
    const response = await fetch(currentUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken' : getCookie('_xsrf'),
        },
        body: JSON.stringify({"username": username, "confirm_username": confirmUsername})
    })
    if(response.status == 200){
        window.location.replace('/')
    }else{
        const message = await response.json()
        const displayErrorElement = document.querySelector('.display-error')
        if(response.status == 500){
            displayErrorElement.innerHTML = `<p>${message.details}</p>`
        }else{
            displayErrorElement.innerHTML = `<p>${message.error}</p>`
        }
    }
}
buttonElement.onclick = handleChangeUsername
