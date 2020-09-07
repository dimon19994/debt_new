$("button[name='btn_delete_person']").click(function() {

    var data = { person_id : $(this).data('person_id')}

    $.ajax({
      type: 'POST',
      url: "/delete_person",
      data: data,
      dataType: "text",
      success: function(resultData) {
          location.replace('/login');
      }
});
});


$("button[name='btn_edit_person']").click(function() {

    window.location = "edit_person?person_id="+$(this).data('person_id');

});

$("button[name='btn_detail_event']").click(function() {

    window.location = "detail_event?event_id="+$(this).data('event_id');

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
        dataType: "JSON",
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
        dataType: "JSON",
        success: function (resultData) {
            location.replace(resultData["href"]);
        }
    });
});
