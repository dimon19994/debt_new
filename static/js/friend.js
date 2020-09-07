$("button[name='btn_delete_friend']").click(function () {

    var data = {person_id: $(this).data('person_id')}

    $.ajax({
        type: 'POST',
        url: "/delete_friend",
        data: data,
        dataType: "text",
        success: function (resultData) {
            location.replace('/friends');
        }
    });
});


$("button[name='btn_deny_friend']").click(function () {

    var data = {person_id: $(this).data('person_id')}

    $.ajax({
        type: 'POST',
        url: "/deny_friend",
        data: data,
        dataType: "text",
        success: function (resultData) {
            location.replace('/friends');
        }
    });
});


$("button[name='btn_except_friend']").click(function () {

    var data = {person_id: $(this).data('person_id')}

    $.ajax({
        type: 'POST',
        url: "/except_friend",
        data: data,
        dataType: "text",
        success: function (resultData) {
            location.replace('/friends');
        }
    });
});


