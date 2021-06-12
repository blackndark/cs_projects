document.addEventListener("DOMContentLoaded", function() {

    // Show compose-view on All Posts page
if (document.querySelector("#compose-view")) {

    // Empty compose box
    document.querySelector("#compose-content").innerHTML = "";

    // Enable Post button only when a content is typed
    document.querySelector("#compose-content").onkeyup = () => {
    if (document.querySelector("#compose-content").value.length > 0) {
        document.querySelector("#submit").disabled = false;
    } else {
        document.querySelector("#submit").disabled = true;
    }
    }
    // Run new_post function when the Post button is clicked to send a new post
    document.querySelector("#compose-form").addEventListener("submit", new_post);
}

// Don't show the follow button if the user is looking at own profile
login_user = document.querySelector("#username").innerHTML
user_profile = document.querySelector("#title-link").innerHTML
if (user_profile === login_user) {
    document.querySelector("#follow_button").style.display="none";
}

// Check if the logged in user is already following the profile and adjust Follow/Unfollow state
if (document.querySelector("#follow_button")) {
fetch(`/follow_button/${user_profile}`)
.then(response => response.json())
.then(result => {
    console.log(result)
    if (result["followed"]) {
        document.querySelector("#follow_button").innerHTML = "Unfollow"
        document.querySelector("#follow_button").className = "btn btn-primary"
    } else {
        document.querySelector("#follow_button").innerHTML = "Follow"
        document.querySelector("#follow_button").className = "btn btn-outline-primary"
    }
})
}

// Check if the logged in user has already liked the post and adjust Like button state
let like_post_ids =  document.querySelectorAll("#post-id")
like_post_ids.forEach(like_post_id => {
    fetch(`/like_button/${like_post_id.innerHTML}`)
    .then(response => response.json())
    .then(result => {
        console.log(result)
        if (result["liked"]) {
            // If the post is liked change the class
            like_post_id.parentNode.querySelector("#like-button").className = "btn btn-primary btn-sm"
        } else if (result["not liked"]) {
            // If the post is not liked change the class
            like_post_id.parentNode.querySelector("#like-button").className = "btn btn-outline-primary btn-sm"
        }
    })
})



// If follow button is clicked run the follow function
if (document.querySelector("#follow_button")) {
    document.querySelector("#follow_button").addEventListener("click", follow);
}

// If edit button is clicked run the edit function
if (document.querySelector("#edit-link")) {
    const edit_links = document.querySelectorAll("#edit-link")
    edit_links.forEach(edit_link => {
        edit_link.addEventListener("click", edit)
    })
}

// If like button is clicked run the like function
const like_buttons = document.querySelectorAll("#like-button")
like_buttons.forEach(like_button => {
    like_button.addEventListener("click", like)
})

})

function new_post() {

    fetch("/new", {
        method: "POST",
        body: JSON.stringify({
            content: document.querySelector("#compose-content").value
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
    })
}


// When follow button is clicked send new creator and follower info via POST request
function follow() {

    fetch("/follow", {
        method : "POST",
        body: JSON.stringify({
            creator: document.querySelector("#title-link").innerHTML,
            follower: document.querySelector("#username").innerHTML
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
        // If the following action is successful change the Follow button to Unfollow
        if (result["message"]) {
            document.querySelector("#follow_button").innerHTML = "Unfollow"
            document.querySelector("#follow_button").className = "btn btn-primary"

            // Update profile section (follower, following numbers) for the given username
            const creator = document.querySelector("#title-link").innerHTML
            fetch(`/follow_unfollow/${creator}`)
            .then(response => response.json())
            .then(profile => {
            console.log(profile)
            document.querySelector("#follow").innerHTML = `${profile.followers} Followers &nbsp&nbsp&nbsp ${profile.following} Following`
            })

        } else if (result["unfollowed"]) {
            document.querySelector("#follow_button").innerHTML = "Follow"
            document.querySelector("#follow_button").className = "btn btn-outline-primary"

            // Update profile section (follower, following numbers) for the given username
            const creator = document.querySelector("#title-link").innerHTML
            fetch(`/follow_unfollow/${creator}`)
            .then(response => response.json())
            .then(profile => {
            console.log(profile)
            document.querySelector("#follow").innerHTML = `${profile.followers} Followers &nbsp&nbsp&nbsp ${profile.following} Following`
            })
        }
    })
}


// Edit logged in users post.
function edit() {

    // Reaching the content node of each post to create a textarea with the post content.
    const card_body = this.parentNode.parentNode
    let card_text = card_body.children[2]
    const content = card_text.innerHTML
    card_text.innerHTML = ""
    text_area = document.createElement("textarea")
    text_area.className = "form-control"
    card_text.append(text_area)
    text_area.innerHTML = content

    // Hiding Edit button
    this.parentNode.style.display= "none";

    // Creating save button
    const button = document.createElement("button")
    button.className = "btn btn-primary"
    button.id = "save-edit"
    button.innerHTML = "Save"
    card_body.append(button)

    // Click save button behaviour
    const post_id = card_body.children[5].innerHTML
    card_body.children[6].addEventListener("click", () => {
        save(post_id);
    })
}


// Save edited post
function save(post_id) {

    let post_ids = document.querySelectorAll("#post-id")
    post_ids.forEach(post_number => {
        if (post_number.innerHTML === post_id) {
            let text_area = post_number.parentNode.children[2].innerHTML
        }
    })

    fetch(`/save/${post_id}`, {
        method: "PUT",
        body: JSON.stringify({
            content: text_area.value
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result)
        if (result["message"]) {

            let post_ids = document.querySelectorAll("#post-id")
            post_ids.forEach(post_number => {
                if (post_number.innerHTML === post_id) {
                    post_number.parentNode.children[2].removeChild(post_number.parentNode.children[2].firstChild)
                    post_number.parentNode.children[2].append(text_area.value)
                    post_number.parentNode.children[4].style.display = "block"
                    post_number.parentNode.children[6].style.display = "none"
                }
            })
            

        }
    })
}


// logged in user can like or unlike any post
function like() {

    const post_id = this.parentNode.querySelector("#post-id").innerHTML
    fetch("/like", {
        method: "PUT",
        body : JSON.stringify({
            post_id: post_id,
            follower: document.querySelector("#username").innerHTML
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result)
        if (result["liked"]) {

            // If the post is liked change the class
            this.className = "btn btn-primary btn-sm"

            // Get the updated like count without refreshing the page
            fetch(`/postlikes/${post_id}`)
            .then(response => response.json())
            .then(result => {
                this.querySelector("#like-counter").innerHTML = result.post_likes
            })

        } else if (result["disliked"]) {

            //If the post is disliked change the class
            this.className = "btn btn-outline-primary btn-sm"

            // Get the updated like count without refreshing the page
            fetch(`/postlikes/${post_id}`)
            .then(response => response.json())
            .then(result => {
                this.querySelector("#like-counter").innerHTML = result.post_likes
            })

        }
    })
}
