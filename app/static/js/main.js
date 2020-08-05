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
fileInput.onchange = () => {
    if (fileInput.files.length > 0) {
    const fileName = document.querySelector('#file-js-example .file-name');
    fileName.textContent = fileInput.files[0].name;
    }
}