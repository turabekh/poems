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
        url = "/poems/unlike/" + id
    } else {
        url = "/poems/like/" + id
    }

    fetch(url, {
        method: 'POST', // or 'PUT'
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({"user_id": userId}),
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
        console.error('Error:', error);
        });
}

function makeLikeStr(value) {

}