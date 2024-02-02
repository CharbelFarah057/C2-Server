document.addEventListener('click', function(event) {
    if (event.target.classList.contains('send-btn')) {
        var threadUuid = event.target.getAttribute('data-thread-uuid');
        sendCommand(threadUuid);
    }
});

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('delete-btn')) {
        var threadUuid = event.target.getAttribute('data-thread-uuid');
        deleteBot(threadUuid);
    }
});

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('execute-btn')) {
        var xhr = new XMLHttpRequest();
        var command = document.getElementById('execute-all-input').value;
        xhr.open("POST", "/api/execute_all", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify({command: command}));
        xhr.onload = function() {
            if (xhr.status === 200) {
                location.reload();
            } else {
                alert("Error sending command");
            }
        };
    }
})

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('toggle-output')) {
        var threadUuid = event.target.getAttribute('data-thread-uuid');
        var outputRow = document.getElementById('output-row-' + threadUuid);
        if (outputRow.style.display === 'none') {
            outputRow.style.display = 'table-row';
            event.target.textContent = '↑'; // Change arrow direction
        } else {
            outputRow.style.display = 'none';
            event.target.textContent = '↓'; // Change arrow direction
        }
    }
});


function sendCommand(threadUuid) {
    var command = document.getElementById('input-command-' + threadUuid).value;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/" + threadUuid + "/execute_command", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify({command: command}));

    xhr.onload = function() {
        if (xhr.status === 200) {
            location.reload()
        } else {
            alert("Error sending command");
        }
    };
}

function deleteBot(threadUuid) {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/api/" + threadUuid + "/delete_bot", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send();

    xhr.onload = function() {
        if (xhr.status === 200) {
            window.location.reload(true);
        } else {
            alert("Error deleting bot");
        }
    };
}

// setTimeout(function(){
//     location.reload();
// }, 3000);