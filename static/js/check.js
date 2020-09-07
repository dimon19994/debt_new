$("button[name='btn_delete_check']").click(function () {

    var data = {check_id: $(this).data('check_id')}

    $.ajax({
        type: 'POST',
        url: "/delete_check",
        data: data,
        dataType: "text",
        success: function (resultData) {
            location.replace('/checks');
        }
    });
});

$("button[name='btn_edit_check']").click(function () {

    window.location = "edit_check?check_id=" + $(this).data('check_id');

});

$("button[name='btn_new_check']").click(function () {

    window.location = "new_check?event_id=" + $(this).data('event_id');

});

$("button[name='btn_detail_check']").click(function () {

    window.location = "detail_check?check_id=" + $(this).data('check_id');

});

