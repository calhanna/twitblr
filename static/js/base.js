console.log('external scripts file loaded')

// Initialise Quill

var BackgroundClass = Quill.import('attributors/class/background');
var ColorClass = Quill.import('attributors/class/color');
var SizeStyle = Quill.import('attributors/style/size');
Quill.register(BackgroundClass, true);
Quill.register(ColorClass, true);
Quill.register(SizeStyle, true);

var reply_editors = {};

// Preserve scroll position
document.addEventListener("DOMContentLoaded", function(event) { 
    var scrollpos = localStorage.getItem('scrollpos');
    if (scrollpos) window.scrollTo(0, scrollpos);
});

window.onbeforeunload = function(e) {
    localStorage.setItem('scrollpos', window.scrollY);
};

// Other JS

function Display_Overlay() {
    var overlay = document.getElementById('auth-overlay');
    overlay.classList.toggle("hidden");
}

function Show_Replies(id) {
    var container = document.getElementById("replies-"+ id);
    container.classList.toggle('minimised');
}

function Show_Post_Creator() {
    var post_creator = document.getElementsByClassName("create-post")[0];
    post_creator.classList.toggle('hidden');
}

// Updating post likes
$('.like-button, .dislike-button').on('click', function(e){
    if (user == "None") {
        Display_Overlay();
    } else {

        var button = this;
        if (button.classList.contains('dislike-button')) {
            var action = "Dislike";
        } else {
            var action = "Like";
        }
        $.ajax(
            {
                data: {
                    post_id : this.classList[1],
                    like: action,
                },
                type : 'POST',
                url : add_likes_url
            }
        )
        .done(
            function(data){
                if (data.success) {
                    var buttons = document.getElementsByClassName(button.classList[1]);
                    buttons[1].innerHTML = "<i class='fa fa-thumbs-up' aria-hidden='true'></i>  " + data.like_count;
                    buttons[2].innerHTML = "<i class='fa fa-thumbs-down' aria-hidden='true'></i>  " + data.dislike_count;
                    if (buttons[1] == button) {
                        buttons[1].classList.add("activated");
                    } else {
                        buttons[1].classList.remove("activated");
                    }
                    if (buttons[2] == button) {
                        buttons[2].classList.add("activated");
                    } else {
                        buttons[2].classList.remove("activated");
                    }
                } else {
                    document.getElementById('auth-overlay').classList.toggle('hidden');
                }
                //ColouriseButtons();
            }
        )
        e.preventDefault();
    }

});

// Validate 
function ValidatePost() {
    var post_body = document.getElementById('post-body');

    // Expand post body to fit text
    post_body.style.height = "";
    post_body.style.height = post_body.scrollHeight + 3 + "px";

    // Check character count, update counter
    var length = post_body.innerText.length;
    document.getElementById('counter').innerHTML = length + '/255';
    if (length > 255 || length == 0) {
        counter.style.color = 'red';
        document.getElementById('post-submit').disabled=true;
    } else {
        counter.style.color = 'green';
        document.getElementById('post-submit').disabled=false;
    }
}

function Show_Reply_Creator(parent){
    if (window.user == "None") {
        Display_Overlay();
    } else {
        // Minimise all the other editors
        let all_editors = document.getElementsByClassName("reply-row");
        for (let i = 0; i < all_editors.length; i++) {
            all_editors[i].classList.add("minimised");
        }

        // This function needs to create a new quill editor to write a reply and unminimise the reply row
        let post_id = parent.classList[1];
        let reply_row = document.getElementById('reply-row' + post_id);
        reply_row.classList.toggle('minimised');
        // Create quill editor
        let editor = new Quill('#post-body' + post_id, {
            modules: { toolbar: '#toolbar'+post_id },
            theme: 'snow',
        });
        reply_editors[post_id] = editor;
        console.log(editor)
    }
}

$('.reply-form').submit(function(e) {
    let classList = $(this).attr("class")
    let classArr = classList.split(/\s+/);
    let post_num = classArr[1];
    let editor = reply_editors[post_num];
    let post_body = editor.root.innerHTML;
    let raw_body = editor.root.innerText;
    $.post(create_post_url, {post_content: post_body, reply_id: post_num, stripped_content: raw_body}, function(result){
        console.log(result);
        location.reload();
    });
})


function createElementFromHTML(htmlString) {
    // Stackoverflow code. Creates an html element from a string
    var div = document.createElement('div');
    div.innerHTML = htmlString.trim();

    return div.firstChild;
}

function SendMessage(form) {
    // Send message FUNction. Ajax, also uses fancy button.
    let form_data = form.children('input').last().val()
    console.log(form)
    let classList = form.attr('class').split(/\s+/) // i hate jquery
    let convo_body = form.parent().prev() 
    $.ajax(
        {
            data: {
                message_body: form_data,
                convo_id: parseInt(classList[1])
            },
            type: 'POST',
            url: send_message_url
        }
    )
    .done( function(result) {
        console.log(result["html"])
        convo_body.append(result['html'])
        let latest_message = convo_body.children().last()
        form.children('input').val("")
        convo_body.scrollTop(latest_message.offset().top)
    }
    )
}

$('.convo-submit').on("click", function(e) {
    SendMessage($(this).parent())
})

// Because the messenger body is no longer a <form>, we have to reverse engineer the enter key functionality
$('.messager-form').keyup(function(e){
    if(e.keyCode == 13)
    {
        $(this).children().last().click()
    }
});