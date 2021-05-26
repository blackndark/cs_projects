document.addEventListener("DOMContentLoaded", function () {
    // Use buttons to toggle between views
    document.querySelector("#inbox").addEventListener("click", () => load_mailbox("inbox"));
    document.querySelector("#sent").addEventListener("click", () => load_mailbox("sent"));
    document.querySelector("#archived").addEventListener("click", () => load_mailbox("archive"));
    document.querySelector("#compose").addEventListener("click", compose_email);
    // Run send_email function when Send button is clicked
    document.querySelector("#compose-form").addEventListener("submit", send_email);

    // By default, load the inbox
    load_mailbox("inbox");
});

function compose_email() {
    // Show compose view and hide other views
    document.querySelector("#emails-view").style.display = "none";
    document.querySelector("#compose-view").style.display = "block";
    document.querySelector("#mail-view").style.display = "none";

    // Clear out composition fields
    document.querySelector("#compose-recipients").value = "";
    document.querySelector("#compose-subject").value = "";
    document.querySelector("#compose-body").value = "";
}

function load_mailbox(mailbox) {
    // Remove all previous children elements of mail-view before creating new ones. Running here instead of inside open_email for better user experience.
    const mail_view = document.querySelector("#mail-view");
    while (mail_view.firstChild) {
        mail_view.removeChild(mail_view.firstChild);
    }

    // Show the mailbox and hide other views
    document.querySelector("#emails-view").style.display = "block";
    document.querySelector("#compose-view").style.display = "none";
    document.querySelector("#mail-view").style.display = "none";

    // Show the mailbox name
    document.querySelector("#emails-view").innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    // Fetch all mails
    fetch(`/emails/${mailbox}`)
        .then((response) => response.json())
        .then((emails) => {
            console.log(emails);
            // Create main div that will contain all emails line by line
            const mail = document.createElement("div");
            mail.className = "list-group";
            emails.forEach((email) => {
                console.log(email);
                // Create <a> tags for every single email
                const mail_item = document.createElement("a");
                mail_item.className = "list-group-item list-group-item-action list-group-item-light";
                mail.append(mail_item);
                // Grey out once the meail is read
                if (email.read === true) {
                    mail_item.className = "list-group-item list-group-item-action list-group-item-secondary";
                }
                // Add sender and subject to the <a> tag
                mail_item.innerHTML = `${email.sender + " "}` + "&nbsp" + `<b>${email.subject + " "}<b>`;
                // Create a new <span> element to align date to the end of the line
                const mail_date = document.createElement("span");
                mail_date.style = "float:right";
                mail_date.innerHTML = `${email.timestamp}`;
                mail_item.append(mail_date);
                // Add the main div to to #emails-view
                document.querySelector("#emails-view").append(mail);
                // Ability to click and open each email with an event listener
                mail_item.addEventListener("click", () => {
                    console.log(email.id);
                    open_email(email.id, mailbox);
                });
            });
        });
}

// Send email when Send button is clicked
function send_email(event) {
    event.preventDefault();

    fetch("/emails", {
        method: "POST",
        body: JSON.stringify({
            recipients: document.querySelector("#compose-recipients").value,
            subject: document.querySelector("#compose-subject").value,
            body: document.querySelector("#compose-body").value,
        }),
    })
        .then((response) => response.json())
        .then((result) => {
            console.log(result);
            if (result["message"]) {
                console.debug(result["message"]);
                load_mailbox("sent");
            } else {
                console.debug(result["error"]);
            }
        });
}

// Show contents of the email when clicked on a given email in the mailbox
function open_email(email_id, mailbox) {
    // Show the single mail content and hide other views
    document.querySelector("#emails-view").style.display = "none";
    document.querySelector("#compose-view").style.display = "none";
    document.querySelector("#mail-view").style.display = "block";

    fetch(`/emails/${email_id}`)
        .then((response) => response.json())
        .then((email) => {
            console.log(email);

            //  Archive button and click event listener
            archive_button = document.createElement("button");
            archive_button.className = "btn btn-sm btn-outline-secondary";
            if (email.archived === false) {
                archive_button.innerHTML = "Archive";
                document.querySelector("#mail-view").append(archive_button);
                archive_button.addEventListener("click", () => archive_email(email_id));
            } else {
                archive_button.innerHTML = "Unarchive";
                document.querySelector("#mail-view").append(archive_button);
                archive_button.addEventListener("click", () => unarchive_email(email_id));
            }

            // Hide the Archive button if the mail is in the Sent items
            if (mailbox === "sent") {
                archive_button.style.display = "none";
            }

            // Create new div elements for each component of the email under mail-view
            sender_div = document.createElement("div");
            recipients_div = document.createElement("div");
            timestamp_div = document.createElement("div");
            subject_div = document.createElement("div");
            body_div = document.createElement("div");

            // Reach out to inner HTML and assign values(email content) coming from json data
            sender_div.innerHTML = `From: ` + `<b>${email.sender}<b>`;
            recipients_div.innerHTML = `${"To: " + email.recipients}`;
            timestamp_div.innerHTML = `${"Date: " + email.timestamp}`;
            subject_div.innerHTML = `${"Subject: " + email.subject}`;
            body_div.innerHTML = `<hr><pre>${email.body}</pre><hr>`;

            // Fill the mail-view div with child divs which contain parts of the email content
            mail_view = document.querySelector("#mail-view");
            mail_view.append(sender_div);
            mail_view.append(recipients_div);
            mail_view.append(timestamp_div);
            mail_view.append(subject_div);
            mail_view.append(body_div);

            mark_as_read(email_id);

            // Create reply button and listen for the click event
            reply_button = document.createElement("button");
            reply_button.className = "btn btn-outline-success";
            reply_button.innerHTML = "Reply";
            document.querySelector("#mail-view").append(reply_button);
            reply_button.addEventListener("click", () => reply_email(email_id));
        })
        .catch((error) => console.error("Error:", error));
}

// Send PUT request to mark the opened email as read
function mark_as_read(email_id) {
    fetch(`/emails/${email_id}`, {
        method: "PUT",
        body: JSON.stringify({
            read: true,
        }),
    });
}

// Send PUT request to archive the email when archive button is clicked
function archive_email(email_id) {
    fetch(`/emails/${email_id}`, {
        method: "PUT",
        body: JSON.stringify({
            archived: true,
        }),
    });
    // Additional fetch to update the inbox before even loading the inbox
    fetch(`/emails/inbox`);
    load_mailbox("inbox");
}

// Send PUT request to unarchive the email when unarchive button is clicked
function unarchive_email(email_id) {
    fetch(`/emails/${email_id}`, {
        method: "PUT",
        body: JSON.stringify({
            archived: false,
        }),
    });
    // Additional fetch to update the inbox before even loading the inbox
    fetch(`/emails/inbox`);
    load_mailbox("inbox");
}

// Reply
function reply_email(email_id) {
    fetch(`/emails/${email_id}`)
        .then((response) => response.json())
        .then((email) => {
            compose_email();
            document.querySelector("#compose-recipients").value = email.sender;
            if (!email.subject.includes("Re:")) {
                document.querySelector("#compose-subject").value = `${"Re: " + email.subject}`;
            } else {
                document.querySelector("#compose-subject").value = `${email.subject}`;
            }
            document.querySelector("#compose-body").value = `${
                "\n\nOn " + email.timestamp + " " + email.sender + " wrote:\n\n" + email.body
            }`;
        });
}
