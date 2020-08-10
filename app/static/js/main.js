function toggleText(e) {
    if (e.target.text.trim().toLowerCase() == "read more") {
        e.target.parentNode.style.display = "none";
        e.target.parentNode.nextElementSibling.style.display = "block"
    }
    else {
        e.target.parentNode.style.display = "none";
        e.target.parentNode.previousElementSibling.style.display = "block"
    }
}

$(document).ready(function() {

    // Check for click events on the navbar burger icon
    $(".navbar-burger").click(function() {

        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");

    });
});
document.addEventListener('DOMContentLoaded', () => {
    (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
        $notification = $delete.parentNode;

        $delete.addEventListener('click', () => {
        $notification.parentNode.removeChild($notification);
        });
    });
});

const fileInput = document.querySelector('#file-js-example input[type=file]');
if (fileInput) {
    fileInput.onchange = () => {
        if (fileInput.files.length > 0) {
        const fileName = document.querySelector('#file-js-example .file-name');
        fileName.textContent = fileInput.files[0].name;
        }
    }
}


function showLike(id, userId) {
    var d = document.querySelector("#like-"+id);
    var pText = d.innerText;
    var url;
    if (pText.startsWith("You")) {
        url = "/poems/unlike/" + id + "/" + userId
    } else {
        url = "/poems/like/" + id + "/" + userId
    }
    if (!userId || !id) {window.location.replace("/auth/login")}
    console.log(url)
    fetch(url, {
        method: 'GET', // or 'PUT'
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
      })
      .then(response => response.json())
        .then(data => {
            var p = document.createElement("p");
            p.textContent = data["user_likes"];
            p.setAttribute("class", "help")
            var parentDiv = document.querySelector("#like-"+id);
            parentDiv.innerHTML = "";
            parentDiv.appendChild(p)
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error(error)
            // window.location.replace("/auth/login")
        });
}

function commentSubmit(e, poem_id) {
    e.preventDefault();
    var parent_id = e.target.parent_id.value || null;
    var body = e.target.body.value;
    var url = "/comment/" + poem_id;
    console.log(e.target.csrf_token.value)
    fetch(url, {
        method: 'POST', // or 'PUT'
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-TOKEN': e.target.csrf_token.value
        },
        body: JSON.stringify({"body": body, "parent_id": parent_id}),
        credentials: 'same-origin'
      })
      .then(response => response.json())
        .then(data => {
            var commentListBox = document.querySelector("#comment-list-box-" + poem_id);
            commentListBox.innerHTML = "";
            commentListBox.innerHTML = data["comments"].map(comment => makeComment(comment, data["can_delete"]));
            var commentForm = document.querySelector("#comment-form-" + data["poem_id"]);
            commentForm.body.value = "";
        })
        .catch((error) => {
            console.log("error happened")
        });
}

function commentReply(e, comment_id, poem_id) {
    var parent = e.target.parentElement;
    parent.lastElementChild.innerHTML = `
    <article class="media">
    <div class="media-content">
      <div class="content">
        <div class="field">
          <div class="control">
          <form action="" method="post" onsubmit="commentNestedSubmit(event, ${poem_id}, ${comment_id})">
            <input type="text" name="${comment_id}-comment"class="input is-small is-rounded" placeholder="write a comment">
            <input type="submit" hidden />
          </form>
          </div>
        </div>
      </div>
    </div>
</article>
    `
}

function commentNestedSubmit(e, poem_id, comment_id, main_id) {
    e.preventDefault();
    console.dir(e.target)
    var parent_id = comment_id || null;
    var nestedBody = e.target.childNodes[1].value;
    var url = "/comment/" + poem_id;
    var csrf = document.querySelector("#csrf_token");
    if (!csrf) {window.location.replace("/auth/login")}
    csrf = csrf.value;
    document.querySelector("#body").value = nestedBody;
    document.querySelector("#parent_id").value = parent_id;
    fetch(url, {
        method: 'POST', // or 'PUT'
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-TOKEN': csrf
        },
        body: JSON.stringify({"body": nestedBody, "parent_id": parent_id}),
        credentials: 'same-origin'
      })
      .then(response => response.json())
        .then(data => {
            var commentListBox = document.querySelector("#comment-list-box-" + data["poem_id"]);
            console.log(commentListBox)
            var commentBody = document.querySelector("#body").value = "";
            var commentForm = document.querySelector("#comment-form-" + data["poem_id"]);
            console.log("Comment Form Body", commentForm.body.value)
            commentForm.body.value = "";
            commentListBox.innerHTML = "";
            commentListBox.innerHTML = data["comments"].map(comment => makeComment(comment, data["can_delete"]));

        })
        .catch((error) => {
            console.log("error happened")
        });
}

function deleteComment(e, poem_id, comment_id) {
    var url = "/delete/" + poem_id + "/" + comment_id;
    fetch(url, {
        method: 'GET', // or 'PUT'
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
      })
      .then(response => response.json())
        .then(data => {
            console.log(data)
            var commentListBox = document.querySelector("#comment-list-box-" + data["poem_id"]);
            commentListBox.innerHTML = "";
            commentListBox.innerHTML = data["comments"].map(comment => makeComment(comment, data["can_delete"]));
        })
        .catch((error) => {
            console.error(error)
            // window.location.replace("/auth/login")
        });
}

function makeComment(comment, can_delete=false) {
    return `
    <p class="box has-background-light mt-0" style="border-left: 3px solid ${comment.color}; max-width: ${comment.width}%; margin-left: ${comment.margin}%;">
    <small class="mb-0"><a href="/user/${comment.author}">${comment.author}</a> ${comment.parent_author ? 'replied to <a href="/user/' + comment.parent_author + '">' + comment.parent_author + '</a>': '' }</small> <small>${moment(comment.created_at).format('LLL')}</small>
    ${can_delete ? '<button onclick="deleteComment(event, '  + comment.poem_id + ', ' + comment.id + ')" class="button is-small is-danger is-rounded is-pulled-right">delete</button>' : ''}
    <br>
    <span class="is-size-6">${comment.body}</span>
    <br>
    <i class="fa fa-reply ml-5" aria-hidden="true"></i>
    <a class="ml-1" onclick="commentReply(event, ${comment.id}, ${comment.poem_id})">Reply</a>
    <small> ${comment.replies_count} replies</small>
</p>`
}


