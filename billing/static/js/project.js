let filterButton = $('#filter_button');
let usernameInput = $('#id_username');

usernameInput.keyup(function (event) {
    check_username(usernameInput.val().length);
});


function check_username(length){
    if (length > 0){
        filterButton.prop( "disabled", false );
    }else {
        filterButton.prop( "disabled", true );
    }
}

check_username(usernameInput.val().length);
