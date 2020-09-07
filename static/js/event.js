$("button[name='btn_delete_event']").click(function() {

    var data = { event_id : $(this).data('event_id')}

    $.ajax({
      type: 'POST',
      url: "/delete_event",
      data: data,
      dataType: "text",
      success: function(resultData) {
          location.replace('/events');
      }
});
});


$("button[name='btn_detail_event']").click(function() {

    window.location = "detail_event?event_id="+$(this).data('event_id');

});

$("button[name='btn_new_event']").click(function() {

    window.location = "new_event";

});

$("button[name='btn_edit_event']").click(function() {

    window.location = "edit_event?event_id="+$(this).data('event_id');

});

$("button[name='btn_new_check']").click(function() {

    window.location = "new_check?event_id="+$(this).data('event_id');

});

$("button[name='btn_repay']").click(function() {

    window.location = "new_repay?event_id="+$(this).data('event_id');

});

$("button[name='btn_deny_repay']").click(function () {

    var data = {repay_id: $(this).data('repay_id')}

    $.ajax({
        type: 'POST',
        url: "/deny_repay",
        data: data,
        dataType: "text",
        success: function (resultData) {
            location.reload();
        }
    });
});


$("button[name='btn_except_repay']").click(function () {

    var data = {repay_id: $(this).data('repay_id')}

    $.ajax({
        type: 'POST',
        url: "/except_repay",
        data: data,
        dataType: "text",
        success: function (resultData) {
            location.reload();
        }
    });
});